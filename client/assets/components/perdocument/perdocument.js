(function () {
  'use strict';
  angular
      .module('searchHub.components.perdocument', ['searchHub.services', 'lucidworksView.services',
        'angucomplete-alt', 'angular-humanize'])
      .directive('perdocument', perdocument);

  function perdocument() {
    'ngInject';
    console.log("pd init");
    return {
      restrict: 'EA',
      templateUrl: 'assets/components/perdocument/perdocument.html',
      controller: DocumentController,
      controllerAs: 'dc',
      bindToController: {
      },
      scope: true,
      replace: true
    };
  }


  function DocumentController(QueryPipelineService, SnowplowService,
                              Orwell, $log, $cookies) {
    'ngInject';
    $log.info("DC init");
    var dc = this; //eslint-disable-line
    var perDocumentObservable = Orwell.getObservable('perDocument');
    dc.decorateDocument = decorateDocument;
    dc.getDocType = getDocType;
    dc.backToSearchResults = backToSearchResults;
    dc.docs = [];//TODO: hack so that we can reuse the document template directives
    dc.docType = "";
    activate();

    ////////////////

    /**
     * Initializes a search from the URL object
     */
    function activate() {


      perDocumentObservable.addObserver(function (data) {
        dc.doc_id = data.docId;
        $log.info("PD perD", data, dc.doc_id);
        var query = {
          "q": "id:" + encodeURIComponent(dc.doc_id),
          "wt": "json",
          "rows": 1
        };
        var thePromise = QueryPipelineService.query(query);
        thePromise.then(function(data){
          parseDocument(data);
          $log.info("resolved", data, dc.docs);
        }, function(reason){
          $log.warn("Unabled to fetch the document", reason);
          perDocumentObservable.setContent({});
        });
      });

    }

    function backToSearchResults(){
      //TODO: send a signal
      perDocumentObservable.setContent({});
    }

    /**
     * Decorates the document object before sending to the document directive.
     * @param  {object} doc Document object
     * @return {object}     Document object
     */
    function decorateDocument(doc) {
      return doc;
    }

    function parseDocument(data) {
      $log.info("parse", data);
      //we only expect one here, since we are querying by ID
      if (data && data.response && data.response.numFound > 0) {
        dc.docs = data.response.docs;
        //dc.docType = getDocType(dc.doc);
        $log.info("DC.doc", dc.docs);
      } else {
        $log.warn("Unable to retrieve the document")
      }
    }

    //TODO: duplicated from documents.js
    /**
     * Get the document type for the document.
     * @param  {object} doc Document object
     * @return {string}     Type of document
     */
    function getDocType(doc) {
      // Change to your collection datasource type name
      // if(doc['_lw_data_source_s'] === 'MyDatasource-default'){
      //   return doc['_lw_data_source_s'];
      // }
      var ds = doc['_lw_data_source_s'];
      if (ds) {
        if (ds.indexOf("lucidworks-docs") != -1 || ds.indexOf("lucidworks-knowledge") != -1) {
          return "lucid-docs";
        }
        var idx = ds.indexOf("-");
        if (idx != -1) {
          return ds.substring(0, idx)
        }
      }
      //if we can't figure out the data source name, then let's use the type
      return doc['_lw_data_source_type_s'];
    }

  }
})();
