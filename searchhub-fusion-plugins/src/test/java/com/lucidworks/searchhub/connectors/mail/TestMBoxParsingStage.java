package com.lucidworks.searchhub.connectors.mail;

import com.lucidworks.apollo.common.pipeline.PipelineDocument;
import com.lucidworks.searchhub.connectors.mail.handler.MimeMailParser;
import static org.junit.Assert.*;
import org.junit.Test;

import java.net.URLDecoder;
import java.nio.file.Files;
import java.nio.file.Paths;

public class TestMBoxParsingStage {
  private static final String msgFile = "/lucene-solr-user_message.txt";
  private String messageStr;
  private String messageId = "http://mail-archives.apache.org/mod_mbox/lucene-solr-user/201504.mbox/raw/%3CCAOx+AL605VTzRAbtryijekaLvGOCUMXdb4EpK%2Bs7sNNUJY5t3QQ%40mail.gmail.com%3E";

  public TestMBoxParsingStage() throws Exception {
    messageStr = new String(Files.readAllBytes(Paths.get(getClass().getResource(msgFile).toURI())));
  }

  @Test
  public void testParsing() throws Exception {
    PipelineDocument origDoc = new PipelineDocument();
    origDoc.setId(messageId);
    origDoc.setField("docId", messageId);
    origDoc.setField("_raw_content_", messageStr.getBytes());

    PipelineDocument doc = new MimeMailParser().parse(origDoc);

    assertEquals("id was incorrect:",
      "<CAOx+AL605VTzRAbtryijekaLvGOCUMXdb4EpK+s7sNNUJY5t3QQ@mail.gmail.com>",
      doc.getId());
    assertFieldEquals(doc, "message_id", "<CAOx+AL605VTzRAbtryijekaLvGOCUMXdb4EpK+s7sNNUJY5t3QQ@mail.gmail.com>");
    assertFieldEquals(doc, "project", "lucene-solr");
    assertFieldEquals(doc, "list_type", "user");
    assertFieldEquals(doc, "subject", "Re: edismax operators");
    assertFieldEquals(doc, "subject_simple", "edismax operators");
    assertFieldEquals(doc, "from", "Jack Krupansky");
    assertFieldEquals(doc, "from_email", "jack.krupansky@gmail.com");
    assertFieldEquals(doc, "publishedOnDate", "2015-04-02T12:14:04Z");
    assertFieldEquals(doc, "in_reply_to", "<CAL5zfJbEiS6JeEhLf12KAUJJorCr_BVgFqrtPC=SefSHfAaBbg@mail.gmail.com>");
    // TODO: find which field contains the replied (old) content
    assertFieldDoesntContain(doc, "body_display", "rawquerystring");
    assertFieldContains(doc, "body_display", "parentheses");
  }

  @Test
  public void testIgnoreAttachment() throws Exception {

  }

  private void assertFieldEquals(PipelineDocument doc, String field, Object expected) {
    //assertEquals(expected, doc.getFirstField(field).getValue());
  }

  private void assertFieldContains(PipelineDocument doc, String field, String subString) {
    String fieldContent = doc.getFirstField(field).toString();
    assertTrue("[" + fieldContent + "] does not contain [" + subString + "]", fieldContent.contains(subString));
  }

  private void assertFieldDoesntContain(PipelineDocument doc, String field, String subString) {
    String fieldContent = doc.getFirstField(field).toString();
    assertFalse("[" + fieldContent + "] is not supposed to contain [" + subString + "]", fieldContent.contains(subString));
  }

}
