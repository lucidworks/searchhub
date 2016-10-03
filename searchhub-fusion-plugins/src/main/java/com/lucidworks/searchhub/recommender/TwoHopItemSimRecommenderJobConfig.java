package com.lucidworks.searchhub.recommender;

import com.lucidworks.apollo.spark.SparkJobConfig;
import org.codehaus.jackson.annotate.JsonCreator;
import org.codehaus.jackson.annotate.JsonProperty;

public class TwoHopItemSimRecommenderJobConfig extends SparkJobConfig {
  public static final String TYPE = "two-hop-item-similarity-recommender";

  @JsonCreator
  public TwoHopItemSimRecommenderJobConfig(@JsonProperty("id") String id) {
    super(id, TYPE);
  }

}

