import com.lucidworks.searchhub.analytics.AnalyzerUtils._
import com.lucidworks.searchhub.analytics._
import com.lucidworks.spark.util.SolrSupport
import org.apache.spark.mllib.linalg.{Vectors, Vector => SparkVector}
import org.apache.spark.sql.SQLContext
import org.apache.spark.sql.functions._

//load schema from solr
val opts = Map("zkhost" -> "localhost:9983", "collection" -> "lucidfind", "query" -> "*:*",
    "fields" -> "id,body,title,subject,publishedOnDate,project,content")
val tmpDF = sqlContext.read.format("solr").options(opts).load

//sample a portion of data
val mailDF = tmpDF.sample(false, 0.2)
mailDF.cache()
mailDF.count()


val textColumnName = "body"
//tokenizer: String => List[String] = <function1>
//tokenizer is a function which uses LuceneTextAnalyzer as a rule to tokenize documents
val tokenizer = analyzerFn(noHTMLstdAnalyzerSchema)
//vectorizer: com.lucidworks.searchhub.analytics.TfIdfVectorizer = <function1>
val vectorizer = TfIdfVectorizer.build(mailDF, tokenizer, textColumnName)
//added a field storing vectorized body

//vectorizedMail stored all the important information, every row represents a document
//[id: string, body: string, title: string, subject: string, publishedOnDate: timestamp, project: string, content: string, body_vect: vector]
val vectorizedMail = TfIdfVectorizer.vectorize(mailDF, vectorizer, textColumnName)
vectorizedMail.cache()

val w2vModel = ManyNewsgroups.buildWord2VecModel(vectorizedMail, tokenizer, textColumnName)


/*
val l=Seq(0->2.0, 1->1.0, 2->3.0)
val t=Vectors.sparse(3, l)
t.toArray.zipWithIndex.sortWith(_._1<_._1).take(2).map(_._2)
*/
//input is a string
//output is an array of the synonyms of the string
def findSyn=(a:String)=>w2vModel.findSynonyms("query",5).select("word").map(r=>r(0).asInstanceOf[String]).collect
//input is a SparkVector which maintains the tdidf value of each term(indexed by id)(for each document)
//output is 5 top terms for each document
def getTopTerm=(t:SparkVector)=>t.toArray.zipWithIndex.sortWith(_._1>_._1).take(5).map(_._2).flatMap(vectorizer.dictionary.map(_.swap).get).map(findSyn)
//def getTopTerm=(t:SparkVector)=>t.toArray.zipWithIndex.sortWith(_._1>_._1).take(5).map(_._2).flatMap(vectorizer.dictionary.map(_.swap).get).map(e=>(e,findSyn(e)))
def getTopTermUdf=udf(getTopTerm)
vectorizedMail.withColumn("topTfidfTerm",getTopTermUdf(col("body_vect"))).show


Array("test","query").zip(Array("test","query").map(findSyn)).toMap
//change file tfidfvectorizer.scala
//first make sure the current version can run well
