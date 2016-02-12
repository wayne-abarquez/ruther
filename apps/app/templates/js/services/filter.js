rutherApp.factory('filterService', ['$rootScope', '$http', function($rootScope, $http){
    var service = {};
    
    service.boundary_level_view = '';
    service.boundary_id_view = '';
    
    service.current_view_data = '';
    service.current_view_boundary_type = '';
    service.setCurrentViewData = function(boundary_type, data){
        service.current_view_boundary_type = boundary_type;
        service.current_view_data = data;
    }
    
    service.getCurrentViewBoundaryType = function(){
        if (service.current_view_boundary_type == 'boundary') return 'boundary';
        if (service.current_view_boundary_type == 'facility') return 'facility';

        return 'boundary';
    }

    // These data structure indicates the possible filter selections.
    service.productGroups = {};
    service.products = {};  
    service.boundaryLevels = {};
    service.boundaries = {};
    service.lowestLevelBoundary = -1;
    service.facilities = {};
    service.facility_types = {};
    service.getFacilityName = function(id){return service.facilities[id];};
    service.getBoundaryName = function(id){return service.boundaries[id];};
    service.getFacilityTypeName = function(id){return service.facility_types[id];};
    
    service.setBoundaries = function(boundaries){service.boundaries = boundaries;};
    service.setBoundaryLevels = function(boundary_levels){service.boundaryLevels = boundary_levels;};
    service.setFacilityBoundaryLevel = function(lvl){service.lowestLevelBoundary = lvl;};
    service.setProducts = function(products){service.products = products;};
    service.setProductGroups = function(product_groups){service.productGroups = product_groups;};
    service.setFacilities = function(facilities){service.facilities = facilities;};
    service.setFacilityTypes = function(facility_types){service.facility_types = facility_types;};
    
    service.init = function(rutherWebService){
        rutherWebService.getBoundaries(
            null,
            function(errorcode, errrormsg, request_params, data){
                service.setBoundaries(data);
            },
            function(errorcode, errrormsg, request_params, data){
                console.log("Unable to get boundary levels for filter service");
            },
            null
        )
        
        rutherWebService.getBoundaryLevels(
            null, 
            function(errorcode, errrormsg, request_params, data){
                service.setBoundaryLevels(data); 
                service.setFacilityBoundaryLevel(data['lowestBoundaryLevel']);
            },
            function(errorcode, errrormsg, request_params, data){
                console.log("Unable to get boundary levels for filter service");
            },
            null
        );
        
        rutherWebService.getProducts(
            null, 
            function (errorcode, errrormsg, request_params, data){
                service.setProducts(data);
            },
            function (errorcode, errrormsg, request_params, data){
                console.log("Unable to get products  for filter service");
            },
            null
        );
        
        rutherWebService.getProductGroups(
            null, 
            function (errorcode, errrormsg, request_params, data){
                service.setProductGroups(data);
            },
            function (errorcode, errrormsg, request_params, data){
                console.log("Unable to get product groups for filter service");
            },
            null
        );
        
  
        rutherWebService.getFacilities(
            null, 
            function (errorcode, errrormsg, request_params, data){
                service.setFacilities(data);
            },
            function (errorcode, errrormsg, request_params, data){
                console.log("Unable to get facilties for filter service");
            },
            null
        );
        
        rutherWebService.getFacilityTypes(
            null, 
            function (errorcode, errrormsg, request_params, data){
                service.setFacilityTypes(data);
            },
            function (errorcode, errrormsg, request_params, data){
                console.log("Unable to get facilty types for filter service");
            },
            null
        );
    }
    
    // Current filters represents the currently active filter ( after user hits OK button)
    service.active_boundary_filters = null;
    service.active_product_filters = null;
    service.active_timeframe_filters = '';
    
    service.active_kpi_type_filter = '';
    
    service.setActiveFilters = function(boundary, products, timeframe){
        service.active_boundary_filters = boundary;
        service.active_product_filters = products;
        service.active_timeframe_filters = timeframe;
    };
    
    service.setActiveKPITypeFilter = function(kpi_type){
        service.active_kpi_type_filter = kpi_type;
    }
    
    service.getActiveKPITypeFilter = function(){
        return service.active_kpi_type_filter;
    }
    
    service.getActiveBoundaryFilterType = function(){
        if (service.active_boundary_filters['boundary_scope_ids'].length > 0){
            if (service.active_boundary_filters['boundary_level'] == service.lowestLevelBoundary) return 'facility';
            else return 'boundary';
        } else {
            if (service.active_boundary_filters['boundary_level'] == service.lowestLevelBoundary) return 'facility_level';
            else return 'boundary_level';
        }
    }
    
    service.getActiveBoundaryFilterValue = function(){
        if (service.getActiveBoundaryFilterType() == 'boundary') return service.active_boundary_filters['boundary_scope_ids'];
        else return service.active_boundary_filters['boundary_level'] 
    }
    
    service.getActiveProductFilterType = function(){
        if (service.active_product_filters['product_scope_ids'].length > 0) return 'product';
        else return 'product_group';
    }

    service.getActiveProductFilterName = function(){
        var p_type = service.getActiveProductFilterType();
        var value = service.getActiveProductFilterValue();
        var to_return = [];

        if (p_type == 'product'){
            for (var i in value){
                to_return.push(service.products[value[i]]);
            }
        } else {
            for (var i in value){
                to_return.push(service.productGroups[value[i]]);
            }
        }

        return to_return;
    }
    
    service.getActiveProductFilterValue = function(){
        if (service.getActiveProductFilterType() == 'product') return service.active_product_filters['product_scope_ids']
        else return service.active_product_filters['product_group']
    }
    
    service.getActiveTimeframeFilterName = function(){
        var f_type = service.getActiveTimeframeFilterType();
        var values = service.getActiveTimeframeFilterValue();
        if (f_type == 'day') return values.date_day + '-' + values.date_month + '-' + values.date_year;
        if (f_type == 'month') return values.date_month + '-' + values.date_year;
        if (f_type == 'year') return values.date_year;
        if (f_type == 'week'){
            var date_start_of_week = new Date(values.date_year, values.date_month, values.date_day);
            var date_end_of_week = new Date(date_start_of_week.valueOf());
            date_end_of_week.setDate( date_start_of_week.getDate() + 6 );
            return date_start_of_week.getDate() + '/' + date_start_of_week.getMonth() + '/' + date_start_of_week.getFullYear() + ' - ' + date_end_of_week.getDate() + '/' + date_end_of_week.getMonth() + '/' + date_end_of_week.getFullYear()
        }

        return '';
    }   

    service.getActiveTimeframeFilterType = function(){
        return service.active_timeframe_filters['type'];
    }
    
    service.getActiveTimeframeFilterValue = function(){
        return service.active_timeframe_filters;
    }

    service.getActiveTimeframeFilterName_yyyymmdd = function(){
        var timeframe_raw = service.getActiveTimeframeFilterName();
        var timeframe_type = service.getActiveTimeframeFilterType();
        var timeframe;

        switch(timeframe_type){
            case 'year':
                timeframe = timeframe_raw.toString();
                break;
            case 'month':
                timeframe = timeframe_raw.split('-')[1] + ('00' + timeframe_raw.split('-')[0]).slice(-2)
                break;
            case 'week':
                var end_day = timeframe_raw.split(' - ')[1].split('/');
                timeframe = end_day[2] + ('00' + end_day[1]).slice(-2) + ('00' + end_day[0]).slice(-2);
                break;
            case 'day':
                var end_day = timeframe_raw.split('-');
                timeframe = end_day[2] + ('00' + end_day[1]).slice(-2) + ('00' + end_day[0]).slice(-2);
                break;
        }

        return timeframe;
    }

    service.getActiveFilterParams = function(kpi_type, boundary_filter_type, boundary_filter_value, product_filter_type, product_filter_value, timeframe_filter_type, timeframe_filter_value){
        var params = {};
        
        if (kpi_type != null) params.kpi_type = kpi_type;
        else params.kpi_type =service.getActiveKPITypeFilter();
        
        if (boundary_filter_type != null){
            params.boundary_filter_type = boundary_filter_type;
            params.boundary_filter_value = boundary_filter_value;
        } else {
            params.boundary_filter_type = service.getActiveBoundaryFilterType();
            params.boundary_filter_value = service.getActiveBoundaryFilterValue();
        }
        
        if (product_filter_type != null){
            params.product_filter_type = product_filter_type;
            params.product_filter_value = product_filter_value;
        } else {
            params.product_filter_type = service.getActiveProductFilterType();
            params.product_filter_value = service.getActiveProductFilterValue();
        }
        
        if (timeframe_filter_type != null){
            params.timeframe_filter_type = timeframe_filter_type;
            params.timeframe_filter_value = timeframe_filter_value;
        } else {
            params.timeframe_filter_type = service.getActiveTimeframeFilterType();
            params.timeframe_filter_value = service.getActiveTimeframeFilterValue();
        }
        
        return params;
    }
    
    // These filters are placeholders to indicated what the user has selected so far without pressing OK button
    service.selected_product_filters = null;
    service.selected_boundary_filters = null;
    service.selected_timeframe_filters = '';
    
    service.getSelectedBoundaryFilterType = function(){
        if (service.selected_boundary_filters['boundary_scope_ids'].length > 0){
            if (service.selected_boundary_filters['boundary_level'] == service.lowestLevelBoundary) return 'facility';
            else return 'boundary';
        } else {
            return 'boundary_level';
        }
    };
    
    service.getSelectedBoundaryFilterValue = function(){
        var _ = service.getSelectedBoundaryFilterType() ;
        if ( _ == 'boundary' || _ == 'facility') return service.selected_boundary_filters['boundary_scope_ids'];
        else return service.selected_boundary_filters['boundary_level']; 
    }
    
    service.getSelectedProductFilterType = function(){
        if (service.selected_product_filters['product_scope_ids'].length > 0) return 'product';
        else return 'product_group';
    }
    
    service.getSelectedProductFilterValue = function(){
        if (service.getSelectedProductFilterType() == 'product') return service.selected_product_filters['product_scope_ids'];
        else return service.selected_product_filters['product_group'];
    }
 
    service.getSelectedTimeframeFilterType = function(){
        return service.selected_timeframe_filters['type'];
    }
    
    service.getSelectedTimeframeFilterValue = function(){
        return service.selected_timeframe_filters;
    }

    service.selectedBoundaryFilterChange = function(boundaries){
        service.selected_boundary_filters = boundaries;
        service.broadcastSelectedFilterChanged_Event();
    };
    
    service.selectedProductFilterChange = function(products){
        service.selected_product_filters = products;
        service.broadcastSelectedFilterChanged_Event();
    };

    service.getSelectedFilterKeywords = function(){
        var keywords = [],
            b_scopes = [], 
            p_scopes = [], 
            b_level = null, 
            p_level = null;

        if (service.selected_boundary_filters){
            b_scopes = service.selected_boundary_filters['boundary_scope_ids'];
            b_level = service.selected_boundary_filters['boundary_level'];
        }

        if (service.selected_product_filters){
            p_scopes = service.selected_product_filters['product_scope_ids'];
            p_level = service.selected_product_filters['product_group'];
        }

        // Boundaries
        if (b_scopes.length > 0){
            for (var i=0; i<b_scopes.length; i++){
                if (b_level == service.boundaryLevels['lowestBoundaryLevel']){
                    keywords.push({'desc': service.facilities[b_scopes[i]], 'colorscheme': 'success'});
                } else {
                    keywords.push({'desc': service.boundaries[b_scopes[i]], 'colorscheme': 'success'});
                }
            }
        } else {
            if (b_level){
                keywords.push({'desc': service.boundaryLevels[b_level], 'colorscheme': 'success'});
            }
        }
        
        // Products
        if(p_scopes.length > 0){
            for (var i=0; i<p_scopes.length; i++){
                keywords.push({'desc': service.products[p_scopes[i]], 'colorscheme': 'important'});
            }            
        } else {
            if (p_level){
                for(var i=0; i<p_level.length; i++){
                    keywords.push({'desc': service.productGroups[p_level[i]], 'colorscheme': 'important'});
                }
            }
        }
        
        // Timeframe
        if (service.selected_timeframe_filters){
            if (service.selected_timeframe_filters['type'] == 'year'){
                keywords.push({'desc': service.selected_timeframe_filters['date_year'], 'colorscheme': 'info'});
            }
            
            if (service.selected_timeframe_filters['type'] == 'month'){
                keywords.push({'desc': service.selected_timeframe_filters['date_month'] + '/' + service.selected_timeframe_filters['date_year'], 'colorscheme': 'info'});
            }
            
            if (service.selected_timeframe_filters['type'] == 'day'){
                keywords.push({'desc': service.selected_timeframe_filters['date_day'] + '/' + service.selected_timeframe_filters['date_month'] + '/' + service.selected_timeframe_filters['date_year'], 'colorscheme': 'info'});
            }
            
            if (service.selected_timeframe_filters['type'] == 'week'){
                var week_end = new Date(service.selected_timeframe_filters['epoch']);
                week_end.setDate(week_end.getDate() + 6 );
                var t_str = service.selected_timeframe_filters['date_day'] + '/' + service.selected_timeframe_filters['date_month'] + '/' + service.selected_timeframe_filters['date_year'] + ' - ' + week_end.getDate() + '/' + week_end.getMonth() + '/' + week_end.getFullYear();
                keywords.push({'desc': t_str, 'colorscheme': 'info'});
            }
        }
        return keywords;
    };
    
   
    service.getSelectedFilterParams = function (kpi_type, boundary_filter_type, boundary_filter_value, product_filter_type, product_filter_value, timeframe_filter_type, timeframe_filter_value){
        var params = {};

        
        if (kpi_type != null){
            params.kpi_type = kpi_type;
        } else {
            params.kpi_type =service.getActiveKPITypeFilter();
        }
        
        if (boundary_filter_type != null){
            params.boundary_filter_type = boundary_filter_type;
            params.boundary_filter_value = boundary_filter_value;
        } else {
            params.boundary_filter_type = service.getSelectedBoundaryFilterType();
            params.boundary_filter_value = service.getSelectedBoundaryFilterValue();
        }
        
        if (product_filter_type != null){
            params.product_filter_type = product_filter_type;
            params.product_filter_value = product_filter_value;
        } else {
            params.product_filter_type = service.getSelectedProductFilterType();
            params.product_filter_value = service.getSelectedProductFilterValue();
        }
        
        if (timeframe_filter_type != null){
            params.timeframe_filter_type = timeframe_filter_type;
            params.timeframe_filter_value = timeframe_filter_value;
        } else {
            params.timeframe_filter_type = service.getSelectedTimeframeFilterType();
            params.timeframe_filter_value = service.getSelectedTimeframeFilterValue();
        }
        
        return params;
    }
    
    service.broadcastSelectedFilterChanged_Event = function(){
        $rootScope.$broadcast('SelectedFilterChanged_Event');
    };
    
    service.SelectedFilterChanged_EventListeners = {}

    service.addSelectedFilterChangedEventListener = function(scope, callbackName){
        var me = this;
        if (!me.SelectedFilterChanged_EventListeners[scope.$id]){
            me.SelectedFilterChanged_EventListeners[scope.$id] = {};  
        }
        me.SelectedFilterChanged_EventListeners[scope.$id][callbackName] = $rootScope.$on('SelectedFilterChanged_Event', scope[callbackName]);      
        
        scope.$on("$destroy",function(){
            for (var item in me.SelectedFilterChanged_EventListeners[scope.$id]){
                me.SelectedFilterChanged_EventListeners[scope.$id][item]();                    
            }
        }); 
    }
      
    service.getCurrentBoundaryViewParams = function(kpi_type, product_filter_type, product_filter_value, timeframe_filter_type, timeframe_filter_value){
        var params = {};
        
        if (kpi_type != null){
            params.kpi_type = kpi_type
        } else {
            params.kpi_type =service.getActiveKPITypeFilter();
        }
        
        var _ = service.current_view_data['boundaries'];

        var boundary = [];

        for (var i =0;i< _.length; i++){
            boundary.push(_[i]['id']); 
        }
            
        params.boundary_filter_type = 'boundary';
        params.boundary_filter_value = boundary;
        
        if (product_filter_type != null){
            params.product_filter_type = product_filter_type;
            params.product_filter_value = product_filter_value;
        } else {
            params.product_filter_type = service.getActiveProductFilterType();
            params.product_filter_value = service.getActiveProductFilterValue();
        }
        
        if (timeframe_filter_type != null){
            params.timeframe_filter_type = timeframe_filter_type;
            params.timeframe_filter_value = timeframe_filter_value;
        } else {
            params.timeframe_filter_type = service.getActiveTimeframeFilterType();
            params.timeframe_filter_value = service.getActiveTimeframeFilterValue();
        }
        
        return params;
    };
    return service;
}]);
