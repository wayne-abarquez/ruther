// google.load("earth", "1");
// google.load("maps", "3");
// google.load("maps", "2");
$(document).ready(function(){
    // Set up data breadcrumb cache
    window.data_breadcrumb_cache = [];

    // Set up balloon slot list
    window.MAX_SLOTS_COLUMN = 5;
    window.balloons = [];

    // Set up balloon delete order
    window.balloons_delete_order = [];

    // Set up height of map3d object
    $('#map3d').height($(document).height()-(42));  // 42px is the height of the navbar


    //$('#dp1').datepicker({
    //
    //});

    // Accordion helper functions
    setTimeout(function(){
        // Auto show dataTable contents of .accordion-body to speed up rendering
        $('.accordion-body').on('shown', function(e){
            $('.dataTables_scroll .dataTables_scrollBody tr:nth-child(n+10)', this).show();
        });

        $('.accordion-body').on('show hide', function(e){
            e.stopPropagation();

            // Set up icon toggling on accordions
            $('i', $(this).prev()).toggleClass('icon-chevron-right icon-chevron-down', 200);

            // Auto hide dataTable contents of .accordion-body to speed up rendering
            if (e.type = 'hide'){
                $('.dataTables_scroll .dataTables_scrollBody tr:nth-child(n+10)', this).hide();
            }
        });

        // Hide 10th row onwards of dataTables initially
        $('.dataTables_scroll .dataTables_scrollBody tr:nth-child(n+10)', '.sidebar-nav').hide();
    }, 1000);   // Chevron toggling does not work properly if you do this on document ready immediately

    // close button event on balloon info
    $('body').on('click', '.balloon_close_button', function(e){
        var target = $(this).closest('.balloon_iframe_wrapper');
        if (!target[0].moved){
            window.balloons.splice(target[0].slot_num, 1);   // Delete element from balloons array in place
            rearrange_balloons($('.balloon_iframe_wrapper:not(.ui-draggable)'));    // The original element that we clone
        }

        // Remove balloon name from balloons_delete_order array
        window.balloons_delete_order.splice(window.balloons_delete_order.indexOf(target[0].name), 1);

        target.remove();

        e.preventDefault();
    });

    // escape key event handler
    $(document).keyup(function(e){
        if (e.keyCode == 27){   // esc
            console.log('esc!');
            delete_latest_balloon();
        }
    });

    // Margin auto set on balloon
    balloonPopupIframeMargin();
    $(window).resize(function(){
        balloonPopupIframeMargin();
    });

    // Left panel control logic
    $('.left_panel_control').hover(function(){
        $(this).toggleClass('label-warning');
    });

    $('.left_panel_control').click(function(){
        $('#sidebar-container').toggle();
        $('#left_panel_open_control_container').toggle();
    });

    // Reset tabs on modal on modal close
    /*
    $('#detailed-view-modal').on('hidden', function(){
        $('#detail-modal-Tab a:first').tab('show');
        $('#myTabContent .tab-pane.active').removeClass('active');
        $('#myTabContent .tab-pane:first').addClass('active in');
    });
    */

    // Set the max-height of modal-body
    $('#detailed-view-modal').on('shown', function(){
        //$('#detailed-view-modal .modal-body').attr('style', 'max-height:' + ($(window).height()-300).toString() + 'px!important; overflow-y: auto;');
        $('#myTabContent').attr('style', 'max-height:' + ($(window).height()-300).toString() + 'px!important; overflow-y: auto;');
    });
});

function delete_latest_balloon(){
    var to_delete = window.balloons_delete_order[window.balloons_delete_order.length - 1];
    var balloons = $('.balloon_iframe_wrapper.ui-draggable');
    
    for (var i in balloons){
        if (balloons[i].name == to_delete){
            $(balloons[i]).find('.balloon_close_button').trigger('click');
            break;
        }
    }
}

function move_balloon_to_slot(slot_num, orig, target){
    // 39 is hardcoded offset to see the headers of the balloon
    // 290 is hardcoded width of iframe
    slot_top = orig.offset().top + (slot_num%window.MAX_SLOTS_COLUMN) * 39;
    slot_left = orig.offset().left - ((slot_num/window.MAX_SLOTS_COLUMN)>>0) * 290; 

    target.offset({top: slot_top, left: slot_left});
}

