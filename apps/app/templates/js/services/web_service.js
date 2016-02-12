rutherApp.factory('rutherWebService', ['$rootScope', '$http', function($rootScope, $http) {
    var service = {};
    
    service.getFacilityCount = function (boundary_id, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        var get_parameters = service.buildGetParamsString({ 'boundary_filter_type' : 'boundary', 'boundary_filter_value' : boundary_id});
        service.doAjaxGet("getFacilityCount", get_parameters, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    };
    
    service.getChildBoundaryCount = function (boundary_id, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        var get_parameters = service.buildGetParamsString({ 'boundary_filter_type' : 'boundary', 'boundary_filter_value' : boundary_id});
        service.doAjaxGet("getChildBoundaryCount", get_parameters, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    };
    
    service.getKPI = function (query_parameters, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        console.log('doing ajax getkpi');
        var get_parameters = service.buildGetParamsString(query_parameters);
        service.doAjaxGet("getKPI", get_parameters, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    };
    
    service.getKPIMapData = function(query_parameters, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        var get_parameters = service.buildGetParamsString(query_parameters);
        service.doAjaxGet("kpimapdata", get_parameters, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    };
    
    service.getKPITypes = function (beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        service.doAjaxGet("getKPITypes", null, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    }

    service.getBoundaries = function (beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        service.doAjaxGet("Boundaries", null, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    }    
    
    service.getBoundaryLevels = function (beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        service.doAjaxGet("BoundaryLevels", null, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    }
    
    service.getProducts = function (beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        service.doAjaxGet("Products", null, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    }
    
    service.getProductGroups = function (beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        service.doAjaxGet("ProductGroups", null, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    }
    service.getFacilities = function (beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        service.doAjaxGet("Facilities", null, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    }    
    
    service.getFacilityTypes = function (beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        service.doAjaxGet("FacilityTypes", null, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    }    
    
    service.getAvailableBoundaryPermissions = function (beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
         service.doAjaxGet("BoundaryPermissions", null, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    }
    // Roles
    service.getRoles = function (beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        
        service.doAjaxGet("Roles", null, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    }    
      
    // User
    service.getUsers = function (beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        // console.log('hi');
        service.doAjaxGet("Users", null, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    }    
    
    service.doLDAPSync = function (beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        console.log('LDAPSync');
        service.doAjaxGet("LDAPSync", null, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    }    
    
    service.doLDAPSyncConfirm = function (params, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        console.log('LDAPSyncConfirm');
        service.doAjaxPost("LDAPSync", params, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    }    

    service.getRolePermissions = function(role_id, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        service.doAjaxGet("RolePermissions", "role_id=" + role_id, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    }
    service.updateRolePermission = function(params, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        service.doAjaxPost("RolePermissions/", params, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func);
    }
 

    service.doAjaxGet =  function (url, get_parameters, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        var _ = url;
        if (get_parameters != null)
            _ = _ + '/?' + get_parameters;
            
        $.ajax({
            type : "GET",
            cache: "false",
            url : _,
            dataType : "json",
            contentType: "application/json; charset=utf-8",
            beforeSend: function(){
                if (beforesend_callback_func)
                    beforesend_callback_func();
             },
            success: function(data, textStatus, xhr)
            {
                service.checkAuthorizationStatus(data, xhr);
                
                if (success_callback_func)
                    success_callback_func(data['ErrorCode'], data['ErrorMessage'], data['RequestParams'], data['Data']);        
            },
            
            error :function (xhr)
            {
                if (error_callback_func)
                    error_callback_func('C010101', 'Unable to contact server', '','');   
            },
            complete: function(data, textStatus, xhr){
                if (complete_callback_func)
                    complete_callback_func( data['ErrorCode'], data['ErrorMessage'], data['RequestParams'], data['Data']);
            }
        });
    } 
    service.checkAuthorizationStatus = function (data, xhr)
    {
        if (data['ErrorCode'] == 'A010101') // error code for not authorize to get data.
        {
            var redirect_url = data['Data']['redirect_url'];
            window.location.href = redirect_url;
        }
    }
    // instruct web server to do update
    service.doAjaxPost =  function (url, parameters, beforesend_callback_func, success_callback_func, error_callback_func, complete_callback_func)
    {
        // var _ = url;
        // if (get_parameters != null)
            // _ = _ + '/?' + get_parameters;
            
        $.ajax({
            type : "POST",
            cache: "false",
            url : url,
            data : JSON.stringify(parameters),
            
            contentType: "application/json; charset=utf-8",
            beforeSend: function(){
                if (beforesend_callback_func)
                    beforesend_callback_func();
             },
            success: function(data, textStatus, xhr) 
            {
                service.checkAuthorizationStatus(data, xhr);
                
                if (success_callback_func)
                    success_callback_func(data['ErrorCode'], data['ErrorMessage'], data['RequestParams'], data['Data']);        
            },
            error :function (data) 
            {
                if (error_callback_func)
                    error_callback_func('C010102', 'Unable to contact server', '','');   
            },
            complete: function(data){
                if (complete_callback_func)
                    complete_callback_func( data['ErrorCode'], data['ErrorMessage'], data['RequestParams'], data['Data']);
            }
        });
    }
    
    service.buildGetParamsString = function (params)
    {
    
        var boundary_filter_type = params.boundary_filter_type;
        var boundary_filter_value = params.boundary_filter_value;
        var product_filter_type = params.product_filter_type;
        var product_filter_value = params.product_filter_value;
        var timeframe_filter_type = params.timeframe_filter_type;
        var timeframe_filter_value = params.timeframe_filter_value;
        var kpi_type = params.kpi_type;
        
        var parameters = '';
        
        // var post_data = {'boundary' :  getSelectedBoundary() };
        var _tmpstr =  '';
        if (boundary_filter_type)
        {
            if (boundary_filter_type == 'boundary' || boundary_filter_type == 'facility')
            {
                for (var i=0;i<boundary_filter_value.length;i++)
                {
                    if ( _tmpstr )
                    {
                        _tmpstr += ',' + boundary_filter_value[i];
                    }
                    else
                        _tmpstr += boundary_filter_value[i];
                }
            }
            else
                _tmpstr = boundary_filter_value;

            parameters += 'boundary_filter_type=' + boundary_filter_type;
            parameters += '&boundary_filter_id=' + _tmpstr;
        }
        if ( product_filter_type )
        {
            _tmpstr =  '';      
            if (product_filter_type == 'product')
            {
                for (var i = 0; i< product_filter_value.length; i++)
                {
                    if (_tmpstr)
                        _tmpstr += ',' + product_filter_value[i];
                    else
                         _tmpstr +=  product_filter_value[i];
                }
            }
            else
                _tmpstr = product_filter_value;
            parameters += '&product_filter_type=' + product_filter_type;
            parameters += '&product_filter_id=' + _tmpstr;
        }
        
        if ( timeframe_filter_type )
        {
            parameters += '&timeframe=' + timeframe_filter_type;
            
            if ( timeframe_filter_type == 'week')
            {
                parameters += '&date_year=' + timeframe_filter_value['date_year'] + '&date_month=' +  timeframe_filter_value['date_month']  + '&date_day=' + timeframe_filter_value['date_day'];
            }
            if ( timeframe_filter_type == 'year')
            {
                parameters += '&date_year=' +  timeframe_filter_value['date_year'];
            }
            if ( timeframe_filter_type == 'month')
            {
                parameters += '&date_month=' +  timeframe_filter_value['date_month']  + '&date_year=' + timeframe_filter_value['date_year'];
            }
            if ( timeframe_filter_type == 'day')
            {

                parameters += '&date=' + timeframe_filter_value['date_year'] + '-' +  timeframe_filter_value['date_month'] + '-' + timeframe_filter_value['date_day'];
            }
        }
        if ( kpi_type )
        {
            parameters += '&kpi_type=' + kpi_type;
        }

        return parameters;
    }

    return service;

}]);
