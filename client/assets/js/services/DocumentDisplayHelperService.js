/**
 The QueryPipelineService invokes a Fusion query pipeline.  It is a bit more generic
 than the QueryDataService in View, but has much of the same functiionality.  Eventually we
 should migrate this to View.

 **/

(function () {
  'use strict';

  angular
      .module('searchHub.services.documentdisplayhelper',
          ['lucidworksView.services.apiBase',
            'lucidworksView.services.config'
          ])
      .factory('DocumentDisplayHelperService', DocumentDisplayHelperService);

  var EXTRA_SPACES = new RegExp("(^\\\s*$)", "gm");

  function DocumentDisplayHelperService(ConfigService, $filter) {
    'ngInject';

    var service = {
      processDocument: processDocument
    };
    return service;



    function processDocument(doc) {
      trim(doc, "content");
      trim(doc, "content_txt");
      trim(doc, "body");
      trim(doc, "description");
      doc.length_lFormatted = $filter('humanizeFilesize')(doc.length_l);
      doc.lastModified_dtFormatted = $filter('date')(doc.lastModified_dt);
      return doc;
    }

    function trim(doc, field) {
      if (doc[field] != null) {
        doc[field] = doc[field].replace(EXTRA_SPACES, "");
        doc[field] = doc[field].trim();
      }
    }
  }
})();