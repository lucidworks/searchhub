package com.lucidworks.searchhub.analytics;

import com.lucidworks.apollo.spark.SparkJobConfig;
import org.codehaus.jackson.annotate.JsonCreator;
import org.codehaus.jackson.annotate.JsonProperty;
import org.codehaus.jackson.annotate.JsonTypeName;


@JsonTypeName("mail-threading")
public class MailThreadSparkJobConfig extends SparkJobConfig {
  public static final String TYPE = "mail_threading";

  @JsonCreator
  public MailThreadSparkJobConfig(@JsonProperty("id") String id) {
    super(id);
  }
}
