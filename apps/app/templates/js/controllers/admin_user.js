rutherApp.factory('rutherAdminUserService', ['$rootScope', '$http', function($rootScope, $http) {
    var service = {};

    return service;
}]);

rutherApp.controller('rutherAdminUserController', ['$scope', 'rutherAdminUserService', 'rutherWebService', function ($scope, rutherAdminUserService, rutherWebService){	

    $scope.apply = function()
    {
        if (!$scope.$$phase)
        {
            $scope.$apply();
        }
    }
    $scope.refreshList = function()
    {
        var success_cb = function (errorcode, errrormsg, request_params, data)
        {
           console.log('hi');
            $scope.users = data;

            $scope.apply();
        };
        
        var error_cb = function (errorcode, errrormsg, request_params, data)
        {
           
            console.log('Unable to get roles.');
        };
        
        rutherWebService.getUsers(null, success_cb, error_cb, null);
    }
    
    $scope.refreshList();
}]);


