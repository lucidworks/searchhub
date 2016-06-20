package com.lucidworks.searchhub.connectors.mail.handler;

import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.net.URLEncoder;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;
import java.util.List;

/**
 * Mail archive raw entries are found on the web like so:
 *
 * $MAIL_ARCHIVE_HOST/$PREFIX_PATH/$LIST/${yyyyMM}.mbox/raw/$URL_ENCODED_MESSAGE_ID
 *
 * http://216.136.133.198/mail_files/mahout-dev/200801.mbox/raw/%3CF9210543-78B0-47ED-BD6B-0E850CC08774@apache.org%3E
 * or without URL encoding:
 * http://216.136.133.198/mail_files/mahout-dev/200801.mbox/raw/<F9210543-78B0-47ED-BD6B-0E850CC08774@apache.org>
 *
 * full messageId: <F9210543-78B0-47ED-BD6B-0E850CC08774@apache.org>
 */
public class MailUrlId {

  private final String url;
  private final String messageId;
  private final String list;
  private final String project;
  private final String projectType;
  private final String approxDateStr;
  private final Date approxDate;
  public MailUrlId(String raw) {
    url = raw;
    List<String> parts = Arrays.asList(raw.split("/"));
    int numParts = parts.size();
    if (numParts < 4) {
      throw new IllegalStateException("Mail message url (" + url + ") too short, cannot parse sub-parts");
    }
    try {
      messageId = URLDecoder.decode(parts.get(numParts - 1), "UTF-8").replace(' ', '+');
    } catch (UnsupportedEncodingException e) {
      throw new IllegalStateException(e);
    }
    Date tempDate;
    approxDateStr = parts.get(numParts - 3);
    try {
      SimpleDateFormat sdf = new SimpleDateFormat("yyyyMM");
      tempDate = sdf.parse(approxDateStr);
    } catch (ParseException e) {
      tempDate = new Date();
    }
    approxDate = tempDate;
    list = parts.get(numParts - 4);
    // TODO: doesn't work quite right. Must handle: lucene-lucene-net-dev and hadoop-yarn-dev	and incubator-spark-dev
    if (list.contains("-")) {
      project = list.substring(0, list.lastIndexOf("-"));
      projectType = list.substring(list.lastIndexOf("-") + 1);
    } else {
      project = list;
      projectType = "default";
    }
  }

  public String getUrl() {
    return url;
  }

  public String getList() {
    return list;
  }

  public String getProject() {
    return project;
  }

  public String getProjectType() {
    return projectType;
  }

  public Date getApproxDate() { return approxDate; }

  public String getMessageId() { return messageId; }

  public String getUID() {
    return getList() + "/" + approxDateStr + "/raw/" + messageId;
  }
}
