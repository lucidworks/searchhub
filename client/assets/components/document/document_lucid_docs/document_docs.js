(function() {
  'use strict';

  angular
    .module('searchHub.components.document_lucid_docs', ['lucidworksView.services.signals', 'angular-humanize'])
    .directive('documentLucidDocs', documentLucidDocs);

  function documentLucidDocs() {
    'ngInject';
    var directive = {
      restrict: 'EA',
      templateUrl: 'assets/components/document/document_lucid_docs/document_docs.html',
      scope: true,
      controller: Controller,
      controllerAs: 'vm',
      bindToController: {
        doc: '=',
        highlight: '=',
        expanded: "="
      }
    };

    return directive;

  }

  function Controller($sce, SnowplowService, $filter, Orwell) {
    'ngInject';
    var vm = this;
    var perDocumentObservable = Orwell.getObservable('perDocument');
    activate();

    function activate() {
      vm.postSignal = SnowplowService.postSignal;
      vm.postClickSignal = processClick;
      vm.doc = processDocument(vm.doc);
    }

    function processClick(element, docId, position, score){
      SnowplowService.postClickSignal(element, docId, position, score);
      var payload = {
        "docId": docId
      };
      perDocumentObservable.setContent(payload);
    }

    function processDocument(doc) {
      //make sure we can display the info
      //console.log(doc['subject']);
      doc['id'] = $sce.trustAsHtml(doc['id']);
      doc.length_lFormatted = $filter('humanizeFilesize')(doc.length_l);
      doc.lastModified_dtFormatted = $filter('date')(doc.lastModified_dt);
      return doc;
    }
  }
})();
