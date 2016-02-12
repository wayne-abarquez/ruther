function DrawPolylinesControl( map, div)
{
    var controlDiv = div;
    var control = this;
    // control.ctl_ = ctl
	control.map = map;
    controlDiv.style.padding = '5px';
	
    var drawPolyUI = document.createElement('div');

    drawPolyUI.title = 'Draw Polylines';
    controlDiv.appendChild(drawPolyUI);
	drawPolyUI.style.cursor = 'pointer';
    var drawPolyText = document.createElement('div');
    drawPolyText.innerHTML = 'Draw Polylines';
    drawPolyUI.appendChild(drawPolyText);

    google.maps.event.addDomListener(drawPolyUI, 'click', function()
        {
             control.register_MapClick_EventHandler();
        }
    );
}

DrawPolylinesControl.prototype.register_MapClick_EventHandler = function ()
{
	console.log('DrawPolyLinesControl: Clearing any listener to Map click event');
    ctl = this;
    google.maps.event.clearListeners(ctl.map, 'click');
	console.log("DrawPolyLinesControl: Creating new Polyline objects...");
    var poly = new google.maps.Polyline({StrokeColor: "#0000FF", StrokeOpacity: 1.0, StrokeWeight: 3});
    poly.setMap(ctl.map);
	console.log('DrawPolyLinesControl: Adding listeer to Map click event');
    google.maps.event.addListener(ctl.map,
        'click',
        function(event){
            var path = poly.getPath()
			path.push(event.latLng);
      
        });

    ctl.poly = poly;
};

DrawPolylinesControl.prototype.polyControlDeactivate = function ()
{
    this.poly = null;
    this.unregisterMapClickEventHandler();
    this.registerMapDefaultClickEventHandler();
};

function PlaceMarkerControl(map, div)
{
    var controlDiv = div;
    var control = this;
    // control.ctl_ = ctl
    control.map = map;

    controlDiv.style.padding = '5px';

    var placeMarkerUI = document.createElement('div');
	placeMarkerUI.style.cursor = 'pointer';
    placeMarkerUI.title = 'Place Marker';
    controlDiv.appendChild(placeMarkerUI);

    var placeMarkerText = document.createElement('div');
    placeMarkerText.innerHTML = 'Place Marker';
    placeMarkerUI.appendChild(placeMarkerText);

    google.maps.event.addDomListener(placeMarkerUI, 'click', function()
        {
            control.register_MapClick_EventHandler();
        }
    );
}

PlaceMarkerControl.prototype.register_MapClick_EventHandler = function()
{
    ctl = this;
	google.maps.event.clearListeners(ctl.map, 'click');
	console.log('PlaceMarkerControl: Adding listener to Map Click event')
    google.maps.event.addListener(ctl.map, 'click', function (event) {
        var marker = new google.maps.Marker({
            position: event.latLng,
            map: ctl.map,
        });
        window.setTimeout(function() {
            ctl.map.panTo(marker.getPosition()); }, 1500);

        google.maps.event.addListener(marker, 'rightclick', function(event){
            marker.setMap(null);
        });
    } );
}
