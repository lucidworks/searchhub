import com.lucidworks.searchhub.analytics.AnalyzerUtils._
import com.lucidworks.searchhub.analytics._
import com.lucidworks.spark.util.SolrSupport
import org.apache.spark.ml.classification.RandomForestClassifier
import org.apache.spark.ml.param.IntParam
import org.apache.spark.mllib.linalg.{Vector => SparkVector}
import org.apache.spark.sql.SQLContext
import org.apache.spark.sql.functions._


/***
  * This file is not meant to be imported or loaded in any way - instead, use the lines here inside of
  * the spark shell ($FUSION_HOME/bin/spark-shell).
  * You'll already have a "val sqlContext: SQLContext" in scope, so you can work your way down
  * this file, bit by bit.  It's encapsulated in an object so that it compiles, and if code changes that makes this
  * file not compile, it shows that this example code needs updating.
  */
object SparkShellHelpers {
  val sqlContext: SQLContext = ???
  //Setup our Solr connection
  val opts = Map("zkhost" -> "localhost:9983/lwfusion/3.0.0/solr", "collection" -> "lucidfind", "query" -> "*:*")

  //Try this if you want to get rid of the JIRA bot noise in the index, this tends to lead to better
  //clusters, since the Jenkins/JIRA file handling is pretty primitive so far and thus skews the clusters

  /*
  val opts = Map("zkhost" -> "localhost:9983", "collection" -> "lucidfind", "query" -> "isBot:false",
   "fields" -> "id,body,title,subject,publishedOnDate,project,content”)
   */

  val tmpDF = sqlContext.read.format("solr").options(opts).load
  //Change this depending on how many mail messages you have loaded.  The current settings
  //were based on about 200K messages loaded and wanting the results to finish in a minute or two
  val mailDF = tmpDF.sample(false, 0.2)
  mailDF.cache()
  //materialize the data so that we don't have to hit Solr every time
  mailDF.count()

  val textColumnName = "body"

  val tokenizer = analyzerFn(noHTMLstdAnalyzerSchema)

  val vectorizer = TfIdfVectorizer.build(mailDF, tokenizer, textColumnName)

  val vectorizedMail = TfIdfVectorizer.vectorize(mailDF, vectorizer, textColumnName)
  vectorizedMail.cache()
  //Build a k-means model of size 20
  val kmeansModel = ManyNewsgroups.buildKmeansModel(vectorizedMail, k = 20, maxIter = 10, textColumnName)
  //Join the centroid ids back to the mail, so we can update them in Solr if we want
  val mailWithCentroids = kmeansModel.transform(vectorizedMail)
  mailWithCentroids.groupBy("kmeans_cluster_i").count().show()
  //kmeansModel.clusterCenters.foreach(v => println(f"${math.sqrt(ManyNewsgroups.normSquaredL2(v))}%.2f")

  //Save to Solr if you want
  mailWithCentroids.write.format("solr").options(Map("zkhost" -> "localhost:9983/lwfusion/3.0.0/solr", "collection" -> "lucidfind", "batch_size" -> "1000")).mode(org.apache.spark.sql.SaveMode.Overwrite).save
  // If you want to commit, run these
  SolrSupport.getCachedCloudClient("localhost:9983/lwfusion/3.0.0/solr").commit("lucidfind")

  //Do some cluster analysis to get a feel for what the clusters look like.
  val lenFn = (v: SparkVector) => v.numNonzeros
  val lenUdf = udf(lenFn)
  val withVectLength = mailWithCentroids.withColumn("vect_len", lenUdf(mailWithCentroids("body_vect")))
  withVectLength.groupBy("kmeans_cluster_i").avg("vect_len").show()


  //Build a topic model using Latent Dirichlet Allocation
  val ldaModel = ManyNewsgroups.buildLDAModel(vectorizedMail, k = 5, textColumnName)
  //Get the actual topics
  val topicTerms = ManyNewsgroups.tokensForTopics(ldaModel, vectorizer)
  topicTerms.foreach { case(topicId, list) => println(s"$topicId : ${list.map(_._1).take(10).mkString(",")}") }

  //Enrich our terms by building a Word2Vec model
  val w2vModel = ManyNewsgroups.buildWord2VecModel(vectorizedMail, tokenizer, textColumnName)
  w2vModel.findSynonyms("query", 5).take(5)

  val Array(trainingData, testData) = vectorizedMail.randomSplit(Array(0.8, 0.2), 123L)

  val labelColumnName = "project"
  //Do some classification on the projects.  This is like 20 Newsgroups (http://kdd.ics.uci.edu/databases/20newsgroups/20newsgroups.data.html) on steriods
  val paramGrids: Map[RandomForestClassifier => IntParam, Array[Int]] =
    Map(
      ((rf: RandomForestClassifier) => rf.maxDepth) -> Array(5, 10, 20),
      ((rf: RandomForestClassifier) => rf.maxBins) -> Array(8, 16, 32),
      ((rf: RandomForestClassifier) => rf.numTrees) -> Array(50, 100)
    )
  val (randomForestModel, randomForestMetrics) =
    ManyNewsgroups.trainRandomForestClassifier(trainingData, testData, labelColumnName, textColumnName, paramGrids)

  //For each document, find 5 top terms(by tfidf) and 2 of their synonyms(by w2v model), store them in 'topSyns'
  //output schema looks like following
  /*
  root
 |-- id: string (nullable = false)
 |-- body: string (nullable = true)
 |-- title: string (nullable = true)
 |-- subject: string (nullable = true)
 |-- publishedOnDate: timestamp (nullable = false)
 |-- project: string (nullable = true)
 |-- content: string (nullable = true)
 |-- body_vect: vector (nullable = true)
 |-- topSyns: array (nullable = true)
 |    |-- element: struct (containsNull = true)
 |    |    |-- _1: string (nullable = true)
 |    |    |-- _2: array (nullable = true)
 |    |    |    |-- element: string (containsNull = true)
 */
  def findSyn = (a: String) => w2vModel.findSynonyms(a,2).map(_._1)
  def getTopSyns = (t: SparkVector) => t.toArray.zipWithIndex.sortBy(-_._1).take(5).map(_._2).flatMap(vectorizer.dictionary.map(_.swap).get).map(a => (a, findSyn(a)))
  def getTopSynsUdf = udf(getTopSyns)
  vectorizedMail.withColumn("topSyns", getTopSynsUdf(vectorizedMail("body_vect"))).take(5)
}
