package com.lucidworks.utils.mail.downloader;



import com.lucidworks.searchhub.connectors.BaseDocument;
import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.MissingArgumentException;
import org.apache.commons.cli.Options;
import org.apache.commons.httpclient.Header;
import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpException;
import org.apache.commons.httpclient.HttpMethod;
import org.apache.commons.httpclient.methods.GetMethod;
import org.apache.commons.io.IOUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.MalformedURLException;
import java.net.URL;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.Properties;


/**
 * Initial fetch of full project mail archives
 */
public class ApacheMailMboxGetter {

  static Logger log = LoggerFactory.getLogger(ApacheMailMboxGetter.class);

  public static void printUsage() {
    System.err.println("Usage:\tMailGet <list> [option]");
    System.err.println("Options:");
    System.err.println("\t-test");
    System.err.println("\t-checkDataSourceNames");
    System.err.println("\t-listLists");
    System.err.println("\t-oneList <list-name>");
    System.err.println("\t-output <base dir>");
  }

  public static boolean testMode = false;


  public static String outputDir = ".";

    public static void main(String[] args) {
    ApacheMailMboxGetter mg = new ApacheMailMboxGetter();
    try {
      mg.run(args);
    } catch (Exception e) {
      log.error(e.getMessage());
      e.printStackTrace();
      System.exit(-1);
    }
  }

  public void run(String[] args) throws IOException, MissingArgumentException {

    Options getOptions = new Options();
    getOptions.addOption("test", false, "Test run");
    getOptions.addOption("output", true, "Where to write the files to");

    CommandLineParser cmdLineGnuParser = new BasicParser();

    CommandLine commandLine;

    String[] csvLists = null;

    try {
      commandLine = cmdLineGnuParser.parse(getOptions, args);
      csvLists = commandLine.getArgs();

      if (commandLine.hasOption("test")) {
        testMode = true;
      }
      if (commandLine.hasOption("output")) {
        outputDir = commandLine.getOptionValue("output");

      }
    } catch (org.apache.commons.cli.ParseException e) {
      printUsage();
      System.exit(1);
    }

    if (csvLists == null || csvLists.length == 0) {
      throw new MissingArgumentException("Missing list csv file");
    }

    File listFile = new File(csvLists[0]);
    if (!listFile.exists() || !listFile.canRead()) {
      throw new FileNotFoundException("Cannot access or read the file: " + listFile.getAbsolutePath());
    }

    CsvMailingListSource source = new CsvMailingListSource();
    source.load(listFile);

    long startTime = System.currentTimeMillis();

    int numListsProcessed = 0;

    Properties pollingDates = loadProperties("pollingDates.prop");
    Properties modificationCache = loadProperties("modificationTags.prop");

    for (MailingListDescription list : source) {
      try {

        processList(list, pollingDates, modificationCache);

      } catch (MalformedURLException e) {
        log.error("Ignoring list" + list.name
                + ": Malformed URL: Ignoring list: " + list.newArchive);
        e.printStackTrace();
      } catch (IOException e) {
        log.error("Ignoring list" + list.name
                + ": IO Error, cannot read URL: " + list.newArchive);
        e.printStackTrace();
      } catch (ParseException e) {
        log.error("Ignoring list"
                + list.name
                + ": Error reading last polling date from \"pollingDates\" properties file");
        e.printStackTrace();
      }
      numListsProcessed++;
    }

    saveProperties(pollingDates, "pollingDates.prop");
    saveProperties(modificationCache, "modificationTags.prop");

    if (numListsProcessed > 0) {
      long endTime = System.currentTimeMillis();
      long deltaTime = endTime - startTime;
      log.info(numListsProcessed + " mail lists fetched in " + deltaTime
              + " ms.");
    } else {
      log.info("No mail lists fetched");
    }
  }


  private void processList(MailingListDescription list, Properties pollingDates, Properties modificationCache) throws MalformedURLException, IOException, ParseException {
    String urlStr = list.newArchive;


    BufferedReader br = new BufferedReader(new InputStreamReader(new URL(urlStr).openStream()));

    log.info("List " + list.name + " - " + urlStr + ":");
    String line;

    ArrayList<String> urlsList = new ArrayList<String>();

    while ((line = br.readLine()) != null) {
      int i = line.indexOf(".mbox");
      if (i >= 0) {
        String mboxName = line.substring(i - 6, i + 5);

        if (mboxOlderThanDate(mboxName, pollingDates.getProperty(urlStr))) {
          log.debug(" Ignoring " + mboxName);
          continue;
        }

        urlsList.add(mboxName);
      }
    }
    log.debug("URLS List: " + urlsList);
    for (String mboxName : urlsList) {
      downloadList(urlStr, mboxName, list, modificationCache);
      try {
        //sleep so that we don't invoke the ire of the ASF failban software.
        Thread.currentThread().sleep(1000);
      } catch (InterruptedException e) {
        //do nothing
      }
    }

    DateFormat df = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss");

    pollingDates.setProperty(urlStr, df.format(new Date()));
    br.close();
  }

