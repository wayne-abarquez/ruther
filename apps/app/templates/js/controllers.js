//rutherApp.controller('detailedModalCtrl', ['$scope', '$http', 'filterService', 'ngTableParams', function($scope, $http, filterService, ngTableParams){
rutherApp.controller('detailedModalCtrl', ['$scope', '$http', 'filterService', function($scope, $http, filterService){
    // Doing this so that when we call activateDetailedModal from outside angular, we can still make use of these functions.
    $scope.$http = $http;
    $scope.filterService = filterService;

    $scope.modal_params = {'name': 'jhalley'};
    $scope.data_table = [];
    $scope.forheader = [];
    $scope.salesforce_table = {};
    $scope.default_owner_information = {'name': 'Unknown', 'address': 'Unknown', 'pic': '/resources/media/facility_owner_picture/default/default_profile_picture_117087.jpg'};
    $scope.owner_information = $scope.default_owner_information;

    $scope.salesforce_preloader = true;
    $scope.charts_preloader = true;
    $scope.data_preloader = true;
    $scope.owner_info_preloader = true;

    $scope.activateDetailedModal = function(mp){
        // Put preloaders in place
        $scope.salesforce_preloader = true;
        $scope.charts_preloader = true;
        $scope.data_preloader = true;

        console.log(mp);
        $scope.modal_params = mp;

        // Do headers
        // Boundaries
        $scope.forheader = [{'colorscheme': 'success', 'desc': mp.request_type=='boundary'?$scope.filterService.getBoundaryName(mp.id):$scope.filterService.getFacilityName(mp.id)}];
        // Products
        for(var i in mp.product_filter_value){
            $scope.forheader.push({'colorscheme': 'important', 'desc': mp.product_filter_type=='product_group'?$scope.filterService.productGroups[mp.product_filter_value[i]]:$scope.filterService.products[mp.product_filter_value[i]]});
        }
        // Timeframe
        $scope.forheader.push({'colorscheme': 'info', 'desc': mp.timeframe_filter_name});

        $scope.$apply();

        // Repopulate chart
        $scope.drawChart();

        // Repopulate table
        $scope.populateTable();

        // Repopulate owner information
        if (mp.request_type == 'facility'){
            $scope.ownerInformation();
        }

        // Generate new UUID tag for carousel
        $scope.modal_params.uuid = gen_uuid();

        // Repopulate salesforce table
        $scope.populateSalesforceTable();

        // Open on first tab
        setTimeout(function(){
            $('#detail-modal-Tab a:first').tab('show');
        }, 400);
    };

    $scope.ownerInformation = function(){
        var url = 'getOwnerInformation/' + $scope.modal_params.id;

        // We do this because it takes to download and cache the pic
        $scope.owner_information['pic'] = $scope.default_owner_information['pic'];

        // HTTP Get
        $http.get(url)
            .success(function(data, status){
                $scope.owner_info_preloader = false;
                console.log(data);

                if (!parseInt(data['ErrorCode'])){
                    $scope.owner_information = data['Data'];

                    // Check if picture is blank
                    if (!data['Data']['pic']){
                        $scope.owner_information['pic'] = $scope.default_owner_information['pic'];
                    }
                } else {
                    $scope.owner_information = $scope.default_owner_information;
                }
            }).error(function(data, status){
                $scope.owner_info_preloader = false;
            });

    }

    $scope.populateSalesforceTable = function(){
        var url = 'getSalesforceData/?' + $scope.modal_params.param_query_string;

        // HTTP Get
        $http.get(url)
            .success(function(data, status){
                $scope.salesforce_preloader = false;
                console.log(data);

                if (!parseInt(data['ErrorCode'])){
                    // Redraw table. 
                    $scope.salesforce_table = data['Data'];
                    
                    // Create dataTable
                    setTimeout(function(){
                        $('#detail-modal-salesforce table').dataTable({
                            "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>", 
                            "sPaginationType": "bootstrap"
                        });
                    }, 100);
                } else {
                }
            }).error(function(data, status){
                $scope.salesforce_preloader = false;
            });
    }

    $scope.populateTable = function(){
        $scope.data_table = [];

        // Create URL
        // http://localhost:5000/getChartData/?boundary_filter_type=boundary&boundary_filter_id=1,2&product_filter_type=product_group&product_filter_id=1&timeframe=day&date=2013-9-17
        var url = 'getTableData/?' + $scope.modal_params.param_query_string;

        // HTTP Get
        $http.get(url)
            .success(function(data, status){
                $scope.data_preloader = false;
                console.log(data);

                if (!parseInt(data['ErrorCode'])){
                    // Redraw table. 
                    $scope.data_table = data['Data'];

                    /*
                    $scope.tableParams = new ngTableParams({
                        page: 1,
                        total: data['Data'].length,
                        count: 10
                    });
                    */
                } else {
                }
            }).error(function(data, status){
                $scope.data_preloader = false;
            });
    }

    /*
    $scope.$watch('tableParams', function(params){
        $scope.data_table = $scope.data_table.slice(
            (params.page - 1) * params.count,
            params.page * params.count
        );
    }, true);
    */

    $scope.drawChart = function(){
        // Create URL
        // http://localhost:5000/getChartData/?boundary_filter_type=boundary&boundary_filter_id=1,2&product_filter_type=product_group&product_filter_id=1&timeframe=day&date=2013-9-17
        var url = 'getChartData/?' + $scope.modal_params.param_query_string;

        // HTTP Get
        $http.get(url)
            .success(function(data, status){
                $scope.charts_preloader = false;
                console.log(data);

                if (!parseInt(data['ErrorCode'])){
                    // Draw chart. External js function outside of angular scope
                    drawVisualization(data['Data']);
                } else {
                    $('#chart_div').empty().text('Error getting chart data');
                }
            }).error(function(data, status){
                $scope.charts_preloader = false;
                $('#chart_div').empty().text('Error getting chart data');
            });
    }
}]);

