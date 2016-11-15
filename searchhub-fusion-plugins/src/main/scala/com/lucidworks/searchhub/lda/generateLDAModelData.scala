import sys.process._
import com.lucidworks.searchhub.analytics.AnalyzerUtils._
import com.lucidworks.searchhub.analytics._
import org.apache.spark.sql.SQLContext
import java.io._
import java.util._

import org.apache.spark.storage.StorageLevel._
import com.lucidworks.spark.fusion._
import scala.collection.JavaConversions._

import org.apache.spark.ml.feature.{CountVectorizer, CountVectorizerModel}

import org.apache.spark.rdd._
import org.apache.spark.mllib.clustering.{LDA, DistributedLDAModel, LocalLDAModel}
import org.apache.spark.mllib.linalg.{Vector, Vectors}
import scala.collection.mutable

import org.apache.spark.sql.functions._

/***
  *
  * This file is not meant to be imported or loaded in any way
  * it is a copy of the scripts included in python/fusion_config/w2v_job.json
  */
object generateModelData {

  val sqlContext: SQLContext = ???
  val sc: org.apache.spark.SparkContext = ???

  val opts = scala.collection.immutable.Map("zkhost" -> "localhost:9983", "collection" -> "lucidfind", "query" -> "*:*","fields" -> "id,body,title,subject,publishedOnDate,project,content", "sample_pct" -> "0.01", "sample_seed" -> "5150")
  var mailDF = sqlContext.read.format("solr").options(opts).load

  mailDF = mailDF.repartition(50)
  mailDF.persist(MEMORY_AND_DISK)
  mailDF.count()
//  May not need stopword removal in this method as the probabilities will automatically be low
//  val finalStopwordsRemovalSchema =
//    """{ "analyzers": [
//      |  { "name": "NoStdTokLowerStop",
//      |    "charFilters": [ { "type": "htmlstrip" } ],
//      |    "tokenizer": { "type": "pattern", "pattern":"\\W|\\d", "group":"-1" },
//      |    "filters": [
//      |    { "type": "lowercase" },
//      |    { "type": "stop", "ignoreCase":"true", "words":"stopwords.txt" }] }],
//      |  "fields": [{ "regex": ".+", "analyzer": "NoStdTokLowerStop" } ]}
//    """.stripMargin

  val textColumnName = "body"
  val tokenizer = analyzerFn(noHTMLstdAnalyzerSchema)
  val vectorizer = TfIdfVectorizer.build(mailDF, tokenizer, textColumnName)
  val vectorizedMail = TfIdfVectorizer.vectorize(mailDF, vectorizer, textColumnName)
  vectorizedMail.persist(MEMORY_AND_DISK)

  val ldaModel = ManyNewsgroups.buildLDAModel(vectorizedMail, k = 5, textColumnName)
  val topicTerms = ManyNewsgroups.tokensForTopics(ldaModel, vectorizer)
  topicTerms.foreach {case(topicId, list) => println(s"$topicId : ${list.map(_._1).take(10).mkString(",")}") }

  val reverseDictionary = vectorizer.dictionary.toList.map(_.swap).toMap
  val topicDist = ldaModel.topicsMatrix
  val tokenWeights = for { k <- 0 until ldaModel.getK; i <- 0 until vectorizer.dictionary.size } yield {
    k -> (reverseDictionary(i), topicDist(i, k))
  }

  val toArray = udf[Array[String], String]( _.split(" "))
  val featureDf = mailDF.withColumn("body", toArray(mailDF("body")))

  val cvModel: CountVectorizerModel = new CountVectorizer().setInputCol("body").setOutputCol("features").setVocabSize(10).setMinDF(2).fit(featureDf)
  val newDF = cvModel.transform(featureDf)

  val rdd = newDF.rdd.zipWithIndex()
  val cvRDD = rdd.map(row => (row._2.asInstanceOf[Long], row._1(7).asInstanceOf[Vector]))

//  val cvRDD = newDF.map(row => (row(0).asInstanceOf[Int].asInstanceOf[Long], row(2).asInstanceOf[Vector]))
  val ldaModel2: DistributedLDAModel = new LDA().setK(5).setMaxIterations(20).run(cvRDD).asInstanceOf[DistributedLDAModel]
  val localLDAModel: LocalLDAModel = ldaModel2.toLocal
  val topicDistributions = localLDAModel.topicDistributions(cvRDD)

  println("first topic distribution:"+topicDistributions.first._2.toArray.mkString(", "))

  val myMap = scala.collection.immutable.Map("modelType" -> "com.lucidworks.apollo.pipeline.index.stages.searchhub.lda.LDARelatedTerms")
  val modelType = new java.util.HashMap[String, String](myMap)

  FusionMLModelSupport.saveModelInFusion("localhost:8764","admin","vishalak1964","native", sc, "ldaModel", ldaModel, modelType)
}