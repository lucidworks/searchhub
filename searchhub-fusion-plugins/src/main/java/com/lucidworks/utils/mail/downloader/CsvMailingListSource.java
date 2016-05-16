package com.lucidworks.utils.mail.downloader;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;

public class CsvMailingListSource extends StringMailingListSource {

  public void load(File csvFile) throws IOException {
    BufferedReader file = new BufferedReader(new FileReader(csvFile));

    String line;
    while ((line = file.readLine()) != null) {
      if (line.length() == 0 || line.trim().length() == 0 || line.charAt(0) == '#')
        continue;

      this.addValueAsString(line.trim().split(","));
    }

  }

}
