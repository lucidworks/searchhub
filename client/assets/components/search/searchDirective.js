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
    SearchDataService, SnowplowService, $log) {
    'ngInject';
    var ta = this;
    ta.typeaheadField = ConfigService.getTypeaheadField();
    ta.doTypeaheadSearch = doTypeaheadSearch;
    ta.selectedTypeahead = selectedTypeahead;
    ta.updateSearchQuery = updateSearchQuery;
    ta.initialValue = _.isArray(ta.query)?ta.query[0]:ta.query;
    var currentResults = null;

    function selectedTypeahead(object) {
      if (object) {
        //$log.info(object);
        var newValue = object.originalObject[ta.typeaheadField];
        var selection = _.isArray(newValue)?newValue[0]:newValue;
        //signal our selection
        SnowplowService.postTypeaheadSignal(ta.query, selection, object.originalObject["index"], currentResults);
        ta.query = htmlToPlaintext(selection);
      }
    }
    function htmlToPlaintext(text) {
     return text ? String(text).replace(/<[^>]+>/gm, '') : '';
    }

    function updateSearchQuery(inputString) {
      ta.query = inputString;
    }

    function doTypeaheadSearch(userInputString, timeoutPromise) {
      var deferred = $q.defer();

      function getResponse(query, suggestions) {
        ////{"responseHeader":{"status":0,"QTime":0},"suggest":{"fuzzy":{"hi":{"numFound":1,"suggestions":[{"term":"hive","weight":0,"payload":""}]}}}}
        var results = [];
        //$log.info(suggestions);
        _.forEach(suggestions, function(suggester){
          var res = suggester[query];
          if (res && res["numFound"] && res["numFound"] > 0){
            _.forEach(res["suggestions"], function(suggestion, index){
              suggestion["index"] = index;
              suggestion["term"] = htmlToPlaintext(suggestion["term"]);
              results.push(suggestion);
            })
          }
        });
        return results;
      }

      SearchDataService
        .getTypeaheadResults({q: ta.query, wt: 'json'})
        .then(function (resp) {
          if(resp.hasOwnProperty('suggest')) {
            var objectToResolve = {
              data: getResponse(ta.query, resp["suggest"])
            };
            currentResults = objectToResolve.data;
            deferred.resolve(objectToResolve);
          } else {
            deferred.reject('No response docs');
          }
        })
        .catch(function (error) {
          $log.error(error);
        });

      return deferred.promise;
    }


  }

})();
