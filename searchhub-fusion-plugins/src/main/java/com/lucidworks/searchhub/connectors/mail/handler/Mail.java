package com.lucidworks.searchhub.connectors.mail.handler;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.mail.Address;
import javax.mail.Message;
import javax.mail.MessagingException;
import javax.mail.Multipart;
import javax.mail.Part;
import javax.mail.internet.MimeMessage;
import javax.mail.internet.MimeMessage.RecipientType;
import javax.mail.internet.MimeUtility;
import javax.mail.internet.ParseException;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.StringReader;
import java.io.UnsupportedEncodingException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.TimeZone;

public class Mail {
  private final MailUrlId mailUrlId;

  private MimeMessage message;
  private String hash;
  private String messageId;
  private String list;
  private String threadId = "";

  private String parentId;
  private int depth;
  private Date sentDate;

  private String sentDateStr;
  private MailHash hashBuilder;

  private static final ThreadLocal<DateFormat> solrDateFormatTl = new ThreadLocal<DateFormat>() {
    @Override
    protected DateFormat initialValue() {
      SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'");//TODO: Locale here?
      format.setTimeZone(TimeZone.getTimeZone("UTC"));
      return format;
    }
  };

  public static Logger log = LoggerFactory.getLogger(Mail.class);

  public Mail(MimeMessage m, String mailUrl) {
    this(m, new SimpleMailHash(), mailUrl);
  }

  public Mail(MimeMessage m, MailHash hashBuilder, String mailUrl) {
    this.message = m;
    this.hashBuilder = hashBuilder;
    this.mailUrlId = new MailUrlId(mailUrl);

  }


  public String getSentDateStr() throws MailException {
    if (sentDateStr != null) {
      return sentDateStr;
    }
    Date approximateDate = mailUrlId.getApproxDate();
    Date betterDate = findReasonableDate(message, approximateDate);
    if (betterDate == null) {
      betterDate = approximateDate;
    }
    sentDate = betterDate;
    sentDateStr = solrDateFormatTl.get().format(betterDate);
    return sentDateStr;
  }


  public Date getSentDate() throws MailException {
    getSentDateStr();
    return sentDate;
  }


  public String getSubject() throws MailException {
    try {
      return message.getSubject();
    } catch (MessagingException e) {
      throw new MailException("cant get subject of mail", e);
    }
  }


  public String getContentType() throws MailException {
    try {
      return message.getContentType();
    } catch (MessagingException e) {
      throw new MailException("cant get content type of mail", e);
    }
  }


  private void getText(Part p, Map<String, List<String>> results) throws MessagingException, IOException {
    if (p.isMimeType("text/*")) {
      Object txt = p.getContent();
      String contentType = p.getContentType();
      //strip off character encoding if it is on there
      int i = contentType.indexOf(";");
      if (i != -1) {
        contentType = contentType.substring(0, i).trim();
      }
      List<String> vals = results.get(contentType);
      if (vals == null) {
        vals = new ArrayList<>();
        results.put(contentType, vals);
      }
      vals.add(txt.toString());
    } else if (p.isMimeType("multipart/*")) {
      Multipart mp = (Multipart) p.getContent();
      for (int i = 0; i < mp.getCount(); i++) {
        Part bp = mp.getBodyPart(i);
        getText(bp, results);
      }
    }
  }

  /**
   * @return A map where the key is the mime type and the value is the text associated with that mime type
   * @throws MailException
   */
  public Map<String, List<String>> getText() throws MailException {
    try {
      Map<String, List<String>> results = new HashMap<>();
      getText(message, results);
      return results;
    } catch (MessagingException e) {
      throw new MailException("cant get contents of mail", e);
    } catch (IOException e) {
      throw new MailException("cant get contents of mail", e);
    }
  }


  public String[] getReferences() throws MailException {
    try {
      return message.getHeader("References");
    } catch (MessagingException e) {
      throw new MailException("Cannot get 'References' header of mail", e);
    }
  }


