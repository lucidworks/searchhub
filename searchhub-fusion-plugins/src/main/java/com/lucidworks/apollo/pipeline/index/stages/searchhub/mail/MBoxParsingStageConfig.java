package com.lucidworks.apollo.pipeline.index.stages.searchhub.mail;
// NOTE: Fusion ObjectMapper scans sub-packages of com.lucidworks.apollo.pipeline.index.stages for these configs!

import com.google.common.collect.Lists;
import com.lucidworks.apollo.pipeline.StageConfig;
import com.lucidworks.apollo.pipeline.schema.Annotations;
import com.lucidworks.apollo.pipeline.schema.Annotations.SchemaProperty;
import com.lucidworks.apollo.pipeline.schema.Annotations.ArrayProperty;
import com.lucidworks.apollo.pipeline.schema.Annotations.Schema;
import com.lucidworks.apollo.pipeline.schema.UIHints;
import org.codehaus.jackson.annotate.JsonIgnore;
import org.codehaus.jackson.annotate.JsonCreator;
import org.codehaus.jackson.annotate.JsonProperty;
import org.codehaus.jackson.annotate.JsonTypeName;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.regex.Pattern;


@JsonTypeName(MBoxParsingStageConfig.TYPE)
@Schema(
        type = MBoxParsingStageConfig.TYPE,
        title = "Mailbox Parsing Stage",
        description = "This stage does custom mailbox parsing"
)
public class MBoxParsingStageConfig extends StageConfig {
  private static Logger log = LoggerFactory.getLogger(MBoxParsingStageConfig.class);
  public static final String TYPE = "mbox-parsing";

  @SchemaProperty(title = "Bot Email Patterns", description = "These patterns will be applied to the From Email address to determine if the email is from a bot",
          hints = UIHints.ADVANCED)
  @ArrayProperty
  private final List<String> botEmails;

  @SchemaProperty(title = "Id Pattern", required = true,
          description = "The pattern to be applied to the Id to determine if this is a proper raw MBox Id from mod_mbox",
          hints = {UIHints.ADVANCED}, defaultValue = ".*/\\d{6}\\.mbox/raw/%3[Cc].*%3[eE]$")
  private final String idPatternStr;

  @JsonIgnore
  private final List<Pattern> botEmailPatterns;

  @JsonIgnore
  private final Pattern idPattern;

  @JsonCreator
  public MBoxParsingStageConfig(@JsonProperty("id") String id,
                                @JsonProperty("idPatternStr") String idPatternStr,
                                @JsonProperty("botEmails") List<String> botEmails
  ) {
    super(id);
    log.info("Id Pattern: {}, botEmails: {}", idPatternStr, botEmails);
    this.idPatternStr = idPatternStr;

    if (idPatternStr != null) {
      idPattern = Pattern.compile(idPatternStr);
    } else {
      idPattern = Pattern.compile(".*/\\d{6}\\.mbox/raw/%3[Cc].*%3[eE]$");
    }
    if (botEmails == null || botEmails.isEmpty()) {
      this.botEmails = Lists.newArrayList(
              ".*buildbot@.*",
              ".*git@.*",
              ".*hudson@.*",
              // way of filtering code reviews too?
              ".*jenkins@.*",
              ".*jira@.*",
              ".*subversion@.*",
              ".*svn@.*");
    } else {
      this.botEmails = Collections.unmodifiableList(botEmails);
    }
    botEmailPatterns = new ArrayList<>(this.botEmails.size());
    for (String botEmail : this.botEmails) {
      botEmailPatterns.add(Pattern.compile(botEmail));
    }
  }

  @JsonProperty("botEmails")
  public List<String> getBotEmails() {
    return botEmails;
  }

  @JsonProperty("idPatternStr")
  public String getIdPatternStr() {
    return idPatternStr;
  }

  @JsonIgnore
  public List<Pattern> getBotEmailPatterns() {
    return botEmailPatterns;
  }

  @JsonIgnore
  public Pattern getIdPattern() {
    return idPattern;
  }
}
