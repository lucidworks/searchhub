(function() {
  'use strict';
  angular
    .module('searchHub.controllers.home', ['searchHub.services', 'lucidworksView.services', 'angucomplete-alt', 'angular-humanize'])
      .config(Config)
    .controller('HomeController', HomeController);


  function Config(OrwellProvider) {
    'ngInject';
    OrwellProvider.createObservable('perDocument', {});
  }

  function HomeController($filter, $timeout, ConfigService, QueryService, URLService, Orwell, AuthService, _, $log, $http, $window, $location) {

    'ngInject';
    var hc = this; //eslint-disable-line
    var resultsObservable;
    var perDocumentObservable;
    var query;
    var sorting;

    hc.searchQuery = '*';
    hc.sort = "score";
    activate();

    ////////////////

    /**
     * Initializes a search from the URL object
     */
    function activate() {
      hc.search = doSearch;
      hc.logout = logout;
      hc.onChangeSort = onChangeSort;
      hc.appName = ConfigService.config.search_app_title;
      hc.logoLocation = ConfigService.config.logo_location;
      hc.status = 'loading';
      hc.lastQuery = '';
      hc.grouped = false;
      hc.perDocument = false;
      hc.showRecommendations = false;
      hc.signup = signup;
      hc.login = login;
      hc.signupError = false;
      hc.loginError = false;
      hc.is_login = false;
      query = URLService.getQueryFromUrl();
      console.log(QueryService.getQueryObject());


      //Setting the query object... also populating the the view model
      hc.searchQuery = _.get(query,'q','*');
      // Use an observable to get the contents of a queryResults after it is updated.
      resultsObservable = Orwell.getObservable('queryResults');
      resultsObservable.addObserver(function(data) {
        // updateStatus();
        checkResultsType(data);
        updateStatus();
        // Initializing sorting
        hc.sort = "score";
        var rspSort;
        if (data.responseHeader && data.responseHeader.params && data.responseHeader.params.sort){
          rspSort = data.responseHeader.params.sort;
        }
        getSortFromQuery(query, rspSort);

      });
      perDocumentObservable = Orwell.getObservable('perDocument');
      perDocumentObservable.addObserver(function(data){
        $log.info("HC perD", data);
        if (data.docId){
          hc.perDocument = true;
          hc.showFacets = false;
          hc.showRecommendations = true;
        } else {
          hc.perDocument = false;
          hc.showFacets = true;
          hc.showRecommendations = false;
        }

      });

      // Force set the query object to change one digest cycle later
      // than the digest cycle of the initial load-rendering
      // The $timeout is needed or else the query to fusion is not made.
      $timeout(function(){
        URLService.setQuery(query);
      });
    }

    function signup() {
      $http.post('/signup', hc.user)
        .success(function (data) {
          console.log(data);
          if (data["success"] === true) {
            hc.is_login = true;
            hc.signupError = false;
            hc.msg = data["msg"];
            var snowplow = $window.searchhub_snowplow;
            snowplow('setUserId', hc.user.email);
          } else {
            hc.signupError = true;
            hc.msg = data["msg"];
          }
        })
        .error(function (data) {
          hc.signupError = true;
          hc.msg = "Sign up error!";
        });
    }

    function login() {
      $http.post('/login', hc.user)
        .success(function (data) {
          if (data["success"] === true) {
            hc.is_login = true;
            hc.loginError = false;
            hc.msg = data["msg"]
            var snowplow = $window.searchhub_snowplow;
            snowplow('setUserId', data["email"]);
          } else {
            hc.loginError = true;
            hc.msg = data["msg"];
          }
        })
        .error(function (data) {
          hc.loginError = true;
          hc.msg = "Login error!";
        });
    }

    function getSortFromQuery(query, rspSort){
      //first check to see if sorting is in the response object
      if (rspSort) {
        hc.sort = rspSort.replace(" desc", "").trim();
      } else {
        //check rison
        var tmp = query.sort;
        if (tmp) {
          hc.sort = tmp.replace(" desc", "").trim();
        } else {
          hc.sort = "score";
        }
      }
    }

    function onChangeSort(){
      var query = QueryService.getQueryObject();
      query.sort = hc.sort + " desc";
      QueryService.setQuery(query);
    }

    function checkResultsType(data){
      if (data.hasOwnProperty('response')) {
        hc.numFound = data.response.numFound;
        hc.numFoundFormatted = $filter('humanizeNumberFormat')(hc.numFound, 0);
        hc.lastQuery = data.responseHeader.params.q;
        if(_.has(data, 'facet_counts')){
          return hc.showFacets = !_.isEmpty(data.facet_counts.facet_fields);
        }
        // Make sure you check for all the supported facets before for empty-ness
        // before toggling the `showFacets` flag
      }
      else if(_.has(data, 'grouped')){
        hc.lastQuery = data.responseHeader.params.q;
        var numFoundArray = [];
        _.each(data.grouped, function(group){
          numFoundArray.push(group.matches);
        });
        // For grouping, giving total number of documents found
        hc.numFound = _.sum(numFoundArray);
        hc.numFoundFormatted = $filter('humanizeNumberFormat')(hc.numFound, 0);
        if(_.has(data, 'facet_counts')){
          return hc.showFacets = !_.isEmpty(data.facet_counts.facet_fields);
        }
      }
      else {
        hc.numFound = 0;
      }
    }

    function updateStatus(){
      var status = '';
      //console.log(hc.numFound);
      if(hc.numFound === 0){
        status = 'no-results';
        if(hc.lastQuery === ''){
          status = 'get-started';
        }
      } else {
        status = 'normal';
      }
      hc.status = status;
    }

    /**
     * Initializes a new search.
     */
    function doSearch() {
      query = {
        q: hc.searchQuery,
        start: 0,
        // TODO better solution for turning off fq on a new query
        fq: []
      };
      //$log.info(query);
      URLService.setQuery(query);
    }


    /**
     * Logs a user out of a session.
     */
    function logout(){
      hc.is_login = false;
      AuthService.destroySession();
    }
  }
})();