  public String getFrom() throws MailException {
    Address[] addresses;
    try {
      addresses = message.getFrom();
    } catch (MessagingException e) {
      throw new MailException("cant get from header of mail", e);
    }
    if (addresses == null || addresses.length < 1) {
      return null;
    }

    return extractAddressHeader(addresses[0]);
  }

  protected String extractAddressHeader(Address add) throws MailException {

    String from_header = add.toString();

    try {
      if ("rfc822".equals(add.getType())) {
        from_header = MimeUtility.decodeText(add.toString());
      } else {
        from_header = MimeUtility.decodeWord(add.toString());
      }

    } catch (ParseException e) {
      String mess = "From header parse exception (" + e.getMessage()
              + ") msgid=" + this.getId() + " from=" + add.toString()
              + " from type=" + add.getType();
      log.info(mess);
    } catch (UnsupportedEncodingException e) {
      String mess = "From header unsupported encoding exception ("
              + e.getMessage() + ") msgid=" + this.getId() + " from="
              + add.toString() + " from type=" + add.getType();
      log.info(mess);
    }

    return from_header;
  }


  public String[] getTo() throws MailException {

    Address[] addresses;

    try {
      addresses = message.getRecipients(RecipientType.TO);

      if (addresses == null || addresses.length < 1) {
        return null;
      }

      String[] strAddresses = new String[addresses.length];

      for (int i = 0; i < addresses.length; i++) {
        strAddresses[i] = extractAddressHeader(addresses[i]);
      }

      return strAddresses;

    } catch (MessagingException e) {
      throw new MailException("cant get header of mail", e);
    }
  }


  public String[] getToAddresses() throws MailException {

    String[] headers = getTo();
    if (headers == null)
      return new String[0];

    String[] addresses = new String[headers.length];

    for (int i = 0; i < headers.length; i++) {
      addresses[i] = extractAddressFromHeader(headers[i]);
    }

    return addresses;
  }

  protected String extractAddressFromHeader(String header) {

    int edx = header.lastIndexOf('>');
    if (edx > 0) {
      int idx = header.lastIndexOf('<', edx);
      if (idx >= 0) {
        header = header.substring(idx + 1, edx);
      }
    }
    return header;
  }


  public String getFromEmail() throws MailException {
    String from_email = this.getFrom();

    if (from_email == null)
      return null;

    return extractAddressFromHeader(from_email);
  }


  public String getId() throws MailException {
    return getHashId();
  }


  public String getThreadId() throws MailException {
    return threadId;
  }


  public String getParentId() throws MailException {
    return parentId;
  }


  public int getSize() throws MailException {
    try {
      return message.getSize();
    } catch (MessagingException e) {
      throw new MailException("cant get size of mail", e);
    }
  }


  public int getDepth() throws MailException {
    return depth;
  }


  public String getBaseSubject() throws MailException {

    String subject = getSubject();
    if (subject == null)
      return "null";

    String simplifiedSubject = getSubject().toLowerCase();
    simplifiedSubject = simplifiedSubject.replaceAll("re:", "");

    //TODO: to deal with CVS files, this is a simple workaround that may be improved in the future. Added in LUCIDFIND-214
    simplifiedSubject = simplifiedSubject.replaceAll(",", "");

    simplifiedSubject = simplifiedSubject.trim();

    return simplifiedSubject.length() > 0 ? simplifiedSubject : "null";
  }


  public String getInReplyTo() throws MailException {
    String[] reply;
    try {
      reply = message.getHeader("In-Reply-To");
    } catch (MessagingException e) {
      throw new MailException("cannot get in-reply-to header", e);
    }
    if (reply != null && reply.length > 0 && reply[0] != null) {
      return reply[0];
    }
    return null;
  }


  public int getMessageNumber() throws MailException {
    return message.getMessageNumber();
  }