rutherApp.controller('sidebarFilter', ['$scope', '$http', '$location', 'filterService', 'googleEarthService', 'rutherWebService', function ($scope, $http, $location, filterService, googleEarthService, rutherWebService){	
    
    filterService.init(rutherWebService);
    
    /* Start - filterService event handlers */
    $scope.selectedFilterChanged_EventHandler = function ()
    {
        $scope.filter_keywords = filterService.getSelectedFilterKeywords();    
        $scope.apply();
    };
    
    filterService.addSelectedFilterChangedEventListener($scope,  'selectedFilterChanged_EventHandler');
    /* End - filterService event handlers */

    /* Start - googleEarthService event handlers */
    $scope.googleEarthDblRightClick_EventHandler = function ()
    {
        console.log('click once');
        $scope.changeDisplayLoading();
        $('#topdisplaybanner').text('Processing data...').show();
        $scope.apply();
        setTimeout( function () {
            var data = googleEarthService.zoomOutToPreviousBreadcrumb();
            
            if ( data )
            {
                filterService.setCurrentViewData ( 'boundary', data );

                var _ = data['boundaries']
                if (_)
                {
                    var boundary = [];

                    for (var i =0;i< _.length; i++)
                        boundary.push(_[i]['id']); 
                    
                    
                    var boundary_filter_type = 'boundary' ;

                    var success_callback_func = function (errorcode, errrormsg, request_params, data)
                    {
                        
                        googleEarthService.updateKPI(request_params['kpi_type'], data);
                        $scope.changeDisplayDone ()
                    }   
                    var complete_callback_func = function (errorcode, errrormsg, request_params, data)
                    {
                        $scope.changeDisplayDone ();
                    }
                    
                    var q_params = filterService.getActiveFilterParams(filterService.getActiveKPITypeFilter(), 'boundary', boundary);
                    console.log('getKpi');
                    rutherWebService.getKPI(q_params, null, success_callback_func, null, complete_callback_func );  
                }
                // Display message on top banner
                $('#topdisplaybanner').text('Done').delay('1000').fadeOut(300);

            }
        }, 25);
    }
    
    googleEarthService.addDblRightClickEventListener($scope, 'googleEarthDblRightClick_EventHandler');
    
    $scope.boundaryDoubleLeftClick_EventHandler = function (event, boundary_level, boundary_id, children_level, children)
    {
        $scope.changeDisplayLoading();
        $scope.apply();
        
        var boundary_filter_type = 'boundary';
        if ( children_level == filterService.lowestLevelBoundary )
        {
            boundary_filter_type = 'facility';
        }
        
        var success_cb = function (errorcode, errrormsg, request_params, data) {
            googleEarthService.processKPIMapData(data);
        
            filterService.setCurrentViewData (request_params['boundary_filter_type'], data);

            if (request_params['boundary_filter_type'] == 'boundary')
            {
                var _ = data['boundaries']
                var boundary = [];

                for (var i =0;i< _.length; i++)
                {
                    boundary.push(_[i]['id']); 
                }
                
                var boundary_filter_type = request_params['boundary_filter_type'] ;
                if (boundary_filter_type == 'boundary')
                {
                    var success_callback_func = function(errorcode, errrormsg, request_params, data)
                    {
                        var kpi_type = request_params['kpi_type'];
                        googleEarthService.updateKPI(kpi_type, data);
                    } ;  
                    
                    var complete_callback_func = function (errorcode, errrormsg, request_params, data)
                    {
                        $scope.changeDisplayDone ();
                    };
                    
                    var beforesend_callback_func = function (errorcode, errrormsg, request_params, data)
                    {
                        $scope.changeDisplayLoading ();
                    };
                   
                   var q_params = filterService.getActiveFilterParams(filterService.getActiveKPITypeFilter(), 'boundary', boundary);
                   
                   rutherWebService.getKPI(q_params, beforesend_callback_func, success_callback_func, null, complete_callback_func );       
                }
            }
            // faciity no need to do anything.
            else
            {
                $scope.changeDisplayDone ();
            }
        };
        
        var error_cb = function(errorcode, errrormsg, request_params, data)
        {
            console.log('Unable to getKPIMapData.')
            $scope.changeDisplayEnabled ()
        };

        var q_params = filterService.getActiveFilterParams(null, boundary_filter_type, children);
        
        rutherWebService.getKPIMapData( q_params, null, success_cb, error_cb );
    };
    
    googleEarthService.addBoundaryDoubleLeftClickEventListener($scope, 'boundaryDoubleLeftClick_EventHandler');
    
    /* END googleEarthService event handlers */
    
    $scope.apply = function()
    {
        if (!$scope.$$phase)
        {
            $scope.$apply();
        }
    }

    $scope.doSubmit = function(){
        var success_cb = function (errorcode, errrormsg, request_params, data){
            googleEarthService.processKPIMapData(data);
            
            filterService.setCurrentViewData(request_params['boundary_filter_type'], data);
            filterService.setActiveFilters(filterService.selected_boundary_filters, filterService.selected_product_filters, filterService.selected_timeframe_filters);

            console.log('filterService.selected_timeframe_filters: ', filterService.selected_timeframe_filters);

            var success_callback_func = function(errorcode, errrormsg, request_params, data){
                googleEarthService.updateKPI(request_params['kpi_type'], data);
            }   
            
            var complete_callback_func = function(errorcode, errrormsg, request_params, data){
                $scope.changeDisplayDone();
            }
            
            var b_filter_type = request_params['boundary_filter_type'];
            var b_filter_id = request_params['boundary_filter_id'];
            
            if ((b_filter_type == 'boundary_level' && b_filter_id < filterService.lowestLevelBoundary) || b_filter_type == 'boundary'){
                var q_params = filterService.getCurrentBoundaryViewParams();
                rutherWebService.getKPI(q_params, null, success_callback_func, null, complete_callback_func) ;    
            }
            else
                $scope.changeDisplayDone();
        };
        
        var beforesend_cb = function(){$scope.changeDisplayLoading();};
        var error_cb = function(){console.log('Unable to getKPIMapData.');};
        
        googleEarthService.clearBreadcrumbCache();
  
        $scope.wait_for_it = true;
        
        //var params = filterService.getSelectedFilterParamsV2();
        var params = filterService.getSelectedFilterParams();
        
        rutherWebService.getKPIMapData(params, beforesend_cb, success_cb, error_cb, null);
        
        return false;
    }
      
    
    $scope.changeDisplayDone = function()
    {
        $('#btn_filterOK').delay('10').fadeIn(10);   
        $('#filterResetButton').delay('10').fadeIn(10);   
        
        $scope.btn_loading_display = '';
        $scope.btn_filterOK_disabled = false;
        
 
        $('#topdisplaybanner').text('Done').delay('1500').fadeOut(300);
        $scope.apply();

    }
    
    $scope.changeDisplayLoading = function ()
    {
        $scope.btn_loading_display = true;
        $scope.btn_filterOK_disabled = true;

        // Display message on top banner
        $('#topdisplaybanner').text('Fetching data...').show();
        $scope.apply();
    }

    $('#dp1').datepicker({
        weekStart: 4,
        onRender: function (date) { // disable future dates
            return date.valueOf() > new Date().valueOf() ? 'disabled' : '';
        }
    })
        .on('changeDate', function(ev, params){
        console.log('getval date: ', $('#dp1').data('datepicker').getValue());
        filterService.selected_timeframe_filters = $('#dp1').data('datepicker').getValue();
        filterService.broadcastSelectedFilterChanged_Event();
    });

    $scope.timeframe_update = function(){
        filterService.selected_timeframe_filters = $('#dp1').val();
        filterService.broadcastSelectedFilterChanged_Event();
    }

    /* ---
       v2 Filter stuff
    --- */
    $scope.selected_options = {
        'boundaries': [],
        'products': [],
        'timeframe': [],
    }
}])



