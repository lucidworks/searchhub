(function() {
  'use strict';

  angular
    .module('searchHub.components.document_github', ['lucidworksView.services.signals'])
    .directive('documentGithub', documentGithub);

  function documentGithub() {
    'ngInject';
    var directive = {
      restrict: 'EA',
      templateUrl: 'assets/components/document/document_github/document_github.html',
      scope: true,
      controller: Controller,
      controllerAs: 'vm',
      bindToController: {
        doc: '=',
        highlight: '='
      }
    };

    return directive;

  }

  function Controller($sce, SnowplowService, $filter, $log) {
    'ngInject';
    var vm = this;

    activate();

    function activate() {
      vm.postSignal = SnowplowService.postSignal;
      vm.postClickSignal = SnowplowService.postClickSignal;
      vm.doc = processDocument(vm.doc);
    }

    function processDocument(doc) {
      return doc;
    }

  }
})();
