package com.lucidworks.apollo.pipeline.query.stages.searchhub.mail;

import com.lucidworks.apollo.pipeline.Context;
import com.lucidworks.apollo.pipeline.StageAssistFactoryParams;
import com.lucidworks.apollo.pipeline.query.QueryRequestAndResponse;
import com.lucidworks.apollo.pipeline.query.QueryStage;

// Placeholder for now, might not need it.
public class CFThreadRecommenderStage extends QueryStage<CFThreadRecommenderStageConfig> {

  protected CFThreadRecommenderStage(StageAssistFactoryParams params) {
    super(params);
  }

  @Override
  public QueryRequestAndResponse process(QueryRequestAndResponse queryRequestAndResponse, Context context) throws Exception {
    return null;
  }

  @Override
  public Class<CFThreadRecommenderStageConfig> getStageConfigClass() {
    return null;
  }
}
