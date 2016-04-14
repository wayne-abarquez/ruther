function hsv2rgb(h,s,v) {
// Adapted from http://www.easyrgb.com/math.html
// hsv values = 0 - 1, rgb values = 0 - 255
var r, g, b;
var RGB = new Array();
if(s==0){
  RGB['red']=RGB['green']=RGB['blue']=Math.round(v*255);
}else{
  // h must be < 1
  var var_h = h * 6;
  if (var_h==6) var_h = 0;
  //Or ... var_i = floor( var_h )
  var var_i = Math.floor( var_h );
  var var_1 = v*(1-s);
  var var_2 = v*(1-s*(var_h-var_i));
  var var_3 = v*(1-s*(1-(var_h-var_i)));
  if(var_i==0){ 
    var_r = v; 
    var_g = var_3; 
    var_b = var_1;
  }else if(var_i==1){ 
    var_r = var_2;
    var_g = v;
    var_b = var_1;
  }else if(var_i==2){
    var_r = var_1;
    var_g = v;
    var_b = var_3
  }else if(var_i==3){
    var_r = var_1;
    var_g = var_2;
    var_b = v;
  }else if (var_i==4){
    var_r = var_3;
    var_g = var_1;
    var_b = v;
  }else{ 
    var_r = v;
    var_g = var_1;
    var_b = var_2
  }
  //rgb results = 0 ÷ 255  
  RGB['red']=Math.round(var_r * 255);
  RGB['green']=Math.round(var_g * 255);
  RGB['blue']=Math.round(var_b * 255);
  }
return RGB;  
};

function convert(integer) { 
    var str = Number(integer).toString(16); 
    return str.length == 1 ? "0" + str : str; 
};

function rgbToHex(a, r, g, b) {
    return   convert(a) + convert(b) + convert(g) +  convert(r) ;
};

function calculateKPIColor(kpi){
    if(kpi == null){
        return rgbToHex(225, 128, 128, 128);
    }
    
    var min = 0;
    var max = 100;
    var rgb = {};
    var percentFade = kpi / 100;

    if (percentFade >= 0 && percentFade <= 0.25){
        rgb['red'] = 255;
        rgb['green'] = 0;
        rgb['blue'] = 0;
        // percentFade = 0;
    } else if (percentFade > 0.25 && percentFade <= 0.50){
        rgb['red'] = 255;
        rgb['green'] = 255;
        rgb['blue'] = 0;
        // percentFade = 0.33;
    } else if (percentFade > 0.5 && percentFade <= 0.75){
        rgb['red'] = 0;
        rgb['green'] = 255;
        rgb['blue'] = 0;
        // percentFade = 0.66;
    } else {
        // percentFade = 1;
        rgb['red'] = 0;
        rgb['green'] = 0;
        rgb['blue'] = 255;
    }

    console.log(kpi);
    console.log(rgb);
    // var h = percentFade * 0.5 ;
    // var s = 1;
    // var v = 1;
    // var rgb = hsv2rgb(h, s, v);
    
    return rgb
}



function getColorTwo(kpi)
{   
    var rgb = calculateKPIColor ( kpi );
    return rgbToHex(225, rgb['red'], rgb['green'], rgb['blue'] );
}

function getColorThree(kpi){
    var rgb = calculateKPIColor(kpi);
    return [225, rgb['red'], rgb['green'], rgb['blue']];
}

function buildGetKPIDataURL(boundary_level, boundary_id, products, timeframe){
    var url = 'getKPIData?';
    
    if (boundary_level){
        url += 'boundary_level=' + boundary_level;
    }
    
    if (boundary_id > 0){
        url += '&boundary_id=' + boundary_id; 
    }
    
    if (products['type'] == 'product'){
        url += '&product_id=' + products['id'];
    }

    if (products['type'] == 'product_group'){
        url += '&product_group=' + products['id'];
    }
    
    if (timeframe)
    {
        url += '&timeframe=' + timeframe['type'];
        if ( timeframe['type'] == 'week')
        {
            url += '&date_year=' + timeframe['date_year'] + '&date_month=' +  timeframe['date_month']  + '&date_day=' + timeframe['date_day'];
        }
        if ( timeframe['type'] == 'year')
        {
            url += '&date_year=' +  timeframe['date_year'];
        }
        if ( timeframe['type'] == 'month')
        {
            url += '&date_month=' +  timeframe['date_month']  + '&date_year=' + timeframe['date_year'];
        }
        if ( timeframe['type'] == 'day')
        {
            url += '&date=' + timeframe['date_year'] + '-' +  timeframe['date_month'] + '-' + timeframe['date_day'];
        }
        
    }
    return url
}


/*****************************************************************************************
    PolygonPlacemark
    
    contains information and functions to place a Polygon Placemark on google earth

******************************************************************************************/

function Boundary(boundary, factory){
    this.boundary = boundary;
    this.id = boundary.id;
    this.level = boundary.level;
    this.current_kpi = {};
    this.name = boundary['name']; 
    this.coords = boundary['coords']; 
    this.style = boundary['color'];
    this.children_level = boundary['children_level'];
    this.timeframe = boundary['timeframe'];
    this.children = boundary['children'];
    // this._polygonPlacemark = []; 
    this._balloon_id = "#balloon_popup_polygons";

    this.factory = factory;
};

