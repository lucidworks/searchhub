package com.lucidworks.searchhub.connectors.stackoverflow;


import com.lucidworks.apollo.pipeline.schema.ArrayType;
import com.lucidworks.apollo.pipeline.schema.StringType;
import com.lucidworks.apollo.pipeline.schema.UIHints;
import com.lucidworks.common.models.DataSourceConstants;
import com.lucidworks.common.models.DataSourceType;

/**
 *
 *
 **/

public class StackOverflowType extends DataSourceType {
  public static final String TYPE = "stack-overflow-connector";
  public static final String CATEGORY = DataSourceConstants.CATEGORY_SOCIAL;
  public static final String TITLE = "Stack Overflow Connector";
  public static final String DESCRIPTION = "Connects to Stack Overflow and returns questions, answers and other data from StackOverflow";

  public static final String TAGS = "tags";
  public static final String CLIENT_ID = "client_id";
  public static final String CLIENT_SECRET = "client_secret";
  public static final String KEY = "key";

  public StackOverflowType() {
    super(CATEGORY, DESCRIPTION, TITLE);
  }

  @Override
  protected void addConnectorSpecificSchema() {
    schema.withProperty(TAGS, ArrayType.createStringArray(StringType.create()).withDescription("Set of tags to restrict on").withTitle("Tags to Follow"));
    schema.withProperty(CLIENT_ID, StringType.create().withTitle("Client ID").withDescription("The Client ID of your Stack Overflow Application. See https://api.stackexchange.com/docs/authentication for more information"));
    schema.withProperty(CLIENT_SECRET, StringType.create().withTitle("Client Secret").withDescription("The client secret of your application").withHints(UIHints.SECRET));
    //TODO: figure out OAuth flow

  }
}
