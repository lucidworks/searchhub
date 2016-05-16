package com.lucidworks.searchhub.analytics;

import com.lucidworks.apollo.spark.SparkJobConfig;
import org.codehaus.jackson.annotate.JsonProperty;

public class MailThreadSparkJobConfig extends SparkJobConfig {
  public static final String TYPE = "mail_threading";

  public MailThreadSparkJobConfig(@JsonProperty("id") String id) {
    super(id, TYPE);
  }
}
