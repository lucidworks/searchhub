package com.lucidworks.searchhub.analytics

import org.apache.spark.rdd.RDD
import org.apache.spark.sql.{Row, DataFrame}


object MailThreadJob {

  // simple struct to let us do the grouping
  case class MessageThreadItem(id: String, subjectSimple: String, inReplyTo: String, threadId: String, thread_size_i: Int = 0)

  // TODO: apply this to all IDs in the index!
  val normalizeId = (id: String) => Option(id).map(_.split("/").last.replaceAll(" ", "+")).getOrElse(id)

  val rowToMessageThreadItem = (row: Row) => MessageThreadItem(
    normalizeId(row.getAs[String]("id")),
    row.getAs[String]("subject_simple"),
    row.getAs[String]("in_reply_to"),
    row.getAs[String]("threadId")
  )

  def createThreadGroups(mailDataFrame: DataFrame, alwaysOverride: Boolean = false): DataFrame = {
    import org.apache.spark.sql.functions._
    import mailDataFrame.sqlContext.implicits._
    val idTrmUdf = udf((id: String) => id.split("/").last)
    mailDataFrame.withColumn("id", idTrmUdf(col("id")))
    val subjectGroups: RDD[(String, Iterable[Row])] = mailDataFrame.rdd.groupBy(_.getAs[String]("subject_simple"))
    val messageThreadItems = subjectGroups.values.flatMap(createThreads).toDF()
      .select("id", "threadId", "thread_size_i").withColumnRenamed("threadId", "newThreadId")
    val reJoined = mailDataFrame.join(messageThreadItems, "id")
    val overrideIfEmpty = udf((oldCol: String, overrideCol: String) =>
      if (alwaysOverride || oldCol == null || oldCol.equalsIgnoreCase("unknown")) {
        overrideCol
      } else {
        oldCol
      })
    val withNewThreadIdCol =
      reJoined.withColumn("overRiddenThreadId", overrideIfEmpty(reJoined.col("threadId"), reJoined.col("newThreadId")))
      .drop("threadId")
      .drop("newThreadId")
    val renamed = withNewThreadIdCol.withColumnRenamed("overRiddenThreadId", "threadId")
    renamed
  }

  def countThreads(mailDataFrame: DataFrame): Long = mailDataFrame.select("threadId").distinct().count()


  def createThreads(rows: Iterable[Row]): List[MessageThreadItem] = {
    val items: List[MessageThreadItem] = rows.toList.map(rowToMessageThreadItem)
    createThreads(items)
  }

  def createThreads(items: List[MessageThreadItem]): List[MessageThreadItem] = {
    val itemsById = items.map(item => item.id -> item).toMap
    val edges = items.map(item => item.id -> item.inReplyTo)
    val components =
      GraphUtils.connectedComponents(edges).values.toList.toSet.map((ids: List[String]) => ids.flatMap(itemsById.get))
    components.toList.flatMap { component =>
      // as it's possible there will be no messages in this thread which have no inReplyTo (as the originator of the
      // thread may be missing from this component, or the DataFrame entirely), leave the threadIds alone in this case.
      // another option, however, is to take the most common inReplyTo, and assign that as the threadId. But then that
      // message may not be in the index, leading to possible UI issues.
      val threadIdOpt = component.find(_.inReplyTo == null).map(_.id)
      val res = threadIdOpt.map(threadId =>
        component.map(item => item.copy(threadId = threadId, thread_size_i = component.size))).getOrElse(component)
      res
    }
  }

}
