import com.lucidworks.searchhub.analytics.AnalyzerUtils._
import com.lucidworks.searchhub.analytics._
import com.lucidworks.spark.util.SolrSupport
import org.apache.spark.mllib.linalg.{Vector => SparkVector}
import org.apache.spark.sql.SQLContext
import org.apache.spark.sql.functions._
import scala.collection.JavaConverters._


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
  val opts = Map("zkhost" -> "localhost:9983", "collection" -> "lucidfind", "query" -> "*:*",
    "fields" -> "id,body,title,subject,publishedOnDate,project,content")

  //Try this if you want to get rid of the JIRA bot noise in the index, this tends to lead to better
  //clusters, since the Jenkins/JIRA file handling is pretty primitive so far and thus skews the clusters

  /*
  val opts = Map("zkhost" -> "localhost:9983", "collection" -> "lucidfind", "query" -> "isBot:false",
   "fields" -> "id,body,title,subject,publishedOnDate,project,content”)
   */

  val tmpDF = sqlContext.read.format("solr").options(opts).load//this is a dataframe of orignal data
  //Change this depending on how many mail messages you have loaded.  The current settings
  //were based on about 200K messages loaded and wanting the results to finish in a minute or two
  val mailDF = tmpDF.sample(false, 0.2)//this is a dataframe, sampled 20%
  mailDF.cache()
  //materialize the data so that we don't have to hit Solr every time
  mailDF.count()

  val textColumnName = "body"

  val tokenizer = analyzerFn(noHTMLstdAnalyzerSchema)//tokenizer, String => List[String] = <function1>

  val vectorizer = TfIdfVectorizer.build(mailDF, tokenizer, textColumnName)//from dataframe 'mailDF', find the column
  //'textColumnName', and pass it to tokenizer. vectorizer is a TfIdfVectorizer

  val outputMap=vectorizer.idfs.asJava
  //save the map to some place, in the form of Java's HashMap
