package com.lucidworks.searchhub.recommender

import org.apache.spark.sql.{Row, DataFrame}
case class UserId(id: String)
case class ItemId(id: String)
case class Pref(userId: UserId, itemId: ItemId, weight: Double)

case class ItemSim(itemId1: ItemId, itemId2: ItemId, weight: Double)
case class UnStructSim(itemId1: String, itemId2: String, weight_d: Double)
object SimpleTwoHopRecommender extends Serializable {

  def itemRecs(userItemMatrix: DataFrame, userIdCol: String, itemIdCol: String, weightCol: String,
              recsPerItem: Int = 10, outerProductLimit: Int = 100): DataFrame = {
    val toPref = (row: Row) =>
      Pref(UserId(row.getAs[String](userIdCol)), ItemId(row.getAs[String](itemIdCol)), row.getAs[Double](weightCol))
    val prefMatrix = userItemMatrix.rdd.map(toPref)
    val matrixProduct = prefMatrix.groupBy(_.userId).flatMap { case (userId, prefs) =>
      val topPrefs = prefs.toList.sortBy(-_.weight).take(outerProductLimit)
      for {
        pref1 <- prefs
        pref2 <- prefs
        if pref1.itemId != pref2.itemId
      } yield {
        ItemSim(pref1.itemId, pref2.itemId, pref1.weight * pref2.weight)
      }
    }
    val matrixSumReduced = matrixProduct.groupBy(sim => (sim.itemId1, sim.itemId2)).map { case (_, sims: Iterable[ItemSim]) =>
      sims.reduce { (s1: ItemSim, s2: ItemSim) => s1.copy(weight = s1.weight + s2.weight) }
    }
    val recs = matrixSumReduced.groupBy(_.itemId1).mapValues(_.toList.sortBy(-_.weight).take(recsPerItem)).flatMap(_._2)
    val unStrucRecs = recs.map(s => UnStructSim(s.itemId1.id, s.itemId2.id, s.weight))
    import userItemMatrix.sqlContext.implicits._
    unStrucRecs.toDF.withColumnRenamed("itemId1", "rec_for_" + itemIdCol).withColumnRenamed("itemId2", itemIdCol)
  }
}
/*
 val opts = Map("zkhost" -> "localhost:9983", "collection" -> "lucidfind_signals_aggr", "query" -> "*:*")
 val tmpDF = sqlContext.read.format("solr").options(opts).load
 val recs = SimpleTwoHopRecommender.itemRecs(tmpDF, "from_email_s", "subject_simple_s", "weight_d", 10, 100)
 import sqlContext.implicits._
 import org.apache.spark.sql.functions._
 val finalRecs = recs.filter(not($"rec_for_subject_simple_s".contains("review request"))).filter(not($"subject_simple_s".contains("review request")))
 finalRecs.write.format("solr").options(Map("zkhost" -> "localhost:9983", "collection" -> "lucidfind_thread_recs")).mode(org.apache.spark.sql.SaveMode.Overwrite).save
 com.lucidworks.spark.util.SolrSupport.getCachedCloudClient("localhost:9983").commit("lucidfind_thread_recs")
 */