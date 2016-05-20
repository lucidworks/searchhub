(function () {
  'use strict';

  angular
    .module('searchHub.components.search')
    .factory('SearchDataService', SearchDataService);

  function SearchDataService($http, $q, ConfigService, ApiBase, QueryBuilder, QueryDataService){
    'ngInject';

    return {
      getTypeaheadResults: getTypeaheadResults
    };

    ////////////

    function getTypeaheadResults(query){
      var deferred = $q.defer();
      var fullUrl = getQueryUrl() + '?suggest.q=' + query["q"];
      console.log(fullUrl);
      $http
        .get(fullUrl)
        .then(success)
        .catch(failure);

      function success(response) {
        deferred.resolve(response.data);
      }

      function failure(err) {
        console.log(err);
        deferred.reject(err.data);
      }

      return deferred.promise;
    }

    /**
     * Private function
     */
    function getQueryUrl(){
      var requestHandler = ConfigService.getTypeaheadRequestHandler();

      return QueryDataService.getPipelineEndpoint(ConfigService.getTypeaheadPipeline(), requestHandler);
    }

  }
})();
