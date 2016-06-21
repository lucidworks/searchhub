(function() {
  'use strict';
  angular
    .module('searchHub.controllers.document', ['searchHub.services', 'lucidworksView.services', 'angucomplete-alt', 'angular-humanize'])
    .controller('DocumentController', DocumentController);


  function DocumentController($filter, $timeout, ConfigService, QueryService, URLService, Orwell, AuthService, $location, _, $log) {

    'ngInject';
    var dc = this; //eslint-disable-line

    activate();

    ////////////////

    /**
     * Initializes a search from the URL object
     */
    function activate() {
      dc.doc_id = $location.search()["doc_id"];
      $log.info(dc.doc_id);
    }

  }
})();
