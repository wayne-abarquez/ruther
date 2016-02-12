rutherApp.controller('rutherAdminSyncController', ['$scope', 'rutherWebService', function ($scope, rutherWebService){	

    $scope.apply = function()
    {
        if (!$scope.$$phase)
            $scope.$apply();
        
    };
    
    $scope.displayMessage = function(msg)
    {
        $scope.message = msg;
        $scope.apply();
    };
    
    $scope.resetMessageDisplay = function ()
    {
        $scope.fails = false;  $scope.success = false; $scope.wait = false; $scope.apply();
    }
    
    $scope.displaySuccessMessage = function (msg)
    {
        $scope.resetMessageDisplay();
        $scope.success = true; $scope.success_message = msg; $scope.apply();
    }
    
    $scope.displayFailMessage = function (msg)
    {
        $scope.resetMessageDisplay();
        $scope.fails = true; $scope.fails_message = msg; $scope.apply();
    }
    
    $scope.displayWaitMessage = function ()
    {
        $scope.resetMessageDisplay();
        $scope.wait = true; $scope.apply();
    }
    
    $scope.LDAP = function () 
    {

        var success_cb = function (errorcode, errrormsg, request_params, data)
        {   
            
            if (data.need_sync)
            {
                
                $scope.new_roles = data.new_roles;
                $scope.defunct_roles = data.defunct_roles;
                $scope.new_users = data.new_users;
                $scope.defunct_users = data.defunct_users;
                $scope.changed = data.changed;
                $scope.need_sync = data.need_sync;
                
                $scope.data = data;
                $scope.displaySuccessMessage ('Changes detected');
            }
            
            else
            {
                $scope.displaySuccessMessage ('No changes detected');
            }
            
        };
    
        var error_cb = function (errorcode, errrormsg, request_params, data)
        {
            $scope.please_wait = false;
            $scope.confirmed = true;
            $scope.error = true;
            console.log('Unable to get roles.');
        };

        $scope.new_roles = null;
        $scope.defunct_roles = null;
        $scope.new_users = null;
        $scope.defunct_users = null;
        $scope.changed = null;
        $scope.need_sync = null;
        
        $scope.displayWaitMessage();
        
        $scope.data = null;
        rutherWebService.doLDAPSync(null, success_cb, error_cb, null);
    };

    $scope.LDAPConfirm = function () 
    {
        //$scope.displayMessage('Syncing...');
        var success_cb = function (errorcode, errrormsg, request_params, data)
        {        


            if (errorcode == 'OK')
            {
                
                $scope.new_roles = data.new_roles;
                $scope.defunct_roles = data.defunct_roles;
                $scope.new_users = data.new_users;
                $scope.defunct_users = data.defunct_users;
                $scope.changed = data.changed;
                $scope.displaySuccessMessage ('Changes saved');
            }
            else
            {
                $scope.displayFailMessage('Failed saving');

            }
        };
    
        var error_cb = function (errorcode, errrormsg, request_params, data)
        {
            $scope.displayFailMessage('Failed saving');
        };

        params = $scope.data;
        $scope.need_sync = false;
        $scope.displayWaitMessage();
        rutherWebService.doLDAPSyncConfirm(params, null, success_cb, error_cb, null);
    };
}])