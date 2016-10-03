package com.lucidworks.searchhub.analytics;

import com.lucidworks.spark.job.SparkJob;
import org.apache.spark.SparkContext;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.sql.DataFrame;
import org.apache.spark.sql.SQLContext;
import org.apache.spark.sql.SaveMode;

import java.util.HashMap;
import java.util.Map;

public class MailThreadSparkJob extends SparkJob<Long, MailThreadSparkJobConfig> {

  public MailThreadSparkJob(String jobId, MailThreadSparkJobConfig jobConfig) {
    super(jobId, jobConfig);
  }

  @Override
  public Long run(JavaSparkContext javaSparkContext) {
    SparkContext ctx = SparkContext.getOrCreate(javaSparkContext.getConf());
    SQLContext sqlContext = SQLContext.getOrCreate(ctx);

    // TODO: load these options from the config
    Map<String, String> options = new HashMap<>();
    options.put("zkHost", "localhost:9983");
    options.put("collection", "lucidfind");
    options.put("query", "*:*");
    Boolean overrideThreadIds = true;

    DataFrame mailDataFrame = sqlContext.read().format("solr").options(options).load();
    mailDataFrame = MailThreadJob.createThreadGroups(mailDataFrame, MailThreadJob.accumulators(ctx), overrideThreadIds);
    long numDocs = MailThreadJob.countThreads(mailDataFrame);
    mailDataFrame.write().format("solr").options(options).mode(SaveMode.Overwrite).save();
    return numDocs;
  }
}
