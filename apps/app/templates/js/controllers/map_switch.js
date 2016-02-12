rutherApp.controller('MapSwitchControl', ['$scope', 'googleEarthService', function ($scope, googleEarthService){	
    $scope.changeToGoogleEarth = function()
    {
        googleEarthService.switchToGoogleEarth();
    };
    
    $scope.changeToGoogleRoadmap = function ()
    {
        googleEarthService.switchToGoogleMap(google.maps.MapTypeId.ROADMAP);
    };
    
    $scope.changeToGoogleSatelliteMap = function ()
    {
        googleEarthService.switchToGoogleMap(google.maps.MapTypeId.SATELLITE);
    };
    
}]);