'use strict';

angular.module('appkitApp').config(function($stateProvider, $urlRouterProvider,$locationProvider) {

  // For any unmatched url, redirect to homepage /
  var defaultPage = 'search';
  $urlRouterProvider.otherwise(defaultPage);
  $locationProvider.html5Mode(false);


  // Default views
  $stateProvider

    // Default rule to display view based on url
    .state('page', {
      url: '/{slug}',
      templateUrl: function (params) {

        if (params.slug === '') {
          params.slug = defaultPage;
        }

        return 'views/' + params.slug + '.html';
      },
      controller: 'MainCtrl'
    })

    .state('details', {
      url: '/{slug}/{id}',
      templateUrl: function (params) {

        if (params.slug === '' || params.id === '') {
          params.slug = defaultPage;
        }

        return 'views/' + params.slug + '-detail.html';
      },
      controller: 'MainCtrl'
    })


});
