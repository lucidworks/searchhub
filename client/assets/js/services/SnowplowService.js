/*
The Snowplow Service uses https://github.com/snowplow/snowplow/wiki/javascript-tracker as means for sending
browser events to Fusion's signal service, which can then be used to drive things like recommendations and
document boosts

 */
(function () {
  'use strict';

  angular
    .module('searchHub.services.snowplow', ['lucidworksView.services.apiBase',
      'lucidworksView.services.config'
    ])
    .factory('SnowplowService', SnowplowService);

  function SnowplowService(QueryService, IDService, $window, $log, $cookies) {
    'ngInject';
    var snowplow = $window.searchhub_snowplow;
    var userId = $cookies.getObject("shub_user_id");
    $log.info("User Id: " + userId);
    if (!userId) {
      var uuid = IDService.generateUUID();
      var options = {
        "expires": new Date(2030, 1, 1, 0, 0, 0, 0)
      };
      $log.info("Defining user as: " + uuid);
      $cookies.putObject('shub_user_id', uuid, options);
    }
    //TODO: once we support registration, use that here instead of a cookie UUID
    snowplow('setUserIdFromCookie', 'shub_user_id');
    var service = {
      postClickSignal: postClickSignal,
      postSignalData: postSignalData,
      postSearchSignal: postSearchSignal,
      postTypeaheadSignal: postTypeaheadSignal
    };

    return service;



    //Useful when doing a simple click
    function postClickSignal(element, docId, position, score) {
      $log.info("Click Signal received for docId: " + docId);
      var queryObj = QueryService.getQueryObject();

      var the_data = {
        "docId": docId,
        "position": position,
        "query": queryObj.q,
        "score": score,
        "signalType": "click"
      };
      //send the UUID with the data so that we can track specific query instances
      if (queryObj["uuid"]){
        the_data["query_unique_id"] = queryObj["uuid"];
      }
      if (queryObj.fq) {
        the_data["fq"] = queryObj.fq
      }
      $log.info("Signal Data: " + the_data);
      snowplow('trackLinkClick', docId, element.id, element.className, element.target, element.innerHTML, [{
        schema: "iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0",
        data: the_data
      }]);
    }

    function postSearchSignal(queryObj, filters, numFound, displayedResults) {
      var the_data = {
        "signalType": "search"
      };
      //send the UUID with the data so that we can track specific query instances
      if (queryObj["uuid"]){
        the_data["query_unique_id"] = queryObj["uuid"];
      }
      var i = 0;
      _.forEach(displayedResults, function (doc) {
        the_data["doc_" + i] = doc["id"];
        i++;
      });
      if (!filters) {
        filters = "";
      }
      var queryTerms = queryObj.q.split(" ");
      $log.info("Posting: " + queryTerms + " filters: " + filters + " numFound: " + numFound + " results length: " + displayedResults.length);
      snowplow('trackSiteSearch',
        queryTerms,
        filters,
        numFound,
        displayedResults.length,
        [{
          schema: "iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0",
          data: the_data
        }]
      );
    }

    function postTypeaheadSignal(typeahead_query, selection, selection_index, typeahead_list){
      var the_data = {
        "signalType": "typeahead",
        "typeahead_query": typeahead_query,//the characters the user typed to make a selection
        "selection": selection,
        "index": selection_index
      };
      if (typeahead_list){
        _.each(typeahead_list, function(entry, index){
          the_data["entry_" + index] = entry;
        })
      }
      postSignalData(null, the_data);
    }

    /*
     *
     * */
    function postSignalData(element, data) {
      $log.info("Posting general signal data as an unstructured event");
      snowplow('trackUnstructEvent', {
        schema: 'iglu:com.acme_company/viewed_product/jsonschema/2-0-0',
        data: data
      });
    }

  }
})();
