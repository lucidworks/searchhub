package com.lucidworks.searchhub.recommender;

import com.lucidworks.spark.job.SparkJob;
import org.apache.spark.SparkContext;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.sql.SQLContext;


public class TwoHopItemSimRecommenderJob extends SparkJob<Long, TwoHopItemSimRecommenderJobConfig> {
  public TwoHopItemSimRecommenderJob(String jobId, TwoHopItemSimRecommenderJobConfig jobConfig) {
    super(jobId, jobConfig);
  }

  @Override
  public Long run(JavaSparkContext javaSparkContext) {
    SparkContext ctx = SparkContext.getOrCreate(javaSparkContext.getConf());
    SQLContext sqlContext = SQLContext.getOrCreate(ctx);
    return SimpleTwoHopRecommender.runRecs(sqlContext, 10, 100);
  }
}
