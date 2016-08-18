(function() {
  'use strict';

  angular
    .module('searchHub.components.document_stack_overflow', ['lucidworksView.services.signals'])
    .directive('documentStackOverflow', documentStackOverflow);

  function documentStackOverflow() {
    'ngInject';
    var directive = {
      restrict: 'EA',
      templateUrl: 'assets/components/document/document_stack_overflow/document_stack_overflow.html',
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

  //var STACK_HEADER = new RegExp("current community")

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
      if (doc["question_txt"]){ //we're specifically going to do a substring here instead of <field> truncation, b/c we don't want the "Read More" in the title.
        doc["question_txt_trunc"] = doc["question_txt"][0].substring(0, 200) + "...";
      }
      doc = DocumentDisplayHelperService.processDocument(doc);
      /*if (doc["body"]) {
        doc["body"] = doc["body"].replace(STACK_HEADER, "");
      }*/
      return doc;
    }

  }
})();
