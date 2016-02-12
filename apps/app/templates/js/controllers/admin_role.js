

rutherApp.factory('rutherPermissionService', ['$rootScope', 'rutherWebService', function($rootScope, rutherWebService) {
    var service = {};
    service.boundaryPermissionSelected = null;
    service.productPermissionSelected = null;
    service.pagePermissionSelected = null;
    service.role_id = null;
    service.selectedBoundaryPermissionChanged = function (data)
    {
        service.boundaryPermissionSelected = data;
    }
    
    service.selectedProductPermissionChange = function (data)
    {
        service.productPermissionSelected = data;
    }
    
    service.selectedPagePermissionChange = function (data)
    {
        console.log(data);
        service.pagePermissionSelected = data;
    }

    return service;
}]);

rutherApp.controller('rutherAdminRoleController', ['$scope', 'rutherWebService', 'rutherPermissionService', function ($scope, rutherWebService, rutherPermissionService) {	

    $scope.selected_options = {
        'boundaries': [],
        'products': [],
        'timeframe': [],
        'pages' : [],
    };
    $scope.apply = function()
    {
        if (!$scope.$$phase)
        {
            $scope.$apply();
        }
    }


    $scope.editPermission = function (role_id, role_name)
    {
        modal = {};
        modal.role_id = role_id;
        modal.role_name = role_name;
        $scope.modal = modal;

        // $scope.permission_html = "<boundary-permission role-id='modal.role_id' boundaries-selected='selected_options.boundaries'></boundary-permission>";
        // rutherPermissionService.broadcastBoundaryPermissionsModalPopUp_Event(role_id);
        rutherPermissionService.role_id = role_id;
        $scope.resetMessageDisplay();
        $scope.boundary_permission_html = '';
        $scope.product_permission_html = '';
        $scope.pages_permission_html  = '';
        var params = {};
        params.role_id = role_id;

        var success_cb = function (errorcode, errormsg, req_params, data)
        {  
            $scope.edit_permission_boundary_data = data['boundary'];
            $scope.product_permissions_hierarchy = data['products'];
            $scope.page_permissions_hierarchy = data['pages'];

            $scope.boundary_permission_html = "<div id='collapse_boundaries' class='collapsible_hierarchy'><boundary-permission data='edit_permission_boundary_data' boundaries-selected='selected_options.boundaries'></boundary-permission></div>";       
            $scope.product_permission_html = "<div id='collapse_products' class='collapsible_hierarchy'><products-permission data='product_permissions_hierarchy' products-selected='selected_options.products'></products-permission></div>";
            $scope.pages_permission_html = "<div id='collapse_pages' class='collapsible_hierarchy'><page-permission data='page_permissions_hierarchy' pages-selected='selected_options.pages'></page-permission></div>";

            $scope.apply();
        }
        
        var error_cb = function  (errorcode, errormsg, req_params, data)
        {
            console.log('error');
        }
        
        rutherWebService.getRolePermissions(role_id, null, success_cb, error_cb, null);               
    }
    
    $scope.closeModal = function ()
    {
        $scope.permission_html = '';
         $scope.resetMessageDisplay();
    }
    
    $scope.savePermissions = function ()
    {
        
        var success_cb = function (errorcode, errormsg, req_params, data)
        {
            $scope.state = '';
            $scope.displaySuccessMessage('Permission changes saved successfully');   
            $scope.apply();
        };
                
        var error_cb = function (errorcode, errormsg, req_params, data)
        {
            $scope.displayFailMessage('Unable to save permissions changes. ErrorCode: ' + errorcode );
            console.log('Failed saving permission changes. ErrorCode: ' + errorcode + ', ErrorMsg: ' + errormsg);
        }
                
        var permissions = {};
        permissions.boundary_permissions = rutherPermissionService.boundaryPermissionSelected;
        permissions.product_permissions = rutherPermissionService.productPermissionSelected;
        permissions.page_permissions = rutherPermissionService.pagePermissionSelected;
        permissions.role_id = rutherPermissionService.role_id;
        $scope.state = 'saving';
        $scope.displayWaitMessage();
        rutherWebService.updateRolePermission(permissions, null, success_cb, error_cb, null);
    }
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
    
    $scope.refreshList = function ()
    {
        var success_cb = function (errorcode, errrormsg, request_params, data)
        {
        
            $scope.roles = data;
            $scope.apply();
        };
        
        var error_cb = function (errorcode, errrormsg, request_params, data)
        {
           
            console.log('Unable to get roles.');
        };
        
        rutherWebService.getRoles(null, success_cb, error_cb, null);
    };
    $scope.refreshList()
    


}]);


