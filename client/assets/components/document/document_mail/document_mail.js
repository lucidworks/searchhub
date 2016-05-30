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

  function Controller($sce, SnowplowService, $filter, $log, QueryService) {
    'ngInject';
    var vm = this;

    activate();

    function activate() {
      vm.queryObject = QueryService.getQueryObject();
      $log.info("see Query Obj in document:");
      $log.info(vm.queryObject);

      vm.postSignal = SnowplowService.postSignal;
      vm.postClickSignal = SnowplowService.postClickSignal;
      vm.doc = processDocument(vm.doc);
    }

    function processDocument(doc) {
      //make sure we can display the info
      $log.info(doc['subject']);
      //doc['body'] = $sce.trustAsHtml(doc['body']);
      doc['subject'] = $sce.trustAsHtml(doc['subject']);
      $log.info(doc['subject']);
      doc['id'] = $sce.trustAsHtml(doc['id']);
      doc['test']=testFunction(doc['body'],vm.queryObject,100,1);
      $log.info("see output");
      $log.info(doc['test']);
      $log.info("see original");
      $log.info(doc['body']);
      doc.length_lFormatted = $filter('humanizeFilesize')(doc.length_l);
      doc.lastModified_dtFormatted = $filter('date')(doc.lastModified_dt);
      $log.info("see last modified");
      $log.info(doc.lastModified_dtFormatted);
      $log.info("see doc");
      $log.info(doc);
      return doc;
    }

    function testFunction(para,q,len,skip){
      //$log.info(para);
      q=q['q'];
      //$log.info(q);
      $log.info(para);
      $log.info(typeof para);
      var splittedIntoArray=para.split(/[\s,]+/);
      $log.info("see splitted");
      $log.info(splittedIntoArray);
      var containHighlight=splittedIntoArray.map(a=>a.toLowerCase().includes(q.toLowerCase()));
      $log.info("check variable");
      $log.info(containHighlight);
      $log.info(containHighlight.length);
      var paraLength=containHighlight.length;
      //$log.info(paraLength);
      var max=0;
      var maxind=0;
      var i=0;
      while (i+len<=paraLength){
        //$log.info("checkpoint");
        var tmp = containHighlight.slice(i,i+len).reduce((a, b) => a + b, 0);
        $log.info(tmp);
        if(tmp>max){
          max=tmp;
          maxind=i;
        }
        i=i+skip;
      }
      return splittedIntoArray.slice(maxind,maxind+len).join(" ");

    }


  }
})();