/* ---
   New stuff 
--- */
rutherApp.directive('balloonInfo', ['$http', '$timeout', 'filterService', 'googleEarthService', 'rutherWebService', function($http, $timeout, filterService, googleEarthService, rutherWebService){
    return{
        restrict: 'E',
        scope: {  },
        templateUrl: 'balloon_info.html',
        link: function(scope, elem, attrs){
            scope._t = null;
            scope.outlet_subtype_preloader = true;
            scope.processing = false;
            scope.request_type = '';
 
            // Add left click event when boundary polygon clicked
            scope.boundaryLeftClick_EventHandler = function(event, boundary){
                if (scope.processing){
                    $('#topdisplaybanner').text('Please wait...').show().delay('1500').fadeOut(300);
                } else {
                    scope.processing = true;
                    $('#topdisplaybanner').text('Please wait...').show().delay('1500').fadeOut(300);

                    scope._t = {
                        'id': boundary['id'], 
                        'uuid': gen_uuid(),
                        'boundary_filter_name': '',
                        'product_filter_name': filterService.getActiveProductFilterName(), 
                        'product_filter_type': filterService.getActiveProductFilterType(),
                        'product_filter_value': filterService.getActiveProductFilterValue(),
                        'timeframe_filter_name': filterService.getActiveTimeframeFilterName(), 
                        'timeframe_filter_value': filterService.getActiveTimeframeFilterValue(),
                        'param_query_string': rutherWebService.buildGetParamsString(filterService.getActiveFilterParams(0, 'boundary', [boundary['id']])),
                        'kpi': '', 
                        'kpi_request': false, 
                        'child_boundary': [], 
                        'child_boundary_request': false, 
                        'facility': [], 
                        'facility_request': false,
                        'request_type': 'boundary',
                    }
                    
                    scope._t['boundary_filter_name'] = (filterService.lowestLevelBoundary == boundary['level'])?filterService.getFacilityName(boundary['id']):filterService.getBoundaryName(boundary['id']);
                    scope.request_type = 'boundary';
                    scope.getKPIForBoundary(boundary['id'])
                    scope.getFacilityCount(boundary['id']);
                    scope.getChildBoundaryCount(boundary['id']);
                    scope.getOutletTypeCountsPerBoundary(boundary['id']);
                    scope.getOutletSubtypeCountsPerBoundary(boundary['id']);

                    setTimeout(scope.checkDataRequestStatus, 0, 0);
                }
            }
            
            googleEarthService.addBoundaryLeftClickEventListener(scope, 'boundaryLeftClick_EventHandler');
            
            // add left click event when a facility clicked
            scope.facilityLeftClick_EventHandler = function(event, facility){
                if (scope.processing){
                    $('#topdisplaybanner').text('Please wait...').show().delay('1500').fadeOut(300);
                } else {
                    scope.data = null;
                    scope.processing = true;
                    $('#topdisplaybanner').text('Please wait...').show().delay('1500').fadeOut(300);

                    scope._t = {
                        'id': facility['id'], 
                        'uuid': gen_uuid(),
                        'boundary_filter_name': filterService.getFacilityName(facility['id']),
                        'product_filter_name': filterService.getActiveProductFilterName(), 
                        'product_filter_type': filterService.getActiveProductFilterType(),
                        'product_filter_value': filterService.getActiveProductFilterValue(),
                        'timeframe_filter_name': filterService.getActiveTimeframeFilterName(), 
                        'timeframe_filter_value': filterService.getActiveTimeframeFilterValue(),
                        'param_query_string': rutherWebService.buildGetParamsString(filterService.getActiveFilterParams(0, 'facility', [facility['id']])),
                        'kpi': '', 
                        'kpi_request': false, 
                        'child_boundary': [], 
                        'child_boundary_request': false, 
                        'facility': [], 
                        'facility_request': false,
                        'request_type': 'facility',
                        'facility_outlet_type': '',
                    }
                   
                    scope.getOutletTypeForFacility(facility['id']);
                    scope.request_type = 'facility';
                    scope.getKPIForFacility(facility['id'])

                    setTimeout(scope.checkDataRequestStatus, 0, 0);
                }
            }
            googleEarthService.addFacilityLeftClickEventListener(scope, 'facilityLeftClick_EventHandler');

            scope.getOutletTypeForFacility = function(facility_id){
                $http.get('getFacilityOutletType/' + facility_id + '/')
                    .success(function(data, status){
                        console.log(data);

                        if (!parseInt(data['ErrorCode'])){
                            scope._t['facility_outlet_type'] = data['Data'];
                        } else {
                            scope._t['facility_outlet_type'] = 'Unknown';
                        }
                    }).error(function(data, status){
                        scope._t['facility_outlet_type'] = 'Unknown';
                    });
            }

            scope.getOutletTypeCountsPerBoundary  = function(boundary_id){
                $http.get('getOutletTypeCountsPerBoundary/' + boundary_id + '/?' + scope._t['param_query_string'])
                    .success(function(data, status){
                        console.log(data);

                        if (!parseInt(data['ErrorCode'])){
                            scope._t['outlet_type_counts'] = data['Data']['outlets'];
                            scope._t['all_outlets'] = data['Data']['all'];
                        } else {
                            scope._t['outlet_type_counts'] = 'Unknown';
                        }
                    }).error(function(data, status){
                        scope._t['outlet_type_counts'] = 'Unknown';
                    });
            }

            scope.getOutletSubtypeCountsPerBoundary  = function(boundary_id){
                $http.get('getOutletSubtypeCountsPerBoundary/' + boundary_id + '/?' + scope._t['param_query_string'])
                    .success(function(data, status){
                        scope.outlet_subtype_preloader = false;
                        console.log(data);

                        if (!parseInt(data['ErrorCode'])){
                            scope._t['outlet_subtype_counts'] = data['Data'];
                        } else {
                            scope._t['outlet_subtype_counts'] = 'Unknown';
                        }
                    }).error(function(data, status){
                        scope.outlet_subtype_preloader = false;
                        scope._t['outlet_subtype_counts'] = 'Unknown';
                    });
            }

            scope.getKPIForBoundary = function(boundary_id){
                var success_func_cb = function(errorcode, errrormsg, request_params, data){
                    console.log(request_params);
                    console.log(data);
                    var boundary_id = request_params['boundary_filter_id'][0];
                    var _ = data[boundary_id];
                    var kpis = [];
                    var _tmp = {};
                        
                    for(kpi_type_id in _){
                        facility_type_id = _[kpi_type_id].facility_type_id;
                        if (_tmp[facility_type_id] != null)
                            _tmp[facility_type_id].kpi.push(_[kpi_type_id]);
                        else
                            _tmp[facility_type_id] = { 'facility_type_name' :filterService.getFacilityTypeName ( facility_type_id ), 'kpi' : [ _[kpi_type_id] ] };
                    }
                    
                    for (facility_type_id in _tmp)
                        kpis.push(_tmp[facility_type_id]);

                    scope._t['kpi'] = kpis;
                    scope._t['kpi_request'] = true;
                };
                
                var error_func_cb = function(errorcode, errrormsg, request_params, data) {};
                var q_params = filterService.getActiveFilterParams(0, 'boundary', [boundary_id]);
                rutherWebService.getKPI(q_params, null, success_func_cb, error_func_cb, null);
            }
            
            scope.getKPIForFacility = function(facility_id){
                var success_func_cb = function(errorcode, errrormsg, request_params, data){
                    var facility_id = request_params['boundary_filter_id'][0];
                    var _ = data[facility_id];

                    var kpis = [];
                    var _tmp = {};
                        
                    for(kpi_type_id in _){
                        facility_type_id = _[kpi_type_id].facility_type_id;
                        if (_tmp[facility_type_id] != null)
                            _tmp[facility_type_id].kpi.push(_[kpi_type_id]);
                        
                        else
                            _tmp[facility_type_id] = { 'facility_type_name' :filterService.getFacilityTypeName ( facility_type_id ), 'kpi' : [ _[kpi_type_id] ] };
                    }
                    
                    for (facility_type_id in _tmp)
                        kpis.push(_tmp[facility_type_id]);

                    scope._t['kpi'] = kpis;
                    scope._t['kpi_request'] = true;
                };
                
                var error_func_cb = function  (errorcode, errrormsg, request_params, data){};
                var q_params = filterService.getActiveFilterParams(0, 'facility', [facility_id]);
                
                rutherWebService.getKPI(q_params, null, success_func_cb, error_func_cb,  null );
            }
            
            scope.createDetailsWindow = function (data)
            {
 
                scope.data = data;

                scope.$apply();
                
                $timeout(function(){    // We need to wait for the data to bind. Is there a way to detect the finished data binding?
                            var balloon_iframe_wrapper = $(elem).closest('.balloon_iframe_wrapper');
                            var cloned_balloon_iframe_wrapper;
                            var clone_position;
                            var slot_num;

                            // We no longer want multiple popups, so we close all open popups before we open a new one
                            // Simulates single popup, and its the fastest way of doing things.
                            $('.balloon_close_button', '.balloon_iframe_wrapper[id!="balloon_popup_iframe"]').trigger('click');

                            // We do a deep copy - this removes all bindings
                            balloon_iframe_wrapper.before(balloon_iframe_wrapper.clone());
                            cloned_balloon_iframe_wrapper = balloon_iframe_wrapper.prev();

                            // Remove ids so there is no conflict
                            cloned_balloon_iframe_wrapper.attr('id', ''); 
                            $('#balloon_popup_polygons', cloned_balloon_iframe_wrapper).attr('id', '')

                            // Rearrange balloons if we have to
                            rearrange_balloons(balloon_iframe_wrapper);

                            // Calculate the correct position of copy and move it there
                            slot_num = window.balloons.length;
                            move_balloon_to_slot(slot_num, balloon_iframe_wrapper, cloned_balloon_iframe_wrapper);

                            // Fill up attributes for clone
                            cloned_balloon_iframe_wrapper[0].name = gen_uuid();
                            cloned_balloon_iframe_wrapper[0].slot_num = slot_num;
                            cloned_balloon_iframe_wrapper[0].moved = false;

                            // Push clone to stack
                            window.balloons.push(cloned_balloon_iframe_wrapper);
                            window.balloons_delete_order.push(cloned_balloon_iframe_wrapper[0].name);

                            // Show copy
                            $('.balloon_popup_wrapper', cloned_balloon_iframe_wrapper).show();
                            $('.well', cloned_balloon_iframe_wrapper).effect('highlight', {color:'orange'}, 500)

                            // Apply draggable and all other listeners
                            // Applying close on document load via event bubbling on the body instead. Cleaner this way.
                            cloned_balloon_iframe_wrapper.draggable({
                                stack: '.balloon_iframe_wrapper',
                                stop: function(e, ui){
                                    this.moved = true;

                                    // Delete element from array in place
                                    window.balloons.splice(this.slot_num, 1); 

                                    // Move element to the last place in the delete order
                                    window.balloons_delete_order.splice(window.balloons_delete_order.indexOf(this.name), 1);
                                    window.balloons_delete_order.push(this.name);

                                    rearrange_balloons($('.balloon_iframe_wrapper:not(.ui-draggable)'));
                                },
                            });
                            scope._t = null;
                            scope.processing = false;
                }, 50);
                        
            }
            scope.getFacilityCount = function(boundary_id)
            {
                var success_func_cb = function  (errorcode, errrormsg, request_params, data) { scope._t.facility_request = true; scope._t.facility = data; };
                var error_func_cb = function  (errorcode, errrormsg, request_params, data)  { };
                
                rutherWebService.getFacilityCount([boundary_id], null, success_func_cb, error_func_cb, null);
            }
            
            scope.manipulateData = function ()
            {
                if (scope._t)
                {
                    scope._t.general_info = [];
                    for (var key in scope._t.child_boundary)
                        scope._t.general_info.push(scope._t.child_boundary[key]);
                    
                    for (var key in scope._t.facility)
                        scope._t.general_info.push(scope._t.facility[key]);                    
                }
            }
            
            scope.getChildBoundaryCount = function(boundary_id)
            {
                var success_func_cb = function  (errorcode, errrormsg, request_params, data) { scope._t.child_boundary_request = true; scope._t.child_boundary = data };
                var error_func_cb = function  (errorcode, errrormsg, request_params, data) { };
                
                rutherWebService.getChildBoundaryCount([boundary_id], null, success_func_cb, error_func_cb, null);
            }
            
            scope.checkDataRequestStatus = function(tries){
                var t = tries;
                var complete = false;
                
                complete = (scope.request_type == 'boundary' && scope._t && scope._t['kpi_request'] && scope._t['facility_request'] && scope._t['child_boundary_request'] && scope._t['outlet_type_counts']) ||
                (scope.request_type == 'facility' && scope._t && scope._t['kpi_request'] && scope._t['facility_outlet_type']);
                
                if (!complete){
                    if ( t <= ( 40000 / 200 ) ){
                        setTimeout(function() { scope.checkDataRequestStatus (t+1) }, 200);
                    } else {
                        $('#topdisplaybanner').text('Unable to get data.....').show().delay('1500').fadeOut(300);
                        scope._t = null;
                        scope.processing = false;
                    }
                } else {
                    scope.manipulateData();
                    scope.createDetailsWindow(scope._t);
                }
            };
            

        },
    }
}]);