rutherApp.directive('boundariesMember', ['$compile', function($compile){
    return {
        restrict: 'E',
        replace: true,
        require: ['^boundaryPermission', '^boundariesCollection'],
        scope: {
            member: '=',
        },
        templateUrl: 'boundaries_member.html',
        link: function(scope, element, attrs, ctrls){
            scope.isvisible = false;

            if (angular.isArray(scope.member.children)){
                element.append("<boundaries-collection collection='member.children' isvisible='isvisible' ng-show='isvisible'></boundaries-collection>");
                $compile(element.find('boundaries-collection'))(scope);
            }

            scope.checkboxClicked = function(member){
                ctrls[1].checkbox_clicked();
            }

            scope.badgeClicked = function(){
                scope.isvisible = !scope.isvisible;
                if (scope.isvisible){
                    element.find('label:first').find('.icon-caret-down').addClass('icon-caret-up').removeClass('icon-caret-down');
                    element.find('label:first').find('.badge').addClass('badge-warning').removeClass('badge-info');
                } else {
                    element.find('label:first').find('.icon-caret-up').addClass('icon-caret-down').removeClass('icon-caret-up');
                    element.find('label:first').find('.badge').addClass('badge-info').removeClass('badge-warning');
                }

            }
        }
    }
}]);

rutherApp.directive('boundariesCollection', [function(){
    return {
        restrict: 'E',
        replace: true,
        require: ['^boundaryPermission'],
        scope: {
            collection: "=",
            isvisible: "=",
        },
        templateUrl: 'boundaries_collection.html',
        controller: function($scope){
            this.checkbox_clicked = function ()
            {
                $scope.call_recursiveCheckLogic();
            }
            
        },
        link: function(scope, element, attrs, ctrls){
            scope.call_recursiveCheckLogic = function(){
                ctrls[0].recursiveCheckLogicWrapper();
            }

            scope.$watch('collection', function(newVal, oldVal){
                if (scope.collection && scope.collection.length > 0){
                    if (scope.collection[0].level % 2){
                        element.addClass('bg-blue');
                    } else {
                        element.addClass('bg-white');
                    }
                }
            });
        }
    }
}]);

rutherApp.directive('boundaryPermission', ['rutherPermissionService', function(rutherPermissionService){
    return {
        restrict: 'E',
        replace: true,
        scope: {
            boundariesSelected: "=",
            data: "="
        },
        templateUrl: 'boundaries_filter2.html',
        controller: function($scope){
            
            this.recursiveCheckLogicWrapper = function(){
               $scope.checkSelectedBoundaryPermissions();
            };
            
        },
        link: function(scope, element, attrs, controller){
            //scope.boundariesSelected = [];
            /* Load the boundary data */
            scope.apply = function()
            {
                 if (!scope.$$phase)
                {
                    scope.$apply();
                }
            }

            
            scope.populateFilterBoundaries = function(role_id){
                data = scope.data;  
                scope.boundaries = data['boundaries'];                   
                scope.top_lvl_desc = data['top_lvl_desc'];
                scope.facilities_lvl = data['facilities_lvl'];
                scope.top_lvl_all_select = data['top_lvl_permission']
                window.x = scope.boundaries;
                scope.checkSelectedBoundaryPermissions();

            }

            scope.resetPermissions = function ()
            {
                scope._recursiveResetPermissions(scope.boundaries);
                scope.top_lvl_all_select = false;
                scope.checkSelectedBoundaryPermissions();
            };
            
            scope._recursiveResetPermissions = function (x)
            {
                for (var i in x){
                    if (angular.isArray(x[i].children)){
                        scope._recursiveResetPermissions(x[i].children);
                        }
                    x[i].permission = false;
                }

            }
            // scope.populateFilterBoundaries();   // We populate the data
            /* End load */

            scope.isvisible = true;

            scope.recursiveCheckLogic = function(x){
               var selected_boundaries = [];
               var needs_push = false;
               var current_boundary = {};
                for (var i in x){
                    needs_push = false;
                    current_boundary = {'id' : x[i].id, 'name' : x[i].name, 'level' : x[i].level, 'permission' : false };
                    if (angular.isArray(x[i].children)){
                        var selected_children_boundary = scope.recursiveCheckLogic(x[i].children);
                        if (selected_children_boundary.length)
                        {
                            current_boundary.children = selected_children_boundary;
                            needs_push = true;
                        }

                    }

                    if (x[i].permission){
                        current_boundary.permission = x[i].permission;
                        needs_push = true;
                    }
                    
                    if (needs_push)
                        selected_boundaries.push(current_boundary);
                }
                
                return selected_boundaries;
            }

            
            scope.checkSelectedBoundaryPermissions = function ()
            {
                scope.boundariesSelected = {};
                
                scope.boundariesSelected.top_lvl_desc = scope.top_lvl_desc;
                scope.boundariesSelected.facilities_lvl = scope.facilities_lvl;
                
                var selected_boundaries = scope.recursiveCheckLogic(scope.boundaries);
                scope.boundariesSelected.boundaries = selected_boundaries;
                scope.boundariesSelected.top_lvl_permission = false;
                if ( scope.top_lvl_all_select )
                     scope.boundariesSelected.top_lvl_permission =  scope.top_lvl_all_select;
                
                scope.mapToPermissionService();
                
            };
            
            scope.top_lvl_click = function(){
                scope.checkSelectedBoundaryPermissions();
            }

            scope.mapToPermissionService = function(){
                rutherPermissionService.selectedBoundaryPermissionChanged(scope.boundariesSelected);
            }
            
            scope.populateFilterBoundaries();
        }
    }
}]);

