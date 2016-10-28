(function() {
  'use strict';

  angular
    .module('searchHub.components.document_mail', ['lucidworksView.services.signals', 'angular-humanize'])
    .directive('documentMail', documentMail);

  function documentMail() {
    'ngInject';
    var directive = {
      restrict: 'EA',
      templateUrl: 'assets/components/document/document_mail/document_mail.html',
      scope: true,
      controller: Controller,
      controllerAs: 'vm',
      bindToController: {
        doc: '=',
        highlight: '=',
        expanded: '=',
        showBody: '=',
        documentBodyId: '='
      }
    };

    return directive;

  }

  function Controller($sce, SnowplowService, PerDocumentService, DocumentDisplayHelperService, $log, ExperimentManagementService) {
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
      ExperimentManagementService.postReward("document_body_experiment", vm.documentBodyId, 1.0);
    }

    function processDocument(doc) {
      //make sure we can display the info
      //$log.info(doc['subject']);
      doc = DocumentDisplayHelperService.processDocument(doc);
      doc['body'] = $sce.trustAsHtml(doc['body']);
      doc['subject'] = $sce.trustAsHtml(doc['subject']);
      //$log.info(doc['subject']);
      doc['id'] = $sce.trustAsHtml(doc['id']);
      return doc;
    }
  }
})();
