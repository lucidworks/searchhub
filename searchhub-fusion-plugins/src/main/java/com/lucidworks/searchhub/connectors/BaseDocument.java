package com.lucidworks.searchhub.connectors;


import org.apache.commons.lang.WordUtils;
import org.apache.solr.common.SolrInputDocument;

/**
 *
 */
@SuppressWarnings("serial")
public class BaseDocument extends SolrInputDocument {
  public enum Source {
    lucid, modules, email, issue, issue_comment, wiki, web, code, book_section, refguide, searchhub
  }



  public static final String FIELD_ID             = "id";
  public static final String FIELD_DATA_SOURCE    = "data_source";
  public static final String FIELD_DATA_SOURCE_TYPE = "data_source_type";
  public static final String FIELD_DATA_SOURCE_NAME = "data_source_name";
  public static final String FIELD_PROJECT        = "project";
  public static final String FIELD_SOURCE         = "source";
  public static final String FIELD_URL            = "url";
  public static final String FIELD_TITLE          = "title";
  public static final String FIELD_CONTENT        = "body";
  public static final String FIELD_CREATED_DATE   = "dateCreated";
  public static final String FIELD_MODIFIED_DATE  = "lastModified";
  public static final String FIELD_CREATOR        = "author";
  public static final String FIELD_MODIFIER       = "modifier";
  public static final String FIELD_CONTENT_DISPLAY = "body_display";


  public BaseDocument(Source source, String project, String id) {
    this(source, project, id, "");
  }

  public BaseDocument(Source source, String project, String id, String list) {
    super();

    this.setField(FIELD_ID, id);
    String sourceName = source.name();
    this.setField(FIELD_SOURCE, sourceName);
    this.setField(FIELD_PROJECT, project);
  }
}
