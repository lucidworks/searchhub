/*
The Snowplow Service uses https://github.com/snowplow/snowplow/wiki/javascript-tracker as means for sending
browser events to Fusion's signal service, which can then be used to drive things like recommendations and
document boosts

 */
(function () {
  'use strict';

  angular
    .module('searchHub.services.perdocument', ['lucidworksView.services.apiBase',
      'lucidworksView.services.config'
    ])
    .factory('PerDocumentService', PerDocumentService);

  function PerDocumentService(Orwell, $log) {
    'ngInject';

    var perDocumentObservable = Orwell.getObservable('perDocument');

    var service = {
      processPerDocument: processPerDocument
    };

    return service;

    function processPerDocument(docId, threadId, subjectSimple){
      docId = docId + "";
      $log.info("Process per doc:", docId);
      if (docId && docId.endsWith("_original") == false) {//as long as we aren't clicking through to the original document
        var payload = {
          "docId": docId,
          "threadId": threadId,
          "subjectSimple": subjectSimple
        };
        perDocumentObservable.setContent(payload);
      }
    }

  }
})();
