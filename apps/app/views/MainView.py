from flask import render_template, flash, redirect, session, url_for, request, g, jsonify,make_response
from flask.ext.login import login_user, logout_user, current_user, login_required, fresh_login_required
from functools import update_wrapper
import pprint
from app import app 
import config
from app.models import *
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import os, simplejson, time
import re
import glob
import HTMLParser
from wrappers.audit_logs import log_access
from sqlalchemy import *
log = app.logger


REL_PATH_TO_KML = 'samples/Provinces.kml'
ABS_PATH_TO_KML = os.path.join(config.basedir, '..', REL_PATH_TO_KML)
DEFAULT_KPI_RGB = '0,0,0,0.5'
DEFAULT_KPI_RGB_NOALPHA = '0,0,0'

# def nocache(f):
    # def new_func(*args, **kwargs):
        # resp = make_response(f(*args, **kwargs))
        # resp.cache_control.no_cache = True
        # return resp
    # return update_wrapper(new_func, f)

# def timeit(f):
    # def decorated_function(*args, **kwargs):
        # start = time.time()
        # ret = f(*args, **kwargs)
        # end = time.time()
        # app.logger.info('Time taken to process %s: %0.2f s', f.__name__, end-start)
        # return ret
    # return decorated_function


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
# @nocache
@log_access
def index():
    # log.debug(g.user)
    return render_template('/index.html', user = g.user)


@app.route('/getFilterProductsHierarchy', methods=['GET'])
@login_required
def getFilterProductsHierarchy():
    return jsonify({
        'products': g.user.role_permission.getProductFilterHierarchy(),
    })

@app.route('/getFilterBoundariesHierarchy', methods=['GET'])
@login_required
def getFilterBoundariesHierarchy():
    return jsonify ( g.user.role_permission.getBoundaryFilterHierarchy() )    

@app.route('/BoundaryLevels', methods=['GET'])
@login_required
def BoundaryLevels():
    b = { obj.id : obj.description for obj in BoundaryLevelDesc.query.all() }
    b['lowestBoundaryLevel'] = BoundaryLevelDesc.query.order_by(BoundaryLevelDesc.id.desc())[0].id
    
    return jsonify({
        'ErrorCode': 'OK',
        'ErrorMessage': 'OK', 
        'Data': b ,
        'RequestParams' : ''
    })

@app.route('/Boundaries', methods=['GET'])
@login_required
def Boundaries():
    return jsonify({
        'ErrorCode': 'OK',
        'ErrorMessage': 'OK', 
        'Data': { obj.id : obj.name for obj in Boundary.query.all() } ,
        'RequestParams' : ''
    })

@app.route('/Facilities', methods=['GET'])
@login_required
def Facilities():
    return jsonify({
        'ErrorCode': 'OK',
        'ErrorMessage': 'OK', 
        'Data': { obj.id : obj.name for obj in Facility.query.filter_by(facility_type_id=config.STORE_TYPE_ID).all() } ,
        'RequestParams' : ''
    })

@app.route('/FacilityTypes', methods=['GET'])
@login_required
def FacilityTypes():
    return jsonify({
        'ErrorCode': 'OK',
        'ErrorMessage': 'OK', 
        'Data': { obj.id : obj.name for obj in FacilityType.query.all() } ,
        'RequestParams' : ''
    })
    
@app.route('/Products', methods=['GET'])
@login_required
def Products():
    return jsonify({
        'ErrorCode': 'OK',
        'ErrorMessage': 'OK', 
        'Data': { obj.id : obj.name for obj in Product.query.all() } ,
        'RequestParams' : ''
    })


@app.route('/ProductGroups', methods=['GET'])
@login_required
def ProductGroups():
    return jsonify({
        'ErrorCode': 'OK',
        'ErrorMessage': 'OK', 
        'Data': { obj.id : obj.description for obj in ProductGroup.query.all() } ,
        'RequestParams' : ''
    })


@app.route('/getKPITypes', methods=['GET'])
@login_required
def getKPITypes(): 
    return jsonify({
        'ErrorCode': 'OK',
        'ErrorMessage': 'OK', 
        'Data': {'KPITypes' : [{'id' : obj.id, 'name' : obj.name } for obj in KPIType.query.all() ]} ,
        'RequestParams' : ''
    })
    
# this is most definitely not the best way to do this
# the best way is to add another column on OutletType that refers to the path of the custom outlet type icon.
# but this is the easiest way to do it for the preview demo. Need to redo after the preview demo.
def getSmartfrenOutletIcon(outlet_type):
    
    if outlet_type == 'premium':
        return '/resources/smartfren/outlet_icons/diamond_icon_25.png'
    if outlet_type == 'regular':
        return '/resources/smartfren/outlet_icons/oval_icon_25.png'
    if outlet_type == 'star':
        return '/resources/smartfren/outlet_icons/star_icon_25.png'        
    if outlet_type == 'smile':
        return '/resources/smartfren/outlet_icons/happy_icon_25.png'
    if outlet_type == 'smartfren gadget outlet':
        return '/resources/smartfren/outlet_icons/gadget_icon_25.png'
        
@app.route('/kpimapdata/', methods=['GET'])
@login_required
@log_access
def kpimapdata():
    start = time.time()
    boundary_filter_type = request.args.get('boundary_filter_type', '')
    if boundary_filter_type == 'boundary_level':
        b_id = int(request.args.get('boundary_filter_id',0))
    else:
        b_id = [ int(obj) for obj in request.args.get('boundary_filter_id','').split(',') ] if request.args.get('boundary_filter_id','') else []

    # Define variables
    #icon_schema = FacilitySchema.query.filter_by(column_name = 'icon').one()
    base_level = BoundaryLevelDesc.query.order_by(BoundaryLevelDesc.id.desc()).limit(1).first()

    # Determine if user wants a poly or a point data set
    if boundary_filter_type == 'boundary_level' and b_id == base_level.id: # User wants stores
        return_data = {'outlets': []}
        # stores = Facility.query.filter_by(facility_type_id=config.STORE_TYPE_ID).all()
        q = Facility.query.outerjoin(FacilityOutletTypeMapping, Facility.id == FacilityOutletTypeMapping.id).outerjoin(OutletType, FacilityOutletTypeMapping.outlettype_id == OutletType.id).add_entity ( OutletType )
        stores = q.filter_by(facility_type_id=config.STORE_TYPE_ID).all()
        
        for store, outlet_type in stores:
            # icon_schema = getSmartfrenOutletIcon(outlet_type.maintype)
            return_data['outlets'].append(get_point_data(store, outlet_type.maintype, b_id)) 

    elif boundary_filter_type == 'facility':
        return_data = {'outlets': []}
        q = Facility.query.outerjoin(FacilityOutletTypeMapping, Facility.id == FacilityOutletTypeMapping.id).outerjoin(OutletType, FacilityOutletTypeMapping.outlettype_id == OutletType.id).add_entity ( OutletType )
        stores = q.filter(Facility.id.in_(b_id))
       
        #stores = [Facility.query.get(outlet_id) for outlet_id in b_id]

        for store, outlet_type in stores:
            # icon_schema = getSmartfrenOutletIcon(outlet_type.maintype)
            return_data['outlets'].append(get_point_data(store, outlet_type.maintype, b_id)) 

    elif boundary_filter_type == 'boundary_level':  
        return_data = {'boundaries': []}

        boundaries = Boundary.query.filter_by(level_id=b_id).all()
        for boundary in boundaries:
            return_data['boundaries'].append(get_polygon_data(boundary, base_level))
    else:
        return_data = {'boundaries': []}
        boundaries = [Boundary.query.get(boundary_id) for boundary_id in b_id]

        for boundary in boundaries:
            return_data['boundaries'].append(get_polygon_data(boundary, base_level)) 
    end = time.time()
    
    log.info('time taken: %0.2f', end- start)
    
    return jsonify({
        'ErrorCode': 'OK',
        'ErrorMessage': 'OK', 
        'Data': return_data ,
        'RequestParams' : {'boundary_filter_type' : boundary_filter_type, 'boundary_filter_id' : b_id }
    })
    
def get_polygon_data(boundary, base_level):
    children_level = boundary.level_id + 1
   
    return {
        'id': boundary.id,
        'parent_id': boundary.parent_id,
        'name': boundary.name,
        'level': boundary.level_id,
        'children_level': children_level,
        'children': [i.id for i in Boundary.query.filter_by(parent_id=boundary.id).all()] if children_level != base_level.id else [i.id for i in Facility.query.filter_by(boundary_id=boundary.id).all()],
        'type_name': 'boundary',
        'coords': [polys.encoded_poly for polys in BoundaryPolygons.query.filter_by(boundary=boundary).all()],
    }

def get_point_data(store, outlet_type, boundary_level_id):
    # icon_query = FacilityCustomData.query.filter_by(facility=store, schema=icon_schema)

    return {
        'id': store.id,
        'name': store.name,
        'level': boundary_level_id,
        'type_name' : 'store',
        'icon': {
            'href': getSmartfrenOutletIcon(outlet_type), #'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=?|ffffff|000000' if not icon_query.count() else HTMLParser.HTMLParser().unescape(icon_query.one().data),
        },
        'coords': [store.geom.coords(db.session)[::-1]+[0]],
    }

