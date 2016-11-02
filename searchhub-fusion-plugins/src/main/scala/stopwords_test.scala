/**
  * Created by lasyamarla on 11/1/16.
  */
import sys.process._
import com.lucidworks.searchhub.analytics.AnalyzerUtils._
import com.lucidworks.searchhub.analytics._
import org.apache.spark.sql.SQLContext
import java.io._
import com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.PrepareFileModified
import org.slf4j.impl.StaticLoggerBinder
import org.apache.spark.storage.StorageLevel._
import com.lucidworks.spark.fusion._

import com.lucidworks.spark.analysis.LuceneTextAnalyzer

val sqlContext: SQLContext = ???
val sc: org.apache.spark.SparkContext = ???

val opts = Map("zkhost" -> "localhost:9983", "collection" -> "lucidfind", "query" -> "*:*","fields" -> "id,body,title,subject,publishedOnDate,project,content", "sample_pct" -> "0.01", "sample_seed" -> "5150")
var mailDF = sqlContext.read.format("solr").options(opts).load
mailDF = mailDF.repartition(50)
mailDF.persist(MEMORY_AND_DISK)
mailDF.count()


val simple_removal_schema = """{ "analyzers": [{ "name": "StdTokLowerStop",
               |                  "tokenizer": { "type": "standard" },
               |                  "filters": [{ "type": "lowercase" },
               |                              { "type": "stop" }] }],
               |  "fields": [{ "name": "simple_stopwords", "analyzer": "StdTokLowerStop" } ]}
             """.stripMargin

val partial_removal_schema = """{ "analyzers": [{ "name": "StdTokLowerStop",
                               |                  "tokenizer": { "type": "standard" },
                               |                  "filters": [{ "type": "lowercase" },
                               |                              { "type": "stop",
                               |                               "ignoreCase": "true",
                               |                               "words":"stopwords.txt"}] }],
                               |  "fields": [{ "name": "partial_stopwords", "analyzer": "StdTokLowerStop" } ]}
                             """.stripMargin

val full_removal_schema = """{ "analyzers": [{ "name": "NonStdTokLowerStop",
               |                  "tokenizer": { "type": "pattern",
               |                                 "pattern": "\\W|\\d",
               |                                 "group":"-1"},
               |                  "filters": [{ "type": "lowercase" },
               |                              { "type": "stop",
               |                               "ignoreCase": "true",
               |                               "words":"stopwords.txt"}] }],
               |  "fields": [{ "name": "detailed_stopwords", "analyzer": "NonStdTokLowerStop" } ]}
             """.stripMargin

val simple_stopword_removal_analyzer = new LuceneTextAnalyzer(simple_removal_schema)
val partial_stopword_removal_analyzer = new LuceneTextAnalyzer(partial_removal_schema)
val full_stopword_removal_analyzer = new LuceneTextAnalyzer(full_removal_schema)

// File Test
val file = sc.textFile("/Users/lasyamarla/Desktop/stopwords_test.txt")
val simple_stopwords_counts = file.flatMap(line => simple_stopword_removal_analyzer.analyze("simple_stopwords", line)).map(word => (word, 1)).reduceByKey(_ + _).sortBy(_._2, false)
val partial_stopwords_counts = file.flatMap(line => partial_stopword_removal_analyzer.analyze("partial_stopwords", line)).map(word => (word, 1)).reduceByKey(_ + _).sortBy(_._2, false)
val full_stopwords_counts = file.flatMap(line => full_stopword_removal_analyzer.analyze("full_stopwords", line)).map(word => (word, 1)).reduceByKey(_ + _).sortBy(_._2, false)


// MailDF Test
val dfString = mailDF.select("body").collect.map(_.toSeq).map(_.toString)
val wordOnesSimple = dfString.flatMap(line => simple_stopword_removal_analyzer.analyze("detailed_stopwords", line)).map(word => (word, 1))
val wordOnesSimpleRDD = sc.parallelize(wordOnesSimple).reduceByKey(_ + _).sortBy(_._2, false)

val wordOnesPartial = dfString.flatMap(line => partial_stopword_removal_analyzer.analyze("detailed_stopwords", line)).map(word => (word, 1))
val wordOnesPartialRDD = sc.parallelize(wordOnesPartial).reduceByKey(_ + _).sortBy(_._2, false)

val wordOnesFull = dfString.flatMap(line => full_stopword_removal_analyzer.analyze("detailed_stopwords", line)).map(word => (word, 1))
val wordOnesFullRDD = sc.parallelize(wordOnesFull).reduceByKey(_ + _).sortBy(_._2, false)

// MailDF Full Script (acting with full_removal)


val final_stopwords_removal_schema =
  """{ "analyzers": [
    |  { "name": "NoStdTokLowerStop",
    |    "charFilters": [ { "type": "htmlstrip" } ],
    |    "tokenizer": { "type": "pattern", "pattern":"\\W|\\d", "group":"-1" },
    |    "filters": [
    |    { "type": "lowercase" },
    |    { "type": "stop", "ignoreCase":"true", "words":"PATH TO STOPWORDS FILE" }] }],
    |  "fields": [{ "regex": ".+", "analyzer": "NoStdTokLowerStop" } ]}
  """.stripMargin

val textColumnName = "body"
val tokenizer = analyzerFn(final_stopwords_removal_schema)
val vectorizer = TfIdfVectorizer.build(mailDF, tokenizer, textColumnName)

val vectorizedMail = TfIdfVectorizer.vectorize(mailDF, vectorizer, textColumnName)
vectorizedMail.persist(MEMORY_AND_DISK)
val filedir=new File("modelId")
if(filedir.exists)"rm -rf modelId"!

filedir.mkdir()
val idfMapData=new File(filedir,"idfMapData")

sc.parallelize(vectorizer.idfs.toSeq).saveAsTextFile("modelId/idfMapData")
val w2vModel = ManyNewsgroups.buildWord2VecModel(vectorizedMail, tokenizer, textColumnName)
val w2vModelFile=new File("modelId/w2vModelData")
w2vModel.save(sc, "modelId/w2vModelData")
//call PrepareFile.createZipFile to add a metadata json file, and zip 'modelId'
PrepareFileModified.createZipAndSendFile
