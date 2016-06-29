/**
 The QueryPipelineService invokes a Fusion query pipeline.  It is a bit more generic
 than the QueryDataService in View, but has much of the same functiionality.  Eventually we
 should migrate this to View.

 **/

(function () {
  'use strict';

  angular
      .module('searchHub.services.querypipeline',
          ['lucidworksView.services.apiBase',
        'lucidworksView.services.config'
      ])
      .factory('QueryPipelineService', QueryPipelineService);

  function QueryPipelineService(QueryDataService, ConfigService, QueryBuilder, $http, $q, ApiBase) {
    'ngInject';

    var service = {
      query: query,
      queryProfile: queryProfile,
      queryPipeline: queryPipeline,
      queryPipelineWithCollection: queryPipelineWithCollection
    };
    return service;

    /**
     * Query the ConfigService profile or pipeline (i.e. the profile/pipe in FUSION_CONFIG.js
     * @param queryObject
     */
    function query(queryObject) {
      if (ConfigService.getIfQueryProfile()) {
        return queryProfile(queryObject, ConfigService.getQueryProfile());
      } else {
        return queryPipeline(queryObject, ConfigService.getQueryPipeline());
      }

    }

    function doQuery(url) {
      var deferred = $q.defer();
      $http
          .get(url)
          .then(success)
          .catch(failure);

      function success(response) {
        // Set the content to populate the rest of the ui.
        deferred.resolve(response.data);
      }
      function failure(err) {
        deferred.reject(err.data);
      }

      return deferred.promise;
    }


    function queryProfile(queryObject, profileName) {
      var queryString = QueryBuilder.objectToURLString(queryObject);
      return doQuery(getQueryUrl(profileName, null) + '?' + queryString);
    }

    function queryPipelineWithCollection(collection, queryObject, pipelineName){
      var queryString = QueryBuilder.objectToURLString(queryObject);
      var theUrl = ApiBase.getEndpoint() + 'api/apollo/query-pipelines/' +
          pipelineName + '/collections/' + collection +
          '/select?' + queryString;
      return doQuery(theUrl);
    }

    /**
     * return a promise on the $http.get
     * @param queryObject
     * @param pipelineName
     */
    function queryPipeline(queryObject, pipelineName) {
      var queryString = QueryBuilder.objectToURLString(queryObject);
      return doQuery(getQueryUrl(null, pipelineName) + '?' + queryString);

    }

    function getQueryUrl(profile, pipeline) {
      if (profile){
        return QueryDataService.getProfileEndpoint(profile, 'select');
      } else {
        return QueryDataService.getPipelineEndpoint(pipeline, 'select');
      }
    }
  }
})();