function rearrange_balloons(orig){
    for (var i in window.balloons){
        i = parseInt(i);
        if (window.balloons[i][0].slot_num != i){
            console.log('Rearrange!');
            move_balloon_to_slot(i, orig, window.balloons[i]);
            window.balloons[i][0].slot_num = i;
        }
    }
}

function gen_uuid(){
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {var r = Math.random()*16|0,v=c=='x'?r:r&0x3|0x8;return v.toString(16);});
}

function datepicker_click(input_target, date_type){
    $('#datepicker_spacer').show();
    $('#'+input_target)
        .datepicker(date_type)
        .datepicker('show')
        .on('hide', function(){
            $('#datepicker_spacer').hide();
        })
        .on('changeDate', function(ev){
            $('#'+input_target).datepicker('hide');
        });
}

function balloonPopupIframeMargin(){
    $('#balloon_popup_iframe').css('margin-left', $(window).width() - $('#balloon_popup_polygons').width() - 40);
}

function resetFilters(){
    // Clear boundaries
    $('.boundaries-filter-list input:checkbox:checked').trigger('click');
    // Clear products
    $('input:checkbox:checked', '#sidebar-container').trigger('click'); 
    // Clear timeframe
    angular.element($('#dp1')).scope().timeframe_update();  // This is not the correct way to do this!
    $('#dp1').val('');
}

function firstLoadFilters(){
    // Load first top level boundary
    $('.boundaries-filter-list input:checkbox:enabled:first').trigger('click');
    // Load first top level product
    $('input:checkbox:enabled:first', '#sidebar_panel_filter_products').trigger('click');
    // Load October 2015 date, where data is available
    $('#dp1').datepicker('show');
    $('#dp1').val('10/2015');
    datepicker_click('dp1', 'setViewLimitMonth');
    $('#dp1').trigger('changeDate');
    $('#dp1').datepicker('hide');
    // Submit
    $('#btn_filterOK').trigger('click');
}

// $(document).ready(function(){
    // // Set up data breadcrumb cache
    // window.data_breadcrumb_cache = [];

    // // Set up height of map3d object
    // $('#map3d').height($(document).height()-(42));  // 42px is the height of the navbar

    // // Set up icon toggling on accordions
    // setTimeout(function(){
        // $('.accordion-body').on('show hide', function(e){
            // e.stopPropagation();
            // $('i', $(this).prev()).toggleClass('icon-chevron-right icon-chevron-down', 200);
        // });
    // }, 1000);   // Chevron toggling does not work properly if you do this on document ready immediately

    // // btnFilterOk_HookEvents();
    // $('#balloon_close_button').on('click', function(e){
        // $('#balloon_popup_polygons').hide();
    // });

    // // Margin auto set on balloon
    // balloonPopupIframeMargin();
    // $(window).resize(function(){
        // balloonPopupIframeMargin();
    // });

    // // Left panel control logic
    // $('.left_panel_control').hover(function(){
        // $(this).toggleClass('label-warning');
    // });

    // $('.left_panel_control').click(function(){
        // $('#sidebar-container').toggle();
        // $('#left_panel_open_control_container').toggle();
    // });
    
    // $('#balloon_popup_iframe').draggable();

// });

// // To get dataTables working nicely with bootstrap
// $.extend($.fn.dataTableExt.oStdClasses, {
    // 'sWrapper': 'dataTables_wrapper form-inline'
// });

// /* Create an array with the values of all the checkboxes in a column */
// $.fn.dataTableExt.afnSortData['dom-checkbox'] = function  ( oSettings, iColumn ){
    // return $.map( oSettings.oApi._fnGetTrNodes(oSettings), function (tr, i) {
        // return $('td:eq('+iColumn+') input', tr).prop('checked') ? '0' : '1';
    // } );
// }

// function datepicker_click(input_target, date_type){
    // $('#datepicker_spacer').show(); 
    // $('#'+input_target)
        // .datepicker(date_type)
        // .datepicker('show')
        // .on('hide', function(){
            // $('#datepicker_spacer').hide();
        // })
        // .on('changeDate', function(){
            // $('#'+input_target).datepicker('hide');
        // });
// }

// function balloonPopupIframeMargin(){
    // $('#balloon_popup_iframe').css('margin-left', $(window).width() - $('#balloon_popup_polygons').width() - 40);
// }


// function resetFilters(){
    // $('input:checkbox:checked', '#sidebar-container').trigger('click'); 
    // angular.element($('#dp1')).scope().timeframe_update();  // This is not the correct way to do this!
    // $('#dp1').val('');
// }

