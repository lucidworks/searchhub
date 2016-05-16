package com.lucidworks.utils.mail.downloader;

import java.util.ArrayList;
import java.util.Iterator;

public class StringMailingListSource extends MailingListSource {

  private ArrayList<MailingListDescription> lists = new ArrayList<MailingListDescription>();

  public void addValueAsString(String[] values) {

    try {

      if (values.length != 5) {
        throw new IllegalArgumentException("expected 5 elements in the array, got" + values.length);
      }

      String ml = values[0].trim();
      String project = values[1].trim();
      String listType = values[2].trim();
      String urlSuffix = values[3].trim();
      String tlp = values[4].trim();

      lists.add(new MailingListDescription(ml, project, listType, urlSuffix, tlp));

    } catch (IllegalArgumentException e) {
      log.error("Ignoring source. Error parsing line: " + e.getMessage());
      return;
    }

  }

  @Override
  public Iterator<MailingListDescription> iterator() {
    return lists.iterator();
  }

}

