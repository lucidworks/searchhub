import sys.process._
import com.lucidworks.searchhub.analytics.AnalyzerUtils._
import com.lucidworks.searchhub.analytics._
import org.apache.spark.sql.SQLContext
import java.io._
import com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.PrepareFile

/***
  * This file is not meant to be imported or loaded in any way
  * it is a copy of the scripts included in python/fusion_config/w2v_job.json
  */
object generateModelData {
  val sqlContext: SQLContext = ???
  val sc: org.apache.spark.SparkContext = ???
  val opts = Map("zkhost" -> "localhost:9983", "collection" -> "lucidfind", "query" -> "*:*","fields" -> "id,body,title,subject,publishedOnDate,project,content")
  val mailDF = sqlContext.read.format("solr").options(opts).load
  mailDF.cache()
  mailDF.count()
  val textColumnName = "body"
  val tokenizer = analyzerFn(noHTMLstdAnalyzerSchema)
  val vectorizer = TfIdfVectorizer.build(mailDF, tokenizer, textColumnName)
  val vectorizedMail = TfIdfVectorizer.vectorize(mailDF, vectorizer, textColumnName)
  vectorizedMail.cache()
  val filedir=new File("modelId")
  filedir.mkdir()
  val idfMapData=new File(filedir,"idfMapData")
  if(idfMapData.exists)"rm -rf modelId/idfMapData"!

  sc.parallelize(vectorizer.idfs.toSeq).saveAsTextFile("modelId/idfMapData")
  val w2vModel = ManyNewsgroups.buildWord2VecModel(vectorizedMail, tokenizer, textColumnName)
  val w2vModelFile=new File("modelId/w2vModelData")
  if(w2vModelFile.exists)"rm -rf modelId/w2vModelData"!

  w2vModel.save(sc, "modelId/w2vModelData")
  PrepareFile.createZipFile
  "curl -u admin:password123 -X DELETE http://localhost:8764/api/apollo/blobs/modelId666" !

  //the username and password below is hard coded.. may need to find some API to call and get them..
  "curl -u admin:password123 -X PUT --data-binary @modelId.zip -H Content-type:application/zip "+"http://localhost:8764/api/apollo/blobs/modelId666?modelType=com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.W2VRelatedTerms" !
}