/***************************************************************************************
    class BoundaryFactory
    
    Factory to create and place Polygon Placemark for regions.

***********************************************************************************/


function BoundaryFactory(service)
{
    this.boundaries = []
    this.service = service;
}


BoundaryFactory.prototype.createBoundary = function (boundary){
    var p = new Boundary(boundary, this);
    
    this.boundaries.push(p);
    // p.initPlacemark(ge);
    
}

// clear all placemarks created by this factory.
BoundaryFactory.prototype.clear = function ( )
{   
    this.boundaries = [];
};

BoundaryFactory.prototype.visit = function (service)
{
    var data = {};
    data.boundaries = this.boundaries;
    service.updatePlacemarks(data);
}


/*****************************************************************************************
    Facility
    
    contains information and functions to place a facility's Placemark and data modal on google earth

******************************************************************************************/

function Facility(facility, factory) 
{
	this.facility = facility;
    this.id = facility.id;
    this.factory = factory;
   	this.name = facility['name']; this.coords = facility['coords']; this.style = facility['icon'];
    // this._PointPlacemark = null; 

};



/***************************************************************************************
    class FacilityFactory
    
    Factory to create and place Facility.

    TODO: Link with data modal
***********************************************************************************/

function FacilityFactory(service) 
{
    this.facilities = [];
    this.service = service;

};


// create and place placemark for region

FacilityFactory.prototype.createFacility = function (facility)
{  

    var p = new Facility(facility, this ); 
    
    this.facilities.push(p);
    //p.initPlacemark(this.service.ge);

};
FacilityFactory.prototype.visit = function (service)
{
    var data = {};
    data.facilities = this.facilities;

    service.updatePlacemarks(data);
}

// clear all placemarks created by this factory.
FacilityFactory.prototype.clear = function ( )
{   

    this.facilities = [];

};



