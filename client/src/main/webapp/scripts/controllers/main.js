'use strict';

/**
 * @ngdoc function
 * @name appkitApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the appkitApp
 */
angular.module('appkitApp')

    .controller('MainCtrl', ['$rootScope', '$scope', '$stateParams', 'ResponseService', '$location', 'ModalService', '$twigkit', '$timeout', function ($rootScope, $scope, $stateParams, ResponseService, $location, ModalService, $twigkit, $timeout) {
        $scope.params = $stateParams;
        $scope.urlparams = $location.search();
        $rootScope.redirectTo = function (page) {
            $location.path(page);
        };

        $scope.closeModal = function (name) {
            ModalService.close(name);
        };


    }]);

angular.module('appkitApp')
    .filter('encodeURIComponent', function () {
        return window.encodeURIComponent;
    })

    .filter('landingPageLabel', function () {
        return function (input) {
            return input.split('|')[0];
        }
    })

    .filter('landingPageLink', function () {
        return function (input) {
            return input.split('|')[1];
        }
    });

