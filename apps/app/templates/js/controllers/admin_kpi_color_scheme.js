rutherApp.controller('rutherGlobalKPIColorSchemeCtrl', ['$scope', '$http', function ($scope, $http){	
    $scope.color_schemes = {};
    $scope.color_schemes_ordered = [];
    $scope.edit_scheme_id = null;
    $scope.linear_color_map_data = Array(140);

    $scope.refreshList = function(){
        console.log('Refreshing List...');
        $http.get('getKPIColorScheme')
            .success(function(data, status){
                // Table will display color schemes in order lowest to highest bounds
                $scope.color_schemes_ordered = data['Data'];

                // Need a dictionary for editing
                for (var i = 0; i < $scope.color_schemes_ordered.length; i++){
                    $scope.color_schemes[$scope.color_schemes_ordered[i].id] = $scope.color_schemes_ordered[i];
                }

                // Create linear color map
                // Apply default to all first
                for (var i = 0; i < 140; i++){
                    $scope.linear_color_map_data[i] = $scope.color_schemes[1]['rgb'];
                }

                // Apply color schemes
                var offset = 20;
                for (var i = 1; i < $scope.color_schemes_ordered.length; i++){
                    var curr_scheme = $scope.color_schemes_ordered[i];
                    for (var j = curr_scheme.lowerbound; j < curr_scheme.upperbound; j++){
                        $scope.linear_color_map_data[offset + j] = curr_scheme.rgb;
                    }
                }
            }).error(function(data, status){
            });
    }

    $scope.linear_map_style = function(n){
        return {'background-color': 'rgb(' + n + ')'}
    }

    $scope.delete_scheme_id = function(todelete){
        var yn = confirm('Are you sure you want to delete this color scheme?')
        if (yn == true){
            var data = {
                'id': todelete,
            }

            $http({
                method: 'POST',
                url: '/deleteKPIColorScheme/', 
                data: $.param(data),
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            }).success(function(data, status){
                if (data['Data'] == 'OK'){  // Success
                    $scope.refreshList();
                } else {    // Error somewhere
                }
            }).error(function(data, status){
            });
        }
    }

    $scope.add_new_color_scheme = function(){
        var data = {
            'lowerbound': $scope.to_add_lowerbound,
            'upperbound': $scope.to_add_upperbound,
            'rgb': $('#to_add_rgb').val(),
        }

        $http({
            method: 'POST',
            url: '/addKPIColorScheme/', 
            data: $.param(data),
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        }).success(function(data, status){
            if (data['Data'] == 'OK'){  // Success
                $scope.refreshList();
                $('#addModal .close').trigger('click');
            } else {    // Error somewhere
            }
        }).error(function(data, status){
        });
    }

    $scope.init_add_modal = function(){
        $scope.to_add_lowerbound = 0;
        $scope.to_add_upperbound = 100;

        // Reset rgb value in input and reinitialize the color icon
        $('#add-colorpicker-control').colorpicker('setValue', 'rgb(0,0,0)');
        $('#add-colorpicker-control').colorpicker('destroy');
        $('#add-colorpicker-control').colorpicker();
    }

    $scope.update_edit_scheme_id = function(toedit){
        $scope.edit_scheme_id = toedit;
        $scope.to_edit_lowerbound = $scope.color_schemes[toedit].lowerbound;
        $scope.to_edit_upperbound = $scope.color_schemes[toedit].upperbound;

        // Reset rgb value in input and reinitialize the color icon
        $('#edit-colorpicker-control').colorpicker('setValue', 'rgb(' + $scope.color_schemes[$scope.edit_scheme_id].rgb  + ')');
        $('#edit-colorpicker-control').colorpicker('destroy');
        $('#edit-colorpicker-control').colorpicker();
    }

    $scope.edit_color_scheme = function(){
        // Check for correctness of bounds - do on front end or backend?
        // Submit
        var data = {
            'id': $scope.edit_scheme_id,
            'lowerbound': $scope.to_edit_lowerbound,
            'upperbound': $scope.to_edit_upperbound,
            'rgb': $('#to_edit_rgb').val(),
        }

        $http({
            method: 'POST',
            url: '/editKPIColorScheme/' + $scope.edit_scheme_id + '/', 
            data: $.param(data),
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        }).success(function(data, status){
            if (data['Data'] == 'OK'){  // Success
                $scope.refreshList();
                $('#editModal .close').trigger('click');
            } else {    // Error somewhere
            }
        }).error(function(data, status){
        });

    }

    // Init
    $scope.refreshList();
    window.x = $scope;
}]);
