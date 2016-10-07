/*
The Snowplow Service uses https://github.com/snowplow/snowplow/wiki/javascript-tracker as means for sending
browser events to Fusion's signal service, which can then be used to drive things like recommendations and
document boosts

 */
(function () {
  'use strict';

  angular
    .module('searchHub.services.experiment', ['lucidworksView.services.apiBase',
      'lucidworksView.services.config'
    ])
    .factory('ExperimentManagementService', ExperimentManagementService);

  function ExperimentManagementService($log, $http, $q, ApiBase) {
    'ngInject';

    var service = {
      getVariant: getVariant,
      postReward: postReward
    };

    return service;



    function getVariant(experimentName){
      var experimentBase = ApiBase.getEndpoint() + "api/apollo/experiments/jobs/";
      var url = experimentBase + experimentName + "/variant";
      $log.info("Get variant for " + experimentName + " url: " + url);
      var deferred = $q.defer();
      $http
        .get(url)
        .then(success)
        .catch(failure);

      function success(response) {
        deferred.resolve(response.data);
      }

      function failure(err) {
        deferred.reject(err.data);
      }
      return deferred.promise;

    }

    function postReward(experimentName, choice, reward){
      var experimentBase = ApiBase.getEndpoint() + "api/apollo/experiments/jobs/";
      $log.info("post reward for " + experimentName + " and choice: " + choice + " reward: " + reward);
      var deferred = $q.defer();
      $http
        .put(experimentBase + experimentName + "/variant/" + choice, {"value": reward}, {"headers":{"Content-Type":"application/json"}})
        .then(success)
        .catch(failure);

      function success(response) {
        deferred.resolve(response.data);
      }

      function failure(err) {
        deferred.reject(err.data);
      }
      return deferred.promise;
    }


  }
})();
