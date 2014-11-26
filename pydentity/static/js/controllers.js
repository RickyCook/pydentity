var pydentity = angular.module('pydentity', []);

pydentity.controller('ObjectsListController', function ($scope, $http) {
    $scope.load_endpoint = function(endpoint) {
        $scope.endpoint = endpoint
        $http.get('/api/v1/' + endpoint).success(function(data) {
            $scope.loading = false
            $scope.objects = data.objects;
        });
    }
    $scope.orderProp = 'rid'
    $scope.loading = true
})
