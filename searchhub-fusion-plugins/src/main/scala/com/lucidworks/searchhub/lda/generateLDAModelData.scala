import sys.process._
import com.lucidworks.searchhub.analytics.AnalyzerUtils._
import com.lucidworks.searchhub.analytics._
import org.apache.spark.sql.SQLContext
import java.io._
import java.util._

import org.apache.spark.storage.StorageLevel._
import com.lucidworks.spark.fusion._
import scala.collection.JavaConversions._

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

  val myMap = scala.collection.immutable.Map("modelType" -> "com.lucidworks.apollo.pipeline.index.stages.searchhub.lda.LDARelatedTerms")
  val modelType = new java.util.HashMap[String, String](myMap)

  FusionMLModelSupport.saveModelInFusion("localhost:8764","admin","vishalak1964","native", sc, "ldaModel", ldaModel, modelType)
}