rutherApp.directive('kpiSelector', ['$http', 'filterService', 'googleEarthService', 'rutherWebService', function($http, filterService, googleEarthService, rutherWebService){

    return{
        restrict: 'E',
        scope: {},
        templateUrl: 'kpi_selector.html',
        link: function(scope, elem, attrs){
        
            var success_func = function (errorcode, errrormsg, request_params, data)
            {
                scope.kpi_types = data['KPITypes'];
                scope.kpi_selected = scope.kpi_types[0];    // So that we don't have an empty option within the select
                filterService.setActiveKPITypeFilter(scope.kpi_selected.id);    // Set initial KPI value. We're cheating here. We'll have to refactor the whole thing later. We shouldn't do too many calls just to draw the polygons.
            };
            
            var error_func = function (errorcode, errrormsg, request_params, data)
            {
                console.log('Unable to get KPI types listing for KPI view filter.');
            };
            
            rutherWebService.getKPITypes(null, success_func, error_func, null);
            
            scope.updateSelector = function(){
                var callback_func = function(errorcode, errormsg, request_params, data)
                {                    
                    googleEarthService.updateKPI(request_params['kpi_type'], data);
                }   
                
                filterService.setActiveKPITypeFilter(scope.kpi_selected.id);
                var q_params = filterService.getCurrentBoundaryViewParams(scope.kpi_selected.id)
                rutherWebService.getKPI(q_params, null, callback_func, null, null);
            }
        },
    }
}]);

