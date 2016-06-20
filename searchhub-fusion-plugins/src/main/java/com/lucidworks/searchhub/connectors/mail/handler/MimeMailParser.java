package com.lucidworks.searchhub.connectors.mail.handler;

import com.google.common.collect.Lists;
import com.lucidworks.apollo.common.pipeline.PipelineDocument;
import com.lucidworks.searchhub.connectors.BaseDocument;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.mail.MessagingException;
import javax.mail.Session;
import javax.mail.internet.MimeMessage;
import java.io.ByteArrayInputStream;
import java.util.List;
import java.util.Properties;
import java.util.regex.Pattern;

public class MimeMailParser {
  private final Logger logger = LoggerFactory.getLogger(MimeMailParser.class);

  public static final String RAW_CONTENT = "_raw_content_";

  public static final String FIELD_PROJECT = "project";
  public static final String FIELD_FROM = "from";
  public static final String FIELD_FROM_EMAIL = "from_email";
  public static final String FIELD_MESSAGE_ID = "message_id";
  public static final String FIELD_GROUP_ID = "group_id";
  public static final String FIELD_NEXT_ID = "next_id";
  public static final String FIELD_CHILD_ID = "child_id";
  public static final String FIELD_PARENT_ID = "parent_id";
  public static final String FIELD_LIST = "list";
  public static final String FIELD_LIST_TYPE = "list_type";
  public static final String FIELD_HASH_ID = "hash_id";
  public static final String FIELD_SIZE = "fileSize";
  public static final String FIELD_DEPTH = "depth";
  public static final String FIELD_REPLIES = "replies";
  public static final String FIELD_NUMBER = "number";
  public static final String FIELD_HEADER = "header_";
  public static final String FIELD_SUBJECT = "subject";
  public static final String FIELD_SUBJECT_SIMPLE = "subject_simple";
  public static final String FIELD_IN_REPLY_TO = "in_reply_to";
  public static final String FIELD_CONTAINS = "contains";

  public static final String FIELD_THREAD_ID = "threadId";
  public static final String FIELD_SENT_DATE = "publishedOnDate";

  private final List<Pattern> botEmailPatterns;
  private final Pattern idPattern;
  private final Session session;

  public MimeMailParser() {
    idPattern = Pattern.compile(".*/\\d{6}\\.mbox/raw/%3[Cc].*%3[eE]$");
    botEmailPatterns = Lists.newArrayList(
            Pattern.compile(".*buildbot@.*"),
            Pattern.compile(".*git@.*"),
            Pattern.compile(".*hudson@.*"),
            // way of filtering code reviews too?
            Pattern.compile(".*jenkins@.*"),
            Pattern.compile(".*jira@.*"),
            Pattern.compile(".*subversion@.*"),
            Pattern.compile(".*svn@.*")
    );


    session = Session.getDefaultInstance(new Properties());
  }

  //Used by the stage
  public MimeMailParser(Pattern idPattern, List<Pattern> botEmailPatterns) {
    this.idPattern = idPattern;
    this.botEmailPatterns = botEmailPatterns;
    session = Session.getDefaultInstance(new Properties());
  }

  public PipelineDocument parse(PipelineDocument doc) throws MessagingException, MailException {
    String docId = doc.getId();
    if (docId == null) {
      logger.warn("null docId, skipping: " + doc);
      return null;
    }
    if (!idPattern.matcher(docId).matches()) {
      logger.debug("doc with ID: " + docId + " does not match raw mbox message URL format, skipping");
      return null;
    }
    if (!doc.hasField(RAW_CONTENT)) {
      logger.debug(RAW_CONTENT + " field empty in doc with ID: " + docId + ", skipping");
      return null;
    }
    String rawText = new String(((byte[]) doc.getFirstFieldValue(RAW_CONTENT)));
    MimeMessage message = new MimeMessage(session, new ByteArrayInputStream(rawText.getBytes()));
    Mail mail = new Mail(message, docId);
    String newDocId = mail.getMailUrlId().getMessageId();
    doc.setId(newDocId);
    addMailFields(mail, doc);
    return doc;
  }

  private void setDataSourceFields(PipelineDocument doc) {
    if (doc.hasField("_lw_data_source_s")) {
      String dataSource = doc.getFirstFieldValue("_lw_data_source_s").toString();
      String[] sourceParts = dataSource.split("-");
      if (sourceParts.length > 2) {
        doc.setField(FIELD_PROJECT, sourceParts[2]);
      }
    }
  }

  private void setBotField(PipelineDocument doc, String fromEmail) {
    if (fromEmail != null) {
      String email = fromEmail.toLowerCase();
      for (Pattern pattern : botEmailPatterns) {
        if (pattern.matcher(email).matches()) {
          doc.setField("isBot", true);
          return;
        }
      }
    }
    doc.setField("isBot", false);
  }

  private PipelineDocument addMailFields(Mail mail, PipelineDocument doc) throws MailException {
    setDataSourceFields(doc);
    // TODO: parse list and project type from _lw_data_source_s, not url
    doc.setField(FIELD_LIST, mail.getMailUrlId().getList());
    doc.setField(FIELD_LIST_TYPE, mail.getMailUrlId().getProjectType());
    doc.setField(FIELD_HASH_ID, mail.getHashId());
    doc.setField(FIELD_MESSAGE_ID, mail.getMailUrlId().getMessageId());
    doc.setField(FIELD_SUBJECT, mail.getSubject());
    doc.setField(BaseDocument.FIELD_TITLE, mail.getSubject());
    doc.setField(FIELD_SUBJECT_SIMPLE, mail.getBaseSubject());
    doc.setField(FIELD_SIZE, mail.getSize());
    String fromEmail = mail.getFromEmail();
    String from = mail.getFrom();
    if (from != null) {
      from = from.replaceAll(fromEmail, "").replaceAll("[<>]", "").replaceAll("\"", "").trim();
    }
    doc.setField(BaseDocument.FIELD_CREATOR, from);
    doc.setField(FIELD_FROM, from);
    doc.setField(FIELD_FROM_EMAIL, fromEmail);
    setBotField(doc, fromEmail);
    doc.setField(FIELD_NUMBER, mail.getMessageNumber());
    doc.setField(FIELD_SENT_DATE, mail.getSentDateStr());
    doc.setField(BaseDocument.FIELD_CREATED_DATE, mail.getSentDateStr());
    doc.setField(BaseDocument.FIELD_MODIFIED_DATE, mail.getSentDateStr());
    doc.setField(FIELD_IN_REPLY_TO, mail.getInReplyTo());
    doc.setField(BaseDocument.FIELD_CONTENT, mail.getNewContent());
    doc.setField(BaseDocument.FIELD_CONTENT_DISPLAY, mail.getDisplayContent());

    //Thread information
    doc.setField(FIELD_THREAD_ID, "unknown");
    doc.setField(FIELD_GROUP_ID, mail.getThreadId());
    doc.setField(FIELD_PARENT_ID, mail.getParentId());
    doc.setField(FIELD_DEPTH, mail.getDepth());

    return doc;
  }
}