@app.route('/getOutletSubtypeCountsPerBoundary/<int:boundary_id>/', methods=['GET'])
@login_required
def getOutletSubtypeCountsPerBoundary(boundary_id): 
    ret_data = {'ErrorCode': '000000', 'ErrorMessage': 'OK', 'RequestParams': {}, 'Data': None}

    boundary_product_month = '''
        WITH RECURSIVE nodes(id) AS (
            SELECT s1.id
            FROM boundaries s1 WHERE parent_id = %s
                UNION
            SELECT s2.id
            FROM boundaries s2, nodes s1 WHERE s2.parent_id = s1.id
        ) 
        SELECT
            ros1.id as subtype_id,
            ros1.subtype as subtype_desc,
            COALESCE(x.total_outlet_count, 0) AS total_outlet_count,
            COALESCE(x.total_activation, 0) AS total_activation
        FROM
            regular_outlet_subtypes ros1 
        LEFT JOIN (    
            SELECT
                ros.id AS subtype_id,
                SUM(s."outletCount") AS total_outlet_count,
                SUM(s.activation) AS total_activation
            FROM 
                boundary_product_monthly_subtype s
            LEFT JOIN
                regular_outlet_subtypes ros on s.regular_outlet_subtype_id = ros.id
            WHERE
                (s.boundary_id IN (SELECT * FROM nodes) OR s.boundary_id IN (%s))
            AND s.product_id in (%s)
            AND s.month = %s
            AND s.year = %s
            GROUP BY ros.id
        ) x on ros1.id = x.subtype_id
    '''
    boundary_product_year = '''
        WITH RECURSIVE nodes(id) AS (
            SELECT s1.id
            FROM boundaries s1 WHERE parent_id = %s
                UNION
            SELECT s2.id
            FROM boundaries s2, nodes s1 WHERE s2.parent_id = s1.id
        ) 
        SELECT
            ros1.id as subtype_id,
            ros1.subtype as subtype_desc,
            COALESCE(x.total_outlet_count, 0) AS total_outlet_count,
            COALESCE(x.total_activation, 0) AS total_activation
        FROM
            regular_outlet_subtypes ros1 
        LEFT JOIN (    
            SELECT
                ros.id AS subtype_id,
                SUM(s."outletCount") AS total_outlet_count,
                SUM(s.activation) AS total_activation
            FROM 
                boundary_product_yearly_subtype s
            LEFT JOIN
                regular_outlet_subtypes ros on s.regular_outlet_subtype_id = ros.id
            WHERE
                (s.boundary_id IN (SELECT * FROM nodes) OR s.boundary_id IN (%s))
            AND s.product_id in (%s)
            AND s.year = %s
            GROUP BY ros.id
        ) x on ros1.id = x.subtype_id
    '''
    boundary_product_day = '''
        WITH RECURSIVE nodes(id) AS (
            SELECT s1.id
            FROM boundaries s1 WHERE parent_id = %s
                UNION
            SELECT s2.id
            FROM boundaries s2, nodes s1 WHERE s2.parent_id = s1.id
        ) 
        SELECT
            ros1.id as subtype_id,
            ros1.subtype as subtype_desc,
            COALESCE(x.total_outlet_count, 0) AS total_outlet_count,
            COALESCE(x.total_activation, 0) AS total_activation
        FROM
            regular_outlet_subtypes ros1 
        LEFT JOIN (    
            SELECT
                ros.id AS subtype_id,
                SUM(s."outletCount") AS total_outlet_count,
                SUM(s.activation) AS total_activation
            FROM 
                boundary_product_daily_subtype s
            LEFT JOIN
                regular_outlet_subtypes ros on s.regular_outlet_subtype_id = ros.id
            WHERE
                (s.boundary_id IN (SELECT * FROM nodes) OR s.boundary_id IN (%s))
            AND s.product_id in (%s)
            AND s.date = '%s'
            GROUP BY ros.id
        ) x on ros1.id = x.subtype_id
    '''
    boundary_product_week = '''
        WITH RECURSIVE nodes(id) AS (
            SELECT s1.id
            FROM boundaries s1 WHERE parent_id = %s
                UNION
            SELECT s2.id
            FROM boundaries s2, nodes s1 WHERE s2.parent_id = s1.id
        ) 
        SELECT
            ros1.id as subtype_id,
            ros1.subtype as subtype_desc,
            COALESCE(x.total_outlet_count, 0) AS total_outlet_count,
            COALESCE(x.total_activation, 0) AS total_activation
        FROM
            regular_outlet_subtypes ros1 
        LEFT JOIN (    
            SELECT
                ros.id AS subtype_id,
                SUM(s."outletCount") AS total_outlet_count,
                SUM(s.activation) AS total_activation
            FROM 
                boundary_product_weekly_subtype s
            LEFT JOIN
                regular_outlet_subtypes ros on s.regular_outlet_subtype_id = ros.id
            WHERE
                (s.boundary_id IN (SELECT * FROM nodes) OR s.boundary_id IN (%s))
            AND s.product_id in (%s)
            AND s.start_week_date = '%s'
            GROUP BY ros.id
        ) x on ros1.id = x.subtype_id
    '''
    product_list = '''
        SELECT 
            product_id 
        FROM 
            productgroup_map 
        WHERE
            group_id IN (%s)
    '''
    # List of boundaries - actually, only one boundary at a time is permitted
    boundary_filter_type = request.args.get('boundary_filter_type', '')
    #b_id = [int(request.args.get('boundary_filter_id', 0))][0]
    b_id = request.args.get('boundary_filter_id', 0)

    # List of products/productgroups
    product_filter_type = request.args.get('product_filter_type', '')
    #p_id = [int(request.args.get('product_filter_id', 0))][0]
    p_id = request.args.get('product_filter_id', 0)

    # Timeframe
    selected_timeframe = request.args.get('timeframe')
    if selected_timeframe == 'month':
        timeframe = {'type': 'month', 'date_month': int(request.args.get('date_month')), 'date_year': int(request.args.get('date_year'))}
        if product_filter_type == 'product_group':
            p_ids = ','.join([str(i[0]) for i in db.engine.execute(product_list%(p_id))])
            M2C = boundary_product_month%(b_id, b_id, p_ids, timeframe['date_month'], timeframe['date_year'])
        else:
            M2C = boundary_product_month%(b_id, b_id, p_id, timeframe['date_month'], timeframe['date_year'])
    elif selected_timeframe == 'year':
        timeframe = {'type': 'year', 'date_year': int(request.args.get('date_year'))}
        if product_filter_type == 'product_group':
            p_ids = ','.join([str(i[0]) for i in db.engine.execute(product_list%(p_id))])
            M2C = boundary_product_year%(b_id, b_id, p_ids, timeframe['date_year'])
        else:
            M2C = boundary_product_year%(b_id, b_id, p_id, timeframe['date_year'])
    elif selected_timeframe == 'day':
        selected_date = [int(i) for i in request.args.get('date').split('-')]
        timeframe = {'type': 'day', 'date_day': int(selected_date[2]), 'date_month': int(selected_date[1]), 'date_year': int(selected_date[0])}
        selected_start = date(int(timeframe['date_year']), int(timeframe['date_month']), int(timeframe['date_day']))
        if product_filter_type == 'product_group':
            p_ids = ','.join([str(i[0]) for i in db.engine.execute(product_list%(p_id))])
            M2C = boundary_product_day%(b_id, b_id, p_ids, selected_start)
        else:
            M2C = boundary_product_day%(b_id, b_id, p_id, selected_start)
    elif selected_timeframe == 'week':
        timeframe = {'type': 'week', 'date_day': int(request.args.get('date_day')), 'date_month': int(request.args.get('date_month')), 'date_year': int(request.args.get('date_year'))}
        selected_start = date(int(request.args.get('date_year')), int(request.args.get('date_month')), int(request.args.get('date_day')))
        if product_filter_type == 'product_group':
            p_ids = ','.join([str(i[0]) for i in db.engine.execute(product_list%(p_id))])
            M2C = boundary_product_week%(b_id, b_id, p_ids, selected_start)
        else:
            M2C = boundary_product_week%(b_id, b_id, p_id, selected_start)

    subtype_count = {}
    rows = db.engine.execute(M2C)
    for row in rows:
        # subtype_id |  subtype_desc  | total_outlet_count | total_activation
        #------------+----------------+--------------------+------------------
        #          4 | silver         |                353 |             3057
        subtype_count[row[0]] = {
            'subtype_desc': '%s'%(row[1].title()),
            'total_outlet_count': row[2],
            'total_activation': row[3],
        }

    try:
        ret_data['Data'] = subtype_count
    except:
        ret_data['ErrorCode'] = '008000'
        ret_data['ErrorMessage'] = 'Error getting outletsubtype count for boundary.'
        
    return jsonify(ret_data)

