package com.lucidworks.searchhub.analytics


import java.text.{SimpleDateFormat, DateFormat}

import scala.collection.JavaConverters._

import com.lucidworks.apollo.common.pipeline.PipelineDocument
import com.lucidworks.searchhub.connectors.BaseDocument
import com.lucidworks.searchhub.connectors.mail.handler.MimeMailParser
import org.apache.spark.sql.Row

/**
  * Spark-Solr Schema for a DataFrame of the searchhub index
  */
case class MailMessage(id: String, project: String, list: String, listType: String,
                       from: String, fromEmail: String, inReplyTo: String,
                       threadId: String, numReplies: Int,
                       subject: String, simpleSubject: String, body: String, displayBody: String,
                       publishedOnDate: java.sql.Timestamp)

object MailMessage {

  def fromRawString(id: String, contents: String): Option[MailMessage] = {
    val mailParser = new MimeMailParser//TODO: fix this to take in configurable patterns like the real stage does
    val doc = new PipelineDocument(id)
    doc.setField("_raw_content_", contents.getBytes)
    val parsedDocOpt = try {
      Option(mailParser.parse(doc))
    } catch {
      case e: Exception =>
        println("unable to parse " + id)
        None
    }
    parsedDocOpt.map { parsedDoc =>
      val solrDateFmt: DateFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'")
      def concatenated(field: String): String = parsedDoc.getFieldValues(field).asScala.mkString(" ")
      MailMessage(
        id = id,
        project = concatenated(MimeMailParser.FIELD_PROJECT),
        list = concatenated(MimeMailParser.FIELD_LIST),
        listType = concatenated(MimeMailParser.FIELD_LIST_TYPE),
        from = concatenated(MimeMailParser.FIELD_FROM),
        fromEmail = concatenated(MimeMailParser.FIELD_FROM_EMAIL),
        inReplyTo = concatenated(MimeMailParser.FIELD_IN_REPLY_TO),
        threadId = concatenated(MimeMailParser.FIELD_THREAD_ID),
        numReplies = 0,
        subject = concatenated(MimeMailParser.FIELD_SUBJECT),
        simpleSubject = concatenated(MimeMailParser.FIELD_SUBJECT_SIMPLE),
        body = concatenated(BaseDocument.FIELD_CONTENT),
        displayBody = concatenated(BaseDocument.FIELD_CONTENT_DISPLAY),
        publishedOnDate = new java.sql.Timestamp(
          solrDateFmt.parse(parsedDoc.getFirstFieldValue(MimeMailParser.FIELD_SENT_DATE).toString).getTime)
      )
    }
  }

  def fromRow(row: Row): MailMessage = {
    def concatenated(field: String): String =  row.getAs[String](field)

    MailMessage(
      id = row.getAs[String]("id"),
      project = concatenated(MimeMailParser.FIELD_PROJECT),
      list = concatenated(MimeMailParser.FIELD_LIST),
      listType = concatenated(MimeMailParser.FIELD_LIST_TYPE),
      from = concatenated(MimeMailParser.FIELD_FROM),
      fromEmail = concatenated(MimeMailParser.FIELD_FROM_EMAIL),
      inReplyTo = concatenated(MimeMailParser.FIELD_IN_REPLY_TO),
      threadId = concatenated(MimeMailParser.FIELD_THREAD_ID),
      numReplies = row.getAs[Int](MimeMailParser.FIELD_REPLIES),
      subject = concatenated(MimeMailParser.FIELD_SUBJECT),
      simpleSubject = concatenated(MimeMailParser.FIELD_SUBJECT_SIMPLE),
      body = concatenated(BaseDocument.FIELD_CONTENT),
      displayBody = concatenated(BaseDocument.FIELD_CONTENT_DISPLAY),
      publishedOnDate = row.getAs[java.sql.Timestamp](MimeMailParser.FIELD_SENT_DATE)
    )
  }

}

