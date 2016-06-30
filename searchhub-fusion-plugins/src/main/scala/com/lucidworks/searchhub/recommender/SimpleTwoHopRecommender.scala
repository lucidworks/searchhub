package com.lucidworks.searchhub.recommender

import org.apache.spark.sql.{Row, DataFrame}

object SimpleTwoHopRecommender {

  case class UserId(id: String)
  case class ItemId(id: String)
  case class Pref(userId: UserId, itemId: ItemId, weight: Double)

  case class ItemSim(itemId1: ItemId, itemId2: ItemId, weight: Double)


  def itemRecs(userItemMatrix: DataFrame, userIdCol: String, itemIdCol: String, weightCol: String): DataFrame = {
    val toPref = (row: Row) =>
      Pref(UserId(row.getAs[String](userIdCol)), ItemId(row.getAs[String](weightCol)), row.getAs[Double](weightCol))
    val prefMatrix = userItemMatrix.rdd.map(toPref)
    // key is itemId, give list of frequent users, then flatten:
    val usersPerItem = prefMatrix.groupBy(_.itemId).mapValues(_.toList.sortBy(-_.weight).take(20)).flatMap(_._2)
    // key is userId, give list of frequent items, then flatten:
    val itemsPerUser = prefMatrix.groupBy(_.userId).mapValues(_.toList.sortBy(-_.weight).take(30))

   // val x = usersPerItem.

    val matrixProduct = usersPerItem.groupBy(_.userId).join(itemsPerUser).flatMap { case (userId, (row, col)) =>
      for {
        pref1 <- row
        pref2 <- col
      } yield {
        ItemSim(pref1.itemId, pref2.itemId, pref1.weight * pref2.weight)
      }
    }
    val matrixSumReduced = matrixProduct.groupBy(sim => (sim.itemId1, sim.itemId2)).map { case (_, sims) =>
      sims.reduce { case (s1, s2) => s1.copy(weight = s1.weight + s2.weight) }
    }

    val finalRecs = matrixSumReduced.groupBy(_.itemId1).mapValues(_.toList.sortBy(-_.weight).take(10)).flatMap(_._2)
    import userItemMatrix.sqlContext.implicits._
    finalRecs.toDF.withColumnRenamed("itemId1", "rec_for_" + itemIdCol).withColumnRenamed("itemId2", itemIdCol)
  }
}
