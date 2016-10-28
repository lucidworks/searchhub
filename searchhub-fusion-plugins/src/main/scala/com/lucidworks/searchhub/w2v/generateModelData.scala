import sys.process._
import com.lucidworks.searchhub.analytics.AnalyzerUtils._
import com.lucidworks.searchhub.analytics._
import org.apache.spark.sql.SQLContext
import java.io._
import com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.PrepareFileModified
import org.slf4j.impl.StaticLoggerBinder
import org.apache.spark.storage.StorageLevel._
import com.lucidworks.spark.fusion._

/***
  * This file is not meant to be imported or loaded in any way
  * it is a copy of the scripts included in python/fusion_config/w2v_job.json
  */
object generateModelData {
  val sqlContext: SQLContext = ???
  val sc: org.apache.spark.SparkContext = ???
val opts = Map("zkhost" -> "localhost:9983", "collection" -> "lucidfind", "query" -> "*:*","fields" -> "id,body,title,subject,publishedOnDate,project,content", "sample_pct" -> "0.01", "sample_seed" -> "5150")
var mailDF = sqlContext.read.format("solr").options(opts).load

mailDF = mailDF.repartition(50)
mailDF.persist(MEMORY_AND_DISK)
mailDF.count()

val textColumnName = "body"
val tokenizer = analyzerFn(noHTMLstdAnalyzerSchema)
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
  //if the current zip file already exists in BLOB, delete it
  // "curl -u admin:password123 -X DELETE http://localhost:8764/api/apollo/blobs/relatedTermModel" !

  //send the zip file to BLOB
  //the username and password below is hard coded.. may need to find some API to call and get them..
  // "curl -u admin:password123 -X PUT --data-binary @modelId.zip -H Content-type:application/zip "+"http://localhost:8764/api/apollo/blobs/relatedTermModel?modelType=com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.W2VRelatedTerms" !
}