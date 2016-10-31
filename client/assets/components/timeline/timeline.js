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


  function Controller($sce, $anchorScroll, Orwell, SnowplowService, IDService, QueryService, $log, $scope, URLService, QueryDataService, ConfigService) {
    'ngInject';
    var vm = this; 
    var chart_height = 300;
    // var dateToRange = ConfigService.getTimelineDateField();
    var dateToRange = 'publishedOnDate';
    activate();

    ////////

    function activate() {
      var resultsObservable = Orwell.getObservable('queryResults');
      var queryObservable = Orwell.getObservable('query');
      var num_dates;

      resultsObservable.addObserver(function (data) {
        // Try to get the appropriate results, if there is an error log it
        try {
          // Note we have to make a slice because otherwise javascript will 
          // change the original array and ruin everything! 
          $log.debug("populating timeline_data");
          vm.timeline_data = data.facet_counts.facet_ranges[dateToRange].counts.slice();
          num_dates = vm.timeline_data.length;  
        }
        catch (err) {
          if (err.name === "TypeError") {
            $log.error("GRAPH ERROR: There is no " + dateToRange + " facet range field");
          }
          else {
            $log.error("ERROR: Something has gone wrong");
          }
        }

        vm.data_vals = [];
        if (num_dates == undefined) {
          $log.debug("The number of dates was never populated!")
        }
        else if (num_dates == 0) {
          $log.error("SEARCH ERROR: There are no values for field " + dateToRange + " for this particular search");
        }
        else {
          for (var i = 0; i < num_dates; i+=2) {
            var date = new Date(vm.timeline_data[i]);
            date.setDate(date.getDate() + 1);
            var milliseconds = date.getTime();
            vm.timeline_data[i] = milliseconds
            var sub_array = [milliseconds, vm.timeline_data[i + 1]];
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
                  $log.debug("You clicked on a bar! Let's start a search.")
                  var startClickDate = new Date(e.data[0]);
                  var endClickDate = new Date(e.data[0]);

                  startClickDate.setDate(startClickDate.getDate() - 1);
                  
                  var startClickDateIso = startClickDate.toISOString();
                  var endClickDateIso = endClickDate.toISOString();

                  $log.debug("Clicked on bar Start Date is", startClickDateIso);
                  $log.debug("Clicked on bar End Date is", endClickDateIso);

                  // get the appropriate date range 
                  vm.dateStringToAdd = dateToRange + ":[" + startClickDateIso + " TO " + endClickDateIso + "]"; 
                  var queryObject = QueryService.getQueryObject();

                  // If there are no existing filter queries we have to add 
                  // the fq parameter in the click 
                  if (queryObject['fq'] == undefined || queryObject['fq'].length == 0){
                    $log.debug("Adding the FQ parameter in the click");
                    queryObject['fq'] = [];
                    queryObject['fq'].push(vm.dateStringToAdd);
                    vm.barIsClicked = true;
                  }
                  // Otherwise we simply need to add the parameter or remove the parameter 
                  // from the fq depending on whether we have already clicked or not
                  else {
                    if (queryObject['fq'].indexOf(vm.dateStringToAdd) == -1) {
                      $log.debug("Adding the datestring to the FQ parameter in the click");
                      queryObject['fq'].push(vm.dateStringToAdd);
                      vm.barIsClicked = true;
                    }
                    else {
                      $log.debug("Removing the datestring from the FQ parameter in the click");
                      var index = queryObject['fq'].indexOf(vm.dateStringToAdd);
                      queryObject['fq'].splice(index, 1);
                      vm.barIsClicked = false;
                    }
                  }
                  queryObservable.setContent(queryObject);
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
