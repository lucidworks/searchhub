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
  var SUPPORT_HEADER = new RegExp("Submit a request\\s*$\\s*Sign in\\s*$\\s*Lucidworks Support\\s*$(\\s*Community\\s*$)*(\\s*Show topics\\s*$)*(\\s*Show all posts\\s*$)*(\\s*Lucidworks Community Questions\\s*$)*\\s*New post\\s*$(\\s*Show all\\s*$)?(\\s*Show no status\\s*$)?\\s*All\\s*$\\s*Planned\\s*$\\s*Not planned\\s*$\\s*Completed\\s*$\\s*Answered\\s*$\\s*No status\\s*$\\s*Sort by (votes|recent activity|comments|newest post)\\s*$\\s*Newest post\\s*$\\s*Recent activity\\s*$\\s*Votes\\s*$\\s*Comments\\s*$|", "gm");
  function Controller($sce, SnowplowService, PerDocumentService, DocumentDisplayHelperService, $log) {
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
      //make sure we can display the info
      $log.info("Process Docs Doc:", doc);
      doc['id'] = $sce.trustAsHtml(doc['id']);
      if (doc["content"]) {
        doc["content"] = doc["content"].replace(SUPPORT_HEADER, "");
      }
      if (doc["body"]) {
        doc["body"] = doc["body"].replace(SUPPORT_HEADER, "");
      }

      doc = DocumentDisplayHelperService.processDocument(doc);
      //console.log(doc.content.substring(0,250));

      return doc;
    }
  }




})();
/*
Submit a request
        Sign in

        Lucidworks Support

        Community

        Lucidworks Community Questions

    Lucidworks Community Questions

    New post

        Show no status

            All

            Planned

            Not planned

            Completed

            Answered

            No status

        Sort by votes

            Newest post

            Recent activity

            Votes

            Comments
 */