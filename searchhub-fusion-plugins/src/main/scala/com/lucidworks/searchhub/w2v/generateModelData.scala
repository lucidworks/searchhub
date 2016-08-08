import com.lucidworks.searchhub.analytics.AnalyzerUtils._
import com.lucidworks.searchhub.analytics._
import org.apache.spark.sql.SQLContext
import java.io._
import com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.PrepareFile
import sys.process._
import com.lucidworks.apollo.spark.SparkJobConfig.newId

/***
  * This file is not meant to be imported or loaded in any way - instead, use the lines here inside of
  * the spark shell ($FUSION_HOME/bin/spark-shell).
  * You'll already have a "val sqlContext: SQLContext" in scope, so you can work your way down
  * this file, bit by bit.  It's encapsulated in an object so that it compiles, and if code changes that makes this
  * file not compile, it shows that this example code needs updating.
  */
object generateModelData {
  val sqlContext: SQLContext = ???
  val sc: org.apache.spark.SparkContext = ???
  //Setup our Solr connection
  val opts = Map("zkhost" -> "localhost:9983", "collection" -> "lucidfind", "query" -> "*:*",
    "fields" -> "id,body,title,subject,publishedOnDate,project,content")

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
  //'textColumnName', and pass it to tokenizer. this is a function

  val vectorizedMail = TfIdfVectorizer.vectorize(mailDF, vectorizer, textColumnName)
  //vectorizedMail is a dataframe, with an additional column body_vect
  vectorizedMail.cache()




  //serialization for idf Map,  the data is at the directory bin
  //val file=new File("modelId/idfMapData")
  val filedir=new File("modelId")
  filedir.mkdir()
  val idfMapData=new File(filedir,"idfMapData")
  //val w2vModelData=new File(filedir,"w2vModelData");
  val bw=new BufferedWriter(new FileWriter(idfMapData))
  vectorizer.idfs.foreach(line=>bw.write(line._1+","+line._2+"\n"))
  bw.close()

  //make w2v model
  val w2vModel = ManyNewsgroups.buildWord2VecModel(vectorizedMail, tokenizer, textColumnName)
  //serialization w2v model
  w2vModel.save(sc, "modelId/w2vModelData")
  //deserialize w2v model and run it
  //val newW2vModel=Word2VecModel.load(sc,"modelId/w2vModelData")
  PrepareFile.createZipFile//create the zip file
  "curl -u admin:password123 -X DELETE http://localhost:8764/api/apollo/blobs/modelId28" !

  "curl -u admin:password123 -X PUT --data-binary @modelId.zip -H Content-type:application/zip http://localhost:8764/api/apollo/blobs/modelId28?modelType=com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.W2VRelatedTerms" ! //send the zip file to blob

}
