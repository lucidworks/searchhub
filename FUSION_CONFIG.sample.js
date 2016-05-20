appConfig = { //eslint-disable-line
  // If you don't know what you want for some configuration items,
  // leave them as-is and see what happens in UI.
  // You may need to clear browser history/cache before your changes take affect.

  /**
   * Styles and colors
   *
   * In addition to the functional settings in this file,
   * you can edit the settings file in client/assets/scss/_settings.scss
   *
   * There you can edit settings to change look and feel such as colors, and other
   * basic style parameters.
   */

  /**
   * localhost is used here for same computer use only.
   * You will need to put a hostname or ip address here if you want to go to
   * view this app from another machine.
   */
  host: 'http://localhost',
  port:'8764',

  /**
   * The name of the realm to connect with
   *   default: 'native'
   */
  connection_realm: 'native',

  /**
   * Anonymous access
   *
   * To allow anonymous access add a valid username and password here.
   *
   * SECURITY WARNING
   * It is recommended you use an account with the 'search' role
   * to use anonymous access.
   */
  anonymous_access: {
    username: 'search-user',
  //  password: 'search-user-password-here'
  },

  // The name of your collection
  collection: 'lucidfind',

  // Please specify a pipeline or profile that you want to leverage with this UI.
  query_pipeline_id: 'default',
  query_profile_id: 'default',
  use_query_profile: true, // Force use of query-profile

  // Search UI Title
  // This title appears in a number of places in the app, including page title.
  // In the header it is replaced by the logo if one is provided.
  search_app_title: 'Lucidworks Search Hub',
  // Specify the path to your logo relative to the root app folder.
  // Or use an empty string if you don't want to use a logo.
  // This file is relative to the client folder of your app.
  logo_location: 'assets/img/logo/lucidworks-white.svg',

  /**
   * Document display
   * Fusion seed app is set up to get you started with the following field types.
   * web, local file, jira, slack, and twitter.
   *
   * Customizing document display.
   * You can add your own document displays with Fusion Seed App. You will have to
   * write an html template and add a new directive for your document type.
   * @see https://github.com/lucidworks/lucidworks-view/blob/master/docs/Customizing_Documents.md
   *
   * If you want to edit an existing template for a datasource you can edit the html for that document type in the
   * client/assets/components/document folder.
   */

  /**
   * Default Document display
   *
   * This applies only to document displays that are not handled by the handful of
   * document templates used above.
   *
   * These parameters change the fields that are displayed in the fallback document display.
   * You can also add additional fields by editing the document template.
   * Default Document template is located at:
   *   your_project_directory/client/assets/components/document/document_default/document_default.html
   */
  //In search results, for each doc, display this field as the head field
  head_field: 'id',
  subhead_field: 'subtitle',
  description_field: 'description',
  //In search results, for each doc, use this field to generate link value when a user clicks on head_field
  head_url_field: 'url',
  //In search results, display a image in each doc page (leave empty for no image).
  image_field: 'image',

  // ADDING ADDITIONAL FIELDS TO DEFAULT DOCUMENTS
  //
  // There are 2 ways to add additional fields to the ui.
  // You can either use settings to create a simple list of values with field
  // names or you can edit the html/css, which is far more robust and allows
  // for more customization.
  //
  // SIMPLE CONFIG BASED FIELD DISPLAY
  //
  // This is the simpler option, but wont look as good.
  // It creates a list of field names next to field results
  // in the format of:
  // field label: field result
  //
  // In order to add items to the list you must add the fields to
  // fields_to_display. You can change the label of any field by adding a
  // field mapping in field_display_labels. You can optionally use a wildcard '*'
  // to display all fields.
  //
  // FLEXIBLE HTML FIELD DISPLAY
  //
  // For more advanced layouts edit the document template this provides a great
  // deal of flexibility and allows you to add more complex logic to your results.
  // You are able to use basic javascript to show hide, or alter the display of
  // any or multiple results.
  //
  // The HTML/Angular template is located in the following directory:
  //    your_project_directory/client/assets/components/document/document.html
  fields_to_display:['title','id','name', '*'],
  field_display_labels: {
    'name': 'Document Name',
    '_lw_data_source_s': 'Source',
    'project': 'Project',
    'author_facet': 'Author'
    //'id': 'Identification Number'
    // you can add as many lines of labels as you want
  },

  /**
   * Number of documents shown per page, if not defined will default to 10.
   */
  // docs_per_page: 10,

  /**
   * Landing pages
   *
   * Fusion allows mapping of specific queries links (or other data) with it's
   * landing pages QueryPipeline stage.
   *
   * Default: Do not redirect but show a list of urls that a user can go to.
   */

  // If enabled and a landing page is triggered via a query, the app will redirect
  // the user to the url provided.
  landing_page_redirect: true,

  /**
   * Sorts
   *
   * A list of field names to make available for users to sort their results.
   *
   * NOTE: Only non multi-valued fields are able to be sortable.
   *
   * In order to sort on a multi-valued field you will have to fix the schema
   * for that field and recrawl the data
   */
  //sort_fields: ['title'],

  /**
   * Signals
   *
   * Allow the collection of data regarding search results. The most typical use
   * case is to track click signals for a collection.
   */
  // Signal type for title click.
  signal_type: 'click',
  // This specifies the index pipeline that will be used to submit signals.
  signals_pipeline: '_signals_ingest', // '_signals_ingest' is the fusion default.
  // Should be a unique field per document in your collection.
  // used by signals as a reference to the main collection.
  signals_document_id: 'id',

  /**
   * Typeahead
   *
   * Typeahead or autocomplete shows you a number of suggested queries as you
   * type in the search box.
   */
  typeahead_query_pipeline_id: 'shub-typeahead',
  //typeahaed_query_profile_id: 'default',
  typeahead_fields: ['term'],
  // The request handler defines how typeahead gets it's results.
  // It is recommended to use suggest as it is more performant.
  // It will require some additional configuration.
  // @see https://lucidworks.com/blog/2016/02/04/fusion-plus-solr-suggesters-search-less-typing/

  //typeahead_requesthandler: 'suggest', // recommended (requires configuration)
  typeahead_requesthandler: 'suggest'

};