rutherApp.directive('shimify', function(){
    return{
        restrict: 'A',
        scope: {},
        transclude: true,
        templateUrl: 'shimify.html',
    }
});

rutherApp.directive('boundariesMember', ['$compile', function($compile){
    return {
        restrict: 'E',
        replace: true,
        require: ['^boundariesFilter2', '^boundariesCollection'],
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
                ctrls[1].uncheck_all_nonsiblings();
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
        require: ['^boundariesFilter2'],
        scope: {
            collection: "=",
            isvisible: "=",
        },
        templateUrl: 'boundaries_collection.html',
        controller: function($scope){
            this.uncheck_all_nonsiblings = function(){
                for (var i in $scope.collection){
                    $scope.collection[i].protected = true;
                }

                $scope.call_recursiveCheckLogic();

                for (var i in $scope.collection){
                    $scope.collection[i].protected = false;
                }
            }
        },
        link: function(scope, element, attrs, ctrls){
            scope.call_recursiveCheckLogic = function(){
                ctrls[0].recursiveCheckLogicWrapper();
            }

            scope.$watch('collection', function(newVal, oldVal){
                if (scope.collection && scope.collection.length){
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

rutherApp.directive('boundariesFilter2', ['filterService', '$http', function(filterService, $http){
    return {
        restrict: 'E',
        replace: true,
        scope: {
            boundariesSelected: "=",
        },
        templateUrl: 'boundaries_filter2.html',
        controller: function($scope){
            this.recursiveCheckLogicWrapper = function(){
                $scope.boundariesSelected = [];
                $scope.recursiveCheckLogic($scope.boundaries);

                // clear All Regions checkbox if any of the boundaries are selected
                if ($scope.boundariesSelected.length){
                    $scope.top_lvl_all_select = false;
                }

                $scope.mapToFilterService();
            }
        },
        link: function(scope, element, attrs, controller){
            /* Load the boundary data */
            scope.populateFilterBoundaries = function(){
    	        $http.get('getFilterBoundariesHierarchy')
                .success(function(data, status){
                    scope.boundaries = data['boundaries'];
                    scope.top_lvl_desc = data['top_lvl_desc'];
                    scope.top_lvl_permission = data['top_lvl_permission'];

                    scope.facilities_lvl = data['facilities_lvl'];
                    window.x = scope.boundaries;
                }).error(function(data, status){
                    scope.locations = []; 
                    console.log("Unable to get boundaries listing for filter sidebar"); 
                });
            }

            scope.populateFilterBoundaries();   // We populate the data
            /* End load */

            scope.isvisible = true;

            scope.recursiveCheckLogic = function(x){
                for (var i in x){
                    if (angular.isArray(x[i].children)){
                        scope.recursiveCheckLogic(x[i].children);
                    }

                    if (!x[i].protected){
                        x[i].selected = false;
                    }

                    if (x[i].selected){
                        scope.boundariesSelected.push(x[i]);
                    }
                }
            }

            scope.top_lvl_click = function(){
                if (scope.top_lvl_all_select){
                    scope.recursiveCheckLogic(scope.boundaries);    // uncheck all checkboxes
                    scope.boundariesSelected = [];
                    scope.boundariesSelected.push({'name': 'All Top Regions'})
                } else {
                    scope.boundariesSelected = [];
                }
                scope.mapToFilterService();
            }

            scope.mapToFilterService = function(){
                var data = {};

                data['boundary_scope_ids'] = [];
                if (scope.top_lvl_all_select){
                    data['boundary_level'] = 1;
                } else {
                    if (scope.boundariesSelected.length > 0){
                        data['boundary_level'] = scope.boundariesSelected[0].level;
                        angular.forEach(scope.boundariesSelected, function(val){
                            data['boundary_scope_ids'].push(val.id);
                        });
                    }
                }

                filterService.selectedBoundaryFilterChange(data);
            }
        }
    }
}]);

rutherApp.directive('productsMember', ['$compile', function($compile){
    return {
        restrict: 'E',
        replace: true,
        require: ['^productsFilter2', '^productsCollection'],
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
                ctrls[1].uncheck_all_nonsiblings();
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
        require: ['^productsFilter2'],
        scope: {
            collection: "=",
            isvisible: "=",
        },
        templateUrl: 'products_collection.html',
        controller: function($scope){
            this.uncheck_all_nonsiblings = function(){
                for (var i in $scope.collection){
                    $scope.collection[i].protected = true;
                }

                $scope.call_recursiveCheckLogic();

                for (var i in $scope.collection){
                    $scope.collection[i].protected = false;
                }
            }
        },
        link: function(scope, element, attrs, ctrls){
            scope.call_recursiveCheckLogic = function(){
                ctrls[0].recursiveCheckLogicWrapper();
            }

            scope.$watch('collection', function(newVal, oldVal){
                if (scope.collection){
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

rutherApp.directive('productsFilter2', ['filterService', '$http', function(filterService, $http){
    return {
        restrict: 'E',
        replace : true,
        scope: {
            productsSelected: "=",
        },
        templateUrl: 'products_filter2.html',
        controller: function($scope){
            this.recursiveCheckLogicWrapper = function(){
                $scope.productsSelected = [];
                $scope.recursiveCheckLogic($scope.products);

                // clear All Regions checkbox if any of the boundaries are selected
                //if ($scope.productsSelected.length){
                //    $scope.top_lvl_all_select = false;
                //}

                $scope.mapToFilterService();
            }
        },
        link : function (scope, element, attrs, controller){
            /* Load the boundary data */
            scope.populateFilterProducts = function(){
                $http.get('getFilterProductsHierarchy')
                .success(function(data, status){
                    scope.products = data['products'];
                    window.x = scope.products;
                    window.y = scope.productsSelected;
                }).error(function(data, status){
                    scope.products = []; 
                    console.log("Unable to get products listing for filter sidebar"); 
                });
            }

            scope.populateFilterProducts();   // We populate the data
            /* End load */

            scope.isvisible = true;

            scope.recursiveCheckLogic = function(x){
                for (var i in x){
                    if (angular.isArray(x[i].children)){
                        scope.recursiveCheckLogic(x[i].children);
                    }

                    if (!x[i].protected){
                        x[i].selected = false;
                    }

                    if (x[i].selected){
                        scope.productsSelected.push(x[i]);
                    }
                }
            }

            scope.mapToFilterService = function(){
                var data = {};

                data['product_scope_ids'] = [];
                data['product_group'] = [];
                if (scope.productsSelected.length > 0){
                    if (scope.productsSelected[0].isLowest){
                        angular.forEach(scope.productsSelected, function(val){
                            data['product_scope_ids'].push(val.id);
                        });
                    } else {
                        angular.forEach(scope.productsSelected, function(val){
                            data['product_group'].push(val.id);
                        });
                    }
                }

                filterService.selectedProductFilterChange(data);
            }
        }
    };
}]);

rutherApp.directive('boundariesFilter', ['filterService', '$http', function(filterService, $http){
    return {
        restrict: 'E',
        replace: true,
        scope: {},
        templateUrl: 'boundaries_filter.html',
        link: function (scope, element, attrs, controller){
            /* Load the boundary data */
            scope.populateFilterBoundaries = function(){
    	        $http.get('getFilterBoundaries')
                .success(function(data, status){
                    scope.data = data['boundaries'];
                }).error(function(data, status){
                    scope.locations = []; 
                    console.log("Unable to get boundaries listing for filter sidebar"); 
                });
            }

            scope.populateFilterBoundaries();   // We populate the data
            /* End load */

            scope.checkboxClicked = function(){
                //console.log(scope.data);
            }

            scope.getSelectedFilters = function(){
                var data, 
                    checked = $('input:checkbox:checked', '.sidebar-nav .accordion #sidebar_panel_filter_boundaries'),
                    all_type_checked = $('input:checkbox:checked.boundary_lvl_all_type');

                function getSelectedElements(l){
                    var temp = [];

                    l.each(function(){
                        temp.push($(this).attr('value'));
                    });

                    return temp;
                }

                if (all_type_checked.length){ // An all type was checked
                    data = {
                        'boundary_level': all_type_checked.attr('value'),
                        'boundary_scope_ids' :[]
                    }
                } else if (checked.length){
                    data = {
                        'boundary_level': $('.boundary_lvl_all_type', checked.closest('.accordion-group')).attr('value'),
                        'boundary_scope_ids' : getSelectedElements(checked),
                    }
                }
                console.log(data);
                
                return data;
            };
            
            $('.sidebar-nav  #sidebar_panel_filter_boundaries').on('click', 'input:checkbox', function(e){
                window.curr = this;
                // For National, Regional or Cluster All checkbox 
                if ($(this).hasClass('boundary_lvl_all_type')){
                    // If the checkbox is checked:
                    if ($(this).prop('checked')){
                        // Uncheck the rest of the all checkboxes
                        $('input:checkbox', '.sidebar-nav  #sidebar_panel_filter_boundaries').not(this).prop('checked', false);
                    } else { 
                        // will it even get to this point??
                        var id = $(this).attr('id');
                        $(id).prop('checked', false);
                    }
                } else { // User clicked one of the elements within a boundary
                        var parent_elem = $(this).closest('.boundary-level'); 
                        $('.boundary_lvl_all_type', '.sidebar-nav #sidebar_panel_filter_boundaries').prop('checked', false);
                        $('.boundary-level','.sidebar-nav #sidebar_panel_filter_boundaries').not(parent_elem).find('.boundary_items_checkbox').prop('checked',false);
                }
                
                var boundaries_filters = scope.getSelectedFilters();
                filterService.selectedBoundaryFilterChange(boundaries_filters);
                //e.preventDefault(); // If this is on, checkboxes don't get automatically checked
            });
        }
    };
}])

rutherApp.directive('productsFilter', ['filterService', '$http', function(filterService, $http){
    return {
        restrict: 'E',
        replace : true,
        scope: {},
        templateUrl: 'products_filter.html',
        link : function (scope, element, attrs, controller){
            /* Load the boundary data */
            scope.populateFilterProducts = function(){
                $http.get('getFilterProducts')
                .success(function(data, status){
                    scope.data = data['products'];
                }).error(function(data, status){
                    scope.products = []; 
                    console.log("Unable to get products listing for filter sidebar"); 
                });
            }

            scope.populateFilterProducts();   // We populate the data
            /* End load */

            scope.getSelectedFilters = function(){
                var data, 
                    checked = $('input:checkbox:checked', '.sidebar-nav .accordion #sidebar_panel_filter_products'),
                    all_type_checked = $('input:checkbox:checked.product_group_level_all');

                function getSelectedElements(l){
                    var temp = [];

                    l.each(function(){
                        temp.push($(this).attr('value'));
                    });

                    return temp;
                }

                if (all_type_checked.length){ // An all type was checked
                    data = {
                        'product_group': all_type_checked.attr('value'),
                        'product_scope_ids' :[]
                    }
                } else if (checked.length){
                    data = {
                        'product_group': $('.product_group_level_all', checked.closest('.accordion-group')).attr('value'),
                        'product_scope_ids' : getSelectedElements(checked),
                    }
                }

                return data;
            }

            $('.sidebar-nav  #sidebar_panel_filter_products').on('click', 'input:checkbox', function(e){
                window.curr = this;
                // For Product Groups checkboxes.
                if ($(this).hasClass('product_group_level_all')){
                    // If the checkbox is checked:
                    if ($(this).prop('checked')){
                        // Uncheck the rest of the all checkboxes
                        $('input:checkbox', '.sidebar-nav  #sidebar_panel_filter_products').not(this).prop('checked', false);
                    } else { 
                        // will it even get to this point??
                        var id = $(this).attr('id');
                        $(id).prop('checked', false);
                    }
                } else { 
                    $('input:checkbox', '.sidebar-nav  #sidebar_panel_filter_products').not(this).prop('checked', false);
                }
                var product_filters = scope.getSelectedFilters();
                
                filterService.selectedProductFilterChange(product_filters);
                //e.preventDefault(); // If this is on, checkboxes don't get automatically checked
            });
        }
    };
}]);

rutherApp.directive('detectEndDataTableInit', ['$timeout', function($timeout){
    return {
        restrict: 'A',
        link: function(scope, element, attrs){
            if(scope.$last){
                $timeout(function(){
                    $(element).closest('table').dataTable({
                        'sDom':'fit',
                        'bScrollInfinite': true,
                        'bScrollCollapse': true,
                        'sScrollY': '200px',
                        'iDisplayLength':10000,
                        'aoColumnDefs':[
                            {'aTargets': [0], 'sWidth': '45px', 'sSortDataType': 'dom-checkbox'},
                        ],
                        'aaSorting':[], // Turn off initial sorting
                    });
                },0);  // We need to wait
            }
        }
    }
}]);
