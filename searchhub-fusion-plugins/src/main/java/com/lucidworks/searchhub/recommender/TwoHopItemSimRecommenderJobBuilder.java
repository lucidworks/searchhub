package com.lucidworks.searchhub.recommender;

import com.lucidworks.apollo.Name;
import com.lucidworks.spark.job.SparkJob;
import com.lucidworks.spark.job.SparkJobBuilder;

@Name("two-hop-item-similarity-recommender")
public class TwoHopItemSimRecommenderJobBuilder implements SparkJobBuilder<TwoHopItemSimRecommenderJobConfig> {
  @Override
  public SparkJob<?, TwoHopItemSimRecommenderJobConfig> buildSparkJob(String id, TwoHopItemSimRecommenderJobConfig config) {
    return new TwoHopItemSimRecommenderJob(id, config);
  }

  @Override
  public Class<TwoHopItemSimRecommenderJobConfig> getConfigClass() {
    return TwoHopItemSimRecommenderJobConfig.class;
  }
}