@app.route('/getOutletTypeCountsPerBoundary/<int:boundary_id>/', methods=['GET'])
@login_required
def getOutletTypeCountsPerBoundary(boundary_id): 
    ret_data = {'ErrorCode': '000000', 'ErrorMessage': 'OK', 'RequestParams': {}, 'Data': None}

    boundary_product_month = '''
        WITH RECURSIVE nodes(id) AS (
            SELECT s1.id
            FROM boundaries s1 WHERE parent_id = %s
                UNION
            SELECT s2.id
            FROM boundaries s2, nodes s1 WHERE s2.parent_id = s1.id
        ) 
        SELECT
            ot1.id AS outlettype_id,
            ot1.maintype AS outlettype_desc,
            COALESCE(x.outlet_count, 0) AS outlettype_count,
            COALESCE(x.kpi_percent, 0) AS kpi_percent,
            COALESCE(x.actual_total, 0) AS actual_total,
            COALESCE(x.target_total, 0) AS target_total,
            COALESCE(gkcs.rgb, '%s') AS rgb
        FROM 
            outlettypes ot1
        LEFT JOIN (
            SELECT 
                ot.id AS id,
                COUNT(ot.id) AS outlet_count,
                AVG(s.kpi/s.data_point_count) AS kpi_percent,
                SUM(s.actual) AS actual_total,
                SUM(s.target) AS target_total
            FROM 
                outlettypes ot 
            INNER JOIN
                facility_outlettype_mapping fotm ON ot.id = fotm.outlettype_id
            INNER JOIN
                facilities f ON fotm.facility_id = f.id
            INNER JOIN
                sum_facility_product_month s ON s.facility_id = f.id
            WHERE 
                s.facility_id IN (
                    SELECT 
                        f.id
                    FROM 
                        facilities f 
                    WHERE
                        f.boundary_id IN (SELECT * FROM nodes) OR 
                        f.boundary_id IN (%s)
                    )
            AND kpi_type = 1
            AND product_id in (%s)
            AND date_month = %s
            AND date_year = %s
            GROUP BY ot.id
        ) x ON ot1.id = x.id
        LEFT JOIN
            global_kpi_color_scheme gkcs ON gkcs.lowerbound <= x.kpi_percent AND gkcs.upperbound > x.kpi_percent;
    '''
    boundary_product_year = '''
        WITH RECURSIVE nodes(id) AS (
            SELECT s1.id
            FROM boundaries s1 WHERE parent_id = %s
                UNION
            SELECT s2.id
            FROM boundaries s2, nodes s1 WHERE s2.parent_id = s1.id
        ) 
        SELECT
            ot1.id AS outlettype_id,
            ot1.maintype AS outlettype_desc,
            COALESCE(x.outlet_count, 0) AS outlettype_count,
            COALESCE(x.kpi_percent, 0) AS kpi_percent,
            COALESCE(x.actual_total, 0) AS actual_total,
            COALESCE(x.target_total, 0) AS target_total,
            COALESCE(gkcs.rgb, '%s') AS rgb
        FROM 
            outlettypes ot1
        LEFT JOIN (
            SELECT 
                ot.id AS id,
                COUNT(ot.id) AS outlet_count,
                AVG(s.kpi/s.data_point_count) AS kpi_percent,
                SUM(s.actual) AS actual_total,
                SUM(s.target) AS target_total
            FROM 
                outlettypes ot 
            INNER JOIN
                facility_outlettype_mapping fotm ON ot.id = fotm.outlettype_id
            INNER JOIN
                facilities f ON fotm.facility_id = f.id
            INNER JOIN
                sum_facility_product_year s ON s.facility_id = f.id
            WHERE 
                s.facility_id IN (
                    SELECT 
                        f.id
                    FROM 
                        facilities f 
                    WHERE
                        f.boundary_id IN (SELECT * FROM nodes) OR 
                        f.boundary_id IN (%s)
                    )
            AND kpi_type = 1
            AND product_id in (%s)
            AND date_year = %s
            GROUP BY ot.id
        ) x ON ot1.id = x.id
        LEFT JOIN
            global_kpi_color_scheme gkcs ON gkcs.lowerbound <= x.kpi_percent AND gkcs.upperbound > x.kpi_percent;
    '''
    boundary_product_day = '''
        WITH RECURSIVE nodes(id) AS (
            SELECT s1.id
            FROM boundaries s1 WHERE parent_id = %s
                UNION
            SELECT s2.id
            FROM boundaries s2, nodes s1 WHERE s2.parent_id = s1.id
        ) 
        SELECT
            ot1.id AS outlettype_id,
            ot1.maintype AS outlettype_desc,
            COALESCE(x.outlet_count, 0) AS outlettype_count,
            COALESCE(x.kpi_percent, 0) AS kpi_percent,
            COALESCE(x.actual_total, 0) AS actual_total,
            COALESCE(x.target_total, 0) AS target_total,
            COALESCE(gkcs.rgb, '%s') AS rgb
        FROM 
            outlettypes ot1
        LEFT JOIN (
            SELECT 
                ot.id AS id,
                COUNT(ot.id) AS outlet_count,
                AVG(s.kpi) AS kpi_percent,
                SUM(s.actual) AS actual_total,
                SUM(s.target) AS target_total
            FROM 
                outlettypes ot 
            INNER JOIN
                facility_outlettype_mapping fotm ON ot.id = fotm.outlettype_id
            INNER JOIN
                facilities f ON fotm.facility_id = f.id
            INNER JOIN
                kpi s ON s.facility_id = f.id
            WHERE 
                s.facility_id IN (
                    SELECT 
                        f.id
                    FROM 
                        facilities f 
                    WHERE
                        f.boundary_id IN (SELECT * FROM nodes) OR 
                        f.boundary_id IN (%s)
                    )
            AND kpi_type = 1
            AND product_id in (%s)
            AND date_day = %s
            AND date_month = %s
            AND date_year = %s
            GROUP BY ot.id
        ) x ON ot1.id = x.id
        LEFT JOIN
            global_kpi_color_scheme gkcs ON gkcs.lowerbound <= x.kpi_percent AND gkcs.upperbound > x.kpi_percent;
    '''
    boundary_product_week = '''
        WITH RECURSIVE nodes(id) AS (
            SELECT s1.id
            FROM boundaries s1 WHERE parent_id = %s
                UNION
            SELECT s2.id
            FROM boundaries s2, nodes s1 WHERE s2.parent_id = s1.id
        ) 
        SELECT
            ot1.id AS outlettype_id,
            ot1.maintype AS outlettype_desc,
            COALESCE(x.outlet_count, 0) AS outlettype_count,
            COALESCE(x.kpi_percent, 0) AS kpi_percent,
            COALESCE(x.actual_total, 0) AS actual_total,
            COALESCE(x.target_total, 0) AS target_total,
            COALESCE(gkcs.rgb, '%s') AS rgb
        FROM 
            outlettypes ot1
        LEFT JOIN (
            SELECT 
                ot.id AS id,
                COUNT(ot.id) AS outlet_count,
                AVG(s.kpi/s.data_point_count) AS kpi_percent,
                SUM(s.actual) AS actual_total,
                SUM(s.target) AS target_total
            FROM 
                outlettypes ot 
            INNER JOIN
                facility_outlettype_mapping fotm ON ot.id = fotm.outlettype_id
            INNER JOIN
                facilities f ON fotm.facility_id = f.id
            INNER JOIN
                sum_facility_product_week s ON s.facility_id = f.id
            WHERE 
                s.facility_id IN (
                    SELECT 
                        f.id
                    FROM 
                        facilities f 
                    WHERE
                        f.boundary_id IN (SELECT * FROM nodes) OR 
                        f.boundary_id IN (%s)
                    )
            AND kpi_type = 1
            AND product_id in (%s)
            AND date_start_of_week = '%s'
            GROUP BY ot.id
        ) x ON ot1.id = x.id
        LEFT JOIN
            global_kpi_color_scheme gkcs ON gkcs.lowerbound <= x.kpi_percent AND gkcs.upperbound > x.kpi_percent;
    '''
    boundary_productgroup_month = '''
        WITH RECURSIVE nodes(id) AS (
            SELECT s1.id
            FROM boundaries s1 WHERE parent_id = %s
                UNION
            SELECT s2.id
            FROM boundaries s2, nodes s1 WHERE s2.parent_id = s1.id
        ) 
        SELECT
            ot1.id AS outlettype_id,
            ot1.maintype AS outlettype_desc,
            COALESCE(x.outlet_count, 0) AS outlettype_count,
            COALESCE(x.kpi_percent, 0) AS kpi_percent,
            COALESCE(x.actual_total, 0) AS actual_total,
            COALESCE(x.target_total, 0) AS target_total,
            COALESCE(gkcs.rgb, '%s') AS rgb
        FROM 
            outlettypes ot1
        LEFT JOIN (
            SELECT 
                ot.id AS id,
                COUNT(ot.id) AS outlet_count,
                AVG(s.kpi/s.data_point_count) AS kpi_percent,
                SUM(s.actual) AS actual_total,
                SUM(s.target) AS target_total
            FROM 
                outlettypes ot 
            INNER JOIN
                facility_outlettype_mapping fotm ON ot.id = fotm.outlettype_id
            INNER JOIN
                facilities f ON fotm.facility_id = f.id
            INNER JOIN
                sum_facility_productgroup_month s ON s.facility_id = f.id
            WHERE 
                s.facility_id IN (
                    SELECT 
                        f.id
                    FROM 
                        facilities f 
                    WHERE
                        f.boundary_id IN (SELECT * FROM nodes) OR 
                        f.boundary_id IN (%s)
                    )
            AND kpi_type = 1
            AND product_group_id in (%s)
            AND date_month = %s
            AND date_year = %s
            GROUP BY ot.id
        ) x ON ot1.id = x.id
        LEFT JOIN
            global_kpi_color_scheme gkcs ON gkcs.lowerbound <= x.kpi_percent AND gkcs.upperbound > x.kpi_percent;
    '''
    boundary_productgroup_year = '''
        WITH RECURSIVE nodes(id) AS (
            SELECT s1.id
            FROM boundaries s1 WHERE parent_id = %s
                UNION
            SELECT s2.id
            FROM boundaries s2, nodes s1 WHERE s2.parent_id = s1.id
        ) 
        SELECT
            ot1.id AS outlettype_id,
            ot1.maintype AS outlettype_desc,
            COALESCE(x.outlet_count, 0) AS outlettype_count,
            COALESCE(x.kpi_percent, 0) AS kpi_percent,
            COALESCE(x.actual_total, 0) AS actual_total,
            COALESCE(x.target_total, 0) AS target_total,
            COALESCE(gkcs.rgb, '%s') AS rgb
        FROM 
            outlettypes ot1
        LEFT JOIN (
            SELECT 
                ot.id AS id,
                COUNT(ot.id) AS outlet_count,
                AVG(s.kpi/s.data_point_count) AS kpi_percent,
                SUM(s.actual) AS actual_total,
                SUM(s.target) AS target_total
            FROM 
                outlettypes ot 
            INNER JOIN
                facility_outlettype_mapping fotm ON ot.id = fotm.outlettype_id
            INNER JOIN
                facilities f ON fotm.facility_id = f.id
            INNER JOIN
                sum_facility_productgroup_year s ON s.facility_id = f.id
            WHERE 
                s.facility_id IN (
                    SELECT 
                        f.id
                    FROM 
                        facilities f 
                    WHERE
                        f.boundary_id IN (SELECT * FROM nodes) OR 
                        f.boundary_id IN (%s)
                    )
            AND kpi_type = 1
            AND product_group_id in (%s)
            AND date_year = %s
            GROUP BY ot.id
        ) x ON ot1.id = x.id
        LEFT JOIN
            global_kpi_color_scheme gkcs ON gkcs.lowerbound <= x.kpi_percent AND gkcs.upperbound > x.kpi_percent;
    '''
    boundary_productgroup_day = '''
        WITH RECURSIVE nodes(id) AS (
            SELECT s1.id
            FROM boundaries s1 WHERE parent_id = %s
                UNION
            SELECT s2.id
            FROM boundaries s2, nodes s1 WHERE s2.parent_id = s1.id
        ) 
        SELECT
            ot1.id AS outlettype_id,
            ot1.maintype AS outlettype_desc,
            COALESCE(x.outlet_count, 0) AS outlettype_count,
            COALESCE(x.kpi_percent, 0) AS kpi_percent,
            COALESCE(x.actual_total, 0) AS actual_total,
            COALESCE(x.target_total, 0) AS target_total,
            COALESCE(gkcs.rgb, '%s') AS rgb
        FROM 
            outlettypes ot1
        LEFT JOIN (
            SELECT 
                ot.id AS id,
                COUNT(ot.id) AS outlet_count,
                AVG(s.kpi/s.data_point_count) AS kpi_percent,
                SUM(s.actual) AS actual_total,
                SUM(s.target) AS target_total
            FROM 
                outlettypes ot 
            INNER JOIN
                facility_outlettype_mapping fotm ON ot.id = fotm.outlettype_id
            INNER JOIN
                facilities f ON fotm.facility_id = f.id
            INNER JOIN
                sum_facility_productgroup_day s ON s.facility_id = f.id
            WHERE 
                s.facility_id IN (
                    SELECT 
                        f.id
                    FROM 
                        facilities f 
                    WHERE
                        f.boundary_id IN (SELECT * FROM nodes) OR 
                        f.boundary_id IN (%s)
                    )
            AND kpi_type = 1
            AND product_group_id in (%s)
            AND date_day = %s
            AND date_month = %s
            AND date_year = %s
            GROUP BY ot.id
        ) x ON ot1.id = x.id
        LEFT JOIN
            global_kpi_color_scheme gkcs ON gkcs.lowerbound <= x.kpi_percent AND gkcs.upperbound > x.kpi_percent;
    '''
    boundary_productgroup_week = '''
        WITH RECURSIVE nodes(id) AS (
            SELECT s1.id
            FROM boundaries s1 WHERE parent_id = %s
                UNION
            SELECT s2.id
            FROM boundaries s2, nodes s1 WHERE s2.parent_id = s1.id
        ) 
        SELECT
            ot1.id AS outlettype_id,
            ot1.maintype AS outlettype_desc,
            COALESCE(x.outlet_count, 0) AS outlettype_count,
            COALESCE(x.kpi_percent, 0) AS kpi_percent,
            COALESCE(x.actual_total, 0) AS actual_total,
            COALESCE(x.target_total, 0) AS target_total,
            COALESCE(gkcs.rgb, '%s') AS rgb
        FROM 
            outlettypes ot1
        LEFT JOIN (
            SELECT 
                ot.id AS id,
                COUNT(ot.id) AS outlet_count,
                AVG(s.kpi/s.data_point_count) AS kpi_percent,
                SUM(s.actual) AS actual_total,
                SUM(s.target) AS target_total
            FROM 
                outlettypes ot 
            INNER JOIN
                facility_outlettype_mapping fotm ON ot.id = fotm.outlettype_id
            INNER JOIN
                facilities f ON fotm.facility_id = f.id
            INNER JOIN
                sum_facility_productgroup_week s ON s.facility_id = f.id
            WHERE 
                s.facility_id IN (
                    SELECT 
                        f.id
                    FROM 
                        facilities f 
                    WHERE
                        f.boundary_id IN (SELECT * FROM nodes) OR 
                        f.boundary_id IN (%s)
                    )
            AND kpi_type = 1
            AND product_group_id in (%s)
            AND date_start_of_week = '%s'
            GROUP BY ot.id
        ) x ON ot1.id = x.id
        LEFT JOIN
            global_kpi_color_scheme gkcs ON gkcs.lowerbound <= x.kpi_percent AND gkcs.upperbound > x.kpi_percent;
    '''

    # Internal functions
    #def recursive_get_child_facilities(parent_id):
    #    next_level_id = Boundary.query.get(parent_id).level_id + 1
    #    tmp = []
    #    if next_level_id == db.session.query(func.max(BoundaryLevelDesc.id))[0][0]:
    #        for store in list(Facility.query.filter_by(boundary_id = parent_id).order_by(Facility.id.asc()).values(Facility.id, Facility.name)):
    #            tmp.append({
    #                'id': store[0],
    #                'name': store[1],
    #            })
    #        return tmp
    #    else:
    #        boundary_list = list(Boundary.query.filter_by(level_id = next_level_id, parent_id = parent_id).values(Boundary.id))
    #        for boundary in boundary_list:
    #            tmp += recursive_get_child_facilities(boundary.id)
    #    return tmp
    # End Internal Functions

    #FOTM = FacilityOutletTypeMapping    # because the full model name is just too damn long
    #facilities_list = recursive_get_child_facilities(boundary_id)
    #facilities_count = {i.id: {'desc': '%s'%(i.maintype.title()), 'count':0} for i in OutletType.query.all()}

    #for facility in facilities_list:
    #    mapping = db.session.query(FOTM).filter(FOTM.facility_id == facility['id']).first()

    #    if mapping:
    #        facilities_count[mapping.outlettype.id]['count'] += 1
    #    
    #try:
    #    ret_data['Data'] = facilities_count
    #except:
    #    ret_data['ErrorCode'] = '006000'
    #    ret_data['ErrorMessage'] = 'Error getting outlettype count for boundary.'

    # List of boundaries - actually, only one boundary at a time is permitted
    boundary_filter_type = request.args.get('boundary_filter_type', '')
    #b_id = [int(request.args.get('boundary_filter_id', 0))][0]
    b_id = request.args.get('boundary_filter_id', 0)

    # List of products/productgroups
    product_filter_type = request.args.get('product_filter_type', '')
    #p_id = [int(request.args.get('product_filter_id', 0))][0]
    p_id = request.args.get('product_filter_id', 0)

    # Timeframe
    selected_timeframe = request.args.get('timeframe')
    if selected_timeframe == 'month':
        timeframe = {'type': 'month', 'date_month': int(request.args.get('date_month')), 'date_year': int(request.args.get('date_year'))}
        if product_filter_type == 'product_group':
            M2C = boundary_productgroup_month%(b_id, DEFAULT_KPI_RGB_NOALPHA, b_id, p_id, timeframe['date_month'], timeframe['date_year'])
        else:
            M2C = boundary_product_month%(b_id, DEFAULT_KPI_RGB_NOALPHA, b_id, p_id, timeframe['date_month'], timeframe['date_year'])
    elif selected_timeframe == 'year':
        timeframe = {'type': 'year', 'date_year': int(request.args.get('date_year'))}
        if product_filter_type == 'product_group':
            M2C = boundary_productgroup_year%(b_id, DEFAULT_KPI_RGB_NOALPHA, b_id, p_id, timeframe['date_year'])
        else:
            M2C = boundary_product_year%(b_id, DEFAULT_KPI_RGB_NOALPHA, b_id, p_id, timeframe['date_year'])
    elif selected_timeframe == 'day':
        selected_date = [int(i) for i in request.args.get('date').split('-')]
        timeframe = {'type': 'day', 'date_day': int(selected_date[2]), 'date_month': int(selected_date[1]), 'date_year': int(selected_date[0])}
        if product_filter_type == 'product_group':
            M2C = boundary_productgroup_day%(b_id, DEFAULT_KPI_RGB_NOALPHA, b_id, p_id, timeframe['date_day'], timeframe['date_month'], timeframe['date_year'])
        else:
            M2C = boundary_product_day%(b_id, DEFAULT_KPI_RGB_NOALPHA, b_id, p_id, timeframe['date_day'], timeframe['date_month'], timeframe['date_year'])
    elif selected_timeframe == 'week':
        timeframe = {'type': 'week', 'date_day': int(request.args.get('date_day')), 'date_month': int(request.args.get('date_month')), 'date_year': int(request.args.get('date_year'))}
        selected_start = date(int(request.args.get('date_year')), int(request.args.get('date_month')), int(request.args.get('date_day')))
        if product_filter_type == 'product_group':
            M2C = boundary_productgroup_week%(b_id, DEFAULT_KPI_RGB_NOALPHA, b_id, p_id, selected_start)
        else:
            M2C = boundary_product_week%(b_id, DEFAULT_KPI_RGB_NOALPHA, b_id, p_id, selected_start)

    #facilities_count = {i.id: {'desc': '%s'%(i.maintype.title()), 'count':0} for i in OutletType.query.all()}
    facilities_count = {}
    alltype_count = 0
    all_actual_total = 0
    all_kpi_percent = 0
    rows = db.engine.execute(M2C)
    for row in rows:
        # (2, u'star', 3L, 49.0138888888889, 357799.0, 359596.0)
        all_actual_total += row[4]
        all_kpi_percent += row[3]
        if row[4] > 0: 
            alltype_count += 1

        facilities_count[row[0]] = {
            'desc': '%s'%(row[1].title()),
            'count': row[2]/len(p_id.split(',')),
            'kpi_percent': row[3],
            'actual_total': row[4],
            'target_total': row[5],
            'rgb': 'rgba(%s,0.5)'%row[6]
        }

    try:
        ret_data['Data'] = {'outlets': facilities_count}
        all_kpi_percent /= alltype_count
        ret_data['Data']['all'] = {'actual_total': all_actual_total, 'kpi_percent': all_kpi_percent, 'rgb': 'rgba(%s,0.5)'%getKPIColorRaw(all_kpi_percent)}
    except:
        ret_data['ErrorCode'] = '006000'
        ret_data['ErrorMessage'] = 'Error getting outlettype count for boundary.'
        
    return jsonify(ret_data)
    
