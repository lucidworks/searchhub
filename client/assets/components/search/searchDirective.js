(function () {
  'use strict';

  angular
    .module('searchHub.components.search')
    .directive('search', search);

  function search() {
    'ngInject';
    return {
      restrict: 'EA',
      controller: Controller,
      templateUrl: 'assets/components/search/search.html',
      scope: true,
      controllerAs: 'ta',
      bindToController: {
        query: '='
      },
      require: '^form'
    };
  }

  function Controller($scope, $q, ConfigService, QueryService,
    SearchDataService) {
    'ngInject';
    var ta = this;
    ta.typeaheadField = ConfigService.getTypeaheadField();
    ta.doTypeaheadSearch = doTypeaheadSearch;
    ta.selectedSomething = selectedSomething;
    ta.updateSearchQuery = updateSearchQuery;
    ta.initialValue = _.isArray(ta.query)?ta.query[0]:ta.query;

    function selectedSomething(object) {
      if (object) {
        var newValue = object.originalObject[ta.typeaheadField];
        ta.query = _.isArray(newValue)?newValue[0]:newValue;
      }
    }

    function updateSearchQuery(inputString) {
      ta.query = inputString;
    }

    function doTypeaheadSearch(userInputString, timeoutPromise) {
      var deferred = $q.defer();

      function getResponse(query, suggestions) {
        ////{"responseHeader":{"status":0,"QTime":0},"suggest":{"fuzzy":{"hi":{"numFound":1,"suggestions":[{"term":"hive","weight":0,"payload":""}]}}}}
        console.log(query);
        console.log(suggestions);
        var results = [];
        _.forEach(suggestions, function(suggester){
          console.log("sug");
          console.log(suggester);
          var res = suggester[query];
          console.log(res);
          if (res["numFound"] > 0){
            _.forEach(res["suggestions"], function(suggestion){
              results.push(suggestion);
            })
          }
        });
        return results;
      }

      SearchDataService
        .getTypeaheadResults({q: ta.query, wt: 'json'})
        .then(function (resp) {
          console.log(resp);
          if(resp.hasOwnProperty('suggest')) {
            var objectToResolve = {

              data: getResponse(ta.query, resp["suggest"])
            };
            deferred.resolve(objectToResolve);
          } else {
            deferred.reject('No response docs');
          }
        })
        .catch(function (error) {
          timeoutPromise.reject(error);
        });

      return deferred.promise;
    }


  }

})();
