package com.lucidworks.searchhub.connectors.mail.handler;


import org.junit.Assert;
import org.junit.Test;

import javax.mail.Session;
import javax.mail.internet.MimeMessage;
import java.io.ByteArrayInputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Properties;

/**
 *
 *
 **/
public class MailTest {

  //http://asfmail.lucidworks.io/mail_files/cassandra-user/201605.mbox/raw/%3C4924E32E-FCDC-4F7B-9EC9-C454F9E12F2A@venarc.com%3E
  //http://asfmail.lucidworks.io/mail_files/lucene-dev/201606.mbox/raw/%3CJIRA.12974273.1464711795000.820.1464773399553@Atlassian.JIRA%3E
  @Test
  public void testEvictMessage() throws Exception {
    Session session = Session.getDefaultInstance(new Properties());
    MimeMessage message = new MimeMessage(session, new ByteArrayInputStream(Files.readAllBytes(Paths.get(getClass().getResource("/cassandra-evict-msg.txt").toURI()))));
    Mail mail = new Mail(message, "http://asfmail.lucidworks.io/mail_files/cassandra-user/201605.mbox/%3C284482193.749659.1464463496825.JavaMail.yahoo@mail.yahoo.com%3E");
    String displayContent = mail.getDisplayContent();
    Assert.assertNotNull("display content is null", displayContent);
    Assert.assertTrue(displayContent.trim().startsWith("Hi,\n" +
            "We are using C* 2.0.x ") );

  }

  @Test
  public void testReplyMessage() throws Exception {
    Session session = Session.getDefaultInstance(new Properties());
    MimeMessage message = new MimeMessage(session, new ByteArrayInputStream(Files.readAllBytes(Paths.get(getClass().getResource("/cassandra-debian-msg.txt").toURI()))));
    Mail mail = new Mail(message, "http://asfmail.lucidworks.io/mail_files/cassandra-user/201605.mbox/raw/%3C4924E32E-FCDC-4F7B-9EC9-C454F9E12F2A@venarc.com%3E");
    String displayContent = mail.getDisplayContent();
    Assert.assertNotNull("display content is null", displayContent);
    Assert.assertTrue(displayContent.trim().startsWith("OK to make things even more confusing,") );
    Assert.assertEquals(-1, displayContent.trim().indexOf(">"));

  }

  @Test
  public void testTextOnlyMessage() throws Exception {
    Session session = Session.getDefaultInstance(new Properties());
    MimeMessage message = new MimeMessage(session, new ByteArrayInputStream(Files.readAllBytes(Paths.get(getClass().getResource("/text-only.txt").toURI()))));
    Mail mail = new Mail(message, "http://foo.com/text-only.txt");
    String displayContent = mail.getDisplayContent();
    Assert.assertNotNull("display content is null", displayContent);
    Assert.assertTrue(displayContent.trim().contains("I've updated the patch and the returned collection is now a view."));

  }

  @Test
  public void testHTMLOnlyMessage() throws Exception {
    Session session = Session.getDefaultInstance(new Properties());
    MimeMessage message = new MimeMessage(session, new ByteArrayInputStream(Files.readAllBytes(Paths.get(getClass().getResource("/html-only.txt").toURI()))));
    Mail mail = new Mail(message, "http://foo.com/text-only.txt");
    String displayContent = mail.getDisplayContent();
    Assert.assertNotNull("display content is null", displayContent);
    Assert.assertFalse(displayContent.trim().isEmpty());

  }
}