@app.route('/getFacilityOutletType/<int:facility_id>/', methods=['GET'])
@login_required
def getFacilityOutletType(facility_id): 
    FOTM = FacilityOutletTypeMapping    # because the full model name is just too damn long
    # timeframe - 2013, 201307, 20130707
    ret_data = {'ErrorCode': '000000', 'ErrorMessage': 'OK', 'RequestParams': {}, 'Data': None}

    mapping = FOTM.query.filter_by(facility_id = facility_id).first()

    try:
        maintype = mapping.outlettype.maintype
        ret_data['Data'] = '%s'%(maintype.title())
    except:
        ret_data['ErrorCode'] = '005000'
        ret_data['ErrorMessage'] = 'Error getting facility type.'
        
    return jsonify(ret_data)

@app.route('/getOwnerInformation/<int:facility_id>/', methods=['GET'])
@login_required
def getOwnerInformation(facility_id):
    ret_data = {'ErrorCode': '000000', 'ErrorMessage': 'OK', 'RequestParams': {}, 'Data': None}

    try:
        # Get list of files in the folder if it exists
        lof = glob.glob(config.basedir + '/app/static/resources/media/facility_owner_picture/facility/%s/*'%facility_id)
        name_schema = FacilitySchema.query.filter_by(column_name = 'owner_name').first()
        address_schema = FacilitySchema.query.filter_by(column_name = 'owner_address').first()

        name = FacilityCustomData.query.filter_by(schema=name_schema, facility_id=facility_id).all()
        address = FacilityCustomData.query.filter_by(schema=address_schema, facility_id=facility_id).all()

        ret_data['Data'] = {
            'pic': '/resources/media/facility_owner_picture/facility/%s/%s'%(facility_id, lof[0].split('/')[-1]) if lof else '',
            'name': name[0].data if name else 'Unknown',
            'address': address[0].data if address else 'Unknown',
        }
    except:
        ret_data['ErrorCode'] = '007000'
        ret_data['ErrorMessage'] = 'Error getting owner information for facility.'

    return jsonify(ret_data)


@app.route('/getChartData/', methods=['GET'])
@login_required
#@log_access
def getChartData():
    start = time.time()
    ret_data = {'ErrorCode': '000000', 'ErrorMessage': 'OK', 'RequestParams': {}, 'Data': {}}

    boundary_filter_type = request.args.get('boundary_filter_type', '')
    product_filter_type = request.args.get('product_filter_type','')
    product_filter_ids = [int(i) for i in request.args.get('product_filter_id',0).split(',')]
    timeframes = []
    #kpi_type = int(request.args.get('kpi_type', 0))
    kpi_type = 0
    
    # We need to generate 7 time intervals
    selected_timeframe = request.args.get('timeframe')
    if selected_timeframe == 'month':
        init_date = date(int(request.args.get('date_year')), int(request.args.get('date_month')), 1)
        for i in range(7):
            tmp_date = init_date - relativedelta(months = i)
            timeframes.append({
                'type': 'month',
                'pprint': tmp_date.strftime('%Y-%m'),
                'date_month': tmp_date.month,
                'date_year': tmp_date.year,
            })
    elif selected_timeframe == 'year':
        init_date = date(int(request.args.get('date_year')), 1, 1)
        for i in range(7):
            tmp_date = init_date - relativedelta(years = i)
            timeframes.append({
                'type': 'year',
                'pprint': tmp_date.strftime('%Y'),
                'date_year': tmp_date.year,
            })
    elif selected_timeframe == 'day':
        selected_date = [int(i) for i in request.args.get('date').split('-')]
        init_date = date(int(selected_date[0]), int(selected_date[1]), int(selected_date[2]))
        for i in range(7):
            tmp_date = init_date - relativedelta(days = i)
            timeframes.append({
                'type': 'day',
                'pprint': tmp_date.strftime('%Y-%m-%d'),
                'date_year': tmp_date.year,
                'date_month': tmp_date.month,
                'date_day': tmp_date.day,
            })
    elif selected_timeframe == 'week':
        init_date = date(int(request.args.get('date_year')), int(request.args.get('date_month')), int(request.args.get('date_day')))
        for i in range(7):
            tmp_date = init_date - relativedelta(days = 7*i)
            timeframes.append({
                'type': 'week',
                'pprint': '%s - %s'%(tmp_date.strftime('%Y-%m-%d'), (tmp_date + relativedelta(days=6)).strftime('%Y-%m-%d')),
                'date_year': tmp_date.year,
                'date_month': tmp_date.month,
                'date_day': tmp_date.day,
            })
    timeframes.reverse()    # We want the dates to be asc
   
    if boundary_filter_type == 'boundary_level':
        b_id = int(request.args.get('boundary_filter_id',0))
    else:
        b_id = [int(obj) for obj in request.args.get('boundary_filter_id','').split(',')] if request.args.get('boundary_filter_id','') else []

    ret_data['RequestParams'] = {'boundary_filter_type': boundary_filter_type, 'boundary_filter_id': b_id, 'product_filter_type': product_filter_type, 'product_filter_ids': product_filter_ids, 'timeframes': timeframes, 'kpi_type': kpi_type} 

    # Get kpi for the past 7 timeframes
    raw_data = {'Data': {}}
    for timeframe in timeframes:
        for product_filter_id in product_filter_ids:
            if boundary_filter_type in ('boundary_level', 'boundary'):
                to_be_combined = getBoundaryKPI({'type': boundary_filter_type, 'id': b_id }, {'id': product_filter_id, 'type': product_filter_type}, timeframe, kpi_type)
            else:
                to_be_combined = getFacilityKPI({'type': boundary_filter_type, 'id': b_id }, {'id': product_filter_id, 'type': product_filter_type}, timeframe, kpi_type)

            # sum
            if timeframe['pprint'] not in raw_data['Data']:
                raw_data['Data'][timeframe['pprint']] = to_be_combined
            else:
                for boundary_id in to_be_combined.keys():
                    for kpi_type_id in to_be_combined[boundary_id].keys():
                        raw_data['Data'][timeframe['pprint']][boundary_id][kpi_type_id]['value'] += to_be_combined[boundary_id][kpi_type_id]['value']
                        raw_data['Data'][timeframe['pprint']][boundary_id][kpi_type_id]['polygon_value'] += to_be_combined[boundary_id][kpi_type_id]['polygon_value']

        # average
        if len(product_filter_ids) > 1:
            for boundary_id in raw_data['Data'][timeframe['pprint']].keys():
                for kpi_type_id in raw_data['Data'][timeframe['pprint']][boundary_id].keys():
                    raw_data['Data'][timeframe['pprint']][boundary_id][kpi_type_id]['value'] = raw_data['Data'][timeframe['pprint']][boundary_id][kpi_type_id]['value']/len(product_filter_ids)
                    raw_data['Data'][timeframe['pprint']][boundary_id][kpi_type_id]['polygon_value'] = raw_data['Data'][timeframe['pprint']][boundary_id][kpi_type_id]['polygon_value']/len(product_filter_ids)

        # color
        for boundary_id in raw_data['Data'][timeframe['pprint']].keys():
            for kpi_type_id in raw_data['Data'][timeframe['pprint']][boundary_id].keys():
                raw_data['Data'][timeframe['pprint']][boundary_id][kpi_type_id]['color'] = getKPIColor(raw_data['Data'][timeframe['pprint']][boundary_id][kpi_type_id]['polygon_value'])

    # organize raw data
    # Hard coded right now... Because Activation KPI requires the target, but not sellout and stock.
    organized_data = [[selected_timeframe.title(), 'Activations', 'Activations (Target)', 'Sellouts', 'Stocks']]
    for timeframe in timeframes:
        #['2013/03',  165,                 938,            522,      998, ],
        organized_data.append([timeframe['pprint'], 0, 0, 0, 0])
        for boundary_id in raw_data['Data'][timeframe['pprint']].keys():
            # activations
            organized_data[-1][1] += raw_data['Data'][timeframe['pprint']][boundary_id][1]['actual']
            # activations (target)
            organized_data[-1][2] += raw_data['Data'][timeframe['pprint']][boundary_id][1]['target']
            # sellouts
            organized_data[-1][3] += raw_data['Data'][timeframe['pprint']][boundary_id][2]['actual']
            # activations (target)
            organized_data[-1][4] += raw_data['Data'][timeframe['pprint']][boundary_id][3]['target']
            

    ret_data['Data'] = organized_data

    end = time.time()
    return jsonify (ret_data)

