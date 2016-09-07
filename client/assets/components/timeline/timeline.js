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


  function Controller($sce, $anchorScroll, Orwell, SnowplowService, IDService, QueryService, $log, $scope, URLService) {
    'ngInject';
    var vm = this;
    var chart_height = 200;

    activate();

    ////////

    function activate() {
      console.log("We are in the activate of the timeline");
      var resultsObservable = Orwell.getObservable('queryResults');
      console.log(resultsObservable);
      // Currently this changes based on the search...is this what we want or not? 
      resultsObservable.addObserver(function (data) {
        console.log("The data is as follows!", data);
        var queryObject = QueryService.getQueryObject();
        
        queryObject["uuid"] = IDService.generateUUID();
      
        // Note we have to make a slice because otherwise javascript will 
        // change the original array and ruin everything! 
        var timeline_data = data.facet_counts.facet_ranges.publishedOnDate.counts.slice()

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

      function populate_timeline(data_info){
        vm.d3options = {
          chart: {
            type: 'historicalBarChart',
            bars: {
              dispatch: {
                elementClick: function(e) {
                  console.log(e);
                  console.log("You Clicked on a Bar! Lets start a search.");
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
