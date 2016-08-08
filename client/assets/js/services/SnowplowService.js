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
    //$log.info("User Id: " + userId);
    if (!userId) {
      var uuid = IDService.generateUUID();
      var options = {
        "expires": new Date(2030, 1, 1, 0, 0, 0, 0)
      };
      //$log.info("Defining user as: " + uuid);
      $cookies.putObject('shub_user_id', uuid, options);
    }
    //TODO: once we support registration, use that here instead of a cookie UUID
    snowplow('setUserIdFromCookie', 'shub_user_id');
    var service = {
      postClickSignal: postClickSignal,
      postSignalData: postSignalData,
      postSearchSignal: postSearchSignal,
      postTypeaheadSignal: postTypeaheadSignal,
      postClickRecommendation: postClickRecommendation
    };

    return service;

    function postClickRecommendation(element, docId, position, score, recType){
      $log.info("Click Signal Recommendation received for docId: " + docId);
      var queryObj = QueryService.getQueryObject();

      var the_data = {
        "docId": docId,
        "position": position,
        "query": queryObj.q,
        "score": score,
        "signalType": recType
      };
      //send the UUID with the data so that we can track specific query instances
      if (queryObj["uuid"]){
        the_data["query_unique_id"] = queryObj["uuid"];
      }
      if (queryObj.fq) {
        the_data["fq"] = queryObj.fq
      }
      postInternalClick(docId, element, the_data);
    }

    function postInternalClick(docId, element, the_data){
      $log.info("Signal Data: ", the_data);
      snowplow('trackLinkClick', docId, element.id, element.className, element.target, element.innerHTML, [{
        schema: "iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0",
        data: the_data
      }]);
    }

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
      postInternalClick(docId, element, the_data);
    }

    function postSearchSignal(queryObj, filters, numFound, displayedResults, displayedFacets) {
      var the_data = {
        "signalType": "search"
      };
      //send the UUID with the data so that we can track specific query instances
      if (queryObj["uuid"]){
        the_data["query_unique_id"] = queryObj["uuid"];
      }
      if (!displayedResults){
        displayedResults = [];
      }
      var facetLength = 0;
      if (!displayedFacets){
        displayedFacets = {};
      }
      var i = 0;
      _.forEach(displayedResults, function (doc) {
        the_data["doc_" + i] = doc["id"];
        i++;
      });

      _.forEach(displayedFacets, function (value, key, list) {
        //console.log("Key: " + key + " val: " );
        //console.log(value);
        if (key === "facet_queries"){
          //$log.debug("No signals sent for facet queries");//since View doesn't support displaying them yet
          /*_.forEach(value, function(facet_value, facet_name){
            console.log("fv: " + facet_value + " fn: " + facet_name);
            the_data["facet_query_" + facet_name]

          });*/
        } else if (key === "facet_fields"){
          i = 0;
          _.forEach(value, function(facet_value, facet_name){
            var facets = "";//comma separated list, so that we don't have a bunch of fields for each
            for (var j = 0; j < facet_value.length; j+= 2){
              facets += facet_value[j] + ":" + facet_value[j+1] + ";"
            }
            the_data["facet_fields_" + facet_name] = facets;
            i++;
          });
        } else if (key === "facet_ranges"){
          _.forEach(value, function(facet_value, facet_name){
            the_data["facet_ranges_" + facet_name + "_before"] = facet_value["before"];
            the_data["facet_ranges_" + facet_name + "_after"] = facet_value["after"];
            the_data["facet_ranges_" + facet_name + "_between"] = facet_value["between"];
            the_data["facet_ranges_" + facet_name + "_start"] = facet_value["start"];
            the_data["facet_ranges_" + facet_name + "_end"] = facet_value["end"];
            the_data["facet_ranges_" + facet_name + "_gap"] = facet_value["gap"];
            var facets = "";//comma separated list, so that we don't have a bunch of fields for each
            for (var j = 0; j < facet_value["counts"].length; j+= 2){
              facets += facet_value["counts"][j] + ":" + facet_value["counts"][j+1] + ";"
            }
            the_data["facet_ranges_" + facet_name] = facets;
          });
        } else if (key === "facet_intervals"){
          //$log.debug("No signals sent for facet intervals");
        } else if (key === "facet_heatmaps"){
          //$log.debug("No signals sent for facet heatmaps");
        }
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
