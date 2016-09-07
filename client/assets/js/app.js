(function () {
  'use strict';

  angular
    .module('application', [
      'ui.router',
      'ngAnimate',
      'ngSanitize',
      'ngCookies',
      'nvd3',

      // Foundation
      'foundation',
      'foundation.dynamicRouting',
      'foundation.dynamicRouting.animations',

      // Libraries
      'ngOrwell',
      'rison',

      //Lucidworks View
      'lucidworksView.components',
      'lucidworksView.services',
      //lucidworksView.controllers',

      // SearchHub pieces
      'searchHub.components',
      'searchHub.services',
      'searchHub.controllers'
    ])
    .constant('_', window._) //eslint-disable-line
    .config(config)
    .run(run);

  /**
   * Main app config
   *
   * @param  {Provider} $urlRouterProvider    Provider for url
   * @param  {Provider} $httpProvider         Provider for http
   * @param  {Provider} $locationProvider     Provider for location
   * @param  {Provider} ApiBaseProvider       Provider for ApiBase
   * @param  {Provider} ConfigServiceProvider Provider for ConfigService
   */
  function config($urlRouterProvider, $httpProvider, $locationProvider, ApiBaseProvider,
    ConfigServiceProvider, $windowProvider) {
    'ngInject';
    $urlRouterProvider.otherwise('/search');
    //$httpProvider.interceptors.push('AuthInterceptor');
    //$httpProvider.defaults['withCredentials'] = true; //eslint-disable-line

    $locationProvider.html5Mode({
      enabled: true,
      requireBase: false
    });

    $locationProvider.hashPrefix('!');
    // If using a proxy use the same url.
    if (ConfigServiceProvider.config.use_proxy) {
      var $window = $windowProvider.$get();
      ApiBaseProvider.setEndpoint($window.location.protocol + '//' + $window.location.host +
        '/');
    } else {
      ApiBaseProvider.setEndpoint(ConfigServiceProvider.getFusionUrl());
    }
  }

  /**
   * Main app run time
   *
   * @param  {Service} $document     Document service
   */
  function run($document, $rootScope, ConfigService) {
    'ngInject';
    $rootScope.title = ConfigService.config.search_app_title;
  }
})();