  protected String calculateHash(String data) throws MailException {
    return this.hashBuilder.calculateHash(data);
  }


  public String getHashId() throws MailException {

    if (hash != null) {
      return hash;
    }

    String[] ID_HEADERS = new String[]{"Message-Id", "List-Id",
            "Subject", "Date"};

    try {
      StringBuilder hashtext = new StringBuilder();
      for (String header : ID_HEADERS) {
        hashtext.append(header).append(": ");
        String[] vals = this.message.getHeader(header);
        if (vals != null) {
          for (String value : vals) {
            hashtext.append(value.trim()).append(' ');
          }
        }
        hashtext.append("\n");
      }

      String mailText = hashtext.toString();
      hash = calculateHash(mailText);

      return hash;
    } catch (MessagingException e) {
      throw new MailException("cannot obtain information of header", e);
    }
  }

  public String getDisplayContent() throws MailException {
    Map<String, List<String>> mimeMap = this.getText();
    if (mimeMap == null) {
      return "";
    }
    String contents = getJoinedText(mimeMap);
    if (contents == null) {
      return "";
    }

    BufferedReader reader = new BufferedReader(new StringReader(contents));
    List<String> lines = new LinkedList<String>();
    String line = null;
    try {
      line = reader.readLine();
      while (line != null) {
        lines.add(line);
        line = reader.readLine();
      }

    } catch (IOException e) {
      throw new MailException("cannot read line of contents", e);
    }
    if (lines.isEmpty()) {
      log.warn("WARNING: Empty email");
      return "";
    }
    /*
     * Remove all the lines from the bottom that start with ">" or ":"
     */
    String lastLine = lines.get(lines.size() - 1);
    while (lastLine.startsWith(":") || lastLine.startsWith(">")) {
      lines.remove(lines.size() - 1);
      if (lines.isEmpty()) {
        log.warn("WARNING: Empty email");
        return "";
      }
      lastLine = lines.get(lines.size() - 1);
    }
    return getAsString(lines);
  }

  private String getJoinedText(Map<String, List<String>> mimeMap) {
    StringBuilder result = new StringBuilder();
    //try to get plain text first, then html and then whatever remains.  Merge the lists together within a mime type
    List<String> list = mimeMap.get("text/plain");
    if (list != null && list.isEmpty() == false) {
      //merge the list
      result.append(getAsString(list));
    } else {
      //TODO: perhaps an alternate strategy is to append it all?
      //we couldn't find plain text, so let's see what else we have
      list = mimeMap.get("text/html");//html is a good second choice
      if (list != null && list.isEmpty() == false) {
        result.append(getAsString(list));
      } else {
        //not sure what else we've got, loop over all of it and try to get strings
        for (Map.Entry<String, List<String>> entry : mimeMap.entrySet()) {
          log.warn("adding unknown content type: {}", entry.getKey());
          List<String> value = entry.getValue();
          if (value != null && value.isEmpty() == false) {
            result.append(getAsString(value));
          }
        }
      }
    }
    return result.toString();
  }

  /**
   * This content will be used for search purposes. "getDisplayContent" should be used for display
   */

  public String getNewContent() throws MailException {
    Map<String, List<String>> mimeMap = this.getText();
    if (mimeMap == null) {
      return "";
    }
    String contents = getJoinedText(mimeMap);

    if (contents == null) {
      return "";
    }
    StringBuilder newcontent = new StringBuilder();

    BufferedReader reader = new BufferedReader(new StringReader(contents));
    String line = null;
    try {
      line = reader.readLine();
      while (line != null) {
        if (!(line.startsWith(">") || line.startsWith(":"))) {
          newcontent.append(line).append("\n");
        }
        line = reader.readLine();
      }
    } catch (IOException e) {
      throw new MailException("cannot read line of contents", e);
    }
    return newcontent.toString();
  }

