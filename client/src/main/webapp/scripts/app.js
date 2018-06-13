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
        function ($scope) {
          $scope.changedValue = function (item) {
            // TODO: if item not null then activate button
            $scope.topic = item.id;
          }
          /**
           * Get the document type for the document.
           * @param  {object} doc Document object
           * @return {string}     Type of document
           */
          $scope.getDocType = function (doc) {
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
        });