rutherApp.factory('rutherGoogleMapService', ['$rootScope', function ($rootScope) 
{
    var service = {};
    service.overlays = {};
    service.initView = null;
    
   
    service.initGMaps = function (map_type_id)
    {   var _map_type_id;
        if(map_type_id) _map_type_id = map_type_id;
        else _map_type_id = google.maps.MapTypeId.ROADMAP;
        
        var latlng = null;
        var zoom_value = 5;
        if (service.initView)
        {
            latlng = new google.maps.LatLng(service.initView.latitude, service.initView.longitude);
            zoom_value = service.initView.zoom;
        }
        
        else
            latlng = new google.maps.LatLng(-0.789275, 117.085186);
    
        var mapOptions = {
            zoom: zoom_value,
            center: latlng, //new google.maps.LatLng(-0.789275, 117.085186),
            mapTypeId: google.maps.MapTypeId.MAP,
            mapTypeControlOptions: {
                position: google.maps.ControlPosition.TOP_RIGHT
            },
            //mapTypeId: _map_type_id,
            panControl: false,
            zoomControl: false,
            //mapTypeControl: false,
            scaleControl: false,
            streetViewControl: false,
            overviewMapControl: false
  
        };
        
        var map = new google.maps.Map(document.getElementById("map3d"), mapOptions);
  
        $('#map3d').unbind('mousedown').mousedown(function(e){ 
           var rightclick = (e.which) 
               ? (e.which == 3) 
               : (e.button == 2); 

           if (rightclick) { 
               // console.log('rightclick'); 
               if (service.rightclicked) { 
                  // console.log('double click!'); 
                  service.broadcastDblRightClick_Event();
               } else { 
                   service.rightclicked = true; 
                   setTimeout( resetRightClick, 300); 
               }; 
           }; 
        }); 
        
        var resetRightClick = function () {service.rightclicked = false;};

        service.gm = map;

        firstLoadFilters();
    }
    
    service.clearPlacemarks = function()
    {
        gm = service.gm;
        
        for ( var boundary_id in service.overlays )
        {
            var overlays = service.overlays[boundary_id];
            for (var i = 0; i < overlays.length; i++)
                overlays[i].setMap(null);
        }
    };
    service.deactivate = function ()
    {
         $('body').unbind('mousedown');
    }
    
    
    service._createPolygonOverlay = function ( boundary )
    {
        gm = service.gm;
        var children_level = boundary.children_level;
        var children = boundary.children;
        var boundary_id = boundary.id;
        var boundary_level = boundary.level;
        var polygonPlacemark = null;
        var polygon = null;
        var outer = null;
        var decoded_coords = null;
        var triangleCoords = [ ];

        var first = null;
        for (var j=0; j< boundary.coords.length; j++){
            first = null;
            triangleCoords = [];

            decoded_coords = google.maps.geometry.encoding.decodePath(boundary.coords[j]);
            
            for (var i=0; i<decoded_coords.length; i++){
                if (first == null){
                    first = new google.maps.LatLng(decoded_coords[i].lat(), decoded_coords[i].lng());
                }
                triangleCoords.push(new google.maps.LatLng(decoded_coords[i].lat(), decoded_coords[i].lng()))

            }
            
            triangleCoords.push ( first );
  
            polygonOverlay = new google.maps.Polygon({
                paths: triangleCoords,
                strokeColor: "#FF0000",
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillColor: "#FF0000",
                fillOpacity: 0.35
              });
            if (! service.overlays[boundary.id] )
                service.overlays[boundary.id] = [ polygonOverlay ];
            else
                service.overlays[boundary.id].push( polygonOverlay );
                
            google.maps.event.addDomListener(polygonOverlay, 'mouseover', function(){ service._highlightBoundary(boundary_id); });
            google.maps.event.addDomListener(polygonOverlay, 'mouseout', function(){ service._unhighlightBoundary(boundary_id); });
            
            google.maps.event.addDomListener(polygonOverlay, 'dblclick', function(e){
                service.broadcastBoundaryDoubleLeftClick_Event(boundary_level, boundary_id, children_level, children);
            });
        
            google.maps.event.addDomListener(polygonOverlay, 'click', function(e){
                service.broadcastBoundaryLeftClick_Event(boundary);
            });
        }
        
        service.boundary_overlay_colors = {};       
    }

    var lastBoundaryOverlaysHighlightOptions = {};

    function getBoundaryPolygonOptions (polygon) {
        if(!polygon) return;

        return {
            strokeOpacity: polygon.get('strokeOpacity'),
            strokeWeight: polygon.get('strokeWeight'),
            fillColor: polygon.get('fillColor'),
            fillOpacity: polygon.get('fillOpacity'),
            strokeColor: polygon.get('strokeColor')
        };
    }

    service._highlightBoundary = function ( boundary_id )
    {
        var overlays = service.overlays[boundary_id];
        if (overlays)
        {
            // Fix Error when no data available -wayne
            if(!lastBoundaryOverlaysHighlightOptions[boundary_id])  lastBoundaryOverlaysHighlightOptions[boundary_id] = {};

            for (var i=0; i<overlays.length; i++)
            {
                // Fix Error when no data available -wayne
                lastBoundaryOverlaysHighlightOptions[boundary_id][i] = getBoundaryPolygonOptions(overlays[i]);

                overlays[i].setOptions({   
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: '#ff6600',
                    fillOpacity: 225,
                    strokeColor: '#ff9933'
                });
            }
        }
    };
    
    service._unhighlightBoundary = function ( boundary_id )
    {
        var overlays = service.overlays[boundary_id];
        if (overlays)
        {
            var color = service.boundary_overlay_colors[boundary_id];

            // Fix Error when no data available -wayne
            if(!color && lastBoundaryOverlaysHighlightOptions[boundary_id]) {
                var opts = lastBoundaryOverlaysHighlightOptions[boundary_id];
                for (var i = 0; i < overlays.length; i++) overlays[i].setOptions(opts[i]);
                return;
            }

            for (var i = 0; i < overlays.length; i++) {
                overlays[i].setOptions({
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: '#' + convert(color[1]) + convert(color[2]) + convert(color[3]),
                    fillOpacity: color[0],
                    strokeColor: '#' + convert(color[1]) + convert(color[2]) + convert(color[3])
                });
            }
        }
    };
    
    service._createPointOverlay = function (facility)
    {
        var myLatlng = new google.maps.LatLng(facility.coords[0][1],facility.coords[0][0]);
        var marker = new google.maps.Marker({
            position: myLatlng,
            icon : facility.style['href']
        });
        
        if (! service.overlays[facility.id] )
            service.overlays[facility.id] = [ marker ];
        else
            service.overlays[facility.id].push( marker );
        

         google.maps.event.addDomListener(marker, 'click', function(e){
                service.broadcastFacilityLeftClick_Event(facility);
            
        });
            

    }
    
    service.updatePlacemarks = function ( data )
    {
  
        delete service.overlays;
        service.overlays = {};
        service.drawn = false;
        if ( data.boundaries != null )
        {
            for (var i=0; i<data.boundaries.length; i++)
            {
                service._createPolygonOverlay(data.boundaries[i]);
            }
        }
        
        else
        {
            for (var i=0; i< data.facilities.length; i++)
            {
                service._createPointOverlay(data.facilities[i]);
            }
            
            if (!service.drawn)
                service.draw();
                    
                
        }
    }
    
    // Map version
    service.updateKPIValue = function(data){
        var boundary_colors = {};

        // Get original colors
        for (var boundary_id in service.placemark){
            boundary_colors[boundary_id] = kpi_color;
        }

        // Update colors
        for (var boundary_id in data.kpi_values){
            current_kpi_rgb= data.kpi_values[boundary_id][data.kpi_type]['color'];
            boundary_colors[boundary_id] = [225, current_kpi_rgb['red'], current_kpi_rgb['green'], current_kpi_rgb['blue']]
        }

        service.boundary_overlay_colors = boundary_colors;
        service._changePolygonColor(boundary_colors);
        
        if (!service.drawn) service.draw();
    }
    
    service._changePolygonColor = function( data )
    {
        var normalStyle = null;
        var color = null;

        for (var boundary_id in data)
        {
            color = data[boundary_id];

            var overlays = service.overlays[boundary_id];

            if (overlays)
            {
                for (var i=0;i < overlays.length; i++)
                    overlays[i].setOptions({   
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: '#' + convert(color[1]) + convert(color[2]) + convert(color[3]),
                    fillOpacity: color[0],
                    strokeColor: '#' + convert(color[1]) + convert(color[2]) + convert(color[3])});
            }
        }
    }
    
    service.drawn = false;
    
    service.draw = function ()
    {
        gm = service.gm;
        for (var boundary_id in service.overlays)
        {
            var overlay =  service.overlays[boundary_id];
           for ( var i =0; i < overlay.length; i++)
                overlay[i].setMap(gm);
        }
        
        service.drawn=true;
    }
    
    
    service.changeMapTypeID = function (map_type_id)
    {

        service.gm.setMapTypeId(map_type_id);
    }
    // Event handler
    
    service.boundaryDoubleLeftClick_EventListeners = {}
    service.broadcastBoundaryDoubleLeftClick_Event = function(boundary_level, boundary_id, children_level, children)
    {
        $rootScope.$broadcast('GMap_boundaryDoubleLeftClick_Event', boundary_level, boundary_id, children_level, children);
    }
    
    service.addBoundaryDoubleLeftClickEventListener = function (scope, callbackName) {
            // console.log('adding event to',scope.$id);
            var me = this;
            if (!me.boundaryDoubleLeftClick_EventListeners[scope.$id]) {
                me.boundaryDoubleLeftClick_EventListeners[scope.$id] = {};  
            }
            me.boundaryDoubleLeftClick_EventListeners[scope.$id][callbackName] = $rootScope.$on('GMap_boundaryDoubleLeftClick_Event', scope[callbackName]);      
            
            scope.$on("$destroy",function() {
                for (var item in me.boundaryDoubleLeftClick_EventListeners[scope.$id]) {
                    me.boundaryDoubleLeftClick_EventListeners[scope.$id][item]();                    
                }
            }); 
            // console.log($rootScope.$$boundaryLeftClick_EventListeners);
    }
    
    // Listeners for left click events on boundary polygons
    service.boundaryLeftClick_EventListeners = {}
    service.broadcastBoundaryLeftClick_Event = function(boundary)
    {
        $rootScope.$broadcast('GMap_boundaryLeftClick_Event', boundary); 
    }   
    
    service.addBoundaryLeftClickEventListener = function (scope, callbackName) {
            // console.log('adding event to',scope.$id);
            var me = this;
            if (!me.boundaryLeftClick_EventListeners[scope.$id]) {
                me.boundaryLeftClick_EventListeners[scope.$id] = {};  
            }
            me.boundaryLeftClick_EventListeners[scope.$id][callbackName] = $rootScope.$on('GMap_boundaryLeftClick_Event', scope[callbackName]);      
            
            scope.$on("$destroy",function() {
                for (var item in me.boundaryLeftClick_EventListeners[scope.$id]) {
                    me.boundaryLeftClick_EventListeners[scope.$id][item]();                    
                }
            }); 
            // console.log($rootScope.$$boundaryLeftClick_EventListeners);
    }
    
    service.facilityLeftClick_EventListeners = {}
    service.broadcastFacilityLeftClick_Event = function (facility)
    {
        $rootScope.$broadcast('GMap_facilityLeftClick_Event', facility); 
    }
    service.addFacilityLeftClickEventListener = function (scope, callbackName) {
            // console.log('adding event to',scope.$id);
            var me = this;
            if (!me.facilityLeftClick_EventListeners[scope.$id]) {
                me.facilityLeftClick_EventListeners[scope.$id] = {};  
            }
            me.facilityLeftClick_EventListeners[scope.$id][callbackName] = $rootScope.$on('GMap_facilityLeftClick_Event', scope[callbackName]);      
            
            scope.$on("$destroy",function() {
                for (var item in me.facilityLeftClick_EventListeners[scope.$id]) {
                    me.facilityLeftClick_EventListeners[scope.$id][item]();                    
                }
            }); 
            // console.log($rootScope.$$boundaryLeftClick_EventListeners);
    }
    
    service.DblRightClick_EventListeners = {}
    service.broadcastDblRightClick_Event = function ()
    {
        if (service.data_breadcrumb_cache.length > 1)
        {        
            $rootScope.$broadcast('GMap_DblRightClick_Event'); 
        }            
    }

    service.addDblRightClickEventListener = function (scope, callbackName) {
            // console.log('adding event to',scope.$id);
            var me = this;
            if (!me.DblRightClick_EventListeners[scope.$id]) {
                me.DblRightClick_EventListeners[scope.$id] = {};  
            }
            me.DblRightClick_EventListeners[scope.$id][callbackName] = $rootScope.$on('GMap_DblRightClick_Event', scope[callbackName]);      
            
            scope.$on("$destroy",function() {
                for (var item in me.DblRightClick_EventListeners[scope.$id]) {
                    me.DblRightClick_EventListeners[scope.$id][item]();                    
                }
            }); 
            // console.log($rootScope.$$boundaryLeftClick_EventListeners);
    };
    
    service.getCurrentView = function ()
    {
        map = service.gm
        var mapZoom=map.getZoom(); 
        var mapCenter=map.getCenter();
        return [mapZoom, mapCenter.lat(), mapCenter.lng()];
     
    }
    
    service.setCurrentView = function (zoom, lat, lng)
    {
        service.gm.setZoom(zoom);
        var latlng = google.maps.LatLng(lat, lng);
        service.gm.setCenter(latlng);
    }
    
    service.data_breadcrumb_cache = [];
    service.updateBreadcrumb = function ( data_breadcrumb_cache)
    {
        service.data_breadcrumb_cache = data_breadcrumb_cache;
    };
    return service;
}]);  

