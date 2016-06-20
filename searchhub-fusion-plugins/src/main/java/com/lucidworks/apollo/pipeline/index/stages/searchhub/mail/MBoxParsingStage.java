package com.lucidworks.apollo.pipeline.index.stages.searchhub.mail;


import com.google.inject.assistedinject.Assisted;
import com.lucidworks.apollo.common.pipeline.PipelineDocument;
import com.lucidworks.apollo.common.pipeline.PipelineField;
import com.lucidworks.apollo.pipeline.AutoDiscover;
import com.lucidworks.apollo.pipeline.Context;
import com.lucidworks.apollo.pipeline.StageAssistFactory;
import com.lucidworks.apollo.pipeline.StageAssistFactoryParams;
import com.lucidworks.apollo.pipeline.StageOutput;
import com.lucidworks.apollo.pipeline.index.IndexStage;
import com.lucidworks.searchhub.connectors.mail.handler.MimeMailParser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.inject.Inject;

@AutoDiscover(type = MBoxParsingStageConfig.TYPE, factory = MBoxParsingStage.Factory.class)
public class MBoxParsingStage extends IndexStage<MBoxParsingStageConfig> {
  private final Logger logger = LoggerFactory.getLogger(MBoxParsingStage.class);

  public interface Factory extends StageAssistFactory<PipelineDocument, MBoxParsingStage> {}

  @Override
  public Class<MBoxParsingStageConfig> getStageConfigClass() {
    return MBoxParsingStageConfig.class;
  }

  @Inject
  public MBoxParsingStage(@Assisted StageAssistFactoryParams params) {
    super(params);
  }

  @Override
  public void process(PipelineDocument doc, Context context, StageOutput<PipelineDocument> output) throws Exception {
    logger.info("running MBoxParsingStage on " + doc.getId() + " (which has " + doc.getAllFieldNames().size() + " fields )");

    // TODO: should be cached for better throughput
    MBoxParsingStageConfig config = getConfiguration();
    MimeMailParser parser = new MimeMailParser(config.getIdPattern(), config.getBotEmailPatterns());
    PipelineDocument newDoc = parser.parse(doc);
    if (newDoc == null) {
      return;
    }
    if (newDoc.hasField("publishedOnDate")) {
      logger.info("parsed mail message with docId: " + newDoc.getId() + " has publishedOnDate: "
        + newDoc.getFirstFieldValue("publishedOnDate"));
      output.send(newDoc, context);
    } else {
      logger.info("docId: " + newDoc.getId() + " has no publishedOnDate, dropping");
    }
  }
}
