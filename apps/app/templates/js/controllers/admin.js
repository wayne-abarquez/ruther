rutherApp.factory('rutherAdminPanelService', ['$rootScope', '$http', function($rootScope, $http) {
    var service = {};
    service.activeView='ViewUserPanel';
    service.ViewUserPanel_EventListeners = {}
    service.broadcastViewUserPanel_Event = function ()
    {
        console.log('Viewing User');
        service.activeView='ViewUserPanel';
        $rootScope.$broadcast('ViewUserPanel_Event',  service.activeView);  

    }

    service.addViewUserPanelEventListener = function (scope, callbackName) {
            // console.log('adding event to',scope.$id);
            var me = this;
            if (!me.ViewUserPanel_EventListeners[scope.$id]) {
                me.ViewUserPanel_EventListeners[scope.$id] = {};  
            }
            me.ViewUserPanel_EventListeners[scope.$id][callbackName] = $rootScope.$on('ViewUserPanel_Event', scope[callbackName]);      
            
            scope.$on("$destroy",function() {
                for (var item in me.ViewUserPanel_EventListeners[scope.$id]) {
                    me.ViewUserPanel_EventListeners[scope.$id][item]();                    
                }
            }); 
            // console.log($rootScope.$$boundaryLeftClick_EventListeners);
    }
    
    service.ViewRolePanel_EventListeners = {}
    service.broadcastViewRolePanel_Event = function ()
    {
        console.log('Viewing role');
        service.activeView='ViewRolePanel';
        $rootScope.$broadcast('ViewRolePanel_Event', service.activeView); 
    }

    service.addViewRolePanelEventListener = function (scope, callbackName) {
            // console.log('adding event to',scope.$id);
            var me = this;
            if (!me.ViewRolePanel_EventListeners[scope.$id]) {
                me.ViewRolePanel_EventListeners[scope.$id] = {};  
            }
            me.ViewRolePanel_EventListeners[scope.$id][callbackName] = $rootScope.$on('ViewRolePanel_Event', scope[callbackName]);      
            
            scope.$on("$destroy",function() {
                for (var item in me.ViewRolePanel_EventListeners[scope.$id]) {
                    me.ViewRolePanel_EventListeners[scope.$id][item]();                    
                }
            }); 
            // console.log($rootScope.$$boundaryLeftClick_EventListeners);
    }
    return service;
    
    service.ViewSyncPanel_EventListeners = {}
    service.broadcastViewSyncPanel_Event = function ()
    {
        console.log('Viewing sync');
        service.activeView='ViewSyncPanel';
        $rootScope.$broadcast('ViewSyncPanel_Event', service.activeView); 
    }

    service.addViewSyncPanelEventListener = function (scope, callbackName) {
            // console.log('adding event to',scope.$id);
            var me = this;
            if (!me.ViewSyncPanel_EventListeners[scope.$id]) {
                me.ViewSyncPanel_EventListeners[scope.$id] = {};  
            }
            me.ViewSyncPanel_EventListeners[scope.$id][callbackName] = $rootScope.$on('ViewSyncPanel_Event', scope[callbackName]);      
            
            scope.$on("$destroy",function() {
                for (var item in me.ViewSyncPanel_EventListeners[scope.$id]) {
                    me.ViewSyncPanel_EventListeners[scope.$id][item]();                    
                }
            }); 
            // console.log($rootScope.$$boundaryLeftClick_EventListeners);
    }
    return service;
}]);


// rutherApp.controller('rutherAdminPanelController', ['$scope', 'rutherAdminPanelService', 'rutherAdminUserService', 'rutherAdminRoleService', 'rutherWebService', function ($scope, rutherAdminPanelService, rutherAdminUserService, rutherAdminRoleService, rutherWebService){	
    
    // $scope.viewRole = function ()
    // {
     // rutherAdminPanelService.broadcastViewRolePanel_Event();
    // };
    
    // $scope.viewUser = function ()
    // {
     // rutherAdminPanelService.broadcastViewUserPanel_Event();
    // };
    
    // $scope.viewUser = function ()
    // {
     // rutherAdminPanelService.broadcastViewUserPanel_Event();
    // };
// }]);
