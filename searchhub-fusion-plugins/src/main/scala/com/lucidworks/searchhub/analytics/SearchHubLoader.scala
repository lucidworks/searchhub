package com.lucidworks.searchhub.analytics

import java.io.File
import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.{DataFrame, SQLContext}

import scala.io.Source
import scala.util.Random

object SearchHubLoader {
  val projects = Set("lucene", "hadoop", "hive", "hbase", "nutch", "spark", "mahout", "pig", "kafka", "zookeeper",
    "uima", "oozie", "tika", "accumulo", "manifoldcf", "mesos")
  case class Config(sqlContext: SQLContext, options: Map[String, String] = opts())

  def opts(zkHost: String = "localhost:9983", collection: String = "lucidfind", query: String ="lucidfind") =
    Map("zkhost" -> zkHost, "collection" -> collection, "query" -> query)

  def load(sqlContext: SQLContext, opts: Map[String, String]) = loadFromSolr(Config(sqlContext, opts))

  def loadFromSolr(config: Config): DataFrame = config.sqlContext.read.format("solr").options(config.options).load

  def loadMessages(config: Config): RDD[MailMessage] = {
    config.options.get("localMirrorBaseDir") match {
      case (Some(baseDir)) => loadFromLocalDir(baseDir,
        config.sqlContext.sparkContext,
        config.options.getOrElse("sampleSize", "1000").toInt,
        config.options.getOrElse("seed", "1234").toLong)
      case None => loadFromSolr(config).map(MailMessage.fromRow)
    }
  }

  def loadFromLocalDir(baseDir: String, sparkContext: SparkContext, sampleSize: Int, seed: Long) = {
    println("loading mail files from: " + baseDir)
    val rnd = new Random(seed)
    println("using seed: " + seed)
    val subDirs = baseDir.split(",").toList
    val subRdds = for { dir <- subDirs } yield {
      val topLevel = new File(dir).listFiles()
        .map(f => (projectFromList(listFromPath(f.getAbsolutePath)), f.getAbsolutePath))
        .filter(p => projects.contains(p._1))
        .groupBy(_._1)
        .mapValues(_.map(_._2))
      val messageRdds = for {(project, topLevelSubDirs) <- topLevel} yield {
        println(s"loading messages from: ${topLevelSubDirs.mkString("[", ", ", "]")}")
        val files = topLevelSubDirs.flatMap(deepFilePaths)
        println(s"found ${files.length}, but taking sample of $sampleSize of them")
        val sampleFiles = files.map((_, rnd.nextDouble())).sortBy(_._2).map(_._1).take(sampleSize)
        sparkContext.parallelize(sampleFiles.flatMap(f =>
          MailMessage.fromRawString(f, Source.fromFile(f).getLines().mkString("\n"))).toList)
      }
      messageRdds
    }
    println("returning union of grouped message RDDs")
    val rdds = subRdds.toList.flatten
    sparkContext.union(rdds)
  }

  def recursiveListFiles(f: File): Array[File] = {
    Option(f.listFiles)
      .map(t => t ++ t.filter(_.isDirectory).flatMap(recursiveListFiles))
      .getOrElse(Array.empty[File])
  }

  def listFromPath(path: String) = {
    val parts = path.split("/")
    parts(parts.indexOf("mod_mbox") + 1)
  }

  def projectFromList(list: String) = {
    list.split("-").head match {
      case ("incubator") => list.split("-")(1)
      case h => h
    }
  }

  def deepFilePaths(base: String) = recursiveListFiles(new File(base)).filterNot(_.isDirectory).map(_.getAbsolutePath)
}
