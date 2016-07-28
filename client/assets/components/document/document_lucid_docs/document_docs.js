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
    var regex = new RegExp("(^\\\s*$)", "gm");
    activate();

    function activate() {
      vm.postSignal = SnowplowService.postSignal;
      vm.postClickSignal = processClick;
      vm.doc = processDocument(vm.doc);
    }

    function processClick(element, docId, position, score, threadId, subjectSimple){
      SnowplowService.postClickSignal(element, docId, position, score);
      var payload = {
        "docId": docId,
        "threadId": threadId,
        "subjectSimple": subjectSimple
      };
      perDocumentObservable.setContent(payload);
    }

    function processDocument(doc) {
      //make sure we can display the info
      //console.log(doc['subject']);
      doc['id'] = $sce.trustAsHtml(doc['id']);
      doc.content = doc.content.replace(regex, "");
      //TODO: this is fairly brittle given Zendesk could change.  Probably better to change the crawl to remove this boilerplate
      doc.content = doc.content.replace(HEADER, "");
      //Support docs tend to have a lot of excess whitespace and boilerplate, so let's remove some of it
      doc.content = doc.content.trim();
      //console.log(doc.content.substring(0,250));
      doc.length_lFormatted = $filter('humanizeFilesize')(doc.length_l);
      doc.lastModified_dtFormatted = $filter('date')(doc.lastModified_dt);
      return doc;
    }
  }

  var HEADER = new RegExp("Submit a request\\s*$\\s*Sign in\\s*$\\s*Lucidworks Support\\s*$(\\s*Community\\s*$)*(\\s*Show topics\\s*$)*(\\s*Show all posts\\s*$)*(\\s*Lucidworks Community Questions\\s*$)*\\s*New post\\s*$(\\s*Show all\\s*$)?(\\s*Show no status\\s*$)?\\s*All\\s*$\\s*Planned\\s*$\\s*Not planned\\s*$\\s*Completed\\s*$\\s*Answered\\s*$\\s*No status\\s*$\\s*Sort by (votes|recent activity|comments|newest post)\\s*$\\s*Newest post\\s*$\\s*Recent activity\\s*$\\s*Votes\\s*$\\s*Comments\\s*$|", "gm");


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