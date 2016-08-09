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


  function Controller(QueryPipelineService, SnowplowService, Orwell, $log, $cookies) {
    'ngInject';
    var perDocumentObservable;
    var rc = this; //eslint-disable-line
    rc.mltDocs = [];
    rc.cfDocs = [];
    rc.preCFDocs = [];
    rc.postClickRecommendation = processClick;
    activate();

    ////////////////
    function processClick(element, docId, position, score, recType, threadId, subjectSimple){
      SnowplowService.postClickRecommendation(element, docId, position, score, recType);
      $log.info("Clicked on Rec", docId, position, score);
      var payload = {
        "docId": docId,
        "threadId": threadId,
        "subjectSimple": subjectSimple
      };
      perDocumentObservable.setContent(payload);
    }
    /**
     * Initializes a search from the URL object
     */
    function activate() {
      perDocumentObservable = Orwell.getObservable('perDocument');
      perDocumentObservable.addObserver(function (data) {
        if (data.docId) {

          //use the ID to hit the recommendation pipeline
          //QueryPipelineService.query()
          //We have a doc id, let's also get recommendations
          var userId = $cookies.getObject("shub_user_id");
          var recQuery = {
            "docId":  encodeURIComponent(data.docId),
            "userId": encodeURIComponent(userId),//TODO: should we also send in the session id and the fromEmail for the doc id?
            "threadId": data.threadId,
            "wt": "json"
          };
          if (data.subjectSimple){
            var subj = data.subjectSimple;
            if (subj.constructor === Array && subj.length > 0){
              subj = subj[0];
            }
            $log.info(subj);
            recQuery["subjectSimple"] = encodeURIComponent(subj);
          }
          var mltPromise = QueryPipelineService.queryPipeline(recQuery, "lucidfind-recommendations");
          mltPromise.then(function (data) {
            $log.info("Recs:", data);
            if (data && data.response && data.response.numFound > 0){
              rc.mltDocs = data.response.docs;
            } else {
              $log.warn("Unable to get recommendations, no docs found", data);
            }
          }, function (reason) {
            $log.warn("Unable to get recommendations", reason);
          });
          //Now call the collab filtering pipeline
          var cfPromise = QueryPipelineService.queryPipeline(recQuery, "cf-similar-items-rec");
          cfPromise.then(function (data) {
            $log.info("CF Recs:", data);
            if (data && data.response && data.response.numFound > 0){
              rc.cfDocs = data.response.docs;
            } else {
              $log.warn("Unable to get CF recommendations, no docs found", data);
            }
          }, function (reason) {
            $log.warn("Unable to get recommendations", reason);
          });
          //Now call the precomputed collab filtering pipeline
          var preCompPromise = QueryPipelineService.queryPipelineWithCollection("lucidfind_thread_recs", recQuery, "cf-similar-items-batch-rec");
          preCompPromise.then(function (data) {
            $log.info("pre CF Recs:", data);
            if (data && data.response && data.response.numFound > 0){
              rc.preCFDocs = data.response.docs;
            } else {
              $log.warn("Unable to get pre CF recommendations, no docs found", data);
            }
          }, function (reason) {
            $log.warn("Unable to get recommendations", reason);
          });
        }
      });
    }

  }
})();