rutherApp.factory('rutherGoogleEarthService', ['$rootScope', function ($rootScope) 
{
    var service = {};
    service.boundary_overlay_colors = {}; 
    service.placemark = {};
    service.drawn = false;
    service.ge = null;
    service.initView = null;
    service.initGE = function ()
    {
        google.earth.createInstance('map3d', service.initGECB_SuccessHandler, service.initGECB_ErrorHandler);
    }
    

    
    service.initGECB_SuccessHandler = function (instance)
    {

        service.ge = instance;
        ge = service.ge;
        ge.getWindow().setVisibility(true);
        
        ge.getLayerRoot().enableLayerById(ge.LAYER_BORDERS , true);
        ge.getLayerRoot().enableLayerById(ge.LAYER_ROADS , true);
        ge.getOptions().setFlyToSpeed(ge.SPEED_TELEPORT);
        // Get the current view.
        var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
        console.log(service.initView);
        if(service.initView)
        {
            lookAt.setLatitude(service.initView.latitude);
            lookAt.setLongitude(service.initView.longitude);
            lookAt.setRange(service.initView.range);
        }
        else
        {
            lookAt.setLatitude(-0.789275);
            lookAt.setLongitude(117.085186);
            lookAt.setRange(4000000.0);
        }
        // Set new latitude and longitude values.
        
        // Update the view in Google Earth.
        ge.getView().setAbstractView(lookAt);

        // Create highlight style for style map
        window.highlightStyle = ge.createStyle('');
        window.highlightStyle.getLineStyle().setWidth(2);
        window.highlightStyle.getLineStyle().getColor().set('ff0066FF');   // orange!
        window.highlightStyle.getPolyStyle().getColor().set('cf3399FF');
         
        // Set up backtrack on right double click behaviour for globe
        google.earth.addEventListener(ge.getGlobe(), 'dblclick', function(e){
            if (e.getButton() == 2){
                // Display message on top banner
                     
                // Close the ballon with kpi information
                // $('#balloon_popup_polygons').hide();
        
                // fly speed
                //ge.getOptions().setFlyToSpeed(4.0);
                // Get the current view.
                var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
                // Zoom out to twice the current range.
                lookAt.setRange(lookAt.getRange() * 3.0);
                // Update the view in Google Earth.
                ge.getView().setAbstractView(lookAt);
                
                service.broadcastDblRightClick_Event();
                

            }
        });
        
        service.broadcastGoogleEarthLoaded_Event();
    }
    service.initGECB_ErrorHandler = function (errorCode)
    {
    
    }
    service.deactivate = function ()
    {
         
    }
    
    service.getCurrentView = function ()
    {
        ge = service.ge
        var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
        
        return [lookAt.getRange(), lookAt.getLatitude(), lookAt.getLongitude() ];
     
    }
    
    service.setCurrentView = function (range, lat, lng)
    {
        var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
        
        // Set new latitude and longitude values.
        lookAt.setLatitude(lat);
        lookAt.setLongitude(lng);
        lookAt.setRange(range);
    }
    service.setCurrentView = function (zoom, lat, lng)
    {
        service.gm.setZoom(zoom);
        var latlng = google.maps.LatLng(lat, lng);
        service.gm.setCenter(latlng);
    }
    service.updatePlacemarks = function ( data )
    
    {
  
        delete service.placemark;
        service.placemark = {};
        service.drawn = false;
        if ( data.boundaries != null )
        {
            for (var i=0; i<data.boundaries.length; i++)
            {
                service._createPolygonOverlay(data.boundaries[i]);
            }
        }
        
        else
        {
            for (var i=0; i< data.facilities.length; i++)
            {
                service._createPointOverlay(data.facilities[i]);
                

            }
            
            if (!service.drawn)
                service.draw();
                    
                
        }
    }
    
    service.draw = function ()
    {
        ge = service.ge;
        for (var boundary_id in service.placemark)
        {
          ge.getFeatures().appendChild(service.placemark[boundary_id]);
        }
        
        service.drawn=true;
    }
    
    service._createPointOverlay = function (facility)
    {
       
        var pointPlacemark = ge.createPlacemark('');
        
        var point = ge.createPoint('');
        point.setLatitude(facility.coords[0][1]);
        point.setLongitude(facility.coords[0][0]);
        pointPlacemark.setGeometry(point);
        
        var icon = ge.createIcon('');

        if ('href' in facility.style){ 
            icon.setHref(facility.style['href']);
            var style = ge.createStyle(''); //create a new style
            style.getIconStyle().setIcon(icon); //apply the icon to the style
            pointPlacemark.setStyleSelector(style); //apply the style to the placemark
        }
    
        service.placemark[facility.id] = pointPlacemark;
        //        ge.getFeatures().appendChild(this._PointPlacemark);
        
        google.earth.addEventListener(pointPlacemark, 'click',  function(){
            service.broadcastFacilityLeftClick_Event(facility);
        });
    }
    
    service._createPolygonOverlay = function ( boundary )
    {
        ge = service.ge;
        var children_level = boundary.children_level;
        var children = boundary.children;
        var boundary_id = boundary.id;
        var boundary_level = boundary.level;
        var polygonPlacemark = null;
        var polygon = null;
        var outer = null;
        var decoded_coords = null;

        polygonPlacemark = ge.createPlacemark('');
        polygonPlacemark.setGeometry(ge.createMultiGeometry(''));

        var geoms = polygonPlacemark.getGeometry().getGeometries();
        var polygon = null;

        for (var j=0; j< boundary.coords.length; j++){
            // Create the polygon.
            polygon = ge.createPolygon('');
           
            // Add points for the outer shape.
            outer = ge.createLinearRing('');

            decoded_coords = google.maps.geometry.encoding.decodePath(boundary.coords[j]);

            for (var i=0; i<decoded_coords.length; i++){
                outer.getCoordinates().pushLatLngAlt(decoded_coords[i].lat(), decoded_coords[i].lng(), 0);
            }
            polygon.setOuterBoundary(outer);
            
            geoms.appendChild(polygon);      
        }
       
        // // Apply style to placemark
        var styleMap = ge.createStyleMap('');

        styleMap.setHighlightStyle(window.highlightStyle);
        polygonPlacemark.setStyleSelector(styleMap);
        
        // Add the placemark to Earth.
        //boundary._polygonPlacemark.push(polygonPlacemark);
       
        // On left double click zoom in and display children
        var b = boundary;
        google.earth.addEventListener(polygonPlacemark, 'dblclick', function(e){
            if (e.getButton() == 0){    // left click 
                service.broadcastBoundaryDoubleLeftClick_Event(boundary_level, boundary_id, children_level, children);
            }
        });
        
        google.earth.addEventListener(polygonPlacemark, 'click', function(e){

            if (e.getButton() == 0){    // left click
                service.broadcastBoundaryLeftClick_Event(b);
            } else if (e.getButton() == 2){ // right click

            }
            
        });
        
        service.placemark[boundary.id] = polygonPlacemark;
    }

    service._changePolygonColor = function( data )
    {
        var normalStyle = null;
        var color = null;
        console.log(data);
        for (var boundary_id in data)
        {

            normalStyle = ge.createStyle('');
            color = data[boundary_id];
            normalStyle.getLineStyle().setWidth(2);
            normalStyle.getLineStyle().getColor().set(color);
            normalStyle.getPolyStyle().getColor().set(color);
            
            polyColor = service.placemark[boundary_id].getStyleSelector().setNormalStyle(normalStyle);
        }
    }


    service.updateKPIValue = function(data){
        var kpi_color = getColorTwo(null);
        var boundary_colors = {}
        for ( var boundary_id in service.placemark )
        {
            boundary_colors[boundary_id] = kpi_color;
        }
    
        var kpi_type = data.kpi_type;
        var kpi_values = data.kpi_values;

        for (var boundary_id in data.kpi_values)
        {              
            var kpi_color = getColorTwo(null);
            if (kpi_values && boundary_id in kpi_values)
            {
                current_kpi = kpi_values[boundary_id];
                kpi_color = getColorTwo(current_kpi[kpi_type]['polygon_value']);
            }
            else
                current_kpi = null;
            
            boundary_colors[boundary_id] = kpi_color;
        }
        service.boundary_overlay_colors = boundary_colors;

        service._changePolygonColor (boundary_colors);
        
        if (!service.drawn)
            service.draw();
    }

    service.boundaryDoubleLeftClick_EventListeners = {}
    service.broadcastBoundaryDoubleLeftClick_Event = function(boundary_level, boundary_id, children_level, children)
    {
        $rootScope.$broadcast('GEarth_boundaryDoubleLeftClick_Event', boundary_level, boundary_id, children_level, children);
    }
    
    service.addBoundaryDoubleLeftClickEventListener = function (scope, callbackName) {
            // console.log('adding event to',scope.$id);
            var me = this;
            if (!me.boundaryDoubleLeftClick_EventListeners[scope.$id]) {
                me.boundaryDoubleLeftClick_EventListeners[scope.$id] = {};  
            }
            me.boundaryDoubleLeftClick_EventListeners[scope.$id][callbackName] = $rootScope.$on('GEarth_boundaryDoubleLeftClick_Event', scope[callbackName]);      
            
            scope.$on("$destroy",function() {
                for (var item in me.boundaryDoubleLeftClick_EventListeners[scope.$id]) {
                    me.boundaryDoubleLeftClick_EventListeners[scope.$id][item]();                    
                }
            }); 
            // console.log($rootScope.$$boundaryLeftClick_EventListeners);
    }
    
    // Listeners for left click events on boundary polygons
    service.boundaryLeftClick_EventListeners = {}
    service.broadcastBoundaryLeftClick_Event = function(boundary)
    {
        $rootScope.$broadcast('GEarth_boundaryLeftClick_Event', boundary); 
    }   
    
    service.addBoundaryLeftClickEventListener = function (scope, callbackName) {
            // console.log('adding event to',scope.$id);
            var me = this;
            if (!me.boundaryLeftClick_EventListeners[scope.$id]) {
                me.boundaryLeftClick_EventListeners[scope.$id] = {};  
            }
            me.boundaryLeftClick_EventListeners[scope.$id][callbackName] = $rootScope.$on('GEarth_boundaryLeftClick_Event', scope[callbackName]);      
            
            scope.$on("$destroy",function() {
                for (var item in me.boundaryLeftClick_EventListeners[scope.$id]) {
                    me.boundaryLeftClick_EventListeners[scope.$id][item]();                    
                }
            }); 
            // console.log($rootScope.$$boundaryLeftClick_EventListeners);
    }
    
    service.facilityLeftClick_EventListeners = {}
    service.broadcastFacilityLeftClick_Event = function (facility)
    {
        $rootScope.$broadcast('GEarth_facilityLeftClick_Event', facility); 
    }
    service.addFacilityLeftClickEventListener = function (scope, callbackName) {
            // console.log('adding event to',scope.$id);
            var me = this;
            if (!me.facilityLeftClick_EventListeners[scope.$id]) {
                me.facilityLeftClick_EventListeners[scope.$id] = {};  
            }
            me.facilityLeftClick_EventListeners[scope.$id][callbackName] = $rootScope.$on('GEarth_facilityLeftClick_Event', scope[callbackName]);      
            
            scope.$on("$destroy",function() {
                for (var item in me.facilityLeftClick_EventListeners[scope.$id]) {
                    me.facilityLeftClick_EventListeners[scope.$id][item]();                    
                }
            }); 
            // console.log($rootScope.$$boundaryLeftClick_EventListeners);
    }
    
    service.DblRightClick_EventListeners = {}
    service.broadcastDblRightClick_Event = function ()
    {
        if (service.data_breadcrumb_cache.length > 1)
        {   console.log('GEarth_DblRightClick_Event');
            $rootScope.$broadcast('GEarth_DblRightClick_Event'); 
        }            
    }

    service.addDblRightClickEventListener = function (scope, callbackName) {
            // console.log('adding event to',scope.$id);
            var me = this;
            if (!me.DblRightClick_EventListeners[scope.$id]) {
                me.DblRightClick_EventListeners[scope.$id] = {};  
            }
            me.DblRightClick_EventListeners[scope.$id][callbackName] = $rootScope.$on('GEarth_DblRightClick_Event', scope[callbackName]);      
            
            scope.$on("$destroy",function() {
                for (var item in me.DblRightClick_EventListeners[scope.$id]) {
                    me.DblRightClick_EventListeners[scope.$id][item]();                    
                }
            }); 
            // console.log($rootScope.$$boundaryLeftClick_EventListeners);
    };

    service.GoogleEarthLoaded_EventListeners = {}
    service.broadcastGoogleEarthLoaded_Event = function()
    {

        $rootScope.$broadcast('GoogleEarthLoaded_Event'); 
    };
    
    service.addGoogleEarthLoaded_EventListener = function (scope, callbackName) {
        // console.log('adding event to',scope.$id);
        var me = this;
        if (!me.GoogleEarthLoaded_EventListeners[scope.$id]) {
            me.GoogleEarthLoaded_EventListeners[scope.$id] = {};  
        }
        me.GoogleEarthLoaded_EventListeners[scope.$id][callbackName] = $rootScope.$on('GoogleEarthLoaded_Event', scope[callbackName]);      
        
        scope.$on("$destroy",function() {
            for (var item in me.GoogleEarthLoaded_EventListeners[scope.$id]) {
                me.GoogleEarthLoaded_EventListeners[scope.$id][item]();                    
            }
        }); 
        // console.log($rootScope.$$boundaryLeftClick_EventListeners);
    };
    
    service.clearPlacemarks = function()
    {
        ge = service.ge;
        var features = ge.getFeatures(); 
        while (features.getFirstChild()) { 
            features.removeChild(features.getFirstChild()); 
        } 
    };
    service.data_breadcrumb_cache = [];
    service.updateBreadcrumb = function ( data_breadcrumb_cache)
    {
        service.data_breadcrumb_cache = data_breadcrumb_cache;
    };
    
    return service;
}]);  

