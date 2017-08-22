package com.lucidworks.searchhub.analytics;

import com.lucidworks.apollo.Name;
import com.lucidworks.spark.job.SparkJob;
import com.lucidworks.spark.job.SparkJobBuilder;

// DEPRECATED: Old mail threading job that does not work 
// @Name("mail-threading")
public class MailThreadSparkJobBuilder implements SparkJobBuilder<MailThreadSparkJobConfig> {
  @Override
  public SparkJob<?, MailThreadSparkJobConfig> buildSparkJob(String jobId, MailThreadSparkJobConfig config) {
    return new MailThreadSparkJob(jobId, config);
  }

  @Override
  public Class<MailThreadSparkJobConfig> getConfigClass() { return MailThreadSparkJobConfig.class; }
}
