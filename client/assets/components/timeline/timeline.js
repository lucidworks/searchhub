(function () {
  'use strict';

  angular
      .module('searchHub.components.timeline', ['lucidworksView.services.config',
        'ngOrwell',
      ])
      .directive('timeline', timeline);

    function timeline() {
    'ngInject';
      var directive = {
        restrict: 'EA',
        templateUrl: 'assets/components/timeline/timeline.html',
        scope: true,
        controller: Controller,
        controllerAs: 'vm',
        bindToController: {}
      };
      return directive;
    };


  function Controller($sce, $anchorScroll, Orwell, SnowplowService, IDService, QueryService, $log, $scope, URLService, QueryDataService) {
    'ngInject';
    var vm = this;
    var chart_height = 200;
    var dateToRange = "date";

    activate();

    ////////

    function activate() {
      console.log("We are in the activate of the timeline");
      var resultsObservable = Orwell.getObservable('queryResults');
      console.log(resultsObservable);
      // Currently this changes based on the search...is this what we want or not? 
      resultsObservable.addObserver(function (data) {
        console.log("The data is as follows!", data);
        console.log("The timeline data lives in ", data.facet_counts.facet_ranges[dateToRange].counts);
        var queryObject = QueryService.getQueryObject();
        
        queryObject["uuid"] = IDService.generateUUID();
      
        // Note we have to make a slice because otherwise javascript will 
        // change the original array and ruin everything! 
        var timeline_data = data.facet_counts.facet_ranges[dateToRange].counts.slice();
        var num_dates = timeline_data.length;

        vm.data_vals = [];

        for (var i = 0; i <= num_dates/2; i+=2) {
          var date = new Date(timeline_data[i]);
          // console.log(date);
          var milliseconds = date.getTime();
          timeline_data[i] = milliseconds
          var sub_array = [milliseconds, timeline_data[i + 1]];
          vm.data_vals.push(sub_array);
        }
        populate_timeline(vm.data_vals);
      });

      function addQueryFacet(query, key, title){
        if(!query.hasOwnProperty('fq')){
          query.fq = [];
        }
        var keyObj = {
          key: key,
          values: [title],
          transformer: 'fq:field',
          tag: vm.facetTag
        };
        if(keyObj.tag){
          //Set these properties if the facet has localParams
          //concat the localParams with the key of the facet
          keyObj.key = '{!tag=' + keyObj.tag + '}' + key;
          keyObj.transformer = 'localParams';
          var existingMultiSelectFQ = checkIfMultiSelectFQExists(query.fq, keyObj.key);
          if(existingMultiSelectFQ){
            //If the facet exists, the new filter values are pushed into the same facet. A new facet object is not added into the query.
            existingMultiSelectFQ.values.push(title);
            return query;
          }
        }
        query.fq.push(keyObj);
        $log.debug('final query', query);
        return query;
      }


      function toggleFacet(facet){
        var key = dateToRange;
        var query = QueryService.getQueryObject();
        console.log(key);
        console.log(query);

        // CASE: fq doesnt exist.
        if(!query.hasOwnProperty('fq')){
          query = addQueryFacet(query, key, facet.title);
        }
        updateFacetQuery(query);
      }

      function updateFacetQuery(query) {
        query.start = 0;
        URLService.setQuery(query);
      }

      function populate_timeline(data_info){
        vm.d3options = {
          chart: {
            type: 'historicalBarChart',
            bars: {
              dispatch: {
                elementClick: function(e) {
                  console.log("Lets get the date in a parsable format");
                  var startClickDate = new Date(e.data[0]);
                  
                  var endClickDate = new Date();
                  endClickDate.setDate(startClickDate.getDate() + 1);
                  
                  var startClickDateIso = startClickDate.toISOString();
                  var endClickDateIso = endClickDate.toISOString();

                  console.log("Start Date is", startClickDateIso);
                  console.log("End Date is", endClickDateIso);
                  console.log("You Clicked on a Bar! Lets start a search.");

                  QueryDataService.getQueryResults({q: "date:[" + startClickDateIso + " TO " + endClickDateIso + "]", wt:'json'});
                  //toggleFacet(dateToRange);
                }
              }
            },
            height: chart_height,
            margin: {
              top:0.04*chart_height,
              right:0.20*chart_height,
              bottom:0.20*chart_height,
              left:0.20*chart_height
            },
            x: function(d) {return d[0];},
            y: function(d) {return d[1];},
            showValues: true,
            duration: 100,
            xAxis: {
              axisLabel: 'Date',
              tickFormat: function(d) {
                return d3.time.format('%x')(new Date(d))
              },
              rotateLabels:30,
              showMaxMin: true,
            },
            yAxis: {
              axisLabel: "Event Count",
              axisLabelDistance: -10,
              tickFormat: function(d) {
                return d3.format('.1f')(d);
              }
            },
            tooltip: {
              keyFormatter: function(d) {
                  return d3.time.format('%x')(new Date(d));
              }
            },
            zoom: {
              enabled: true,
              scaleExtent: [1,10],
              usefixedDomain:false, 
              useNiceScale: false,
              horizontalOff: false,
              verticalOff: true,
              unzoomEventType: 'dblclick.zoom'
            },
          }
        };
        vm.d3data = [
          {
            "key" : "Quantity",
            "bar" : true, 
            "values" : data_info
          }
        ];
      }
    }
  }
})();