rutherApp.factory('googleEarthService', ['$rootScope',  'rutherGoogleMapService', 'rutherGoogleEarthService', function($rootScope,  rutherGoogleMapService, rutherGoogleEarthService) {
    var service = {};
    service.boundary_factory = new BoundaryFactory();
    service.facility_factory = new FacilityFactory();

    
    
    service.data_breadcrumb_cache = [];
    service.init = function ()
    {
        // google.load("earth", "1", {"callback" : service.initGE});
        google.load("earth", "1",{"callback" : rutherGoogleMapService.initGMaps} );
        
    }
    
    google.setOnLoadCallback(service.init);
    
    service.updateKPI = function ( kpi_type, kpi_values )
    {

        var data = {}
        data.kpi_type = kpi_type;
        data.kpi_values = kpi_values;
        if (service.view == 0)
            rutherGoogleEarthService.updateKPIValue(data);
        else
            rutherGoogleMapService.updateKPIValue(data);
        service.kpi_data = data;
    };
    
    service.addDblRightClickEventListener = function (scope, callbackName) {  rutherGoogleEarthService.addDblRightClickEventListener (scope, callbackName);  rutherGoogleMapService.addDblRightClickEventListener (scope, callbackName); };
    
    service.addBoundaryDoubleLeftClickEventListener = function (scope, callbackName) { rutherGoogleEarthService.addBoundaryDoubleLeftClickEventListener ( scope, callbackName); rutherGoogleMapService.addBoundaryDoubleLeftClickEventListener ( scope, callbackName); };

    service.addFacilityLeftClickEventListener = function (scope, callbackName) {  rutherGoogleEarthService.addFacilityLeftClickEventListener(scope, callbackName); rutherGoogleMapService.addFacilityLeftClickEventListener(scope, callbackName);  };    
    
    service.addBoundaryLeftClickEventListener = function (scope, callbackName) {   rutherGoogleEarthService.addBoundaryLeftClickEventListener(scope, callbackName ); rutherGoogleMapService.addBoundaryLeftClickEventListener(scope, callbackName ); };
    
    
    service.googleEarthLoaded_EventHandler =  function ()
    {

        if (service.data_breadcrumb_cache.length > 0)
        {
            var data = service.data_breadcrumb_cache[service.data_breadcrumb_cache.length-1];
            service.processKPIMapData( data, true );
            if (data.boundaries)
                service.geo_sv.updateKPIValue(service.kpi_data);
        }
    };
    $rootScope.$on('GoogleEarthLoaded_Event', service.googleEarthLoaded_EventHandler);
    
    
    service.zoomOutToPreviousBreadcrumb = function ()
    {

        if (service.data_breadcrumb_cache.length > 1)
        {   
            var data = service.data_breadcrumb_cache[service.data_breadcrumb_cache.length - 2];
                        
            service.processKPIMapData(data);

            service.popBreadcrumb(); service.popBreadcrumb();

            return data;
        }
        
        return null;
    };
    
    service.view = 1;
    service.geo_sv = rutherGoogleMapService;
    
    service.switchToGoogleEarth = function ()
    {
        var tmp = service.geo_sv.getCurrentView();
        if ( service.view != 0 )
        {
            service.view = 0;
            $('#map3d').empty();
            
            var init_view = {};
            zoom = tmp[0];

            range = Math.exp(( 26-zoom ) * Math.log(2.1)); 

            init_view.range = range;
            init_view.latitude = tmp[1];
            init_view.longitude = tmp[2];
            
            rutherGoogleEarthService.initView = init_view;
            rutherGoogleEarthService.initGE(zoom, tmp[1], tmp[2]);
            service.geo_sv = rutherGoogleEarthService;          
        }
    }
    
    service.switchToGoogleMap = function ( map_type_id )
    {
        var tmp = service.geo_sv.getCurrentView();
        if (service.view != 1)
        {
            range = tmp[0];
            zoom = Math.round(26-(Math.log(range)/Math.log(2.1)));
            
            service.view = 1;
            $('#map3d').empty();

            var init_view = {};
            
            init_view.zoom = zoom;
            init_view.latitude = tmp[1];
            init_view.longitude = tmp[2];

            rutherGoogleMapService.initView = init_view;
            rutherGoogleMapService.initGMaps(map_type_id);
            service.geo_sv = rutherGoogleMapService;

            if (service.data_breadcrumb_cache.length > 0)
            {
                var data = service.data_breadcrumb_cache[service.data_breadcrumb_cache.length-1];
                service.processKPIMapData( data, true );
                if (data.boundaries)
                    service.geo_sv.updateKPIValue(service.kpi_data);
            }
        }
        else
        {
            rutherGoogleMapService.changeMapTypeID (map_type_id);
        }
    }

    service.processKPIMapData = function ( data, do_not_add )
    {
        service.boundary_factory.clear();
        service.facility_factory.clear();

        var geo_sv = null;
        
        if (service.view == 0)
            geo_sv = rutherGoogleEarthService;
        else
            geo_sv = rutherGoogleMapService;
        
        geo_sv.clearPlacemarks();
        if ('boundaries' in data){
            var boundaries = data['boundaries'];

            for (var i=0; i<boundaries.length; i++)
                service.boundary_factory.createBoundary(boundaries[i]); 

            
            service.boundary_factory.visit(geo_sv);
  
        } else if ('outlets' in data){

            var outlets = data['outlets'];
            
            for (var i=0; i<outlets.length; i++){
                service.facility_factory.createFacility(outlets[i]); 
            }
            service.facility_factory.visit(geo_sv);
        }
        
        if (do_not_add == null)
            service.pushBreadcrumb(data);
    };
    

    service.pushBreadcrumb = function ( data )
    {
        service.data_breadcrumb_cache.push(data);
        rutherGoogleMapService.updateBreadcrumb(service.data_breadcrumb_cache);
        rutherGoogleEarthService.updateBreadcrumb(service.data_breadcrumb_cache);
    };
    
    service.clearBreadcrumbCache = function()
    {
        service.data_breadcrumb_cache = [];
        rutherGoogleMapService.updateBreadcrumb(service.data_breadcrumb_cache);
        rutherGoogleEarthService.updateBreadcrumb(service.data_breadcrumb_cache);
    };
    
    service.popBreadcrumb = function ()
    {
        service.data_breadcrumb_cache.pop();
        rutherGoogleMapService.updateBreadcrumb(service.data_breadcrumb_cache);
        rutherGoogleEarthService.updateBreadcrumb(service.data_breadcrumb_cache);
    };
    return service;
        
}]);
