(function() {
  'use strict';

  angular
    .module('searchHub.components.document_website', ['lucidworksView.services.signals'])
    .directive('documentWebsite', documentWebsite);

  function documentWebsite() {
    'ngInject';
    var directive = {
      restrict: 'EA',
      templateUrl: 'assets/components/document/document_website/document_website.html',
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

  function Controller(SnowplowService, PerDocumentService, DocumentDisplayHelperService, $log) {
    'ngInject';
    var vm = this;
    activate();

    function activate() {
      vm.postSignal = SnowplowService.postSignal;
      vm.postClickSignal = processClick;
      vm.doc = processDocument(vm.doc);
    }

    function processClick(element, docId, position, score, threadId, subjectSimple){
      SnowplowService.postClickSignal(element, docId, position, score);
      PerDocumentService.processPerDocument(docId, threadId, subjectSimple);
    }

    function processDocument(doc) {
      doc = DocumentDisplayHelperService.processDocument(doc);
      return doc;
    }

  }
})();