@app.route('/getSalesforceData/', methods=['GET'])
@login_required
def getSalesforceData():
    start = time.time()
    ret_data = {'ErrorCode': '000000', 'ErrorMessage': 'OK', 'RequestParams': {}, 'Data': None}

    # List of boundaries - actually, only one boundary at a time is permitted
    boundary_filter_type = request.args.get('boundary_filter_type', '')
    b_id = [int(request.args.get('boundary_filter_id', 0))][0]

    # Timeframe
    selected_timeframe = request.args.get('timeframe')
    if selected_timeframe == 'month':
        timeframe = {'type': 'month', 'date_month': int(request.args.get('date_month')), 'date_year': int(request.args.get('date_year'))}
        M2C = SalesForceBoundaryKPIMonth if boundary_filter_type == 'boundary' else SalesForceFacilityKPIMonth
    elif selected_timeframe == 'year':
        timeframe = {'type': 'year', 'date_year': int(request.args.get('date_year'))}
        M2C = SalesForceBoundaryKPIYear if boundary_filter_type == 'boundary' else SalesForceFacilityKPIYear
    elif selected_timeframe == 'day':
        selected_date = [int(i) for i in request.args.get('date').split('-')]
        timeframe = {'type': 'day', 'date_day': int(selected_date[2]), 'date_month': int(selected_date[1]), 'date_year': int(selected_date[0])}
        M2C = SalesForceBoundaryKPIDaily if boundary_filter_type == 'boundary' else SalesForceFacilityKPIDaily
    elif selected_timeframe == 'week':
        timeframe = {'type': 'week', 'date_day': int(request.args.get('date_day')), 'date_month': int(request.args.get('date_month')), 'date_year': int(request.args.get('date_year'))}
        selected_start = date(int(request.args.get('date_year')), int(request.args.get('date_month')), int(request.args.get('date_day')))
        M2C = SalesForceBoundaryKPIWeekly if boundary_filter_type == 'boundary' else SalesForceFacilityKPIWeekly
   

    ret_data['RequestParams'] = {'boundary_filter_type': boundary_filter_type, 'boundary_filter_id': b_id, 'timeframe_filter': timeframe} 

    # Get the actual data
    sf_roles = SalesForceRoles.query.all()
    raw_data = {}
    for sf_role in sf_roles:
        raw_data[sf_role.name] = {'total': 0, 'combined_actual': 0, 'combined_kpi': 0, 'children': [], 'id': sf_role.id}
        if selected_timeframe == 'month':
            if boundary_filter_type == 'boundary':
                rows =  M2C.query.filter_by(sales_force_role_id = sf_role.id, boundary_id = b_id, date_month = timeframe['date_month'], date_year = timeframe['date_year']).all()
            else:
                rows =  M2C.query.filter_by(sales_force_role_id = sf_role.id, facility_id = b_id, date_month = timeframe['date_month'], date_year = timeframe['date_year']).all()
        elif selected_timeframe == 'year':
            if boundary_filter_type == 'boundary':
                rows =  M2C.query.filter_by(sales_force_role_id = sf_role.id, boundary_id = b_id, date_year = timeframe['date_year']).all()
            else:
                rows =  M2C.query.filter_by(sales_force_role_id = sf_role.id, facility_id = b_id, date_year = timeframe['date_year']).all()
        elif selected_timeframe == 'day':
            if boundary_filter_type == 'boundary':
                rows =  M2C.query.filter_by(sales_force_role_id = sf_role.id, boundary_id = b_id, date_day = timeframe['date_day'], date_month = timeframe['date_month'], date_year = timeframe['date_year']).all()
            else:
                rows =  M2C.query.filter_by(sales_force_role_id = sf_role.id, facility_id = b_id, date_day = timeframe['date_day'], date_month = timeframe['date_month'], date_year = timeframe['date_year']).all()
        elif selected_timeframe == 'week':
            if boundary_filter_type == 'boundary':
                rows =  M2C.query.filter_by(sales_force_role_id = sf_role.id, boundary_id = b_id, date_start_of_week = date(timeframe['date_year'], timeframe['date_month'], timeframe['date_day'])).all()
            else:
                rows =  M2C.query.filter_by(sales_force_role_id = sf_role.id, facility_id = b_id, date_start_of_week = date(timeframe['date_year'], timeframe['date_month'], timeframe['date_day'])).all()

        for x in rows:
            #sf_name = SalesForce.query.filter_by(id=x.sales_force_id)[0].name
            kpi_rgb = getKPIColorRaw(x.kpi)
            raw_data[sf_role.name]['children'].append({
                'name': SalesForce.query.filter_by(id=x.sales_force_id)[0].name,
                'actual': x.actual,
                'target': x.target,
                'kpi': x.kpi,
                'kpi_rgb': 'rgba(%s,0.5)'%kpi_rgb 
            })
            raw_data[sf_role.name]['total'] += 1
            raw_data[sf_role.name]['combined_actual'] += x.actual
            raw_data[sf_role.name]['combined_kpi'] += x.kpi

        # Calculate combined kpis (average)
        raw_data[sf_role.name]['combined_kpi'] = raw_data[sf_role.name]['combined_kpi']/raw_data[sf_role.name]['total']
        combined_kpi_rgb = getKPIColorRaw(raw_data[sf_role.name]['combined_kpi'])
        raw_data[sf_role.name]['combined_kpi_rgb'] = 'rgba(%s,0.5)'%combined_kpi_rgb 


    ret_data['Data'] = raw_data
    end = time.time()
    
    #app.logger.info('Time taken to process request: %0.2f', end - start)
    return jsonify (ret_data)

