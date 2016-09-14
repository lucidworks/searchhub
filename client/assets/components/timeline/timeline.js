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
    vm.selectBar = false;
    var chart_height = 300;
    var dateToRange = "date";

    activate();

    ////////

    function activate() {
      console.log("In the activate of the timeline");

      var resultsObservable = Orwell.getObservable('queryResults');
      var timeline_data;
      var num_dates;

      resultsObservable.addObserver(function (data) {
        console.log("The data has changed");
        var queryObject = QueryService.getQueryObject();

        queryObject["uuid"] = IDService.generateUUID();


        try {
          // Note we have to make a slice because otherwise javascript will 
          // change the original array and ruin everything! 
          console.log(data);
          timeline_data = data.facet_counts.facet_ranges[dateToRange].counts.slice();
          num_dates = timeline_data.length;  
        }
        catch (err) {
          if (err.name === "TypeError") {
            $log.error("GRAPH ERROR: There is no " + dateToRange + " facet field");
          }
          else {
            $log.error("ERROR: Something has gone wrong");
          }
        }

        vm.data_vals = [];
        if (num_dates == 0) {
          $log.error("SEARCH ERROR: There are no values for field " + dateToRange + " for this particular search");
        }
        else {
          for (var i = 0; i <= num_dates/2; i+=2) {
            var date = new Date(timeline_data[i]);
            date.setDate(date.getDate() + 1);
            var milliseconds = date.getTime();
            timeline_data[i] = milliseconds
            var sub_array = [milliseconds, timeline_data[i + 1]];
            vm.data_vals.push(sub_array);
          }
        }
        populate_timeline(vm.data_vals);
      });

      function populate_timeline(data_info){
        vm.d3options = {
          chart: {
            type: 'historicalBarChart',
            bars: {
              dispatch: {
                elementClick: function(e) {

                  var startClickDate = new Date(e.data[0]);
                  var endClickDate = new Date(e.data[0]);

                  startClickDate.setDate(startClickDate.getDate() - 1);
                  
                  var startClickDateIso = startClickDate.toISOString();
                  var endClickDateIso = endClickDate.toISOString();

                  $log.debug("Start Date is", startClickDateIso);
                  $log.debug("End Date is", endClickDateIso);
                  $log.debug("You Clicked on a Bar! Lets start a search.");

                  // get the appropriate date range 
                  var dateStringToAdd = dateToRange + ":[" + startClickDateIso + " TO " + endClickDateIso + "]"; 
                  var queryObject = QueryService.getQueryObject();
                  
                  if (queryObject['fq'] == undefined || queryObject['fq'].length == 0){
                    queryObject['fq'] = [];
                    queryObject['fq'].push(dateStringToAdd);
                  }
                  else {
                    if (queryObject['fq'].indexOf(dateStringToAdd) == -1) {
                      queryObject['fq'].push(dateStringToAdd);
                    }
                    else {
                      var index = queryObject['fq'].indexOf(dateStringToAdd);
                      queryObject['fq'].splice(index, 1);
                    }
                  }
                  vm.selectBar = true; 
                  
                  // Set the query and launch the search 
                  URLService.setQuery(queryObject); 
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
