(function () {
  'use strict';
  angular
      .module('searchHub.components.recommendations', ['searchHub.services', 'lucidworksView.services',
        'angucomplete-alt', 'angular-humanize'])
      .directive('recommendations', recommendations);

  function recommendations() {
    'ngInject';

    return {
      restrict: 'EA',
      templateUrl: 'assets/components/recommendations/recommendations.html',
      controller: Controller,
      controllerAs: 'rc',
      bindToController: {},
      scope: true,
      replace: true
    };
  }


  function Controller(QueryPipelineService, Orwell, $log, $cookies) {
    'ngInject';
    $log.info("Rec init");
    var perDocumentObservable;
    var rc = this; //eslint-disable-line

    activate();

    ////////////////

    /**
     * Initializes a search from the URL object
     */
    function activate() {
      $log.info("rec here");
      perDocumentObservable = Orwell.getObservable('perDocument');
      perDocumentObservable.addObserver(function (data) {
        if (data.docId) {
          //use the ID to hit the recommendation pipeline
          //QueryPipelineService.query()
          //We have a doc id, let's also get recommendations
          var userId = $cookies.getObject("shub_user_id");
          var recQuery = {
            "docIs":  encodeURIComponent(data.docId),
            "userId": encodeURIComponent(userId),//TODO: should we also send in the session id and the fromEmail for the doc id?
            "wt": "json"
          };
          var thePromise = QueryPipelineService.queryPipeline(recQuery, "lucidfind-recommendations");
          thePromise.then(function (data) {
            $log.info("Recs:", data);
          }, function (reason) {
            $log.warn("Unable to get recommendations", reason);
          })
        }
      });
    }

  }
})();
