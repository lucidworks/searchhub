(function () {
  'use strict';

  angular
      .module('searchHub.components.documents', ['lucidworksView.services.config',
        'ngOrwell', 'lucidworksView.services.landingPage'
      ])
      .directive('documents', documents);

  function documents() {
    'ngInject';
    return {
      restrict: 'EA',
      templateUrl: 'assets/components/documents/documents.html',
      controller: Controller,
      controllerAs: 'vm',
      bindToController: {},
      scope: true,
      replace: true
    };

  }


  function Controller($sce, $anchorScroll, Orwell, SnowplowService, IDService, QueryService, $log) {
    'ngInject';
    var vm = this;
    vm.docs = [];
    vm.highlighting = {};
    vm.getDocType = getDocType;
    vm.groupedResults = false;
    vm.toggleGroupedResults = toggleGroupedResults;
    vm.decorateDocument = decorateDocument;
    vm.showGroupedResults = {};

    activate();

    ////////

    function activate() {
      var resultsObservable = Orwell.getObservable('queryResults');
      resultsObservable.addObserver(function (data) {
        //Every time a query is fired and results come back, this section gets called
        var queryObject = QueryService.getQueryObject();
        //let's make sure we can track individual query/result pairs by assigning a UUID to each unique query
        queryObject["uuid"] = IDService.generateUUID();
        //$log.info("Query Obj:");
        //$log.info(queryObject);
        vm.docs = parseDocuments(data);
        vm.highlighting = parseHighlighting(data);
        vm.getDoctype = getDocType;
        //$anchorScroll('topOfMainContent');
      });
    }

    /**
     * Get the document type for the document.
     * @param  {object} doc Document object
     * @return {string}     Type of document
     */
    function getDocType(doc) {
      // Change to your collection datasource type name
      // if(doc['_lw_data_source_s'] === 'MyDatasource-default'){
      //   return doc['_lw_data_source_s'];
      // }
      var ds = doc['_lw_data_source_s'];
      if (ds) {
        //$log.info("DS", ds);
        if (ds.indexOf("lucidworks-docs") != -1 || ds.indexOf("lucidworks-knowledge") != -1) {
          return "lucid-docs";
        }
        var idx = ds.indexOf("-");
        if (idx != -1) {
          return ds.substring(0, idx)
        }
      }
      //if we can't figure out the data source name, then let's use the type
      return doc['_lw_data_source_type_s'];
    }

    /**
     * Decorates the document object before sending to the document directive.
     * @param  {object} doc Document object
     * @return {object}     Document object
     */
    function decorateDocument(doc) {
      return doc;
    }

    function isNotGrouped(data) {
      return _.has(data, 'response');
    }

    function isGrouped(data) {
      return _.has(data, 'grouped');
    }

    /**
     * Get the documents from
     * @param  {object} data The result data.
     * @return {array}       The documents returned
     */
    function parseDocuments(data) {
      var docs = [];
      if (isNotGrouped(data)) {
        docs = data.response.docs;
      }
      else if (isGrouped(data)) {
        vm.groupedResults = data.grouped;
        parseGrouping(vm.groupedResults);
        //TODO: handle signals for grouped results
        //$log.info("docs: "+ docs.length);
      }
      if (docs.length > 0) {
        var facets = null;
        if (data.facet_counts){
          facets = data.facet_counts;
        }
        //we have docs, let's send over a signal of the query and all the doc ids
        var queryObject = QueryService.getQueryObject();
        SnowplowService.postSearchSignal(queryObject,
            data.responseHeader.params.fq,
            data.response.numFound,
            data.response.docs,
            facets
        )
      }
      return docs;
    }


    function toggleGroupedResults(toggle) {
      vm.showGroupedResults[toggle] = !vm.showGroupedResults[toggle];
    }

    function parseGrouping(results) {
      _.each(results, function (item) {
        _.each(item.groups, function (group) {
          if (_.has(group, 'groupValue') && group.groupValue !== null) {
            vm.showGroupedResults[group.groupValue] = false;
          }
          else {
            vm.showGroupedResults['noGroupedValue'] = true;
          }
          ;
        });
      });
    }

    /**
     * Get highlighting from a document.
     * @param  {object} data The result data.
     * @return {object}      The highlighting results.
     */
    function parseHighlighting(data) {
      if (data.hasOwnProperty('highlighting')) {
        _.each(data.highlighting, function (value, key) {
          var vals = {};
          if (value) {
            _.each(Object.keys(value), function (key) {
              //$log.debug('highlight', value);
              var val = value[key];
              _.each(val, function (high) {
                vals[key] = $sce.trustAsHtml(high);
              });
            });
            vm.highlighting[key] = vals;
          }
        });
      }
      else {
        vm.highlighting = {};
      }
      return vm.highlighting;
    }
  }
})();