  private void downloadList(String urlStr, String mboxName, MailingListDescription list, Properties modificationCache) throws HttpException, IOException {

    String mboxUrlStr = urlStr + mboxName;

    InputStream in = getModifiedUrl(mboxUrlStr, modificationCache);
    if (in == null) {
      return;
    }

    String inboxPath = outputDir +  "/" + list.name;
    File inboxFile = new File(inboxPath);
    inboxFile.mkdirs();
    String mboxPath = inboxPath + "/" + mboxName;
    File mboxFile = new File(mboxPath);
    //mboxFile.mkdirs();
    OutputStream out = new FileOutputStream(mboxFile);
    log.info("    " + mboxName + ": " + mboxUrlStr + " -> " + mboxFile.getAbsolutePath());

    IOUtils.copy(in, out);

    out.close();
    in.close();
  }

  private static InputStream getModifiedUrl(String mboxUrlStr, Properties cache) throws HttpException, IOException {
    HttpMethod get = new GetMethod(mboxUrlStr);
    String cacheEtagKey = mboxUrlStr + "[etag]";
    String cacheModifiedKey = mboxUrlStr + "[lastModified]";


    String etag = cache.getProperty(cacheEtagKey);
    String lastModified = cache.getProperty(cacheModifiedKey);

    if (etag != null) {
      get.addRequestHeader("If-None-Match", etag);
    }

    if (lastModified != null) {
      get.addRequestHeader("If-Modified-Since", lastModified);
    }

    HttpClient client = new HttpClient();

    client.executeMethod(get);

    if (get.getStatusCode() < 300) {
      Header[] etags = get.getResponseHeaders("ETag");
      if (etags.length > 0) {
        String newEtag = etags[0].getValue();
        log.info("   File Etag: " + newEtag);
        if (etag != null) {
          log.info("   Cached Etag: " + etag);
        } else {
          log.info("   Not cached file");
        }

        cache.setProperty(cacheEtagKey, newEtag);
      }

      Header[] mods = get.getResponseHeaders("Last-Modified");
      if (mods.length > 0) {
        String newLastModified = mods[0].getValue();

        cache.setProperty(cacheModifiedKey, newLastModified);
      }

      return get.getResponseBodyAsStream();

    } else {
      log.info("get.getStatusCode(): " + get.getStatusCode());
      Header[] date = get.getResponseHeaders("ETag");
      if (date != null && date.length > 0) {
        log.info("   Not modified (response: " + date[0].getValue() + " - cache: " + etag + "): " + mboxUrlStr);
      } else {
        log.info("  Not modified: " + mboxUrlStr + " and ETag: " + etag + " no date available");
      }
      return null;

    }
  }

  private static Properties loadProperties(String filename) throws IOException {
    File propFile = new File(filename);

    Properties props = new Properties();

    if (propFile.isFile() && propFile.canRead()) {
      FileInputStream file = new FileInputStream(propFile);
      props.load(file);
    }

    return props;
  }

  private static void saveProperties(Properties pollingDates, String filename) throws IOException {
    File propFile = new File(filename);
    FileOutputStream file = new FileOutputStream(propFile);

    pollingDates.store(file, "");
  }

  private static boolean mboxOlderThanDate(String mbox, String pollingDateStr) throws ParseException {
    if (pollingDateStr == null) {
      return false;
    }

    DateFormat df = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss");
    Date pollingDate = df.parse(pollingDateStr);

    Calendar pollingCalendar = new GregorianCalendar();
    pollingCalendar.setTime(pollingDate);
    pollingCalendar.set(Calendar.DAY_OF_MONTH, 1);
    pollingCalendar.set(Calendar.HOUR_OF_DAY, 0);
    pollingCalendar.set(Calendar.MINUTE, 0);
    pollingCalendar.set(Calendar.SECOND, 0);
    pollingCalendar.set(Calendar.MILLISECOND, 0);
    pollingDate = pollingCalendar.getTime();

    String year = mbox.substring(0, 4);
    String month = mbox.substring(4, 6);

    Calendar calendar = new GregorianCalendar(Integer.parseInt(year), Integer.parseInt(month) - 1, 1);
    Date mboxDate = calendar.getTime();

    return mboxDate.compareTo(pollingDate) < 0;

  }

}