@app.route('/getTableData/', methods=['GET'])
@login_required
#@log_access
# Note for params: Single boundary only, multiple products, single timeframe, all kpis
def getTableData():
    start = time.time()
    ret_data = {'ErrorCode': '000000', 'ErrorMessage': 'OK', 'RequestParams': {}, 'Data': None}

    boundary_product_day = '''
        WITH RECURSIVE nodes(id) AS (
            SELECT s1.id
            FROM boundaries s1 WHERE parent_id = %s
                UNION
            SELECT s2.id
            FROM boundaries s2, nodes s1 WHERE s2.parent_id = s1.id
        ) 
        SELECT
            ros1.id as subtype_id,
            ros1.subtype as subtype_desc,
            COALESCE(x.total_outlet_count, 0) AS total_outlet_count,
            COALESCE(x.total_activation, 0) AS total_activation
        FROM
            regular_outlet_subtypes ros1 
        LEFT JOIN (    
            SELECT
                ros.id AS subtype_id,
                SUM(s."outletCount") AS total_outlet_count,
                SUM(s.activation) AS total_activation
            FROM 
                boundary_product_daily_subtype s
            LEFT JOIN
                regular_outlet_subtypes ros on s.regular_outlet_subtype_id = ros.id
            WHERE
                (s.boundary_id IN (SELECT * FROM nodes) OR s.boundary_id IN (%s))
            AND s.product_id in (%s)
            AND s.date = '%s'
            GROUP BY ros.id
        ) x on ros1.id = x.subtype_id
        ORDER BY
            ros1.id ASC
    '''
    boundary_product_week = '''
        WITH RECURSIVE nodes(id) AS (
            SELECT s1.id
            FROM boundaries s1 WHERE parent_id = %s
                UNION
            SELECT s2.id
            FROM boundaries s2, nodes s1 WHERE s2.parent_id = s1.id
        ) 
        SELECT
            ros1.id as subtype_id,
            ros1.subtype as subtype_desc,
            COALESCE(x.total_outlet_count, 0) AS total_outlet_count,
            COALESCE(x.total_activation, 0) AS total_activation
        FROM
            regular_outlet_subtypes ros1 
        LEFT JOIN (    
            SELECT
                ros.id AS subtype_id,
                SUM(s."outletCount") AS total_outlet_count,
                SUM(s.activation) AS total_activation
            FROM 
                boundary_product_weekly_subtype s
            LEFT JOIN
                regular_outlet_subtypes ros on s.regular_outlet_subtype_id = ros.id
            WHERE
                (s.boundary_id IN (SELECT * FROM nodes) OR s.boundary_id IN (%s))
            AND s.product_id in (%s)
            AND s.start_week_date = '%s'
            GROUP BY ros.id
        ) x on ros1.id = x.subtype_id
        ORDER BY
            ros1.id ASC
    '''
    boundary_product_month = '''
        WITH RECURSIVE nodes(id) AS (
            SELECT s1.id
            FROM boundaries s1 WHERE parent_id = %s
                UNION
            SELECT s2.id
            FROM boundaries s2, nodes s1 WHERE s2.parent_id = s1.id
        ) 
        SELECT
            ros1.id as subtype_id,
            ros1.subtype as subtype_desc,
            COALESCE(x.total_outlet_count, 0) AS total_outlet_count,
            COALESCE(x.total_activation, 0) AS total_activation
        FROM
            regular_outlet_subtypes ros1 
        LEFT JOIN (    
            SELECT
                ros.id AS subtype_id,
                SUM(s."outletCount") AS total_outlet_count,
                SUM(s.activation) AS total_activation
            FROM 
                boundary_product_monthly_subtype s
            LEFT JOIN
                regular_outlet_subtypes ros on s.regular_outlet_subtype_id = ros.id
            WHERE
                (s.boundary_id IN (SELECT * FROM nodes) OR s.boundary_id IN (%s))
            AND s.product_id in (%s)
            AND s.month = %s
            AND s.year = %s
            GROUP BY ros.id
        ) x on ros1.id = x.subtype_id
        ORDER BY
            ros1.id ASC
    '''
    boundary_product_year = '''
        WITH RECURSIVE nodes(id) AS (
            SELECT s1.id
            FROM boundaries s1 WHERE parent_id = %s
                UNION
            SELECT s2.id
            FROM boundaries s2, nodes s1 WHERE s2.parent_id = s1.id
        ) 
        SELECT
            ros1.id as subtype_id,
            ros1.subtype as subtype_desc,
            COALESCE(x.total_outlet_count, 0) AS total_outlet_count,
            COALESCE(x.total_activation, 0) AS total_activation
        FROM
            regular_outlet_subtypes ros1 
        LEFT JOIN (    
            SELECT
                ros.id AS subtype_id,
                SUM(s."outletCount") AS total_outlet_count,
                SUM(s.activation) AS total_activation
            FROM 
                boundary_product_yearly_subtype s
            LEFT JOIN
                regular_outlet_subtypes ros on s.regular_outlet_subtype_id = ros.id
            WHERE
                (s.boundary_id IN (SELECT * FROM nodes) OR s.boundary_id IN (%s))
            AND s.product_id in (%s)
            AND s.year = %s
            GROUP BY ros.id
        ) x on ros1.id = x.subtype_id
        ORDER BY
            ros1.id ASC
    '''
    product_list = '''
        SELECT 
            product_id 
        FROM 
            productgroup_map 
        WHERE
            group_id IN (%s)
    '''

    # KPI
    kpi_type = 0
    
    # List of boundaries
    boundary_filter_type = request.args.get('boundary_filter_type', '')
    b_id = [int(request.args.get('boundary_filter_id', 0))]

    # List of products
    product_filter_type = request.args.get('product_filter_type','')
    product_filter_ids = [int(i) for i in request.args.get('product_filter_id',0).split(',')]
    products = []
    if product_filter_type == 'product':
        for i in product_filter_ids:
            products.append({'type': 'product', 'id': i, 'name': Product.query.filter_by(id = i).first().name})
    else:
        for i in product_filter_ids:
            products.append({'type': 'product_group', 'id': i, 'name': ProductGroup.query.filter_by(id = i).first().description})

            # Get all the child products of this group
            for j in ProductGroupMap.query.filter_by(group_id=i).all():
                products.append({'type': 'product', 'id': j.product_id, 'name': Product.query.filter_by(id = j.product_id).first().name})

    # Timeframe
    selected_timeframe = request.args.get('timeframe')
    if selected_timeframe == 'month':
        timeframe = {'type': 'month', 'date_month': int(request.args.get('date_month')), 'date_year': int(request.args.get('date_year'))}
    elif selected_timeframe == 'year':
        timeframe = {'type': 'year', 'date_year': int(request.args.get('date_year'))}
    elif selected_timeframe == 'day':
        selected_date = [int(i) for i in request.args.get('date').split('-')]
        timeframe = {'type': 'day', 'date_day': int(selected_date[2]), 'date_month': int(selected_date[1]), 'date_year': int(selected_date[0])}
        selected_start = date(int(timeframe['date_year']), int(timeframe['date_month']), int(timeframe['date_day']))
    elif selected_timeframe == 'week':
        timeframe = {'type': 'week', 'date_day': int(request.args.get('date_day')), 'date_month': int(request.args.get('date_month')), 'date_year': int(request.args.get('date_year'))}
        selected_start = date(int(request.args.get('date_year')), int(request.args.get('date_month')), int(request.args.get('date_day')))

    ret_data['RequestParams'] = {'boundary_filter_type': boundary_filter_type, 'boundary_filter_id': b_id, 'product_filter_type': product_filter_type, 'product_filter_ids': product_filter_ids, 'timeframe_filter': timeframe, 'kpi_type': kpi_type} 

    raw_data = []
    for product in products:
        # No combining necessary because we only have to handle one boundary
        if boundary_filter_type in ('boundary_level', 'boundary'):
            temp = getBoundaryKPI({'type': boundary_filter_type, 'id': b_id }, {'id': product['id'], 'type': product['type']}, timeframe, kpi_type)
        else:
            temp = getFacilityKPI({'type': boundary_filter_type, 'id': b_id }, {'id': product['id'], 'type': product['type']}, timeframe, kpi_type)

        # Get outlet subtype activations
        #[(1, u'super platinum', 0L, 0L), (2, u'platinum', 0L, 0L), (3, u'gold', 0L, 0L), (4, u'silver', 6L, 49L)]
        if product['type'] == 'product_group':
            p_ids = ','.join([str(i[0]) for i in db.engine.execute(product_list%(product['id']))])
        else:
            p_ids = product['id']

        if selected_timeframe == 'day':
            M2C = boundary_product_day%(b_id[0], b_id[0], p_ids, selected_start)
        elif selected_timeframe == 'week':
            M2C = boundary_product_week%(b_id[0], b_id[0], p_ids, selected_start)
        elif selected_timeframe == 'month':
            M2C = boundary_product_month%(b_id[0], b_id[0], p_ids, timeframe['date_month'], timeframe['date_year'])
        elif selected_timeframe == 'year':
            M2C = boundary_product_year%(b_id[0], b_id[0], p_ids, timeframe['date_year'])

        count = [i for i in db.engine.execute(M2C)]
        kpi_colors = [
            getKPIColorRaw(temp[b_id[0]][1]['polygon_value']),
            getKPIColorRaw(temp[b_id[0]][2]['polygon_value']),
            getKPIColorRaw(temp[b_id[0]][3]['polygon_value'])
        ]

        raw_data.append({
            'name': product['name'],
            'activation_actual': temp[b_id[0]][1]['actual'] if temp else 0,
            'activation_kpi': temp[b_id[0]][1]['polygon_value'] if temp else 0,
            'activation_kpi_rgb': 'rgba(%s,0.5)'%kpi_colors[0], 
            'sellout_actual': temp[b_id[0]][2]['actual'] if temp else 0,
            'sellout_kpi': temp[b_id[0]][2]['polygon_value'] if temp else 0,
            'sellout_kpi_rgb': 'rgba(%s,0.5)'%kpi_colors[1], 
            'stock_actual': temp[b_id[0]][3]['actual'] if temp else 0,
            'stock_kpi': temp[b_id[0]][3]['polygon_value'] if temp else 0,
            'stock_kpi_rgb': 'rgba(%s,0.5)'%kpi_colors[2], 
            'class': 'info' if product['type'] == 'product_group' else '',
            'super_platinum_outlet_total': count[0][2] if count else 0,
            'super_platinum_activation_total': count[0][3] if count else 0,
            'platinum_outlet_total': count[1][2] if count else 0, 
            'platinum_activation_total': count[1][3] if count else 0, 
            'gold_outlet_total': count[2][2] if count else 0, 
            'gold_activation_total': count[2][3] if count else 0, 
            'silver_outlet_total': count[3][2] if count else 0, 
            'silver_activation_total': count[3][3] if count else 0, 
        })

    ret_data['Data'] = raw_data
    end = time.time()
    
    #app.logger.info('Time taken to process request: %0.2f', end - start)
    return jsonify (ret_data)

@app.route('/getKPI/', methods=['GET'])
@login_required
#@log_access
def getKPI():
    start = time.time()
    ret_data = {'ErrorCode': '000000', 'ErrorMessage': 'OK', 'RequestParams': {}, 'Data': None}

    boundary_filter_type = request.args.get('boundary_filter_type', '')
    product_filter_type = request.args.get('product_filter_type','')
    product_filter_ids = [int(i) for i in request.args.get('product_filter_id',0).split(',')]
    kpi_type = int(request.args.get('kpi_type', 0))
    
    selected_timeframe = request.args.get('timeframe')
    if selected_timeframe == 'month':
        timeframe = {'type': 'month', 'date_month': int(request.args.get('date_month')), 'date_year': int(request.args.get('date_year'))}
    elif selected_timeframe == 'year':
        timeframe = {'type': 'year', 'date_year': int(request.args.get('date_year'))}
    elif selected_timeframe == 'day':
        selected_date = [int(i) for i in request.args.get('date').split('-')]
        timeframe = {'type': 'day', 'date_day': int(selected_date[2]), 'date_month': int(selected_date[1]), 'date_year': int(selected_date[0])}
    elif selected_timeframe == 'week':
        timeframe = {'type': 'week', 'date_day': int(request.args.get('date_day')), 'date_month': int(request.args.get('date_month')), 'date_year': int(request.args.get('date_year'))}
        selected_start = date(int(request.args.get('date_year')), int(request.args.get('date_month')), int(request.args.get('date_day')))
   
    #boundary = Boundary.query.get(b_id)
    
    if boundary_filter_type == 'boundary_level':
        b_id = int(request.args.get('boundary_filter_id',0))
    else:
        b_id = [int(obj) for obj in request.args.get('boundary_filter_id','').split(',')] if request.args.get('boundary_filter_id','') else []

    ret_data['RequestParams'] = {'boundary_filter_type': boundary_filter_type, 'boundary_filter_id': b_id, 'product_filter_type': product_filter_type, 'product_filter_ids': product_filter_ids, 'timeframe_filter': timeframe, 'kpi_type': kpi_type} 
    for product_filter_id in product_filter_ids:
        if boundary_filter_type in ('boundary_level', 'boundary'):
            to_be_combined = getBoundaryKPI({'type': boundary_filter_type, 'id': b_id }, {'id': product_filter_id, 'type': product_filter_type}, timeframe, kpi_type)
        else:
            to_be_combined = getFacilityKPI({'type': boundary_filter_type, 'id': b_id }, {'id': product_filter_id, 'type': product_filter_type}, timeframe, kpi_type)

        # sum
        if not ret_data['Data']:
            ret_data['Data'] = to_be_combined
        else:
            for boundary_id in to_be_combined.keys():
                for kpi_type_id in to_be_combined[boundary_id].keys():
                    ret_data['Data'][boundary_id][kpi_type_id]['value'] += to_be_combined[boundary_id][kpi_type_id]['value']
                    ret_data['Data'][boundary_id][kpi_type_id]['polygon_value'] += to_be_combined[boundary_id][kpi_type_id]['polygon_value']

    # average
    if len(product_filter_ids) > 1:
        for boundary_id in ret_data['Data'].keys():
            for kpi_type_id in ret_data['Data'][boundary_id].keys():
                ret_data['Data'][boundary_id][kpi_type_id]['value'] = ret_data['Data'][boundary_id][kpi_type_id]['value']/len(product_filter_ids)
                ret_data['Data'][boundary_id][kpi_type_id]['polygon_value'] = ret_data['Data'][boundary_id][kpi_type_id]['polygon_value']/len(product_filter_ids)

    # color
    for boundary_id in ret_data['Data'].keys():
        for kpi_type_id in ret_data['Data'][boundary_id].keys():
            ret_data['Data'][boundary_id][kpi_type_id]['color'] = getKPIColor(ret_data['Data'][boundary_id][kpi_type_id]['polygon_value'])

    end = time.time()
    
    #app.logger.info('Time taken to process request: %0.2f', end - start)
    return jsonify (ret_data)


