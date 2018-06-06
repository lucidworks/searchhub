'use strict';

/**
 * @ngdoc overview
 * @name appkitApp
 * @description
 * # appkitApp
 *
 * Main module of the application.
 */
angular
    .module('appkitApp', [
        'ui.router',
        'lightning'
    ]);

angular
  .module("appkitApp")
    .controller("ctrl",
    function($scope){
      $scope.changedValue = function(item) {
        // TODO: if item not null then activate button
        $scope.topic = item.id;
      }
    });