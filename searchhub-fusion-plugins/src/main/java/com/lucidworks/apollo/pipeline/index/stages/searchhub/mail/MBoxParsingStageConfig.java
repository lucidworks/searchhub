package com.lucidworks.apollo.pipeline.index.stages.searchhub.mail;
// NOTE: Fusion ObjectMapper scans sub-packages of com.lucidworks.apollo.pipeline.index.stages for these configs!

import com.lucidworks.apollo.pipeline.StageConfig;
import com.lucidworks.apollo.pipeline.schema.Annotations.Schema;
import org.codehaus.jackson.annotate.JsonCreator;
import org.codehaus.jackson.annotate.JsonProperty;
import org.codehaus.jackson.annotate.JsonTypeName;


@JsonTypeName(MBoxParsingStageConfig.TYPE)
@Schema(
  type = MBoxParsingStageConfig.TYPE,
  title = "Mailbox Parsing Stage",
  description = "This stage does custom mailbox parsing"
)
public class MBoxParsingStageConfig extends StageConfig {

  public static final String TYPE = "mbox-parsing";

  @JsonCreator
  public MBoxParsingStageConfig(@JsonProperty("id") String id) {
    super(id);
  }
}