# Internal functions for global kpi color schemes
def getKPIColor(kpi_value):
    if kpi_value != None:
        # lowerbound < kpi <= upperbound
        rgb = GlobalKPIColorScheme.query.filter(GlobalKPIColorScheme.lowerbound < kpi_value).filter(kpi_value <= GlobalKPIColorScheme.upperbound).first()

    if not rgb: 
        rgb = DEFAULT_KPI_RGB_NOALPHA   # black is the default color

    rgb = rgb.rgb.split(',')

    return {'red': rgb[0], 'green': rgb[1], 'blue': rgb[2]}

def getKPIColorRaw(kpi_value):
    if kpi_value != None:
        # lowerbound < kpi <= upperbound
        rgb = GlobalKPIColorScheme.query.filter(GlobalKPIColorScheme.lowerbound < kpi_value).filter(kpi_value <= GlobalKPIColorScheme.upperbound).first()

    if not rgb: 
        return DEFAULT_KPI_RGB_NOALPHA
    else:
        return rgb.rgb

def checkSchemeCorrectness(lowerbound, upperbound, toexclude=None):
    # lowerbound < kpi <= upperbound
    if (lowerbound >= upperbound):
        return False

    check_lowerbound = GlobalKPIColorScheme.query.filter(GlobalKPIColorScheme.lowerbound < lowerbound).filter(lowerbound < GlobalKPIColorScheme.upperbound).filter(GlobalKPIColorScheme.id != toexclude).first()
    check_upperbound = GlobalKPIColorScheme.query.filter(GlobalKPIColorScheme.lowerbound < upperbound).filter(upperbound < GlobalKPIColorScheme.lowerbound).filter(GlobalKPIColorScheme.id != toexclude).first()
    
    if (check_lowerbound or check_upperbound):
        return True
    else:
        return False


# External global kpi color scheme functions
@app.route('/getKPIColorScheme', methods=['GET'])
@login_required
def getKPIColorScheme(): 
    ret_data = {'ErrorCode': '000000', 'ErrorMessage': 'OK', 'RequestParams': {}, 'Data': None}
    #ret_data['Data'] = {i.id:i.serialize for i in GlobalKPIColorScheme.query.order_by('lowerbound asc').all()}
    ret_data['Data'] = [i.serialize for i in GlobalKPIColorScheme.query.order_by('lowerbound asc').all()]

    return jsonify(ret_data)

@app.route('/deleteKPIColorScheme/', methods=['POST'])
@login_required
def deleteKPIColorScheme():
    ret_data = {'ErrorCode': '000000', 'ErrorMessage': 'OK', 'RequestParams': str(request.form), 'Data': None}

    # Parse form
    try:
        scheme_id_to_delete = int(request.form['id'])
        scheme_to_delete = GlobalKPIColorScheme.query.filter_by(id=scheme_id_to_delete).first()
    except:
        ret_data['ErrorCode'] = '002020'
        ret_data['ErrorMessage'] = 'Error parsing request headers for deleting a color scheme'
        return jsonify(ret_data)

    # Delete color scheme
    try:
        db.session.delete(scheme_to_delete)
        db.session.commit()
    except:
        ret_data['ErrorCode'] = '002022'
        ret_data['ErrorMessage'] = 'Error deleting new color scheme. Potential DB error.'
        return jsonify(ret_data)

    # Alls well
    ret_data['Data'] = 'OK'
    return jsonify(ret_data)

@app.route('/addKPIColorScheme/', methods=['POST'])
@login_required
def addKPIColorScheme():
    ret_data = {'ErrorCode': '000000', 'ErrorMessage': 'OK', 'RequestParams': str(request.form), 'Data': None}

    # Parse form
    try:
        # s - scheme to be added
        s = {
            'lowerbound': int(request.form['lowerbound']),
            'upperbound': int(request.form['upperbound']),
            'rgb': re.search('rgb\((.*)\)', request.form['rgb']).group(1)
        }
    except:
        ret_data['ErrorCode'] = '002010'
        ret_data['ErrorMessage'] = 'Error parsing request headers for adding a color scheme'
        return jsonify(ret_data)

    # Check for correctness of bounds and lowerbound < upperbound
    if checkSchemeCorrectness(s['lowerbound'], s['upperbound']):
        ret_data['ErrorCode'] = '002001'
        ret_data['ErrorMessage'] = 'Bounds collision detected.'
        return jsonify(ret_data)

    # Add color scheme
    try:
        scheme_to_add = GlobalKPIColorScheme(
            lowerbound = s['lowerbound'], 
            upperbound = s['upperbound'], 
            rgb = s['rgb']
        )
        db.session.add(scheme_to_add)
        db.session.commit()
    except:
        ret_data['ErrorCode'] = '002012'
        ret_data['ErrorMessage'] = 'Error adding new color scheme. Potential DB error.'
        return jsonify(ret_data)

    # Alls well
    ret_data['Data'] = 'OK'
    return jsonify(ret_data)

@app.route('/editKPIColorScheme/<int:scheme_id>/', methods=['POST'])
@login_required
def editKPIColorScheme(scheme_id): 
    ret_data = {'ErrorCode': '000000', 'ErrorMessage': 'OK', 'RequestParams': str(request.form), 'Data': None}

    # Parse form
    try:
        # s - scheme to be edited
        s = {
            'id': scheme_id,
            'lowerbound': int(request.form['lowerbound']),
            'upperbound': int(request.form['upperbound']),
            'rgb': re.search('rgb\((.*)\)', request.form['rgb']).group(1)
        }
        scheme_to_edit = GlobalKPIColorScheme.query.filter_by(id=s['id']).first()
    except:
        ret_data['ErrorCode'] = '002000'
        ret_data['ErrorMessage'] = 'Error parsing request headers for editing a color scheme'
        return jsonify(ret_data)

    # Check for correctness of bounds and lowerbound < upperbound
    if (not scheme_to_edit.lowerbound == s['lowerbound']) or (not scheme_to_edit.upperbound == s['upperbound']):
        if checkSchemeCorrectness(s['lowerbound'], s['upperbound'], scheme_id):
            ret_data['ErrorCode'] = '002001'
            ret_data['ErrorMessage'] = 'Bounds collision detected.'
            return jsonify(ret_data)

    # Edit Color Scheme
    try:
        scheme_to_edit.lowerbound = s['lowerbound']
        scheme_to_edit.upperbound = s['upperbound']
        scheme_to_edit.rgb = s['rgb']
        db.session.commit()
    except:
        ret_data['ErrorCode'] = '002002'
        ret_data['ErrorMessage'] = 'Error updating color scheme. Potential DB error.'
        return jsonify(ret_data)

    # Alls well
    ret_data['Data'] = 'OK'
    return jsonify(ret_data)

def getFacilityKPI(facility, products, timeframe, kpi_type):
        days = 0

        if products['type'] == 'product':
            product_id = int(products['id'])
            if timeframe['type'] == 'year':
                t = SumFacilityProductYear
                q = t.query.filter_by( product_id = product_id, date_year = timeframe['date_year'] )
                days = 366 if calendar.isleap(timeframe['date_year']) else 365
            # end if
            if timeframe['type'] == 'month':
                t = SumFacilityProductMonth
                q = t.query.filter_by( product_id = product_id, date_year = timeframe['date_year'], date_month = timeframe['date_month'] )
                days =  calendar.monthrange(timeframe['date_year'], timeframe['date_month'])[1]
            # end if
            if timeframe['type'] == 'week':
                t = SumFacilityProductWeek
                q = t.query.filter_by( product_id = product_id, date_start_of_week = date(timeframe['date_year'], timeframe['date_month'], timeframe['date_day']) )
                days = 7
            # end if
            if timeframe['type'] == 'day':
                t = KPI
                q = t.query.filter_by( product_id = product_id, date_day = timeframe['date_day'], date_year = timeframe['date_year'], date_month = timeframe['date_month'] )
                days = 1
            # end if
        else:
            product_group_id = int(products['id'])
            if timeframe['type'] == 'year':
                t = SumFacilityProductGroupYear
                q = t.query.filter_by(product_group_id = product_group_id, date_year = timeframe['date_year'])
                days = 366 if calendar.isleap(timeframe['date_year']) else 365
            # end if
            if timeframe['type'] == 'month':
                t = SumFacilityProductGroupMonth
                q = t.query.filter_by( product_group_id = product_group_id, date_year = timeframe['date_year'], date_month = timeframe['date_month'])
                days =  calendar.monthrange(timeframe['date_year'], timeframe['date_month'])[1]
            # end if
            if timeframe['type'] == 'week':
                t = SumFacilityProductGroupWeek
                q = t.query.filter_by( product_group_id = product_group_id, date_start_of_week = date(timeframe['date_year'], timeframe['date_month'], timeframe['date_day']))
                days = 7
            # end if
            if timeframe['type'] == 'day':
                t = SumFacilityProductGroupDay
                q = t.query.filter_by( product_group_id = product_group_id, date_day = timeframe['date_day'], date_year = timeframe['date_year'], date_month = timeframe['date_month'])
                days = 1            
            # end if
        # end if

        q = q.filter(t.facility_id.in_( facility['id']))
        # end if
        

        q = q.outerjoin ( KPIType, KPIType.id == t.kpi_type ).outerjoin ( AggregationFunctionMap, KPIType.id == AggregationFunctionMap.kpi_type ).add_entity(KPIType).add_entity(AggregationFunctionMap)
        if kpi_type:
            q = q.filter(t.kpi_type == kpi_type)
            
        # end if
        #q = q.filter(t.facility_type_id == config.STORE_TYPE_ID)

        boundary_ret = { }
        
        if ( t == KPI ):
            for obj in q:
                kpi_data, kpi_type_data, func_map = obj
                value, polygon_value, actual, target = 0, 0, kpi_data.actual, kpi_data.target
                value =  kpi_data.kpi
                polygon_value =  value
             
                _ = boundary_ret.setdefault(kpi_data.facility_id, { })
                #_ = _.setdefault(kpi_data.facility_type_id, { })
                
                _[kpi_data.kpi_type] = {
                    'facility_type_id': kpi_data.facility_type_id, 
                    'name': kpi_type_data.name, 
                    'value': value, 
                    'polygon_value': polygon_value,
                    'actual': actual,
                    'target': target,
                } 
        else:
            for obj in q:
                kpi_data, kpi_type_data, func_map = obj
                value, polygon_value, actual, target = 0, 0, kpi_data.actual, kpi_data.target
                value =  ( kpi_data.kpi / kpi_data.data_point_count ) if ( func_map.function_type == AggregateFunctionType.AVERAGE ) else kpi_data.kpi
                polygon_value =  value if ( func_map.function_type == AggregateFunctionType.AVERAGE ) else ( kpi_data.kpi / kpi_data.data_point_count )
                _ = boundary_ret.setdefault(kpi_data.facility_id, { })
                #_ = _.setdefault(kpi_data.facility_type_id, { })
                _[kpi_data.kpi_type] = {
                    'facility_type_id': kpi_data.facility_type_id, 
                    'name': kpi_type_data.name, 
                    'value': value, 
                    'polygon_value': polygon_value,
                    'actual': actual,
                    'target': target,
                } 

        # end for

        return boundary_ret