rutherApp.directive('productsMember', ['$compile', function($compile){
    return {
        restrict: 'E',
        replace: true,
        require: ['^productsPermission', '^productsCollection'],
        scope: {
            member: '=',
        },
        templateUrl: 'products_member.html',
        link: function(scope, element, attrs, ctrls){
            scope.isvisible = false;

            if (angular.isArray(scope.member.children)){
                element.append("<products-collection collection='member.children' isvisible='isvisible' ng-show='isvisible'></boundaries-collection>");
                $compile(element.find('products-collection'))(scope);
            }

            scope.checkboxClicked = function(member){
               ctrls[1].checkbox_clicked();
            }

            scope.badgeClicked = function(){
                scope.isvisible = !scope.isvisible;
                if (scope.isvisible){
                    element.find('label:first').find('.icon-caret-down').addClass('icon-caret-up').removeClass('icon-caret-down');
                    element.find('label:first').find('.badge').addClass('badge-warning').removeClass('badge-info');
                } else {
                    element.find('label:first').find('.icon-caret-up').addClass('icon-caret-down').removeClass('icon-caret-up');
                    element.find('label:first').find('.badge').addClass('badge-info').removeClass('badge-warning');
                }
            }
        }
    }
}]);

rutherApp.directive('productsCollection', [function(){
    return {
        restrict: 'E',
        replace: true,
        require: ['^productsPermission'],
        scope: {
            collection: "=",
            isvisible: "=",
        },
        templateUrl: 'products_collection.html',
        controller: function($scope){
            this.checkbox_clicked = function ()
            {
                $scope.call_recursiveCheckLogic();
            }
        },
        link: function(scope, element, attrs, ctrls){
            scope.call_recursiveCheckLogic = function(){
                ctrls[0].recursiveCheckLogicWrapper();
            }

            scope.$watch('collection', function(newVal, oldVal){
                if (scope.collection && scope.collection.length > 0){
                    if (scope.collection[0].level % 2){
                        element.addClass('bg-blue');
                    } else {
                        element.addClass('bg-white');
                    }
                }
            });
        }
    }
}]);

