package com.lucidworks.searchhub.recommender

import org.apache.spark.sql.{SQLContext, Row, DataFrame}
import org.slf4j.LoggerFactory

case class UserId(id: String)
case class ItemId(id: String)
case class Pref(userId: UserId, itemId: ItemId, weight: Double)

case class ItemSim(itemId1: ItemId, itemId2: ItemId, weight: Double)
case class UnStructSim(itemId1: String, itemId2: String, weight_d: Double)

object SimpleTwoHopRecommender extends Serializable {
  val log = LoggerFactory.getLogger("SimpleTwoHopRecommender")

  def itemRecs(userItemMatrix: DataFrame, userIdCol: String, itemIdCol: String, weightCol: String,
              recsPerItem: Int = 10, outerProductLimit: Int = 100): DataFrame = {
    val toPref = (row: Row) =>
      Pref(UserId(row.getAs[String](userIdCol)), ItemId(row.getAs[String](itemIdCol)), row.getAs[Double](weightCol))
    val prefMatrix = userItemMatrix.rdd.map(toPref)
    if (log.isDebugEnabled) {
      log.debug(s"using ${prefMatrix.count()} preferences to compute item similarity recs")
    }
    val matrixProduct = prefMatrix.groupBy(_.userId).flatMap { case (userId, prefs) =>
      val topPrefs = prefs.toList.sortBy(-_.weight).take(outerProductLimit)
      for {
        pref1 <- topPrefs
        pref2 <- topPrefs
        if pref1.itemId != pref2.itemId
      } yield {
        ItemSim(pref1.itemId, pref2.itemId, pref1.weight * pref2.weight)
      }
    }
    if (log.isDebugEnabled) {
      log.debug(s"total num outer product of prefs: ${matrixProduct.count()}")
    }
    val matrixSumReduced = matrixProduct.groupBy(sim => (sim.itemId1, sim.itemId2)).map { case (_, sims: Iterable[ItemSim]) =>
      sims.reduce { (s1: ItemSim, s2: ItemSim) => s1.copy(weight = s1.weight + s2.weight) }
    }
    if (log.isDebugEnabled) {
      log.debug(s"reduced outer product size: ${matrixSumReduced.count()}")
    }
    val recs = matrixSumReduced.groupBy(_.itemId1).mapValues(_.toList.sortBy(-_.weight).take(recsPerItem)).flatMap(_._2)
    val unStructRecs = recs.map(s => UnStructSim(s.itemId1.id, s.itemId2.id, s.weight))
    if (log.isDebugEnabled) {
      log.debug(s"total numRecs: ${unStructRecs.count()}")
    }
    import userItemMatrix.sqlContext.implicits._
    unStructRecs.toDF.withColumnRenamed("itemId1", "rec_for_" + itemIdCol).withColumnRenamed("itemId2", itemIdCol)
  }

  def runRecs(sqlContext: SQLContext, recsPerItem: Int = 10, outerProductLimit: Int = 100) = {
    val opts = Map("zkhost" -> "localhost:9983", "collection" -> "lucidfind_signals_aggr", "query" -> "*:*")
    val tmpDF = sqlContext.read.format("solr").options(opts).load
    // TODO: fix to use threadId, once that's working
    val recs = SimpleTwoHopRecommender.itemRecs(tmpDF,
      "from_email_s", "subject_simple_s", "weight_d", recsPerItem, outerProductLimit)
    //TODO: include / not include "review request" messages?
    val finalRecs = recs//.filter(not($"rec_for_subject_simple_s".contains("review request"))).filter(not($"subject_simple_s".contains("review request")))
    val totalRecsCount = finalRecs.count()
    finalRecs.write.format("solr").options(Map("zkhost" -> "localhost:9983", "collection" -> "lucidfind_thread_recs")).mode(org.apache.spark.sql.SaveMode.Overwrite).save
    com.lucidworks.spark.util.SolrSupport.getCachedCloudClient("localhost:9983").commit("lucidfind_thread_recs")
    totalRecsCount
  }
}
// SimpleTwoHopRecommender.runRecs(sqlContext)