def getBoundaryKPI(boundary, products, timeframe, kpi_type):
        days = 0

        if products['type'] == 'product':
            product_id = int(products['id'])
            if timeframe['type'] == 'year':
                t = SumBoundaryProductYear
                q = t.query.filter_by( product_id = product_id, date_year = timeframe['date_year'] )
                days = 366 if calendar.isleap(timeframe['date_year']) else 365
            # end if
            if timeframe['type'] == 'month':
                t = SumBoundaryProductMonth
                q = t.query.filter_by( product_id = product_id, date_year = timeframe['date_year'], date_month = timeframe['date_month'] )
                days =  calendar.monthrange(timeframe['date_year'], timeframe['date_month'])[1]
            # end if
            if timeframe['type'] == 'week':
                t = SumBoundaryProductWeek
                q = t.query.filter_by( product_id = product_id, date_start_of_week = date(timeframe['date_year'], timeframe['date_month'], timeframe['date_day']) )
                days = 7
            # end if
            if timeframe['type'] == 'day':
                t = SumBoundaryProductDay
                q = t.query.filter_by( product_id = product_id, date_day = timeframe['date_day'], date_year = timeframe['date_year'], date_month = timeframe['date_month'] )
                days = 1
            # end if
        else:
            product_group_id = int(products['id'])
            if timeframe['type'] == 'year':
                t = SumBoundaryProductGroupYear
                q = t.query.filter_by(product_group_id = product_group_id, date_year = timeframe['date_year'])
                days = 366 if calendar.isleap(timeframe['date_year']) else 365
            # end if
            if timeframe['type'] == 'month':
                t = SumBoundaryProductGroupMonth
                q = t.query.filter_by( product_group_id = product_group_id, date_year = timeframe['date_year'], date_month = timeframe['date_month'])
                days =  calendar.monthrange(timeframe['date_year'], timeframe['date_month'])[1]
            # end if
            if timeframe['type'] == 'week':
                t = SumBoundaryProductGroupWeek
                q = t.query.filter_by( product_group_id = product_group_id, date_start_of_week = date(timeframe['date_year'], timeframe['date_month'], timeframe['date_day']))
                days = 7
            # end if
            if timeframe['type'] == 'day':
                t = SumBoundaryProductGroupDay
                q = t.query.filter_by( product_group_id = product_group_id, date_day = timeframe['date_day'], date_year = timeframe['date_year'], date_month = timeframe['date_month'])
                days = 1            
            # end if
        # end if

        if boundary['type'] == 'boundary_level':
            q = q.filter(t.boundary_level_id == boundary['id'])
        else:
            q = q.filter(t.boundary_id.in_(boundary['id']))
        # end if
        

        q = q.outerjoin ( KPIType, KPIType.id == t.kpi_type ).outerjoin ( AggregationFunctionMap, KPIType.id == AggregationFunctionMap.kpi_type ).add_entity(KPIType).add_entity(AggregationFunctionMap)
        if kpi_type:
            q = q.filter(t.kpi_type == kpi_type)
            
        # end if
        #q = q.filter(t.facility_type_id == config.STORE_TYPE_ID)

        boundary_ret = { }

        for obj in q:
            kpi_data, kpi_type_data, func_map = obj
            value, polygon_value, actual, target = 0, 0, kpi_data.actual, kpi_data.target
            value =  ( kpi_data.kpi / kpi_data.data_point_count ) if ( func_map.function_type == AggregateFunctionType.AVERAGE ) else kpi_data.kpi
            polygon_value =  value if ( func_map.function_type == AggregateFunctionType.AVERAGE ) else ( kpi_data.kpi / kpi_data.data_point_count )
            _ = boundary_ret.setdefault(kpi_data.boundary_id, { })

            _[kpi_data.kpi_type] = {
                'facility_type_id': kpi_data.facility_type_id, 
                'name': kpi_type_data.name, 
                'value': value, 
                'polygon_value': polygon_value,
                'actual': actual,
                'target': target,
            }
        # end for

        return boundary_ret

@app.route('/getFacilityCount/', methods=['GET'])
def getFacilityCount():
    ret_data = { 'ErrorCode' : '000000', 'ErrorMessage': 'OK', 'RequestParams' : {}, 'Data' : None }
    boundary_filter_type = request.args.get('boundary_filter_type', '')
    b_id = int(request.args.get('boundary_filter_id',0))
    ret_data['RequestParams'] = {'boundary_filter_type' : boundary_filter_type, 'boundary_filter_id' : b_id } 

    f = {}
    for obj in FacilityType.query.all():
        f[obj.id] = {'id':obj.id, 'name':obj.name, 'count' : 0}
    boundary = Boundary.query.filter_by(id = b_id)[0]
    
    recurseFacilityCount(f, boundary)
    
    ret_data['Data'] = f
    
    return jsonify(ret_data)
    
def recurseFacilityCount(result, boundary, boundary_levels = None):
        
    lvl = boundary.level_id
    
    if not boundary_levels:
        b_levels = BoundaryLevelDesc.query.order_by(BoundaryLevelDesc.id.desc()).all()[1:]
    else:
        b_levels = boundary_levels
   
    f = result

    if b_levels[0].id == lvl:
        for obj in db.session.query(Facility.facility_type_id, func.count(Facility.id).label('count')).group_by(Facility.facility_type_id).filter(Facility.boundary_id == boundary.id).all():
            # Facility.query.filter_by(boundary_id = boundary.id).group_by(Facility.facility_type_id).count()
            app.logger.debug(obj)
            f[obj[0]]['count'] += obj[1]   
    else:
        for b in Boundary.query.filter_by(parent_id = boundary.id):
            recurseFacilityCount(f, b, b_levels)
  
    
@app.route('/getChildBoundaryCount/', methods=['GET'])
def getChildBoundaryCount():
    ret_data = { 'ErrorCode' : '000000', 'ErrorMessage': 'OK', 'RequestParams' : {}, 'Data' : None }
    boundary_filter_type = request.args.get('boundary_filter_type', '')
    b_id = int(request.args.get('boundary_filter_id',0))
    
    ret_data['RequestParams'] = {'boundary_filter_type' : boundary_filter_type, 'boundary_filter_id' : b_id } 

    f = {}
    boundary = Boundary.query.filter_by(id = b_id)[0]

    for obj in BoundaryLevelDesc.query.order_by(BoundaryLevelDesc.id.desc())[1:]:
        if obj.id > boundary.level_id:
            f[obj.id] = {'id':obj.id, 'name':obj.description, 'count' : 0}
    
    recurseChildBoundaryCount(f, boundary)
    
    ret_data['Data'] = f
    return jsonify(ret_data)

def recurseChildBoundaryCount(result, boundary, boundary_levels = None):
        
    lvl = boundary.level_id
    
    if not boundary_levels:
        b_levels = BoundaryLevelDesc.query.order_by(BoundaryLevelDesc.id.desc()).all()[1:]
    else:
        b_levels = boundary_levels
    
    f = result

    for b in Boundary.query.filter_by(parent_id = boundary.id):
        f[lvl+1]['count'] += 1
        recurseChildBoundaryCount(f, b, b_levels)
            

@app.route('/getKPIData/', methods=['GET'])
def getKPIData(boundary_level = '', id = None):
    boundary_level = int(request.args.get('boundary_level'))
    boundary_scope_id = int(request.args.get('boundary_id'))

    product_id = request.args.get('product_id')
    product_group_id = request.args.get('product_group')
    selected_timeframe = request.args.get('timeframe')
    kpi = {'status' : 'ok'}
    if selected_timeframe == 'month':
        timeframe = { 'type' : 'month', 'date_month' : int(request.args.get('date_month')), 'date_year' : int(request.args.get('date_year')) }
        kpi['date'] = date(int(request.args.get('date_year')), int(request.args.get('date_month')), 1).strftime('%m-%Y')
        
    elif selected_timeframe == 'year':
        timeframe = { 'type' : 'year', 'date_year' : int(request.args.get('date_year')) }
        kpi['date'] = int(request.args.get('date_year'))
    
    elif selected_timeframe == 'day':
        selected_date = [ int (i) for i in request.args.get('date').split('-') ]
        timeframe = { 'type' : 'day', 'date_day': int(selected_date[2]), 'date_month': int ( selected_date[1] ), 'date_year' : int ( selected_date[0] )}
        kpi['date'] = date(int ( selected_date[0] ), int ( selected_date[1] ), int ( selected_date[2] )).isoformat()

    elif selected_timeframe == 'week':
        timeframe = { 'type' : 'week', 'date_day': int(request.args.get('date_day')), 'date_month' : int(request.args.get('date_month')), 'date_year' : int(request.args.get('date_year'))}
        selected_start = date(int(request.args.get('date_year')), int(request.args.get('date_month')), int(request.args.get('date_day')))
        kpi['date'] = "%s - %s" % ( selected_start.isoformat(), ( selected_start + timedelta (days = 6) ).isoformat())
    # end if
    
    store_level = BoundaryLevelDesc.query.order_by(BoundaryLevelDesc.id.desc()).all()[0]
    #construct the filter criteria

    products = {}
    if product_id:
        product = Product.query.get(int(product_id))
        products['id'] = int(product_id)
        products['type'] = 'product'
        kpi['product_name'] = product.name
    else:
        product_group = ProductGroup.query.get(int(product_group_id))
        products['id'] = int(product_group_id)
        products['type'] = 'product_group'
        kpi['product_name'] = product_group.description
        
    if boundary_level != store_level.id:
        b = Boundary.query.filter_by(id = boundary_scope_id).all()[0]
        kpi['stores'] = getStoreCount(b)
        kpi['name'] = b.name
        kpi['level_name'] = b.level.description
        _ = b.kpi(products, timeframe)
        
        kpi['kpi'] = {'activations' : _[1][2], 'sellouts' : _[2][2], 'stocks' : _[3][2], 'status' : ( 'ok' if _['count'] else 'fails' ) }

    else:
        s = Facility.query.filter_by(id = boundary_scope_id, facility_type_id = config.STORE_TYPE_ID).all()[0] 

        kpi['name'] =s.name
        kpi['level_name'] = store_level.description
        _ = s.kpi(products, timeframe)
        
        kpi['kpi'] = {'activations' : _[1][2], 'sellouts' : _[2][2], 'stocks' : _[3][2], 'status' : ( 'ok' if _['count'] else 'fails' )}

    
    return jsonify({'ErrorCode' : 'OK', 'ErrorMessage' : 'OK', 'Data' : kpi })   

@app.route('/postFilter', methods=['GET', 'POST'])
@log_access
def postFilter():
    app.logger.debug(request.json['boundary'])
    try:
        boundary = request.json['boundary']
    except:
        app.logger.error('Request does not contain boundary')
        boundary = ''
    app.logger.debug(boundary)
    return_data = {}
    if boundary:
        if boundary['boundary_level'] == 'national':
            return_data = {
                'polygons': getRegionalPolygons(),
            }    
        elif boundary['boundary_level'] == 'regional':
            return_data = {
                'polygons': getClusterPolygons(boundary['selected'], boundary['selected_elements']),
            }
        elif boundary['boundary_level'] == 'cluster':
            return_data = {'points': getOutletPoints()}
            
    return jsonify({'ErrorCode' : 'OK', 'ErrorMessage' : 'OK', 'Data' : return_data })
    
HEX = '0123456789abcdef'
HEX2 = dict((a+b, HEX.index(a)*16 + HEX.index(b)) for a in HEX for b in HEX)

def rgb(triplet):
    triplet = triplet.lower()
    return (HEX2[triplet[0:2]], HEX2[triplet[2:4]], HEX2[triplet[4:6]])

def triplet(rgb):
    return format((rgb[0]<<16)|(rgb[1]<<8)|rgb[2], '06x')


   
        