rutherApp.directive('productsPermission', ['rutherPermissionService', function(rutherPermissionService){
    return {
        restrict: 'E',
        replace : true,
        scope: {
            productsSelected: "=",
            data: "=",
        },
        templateUrl: 'products_filter2.html',
        controller: function($scope){
            this.recursiveCheckLogicWrapper = function(){

                // $scope.productsSelected = [];

                // $scope.recursiveCheckLogic($scope.products);
                $scope.checkSelectedPermissions($scope.products);
                // $scope.mapToFilterService();
            }
        },
        link : function (scope, element, attrs, controller){
            /* Load the boundary data */
            scope.populate = function(){
                scope.products = scope.data;
                scope.checkSelectedPermissions();
            }


            /* End load */

            scope.resetPermissions = function ()
            {
                scope._recursiveResetPermissions(scope.products);
                scope.top_lvl_all_select = false;
                scope.checkSelectedPermissions();
            };
            
            scope._recursiveResetPermissions = function (x)
            {
                for (var i in x){
                    if (angular.isArray(x[i].children)){
                        scope._recursiveResetPermissions(x[i].children);
                        }
                    x[i].permission = false;
                }
            }

            scope.isvisible = true;

            scope.recursiveCheckLogic = function(x){
               var selected = [];
               var needs_push = false;
               var current = {};
                for (var i in x){
                    needs_push = false;
                    current = {'id' : x[i].id, 'name' : x[i].name, 'level' : x[i].level, 'permission' : false };
                    if(x[i].isLowest)
                        current.isLowest = x[i].isLowest

                    if (angular.isArray(x[i].children)){
                        var selected_children = scope.recursiveCheckLogic(x[i].children);
                        if (selected_children.length)
                        {
                            current.children = selected_children;
                            needs_push = true;
                        }
                    }

                    if (x[i].permission){
                        current.permission = x[i].permission;
                        needs_push = true;
                    }
                    
                    if (needs_push)
                        selected.push(current);
                }
                
                return selected;
            }
            
            scope.checkSelectedPermissions = function ()
            {
                scope.productsSelected = [];
                
                var selected = scope.recursiveCheckLogic(scope.products);
                scope.productsSelected = selected;
                
                scope.mapToPermissionService();
                
            };


            scope.mapToPermissionService = function(){

                rutherPermissionService.selectedProductPermissionChange(scope.productsSelected);
            }
            
            scope.populate();   // We populate the data
        }
    };
}]);

rutherApp.directive('pagePermission', ['rutherPermissionService', function(rutherPermissionService){
    return {
        restrict: 'E',
        replace : true,
        scope: {
            pagesSelected: "=",
            data: "=",
        },
        templateUrl: 'page_permission.html',
        link : function (scope, element, attrs, controller){
            /* Load the boundary data */
            scope.populate = function(){
                scope.pages = scope.data;
                scope.checkSelectedPermissions();
            }

            /* End load */

            scope.resetPermissions = function ()
            {
                scope._recursiveResetPermissions(scope.pages);
                // scope.top_lvl_all_select = false;
                scope.checkSelectedPermissions();
            };
            
            scope._recursiveResetPermissions = function (x)
            {
                for (var i in x){
                    if (angular.isArray(x[i].children)){
                        scope._recursiveResetPermissions(x[i].children);
                        }
                    x[i].permission = false;
                }
            }

            scope.isvisible = true;

            scope.recursiveCheckLogic = function(x){
               var selected = [];
               var needs_push = false;
               var current = {};
                for (var i in x){
                    needs_push = false;
                    current = {'id' : x[i].id, 'name' : x[i].name, 'permission' : false };
                    if(x[i].isLowest)
                        current.isLowest = x[i].isLowest

                    if (angular.isArray(x[i].children)){
                        var selected_children = scope.recursiveCheckLogic(x[i].children);
                        if (selected_children.length)
                        {
                            current.children = selected_children;
                            needs_push = true;
                        }
                    }

                    if (x[i].permission){
                        current.permission = x[i].permission;
                        needs_push = true;
                    }
                    
                    if (needs_push)
                        selected.push(current);
                }
                
                return selected;
            }
            
            scope.checkSelectedPermissions = function ()
            {
                scope.productsSelected = [];
                
                var selected = scope.recursiveCheckLogic(scope.pages);
                scope.pagesSelected = selected;
                
                scope.mapToPermissionService();
                
            };

            scope.checkboxClicked = function(member){
                scope.checkSelectedPermissions();
            };
            
            scope.mapToPermissionService = function(){

                rutherPermissionService.selectedPagePermissionChange(scope.pagesSelected);
            };
            
            scope.populate();   // We populate the data
        }
    };
}]);

rutherApp.directive('permissionhtml', ['$compile', function ($compile )
{ return {
    restrict: 'A',
    replace: true,
    link: function(scope, element, attrs ){
       scope.$watch (   
       function (scope) { return scope.$eval(attrs.permissionhtml); }, 
       function ( value ) { element.html ( value );  $compile(element.contents())(scope); } );
    }
}}]);
