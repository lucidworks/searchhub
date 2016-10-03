package com.lucidworks.searchhub.analytics

import org.apache.spark.{SparkContext, Accumulator}
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.{Row, DataFrame}
import org.slf4j.LoggerFactory


object MailThreadJob {
  val log = LoggerFactory.getLogger("MailThreadJob")

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

  def createThreadGroups(mailDataFrame: DataFrame,
                         accumulatorMap: Map[String, Accumulator[Int]] = Map.empty,
                         alwaysOverride: Boolean = false): DataFrame = {
    import org.apache.spark.sql.functions._
    import mailDataFrame.sqlContext.implicits._
    //val idTrmUdf = udf((id: String) => id.split("/").last)
    //mailDataFrame.withColumn("id", idTrmUdf(col("id")))
    val subjectGroups: RDD[(String, Iterable[Row])] = mailDataFrame.rdd.groupBy(_.getAs[String]("subject_simple"))
    val messageThreadItems = subjectGroups.values.flatMap(x => createThreads(x, accumulatorMap)).toDF()
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

  def accumulators(sc: SparkContext) = {
    val acc = (s: String) => s -> sc.accumulator(0, s)
    Map(
      acc("num_messages"),
      acc("num_msgs_with_threadIds"),
      acc("num_msgs_without_threadIds"),
      acc("num_subjects"),
      acc("num_subjects_with_all_known_threadIds"),
      acc("num_subjects_with_no_known_threadIds"),
      acc("num_subjects_with_some_known_some_unknown_threadIds")
    )
  }
  /*
    val msgAcc = acc("num_messages")
    val msgKnown = acc("num_msgs_with_threadIds")
    val msgUnknown = acc("num_msgs_without_threadIds")
    val subAcc = acc("num_subjects")
    val subWithAllKnownAcc = acc("num_subjects_with_all_known_threadIds")
    val subWithNoKnownAcc = acc("num_subjects_with_no_known_threadIds")
    val subWithMixedAcc = acc("num_subjects_with_some_known_some_unknown_threadIds")
   */
  def createThreads(rows: Iterable[Row], accumulatorMap: Map[String, Accumulator[Int]]): List[MessageThreadItem] = {
    val items: List[MessageThreadItem] = rows.toList.map(rowToMessageThreadItem)
    val threadedItems = createThreads(items)
    val unknown = threadedItems.count(_.threadId.equalsIgnoreCase("unknown"))
    val known = threadedItems.count(!_.threadId.equalsIgnoreCase("unknown"))
    val ct = items.size
    def add(k: String, n: Int) = accumulatorMap.get(k).foreach(_ += n)
    add("num_messages", ct)
    add("num_msgs_without_threadIds", unknown)
    add("num_msgs_with_threadIds", known)
    add("num_subjects", 1)
    if (ct == known) {
      add("num_subjects_with_all_known_threadIds", 1)
    } else if (known == 0) {
      add("num_subjects_with_no_known_threadIds", 1)
    } else {
      add("num_subjects_with_some_known_some_unknown_threadIds", 1)
    }
    val sub = threadedItems.head.subjectSimple
    log.info(s"createThreads: $ct messages, $unknown unknown threadId, subject: $sub")
    threadedItems
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