  private String getAsString(List<String> lines) {
    StringBuilder newcontent = new StringBuilder();
    for (String line : lines) {
      newcontent.append(line + "\n");
    }
    return newcontent.toString().trim();
  }


  public MailUrlId getMailUrlId() throws MailException {
    return mailUrlId;
  }


  public String getList() {
    return list;
  }

  public void setList(String list) {
    this.list = list;
  }


  public void setThreadId(String threadId) {
    this.threadId = threadId;
  }


  public void setParentId(String parentId) {
    this.parentId = parentId;
  }


  public void setDepth(int depth) {
    this.depth = depth;
  }


  public String getMailId() throws MailException {

    if (messageId != null) {
      return messageId;
    }

    String[] vals;
    try {
      vals = message.getHeader("Message-ID");
    } catch (MessagingException e) {
      throw new MailException("cant get id header of mail", e);
    }

    if (vals != null && vals.length > 0) {
      messageId = vals[0];
      return messageId;
    }

    if (messageId == null) {
      messageId = getHashId();
    }

    return messageId;
  }


  private static Date findReasonableDate(Message msg, Date approximateDate) {
    Date min = null;
    Date max = null;
    Calendar cal = Calendar.getInstance();
    if (approximateDate != null) {
      cal.setTime(approximateDate);
      cal.add(Calendar.MONTH, -2);
      min = cal.getTime();
      cal.add(Calendar.MONTH, 4);
      max = cal.getTime();
    } else {
      cal.add(Calendar.MONTH, 1);
      max = cal.getTime();
      cal.add(Calendar.YEAR, -15);
      min = cal.getTime();
    }

    // 1. Try the standard date parsing
    Date date = null;
    try {
      date = msg.getSentDate();
    } catch (MessagingException e) {
    }
    if (date != null && date.after(min) && date.before(max)) {
      return date;
    }

    // 2. Check if the "recieved" date works ok
    try {
      date = msg.getReceivedDate();
    } catch (MessagingException e) {
    }
    if (date != null && date.after(min) && date.before(max)) {
      return date;
    }
    SimpleDateFormat possibleFormats[] = {
            new SimpleDateFormat("d MMM yy HH:mm z"),
            new SimpleDateFormat("d MMM yy HH:mm:ss z"),
            new SimpleDateFormat("d MMM yyyy HH:mm z"),
            new SimpleDateFormat("d MMM yyyy HH:mm:ss z"),
            new SimpleDateFormat("yy/mm/dd HH:mm:ss"),};

    // 3. Try various formats for the "Date" header
    try {
      String[] dateHeader = msg.getHeader("Date");
      if (dateHeader != null) {
        for (String v : dateHeader) {
          for (SimpleDateFormat fmt : possibleFormats) {
            try {
              date = fmt.parse(v);
              if (date != null && date.after(min) && date.before(max)) {
                return date;
              }
            } catch (Exception ex) {
            }
          }
        }
      }
    } catch (MessagingException e) {
    }

    // 4. Try a date in the 'Received' column
    try {
      String[] header = msg.getHeader("Received");
      if (header != null) {
        for (String v : header) {
          int idx = v.lastIndexOf(';');
          if (idx > 0) {
            v = v.substring(idx + 1).trim();
            for (SimpleDateFormat fmt : possibleFormats) {
              try {
                date = fmt.parse(v);
                if (date != null && date.after(min) && date.before(max)) {
                  return date;
                }
              } catch (Exception ex) {
              }
            }
          }
        }
      }
    } catch (MessagingException e) {
    }
    return null;
  }


  public String toString() {
    String mailId;
    String id;
    String list = "unknown";
    String file = "unknown";

    try {
      mailId = getMailId();
    } catch (MailException e) {
      mailId = "unknown";
    }
    try {
      id = getId();
    } catch (MailException e) {
      id = "unknown";
    }

    return String.format("(id: %s, mail_id: %s, list: %s, file: %s)", id, mailId, list, file);

  }
}
