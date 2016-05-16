package com.lucidworks.utils.mail.downloader;

public class MailingListDescription {

  public String name;
  public String project;
  public String type;
  public String urlSuffix;
  public String tlp;
  public String newArchive;
  public String mlName;


  public MailingListDescription(String name, String project,
                                String type, String urlSuffix, String tlp) {

    this.urlSuffix = urlSuffix;
    this.tlp = tlp;
    this.mlName = name;

    this.project = project;
    this.type = type;
    this.name = urlSuffix;
    this.newArchive = "http://mail-archives.apache.org/mod_mbox/"
      + urlSuffix + "/";


  }

}
