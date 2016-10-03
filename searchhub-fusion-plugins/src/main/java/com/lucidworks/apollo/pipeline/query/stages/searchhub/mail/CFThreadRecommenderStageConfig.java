package com.lucidworks.apollo.pipeline.query.stages.searchhub.mail;

import com.lucidworks.apollo.pipeline.StageConfig;
import com.lucidworks.apollo.pipeline.schema.Annotations;
import org.codehaus.jackson.annotate.JsonCreator;
import org.codehaus.jackson.annotate.JsonProperty;
import org.codehaus.jackson.annotate.JsonTypeName;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@JsonTypeName(CFThreadRecommenderStageConfig.TYPE)
@Annotations.Schema(
    type = CFThreadRecommenderStageConfig.TYPE,
    title = "Mailbox Parsing Stage",
    description = "This stage does custom mailbox parsing"
)
public class CFThreadRecommenderStageConfig extends StageConfig {
  private static Logger log = LoggerFactory.getLogger(CFThreadRecommenderStageConfig.class);
  public static final String TYPE = "cf-thread-rec";


  @JsonCreator
  protected CFThreadRecommenderStageConfig(@JsonProperty("id") String id) {
    super(id);
  }
}
