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
        doc: '=bind',
        highlight: '='
      }
    };

    return directive;

  }

  function Controller($sce, SnowplowService, $filter, $log) {
    'ngInject';
    var vm = this;
    vm.shortenSubject={};
    activate();

    function activate() {
      vm.postSignal = SnowplowService.postSignal;
      vm.postClickSignal = SnowplowService.postClickSignal;
      vm.doc = processDocument(vm.doc);
      vm.shortenSubject=shortenSubject(vm.highlight);
    }

    function processDocument(doc) {
      //make sure we can display the info
      doc['shortSub']=doc['subject'].replace(/\s*\(.*?\)\s*/g, '').replace(/\s*\[.*?\]\s*/g, '');
      doc['shortSub']=$sce.trustAsHtml(doc['shortSub']);
      doc['body'] = $sce.trustAsHtml(doc['body']);
      doc['subject'] = $sce.trustAsHtml(doc['subject']);
      //$log.info(doc['subject']);
      doc['id'] = $sce.trustAsHtml(doc['id']);
      doc.length_lFormatted = $filter('humanizeFilesize')(doc.length_l);
      doc.lastModified_dtFormatted = $filter('date')(doc.lastModified_dt);
      return doc;
    }

    function shortenSubject(highlight){
      _.each(highlight, function(value,key){
        if(value['subject']){
          vm.shortenSubject[key]={'subject':(value['subject']+'').replace(/\s*\(.*?\)\s*/g, '').replace(/\s*\[.*?\]\s*/g, '')};
        }
        else{
          $log.info("no subject in highlight");
        }
      });
      return vm.shortenSubject;
    }



  }
})();
