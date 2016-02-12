import sys
sys.path.append('../')
from geoalchemy import *
from app import db
from app.models import *
import cgpolyencode
import re
import random

def add_outlets():
    print 'Adding level: 3'
    with open('../../samples/Provinces.kml', 'r') as f:

        x = ''.join(f.readlines())
        
    outlets = re.findall('<Placemark>.*?</Placemark>', re.findall('<Folder>.*?<name>Outlets</name>.*?</Folder>', x, re.S)[0], re.S)

    # Add icon type to store schema if it hasn't been added yet
    if not bool(FacilitySchema.query.filter_by(column_name='icon').count()):
        icon_schema = FacilitySchema(column_name = 'icon', data_type = FacilityColumnSchema_DataType.String)
        db.session.add(icon_schema)
        db.session.commit()
    else:
        icon_schema = FacilitySchema.query.filter_by(column_name = 'icon').one()

    # Add outlets
    stores_to_add = []
    for outlet in outlets:
        o_name = re.search('<name>(.*?)</name>', outlet).group(1)
        o_lat = re.search('<latitude>(.*?)</latitude>', outlet).group(1)
        o_lon = re.search('<longitude>(.*?)</longitude>', outlet).group(1)
        o_icon = 'http://chart.apis.google.com/chart' + re.search('<styleUrl>(.*?)</styleUrl>', outlet).group(1).strip('#msn_chart')
        
        # Add store
        store_to_add = Facility(name=o_name, geom=WKTSpatialElement("POINT(%s %s)"%(o_lat, o_lon)))
        db.session.add(store_to_add)
        db.session.commit()
        
        # Add icon
        store_to_add_icon = FacilityCustomData(schema_id = icon_schema.id, facility_id = store_to_add.id, data = o_icon)
        db.session.add(store_to_add_icon)
    
    db.session.commit()
    
def add_random_outlets_to_poly(x, bpid):
    print 'Adding level: 3'
    
    randompoint_fn = '''
    CREATE OR REPLACE FUNCTION RandomPoint (
                    geom Geometry,
                    maxiter INTEGER DEFAULT 1000
            )
            RETURNS Geometry
            AS $$
    DECLARE
            i INTEGER := 0;
            x0 DOUBLE PRECISION;
            dx DOUBLE PRECISION;
            y0 DOUBLE PRECISION;
            dy DOUBLE PRECISION;
            xp DOUBLE PRECISION;
            yp DOUBLE PRECISION;
            rpoint Geometry;
    BEGIN
            -- find envelope
            x0 = ST_XMin(geom);
            dx = (ST_XMax(geom) - x0);
            y0 = ST_YMin(geom);
            dy = (ST_YMax(geom) - y0);
            
            WHILE i < maxiter LOOP
                    i = i + 1;
                    xp = x0 + dx * random();
                    yp = y0 + dy * random();
                    rpoint = ST_SetSRID( ST_MakePoint( xp, yp ), ST_SRID(geom) );
                    EXIT WHEN ST_Within( rpoint, geom );
            END LOOP;
            
            IF i >= maxiter THEN
                    RAISE EXCEPTION 'RandomPoint: number of interations exceeded %', maxiter;
            END IF; 
            
            RETURN rpoint;
    END; 
    $$ LANGUAGE plpgsql;
    '''
    
    db.session.execute(randompoint_fn)
    db.session.commit()
    
    bp = BoundaryPolygons.query.get(bpid)
    boundary = bp.boundary
    b = bp.boundary.id

    #iconsets
    iconset = [
        'http://chart.apis.google.com/chart?chst=d_map_pin_letter&amp;chld=S|FF0000|FFFFFF',
        'http://chart.apis.google.com/chart?chst=d_map_pin_letter&amp;chld=P|00FF00|FFFFFF',
        'http://chart.apis.google.com/chart?chst=d_map_pin_letter&amp;chld=R|336699|FFFFFF',
    ]

    # Add icon type to store schema if it hasn't been added yet
    if not bool(FacilitySchema.query.filter_by(column_name='icon').count()):
        icon_schema = FacilitySchema(column_name = 'icon', data_type = FacilityColumnSchema_DataType.String)
        db.session.add(icon_schema)
        db.session.commit()
    else:
        icon_schema = FacilitySchema.query.filter_by(column_name = 'icon').one()

    # Add outlets
    stores_to_add = []
    for i in range(x):
        result=db.session.execute('select ST_AsText(RandomPoint((select geom from boundary_polygons where id= :id)))', { 'id':bpid })
        random_point = result.fetchone()[0]
        # Add store
        store_to_add = Facility(name='%s - Store %s' % (boundary.name, i), geom=WKTSpatialElement(random_point), boundary_id = b, facility_type_id = 1)
        db.session.add(store_to_add)
        db.session.commit()

        # Add icon
        store_to_add_icon = FacilityCustomData(schema_id = icon_schema.id, facility_id = store_to_add.id, data = iconset[random.randint(0,len(iconset)-1)])
        db.session.add(store_to_add_icon)
    
    db.session.commit()

def add_level_polys(level):
    print 'Adding level: %s'%level
    # Prepare poly Encoder
    encoder = cgpolyencode.GPolyEncoder()
    
    # Add level descriptions
    if not BoundaryLevelDesc.query.all():
        boundary_descs = [BoundaryLevelDesc(description=BOUNDARY_LEVELS_DESC[k]) for k in BOUNDARY_LEVELS_DESC]
        db.session.add_all(boundary_descs)
        db.session.commit()
    
    # Add polys
    level_desc = BoundaryLevelDesc.query.get(level)
    with open('../../samples/Level_%s.kml'%level, 'r') as f:
        x = ''.join(f.readlines())
    
    regions = re.findall('<Placemark>.*?</Placemark>', x, re.S)
    for k in range(len(regions)):
        try:
            region = regions[k]
            
            r_name = re.search('<name>(.*?)</name>', region).group(1)
            
            # Add region entry in Boundary table
            boundary = Boundary(name=r_name, level=level_desc)
            db.session.add(boundary)
            #db.session.commit()
            
            # Add polys for boundary
            coords_list = re.findall('coordinates>(.*?)</coordinates>', region, re.S)
            for j in range(len(coords_list)):
                coords = coords_list[j]
                print 'region (%s/%s) | coords (%s/%s)'%(k+1, len(regions), j+1, len(coords_list))
                #p_to_encode = [i.split(',')[:-1] for i in coords.strip().split(' ')]
                #for i in range(len(p_to_encode)): p_to_encode[i]=[float(p_to_encode[i][0]), float(p_to_encode[i][1])]
                #encoded_poly = encoder.encode(p_to_encode)
                wkt_poly = "POLYGON((%s))"%(', '.join([' '.join(i.split(',')[:-1][::-1]) for i in coords.strip().split(' ')]))
                #boundary_poly = BoundaryPolygons(boundary=boundary, geom=WKTSpatialElement(wkt_poly), encoded_poly=encoded_poly['points'], encoded_levels=encoded_poly['levels'])
                boundary_poly = BoundaryPolygons(boundary=boundary, geom=WKTSpatialElement(wkt_poly))
                db.session.add(boundary_poly)
        except:
            continue
            
    db.session.commit()


def re_add_boundaries_polys(level):
    print 'reAdding level: %s'%level
    # Prepare poly Encoder
    encoder = cgpolyencode.GPolyEncoder()
    
    # Add level descriptions
    if not BoundaryLevelDesc.query.all():
        boundary_descs = [BoundaryLevelDesc(description=BOUNDARY_LEVELS_DESC[k]) for k in BOUNDARY_LEVELS_DESC]
        db.session.add_all(boundary_descs)
        db.session.commit()
    
    # Add polys
    level_desc = BoundaryLevelDesc.query.get(level)
    with open('../../samples/Level_%s.kml'%level, 'r') as f:
        x = ''.join(f.readlines())
    
    regions = re.findall('<Placemark>.*?</Placemark>', x, re.S)
    for k in range(len(regions)):
        try:
            region = regions[k]
            
            r_name = re.search('<name>(.*?)</name>', region).group(1)
            
            # Add region entry in Boundary table
            boundary = Boundary.query.filter_by(name=r_name, level=level_desc)[0]          
            print boundary.name
            # Add polys for boundary
            coords_list = re.findall('coordinates>(.*?)</coordinates>', region, re.S)
            for j in range(len(coords_list)):
                coords = coords_list[j]
                print 'region (%s/%s) | coords (%s/%s)'%(k+1, len(regions), j+1, len(coords_list))
                #p_to_encode = [i.split(',')[:-1] for i in coords.strip().split(' ')]
                #for i in range(len(p_to_encode)): p_to_encode[i]=[float(p_to_encode[i][0]), float(p_to_encode[i][1])]
                #encoded_poly = encoder.encode(p_to_encode)
                wkt_poly = "POLYGON((%s))"%(', '.join([' '.join(i.split(',')[:-1][::-1]) for i in coords.strip().split(' ')]))
                #boundary_poly = BoundaryPolygons(boundary=boundary, geom=WKTSpatialElement(wkt_poly), encoded_poly=encoded_poly['points'], encoded_levels=encoded_poly['levels'])
                boundary_poly = BoundaryPolygons(boundary=boundary, geom=WKTSpatialElement(wkt_poly))
                db.session.add(boundary_poly)
                print 'Success'
        except:
            continue
            
    db.session.commit()
    
def define_hierarchy(parent, child):
    print 'Define hierarchy'
    
    # Get all parent polygon ids
    pbpoly_ids = []
    pbs = Boundary.query.filter_by(level_id=parent).all()
    for pb in pbs:
        for pbpoly in pb.BoundaryPolygons:
            pbpoly_ids.append(pbpoly.id)
    
    # Get all child boundaries
    cbs = Boundary.query.filter_by(level_id=child).all()
    for cb in cbs:
        print 'Defining parent for %s (id:%s)'%(cb.name, cb.id)
        try:
            # Get biggest poly in child boundary
            result = db.session.execute('select id from boundary_polygons where boundary_id = :cbid order by ST_Area(geom) desc limit 1', {'cbid': cb.id});
            max_cbpoly_id = result.fetchone()[0]
        except:
            continue
        
        # Get max intersection on all parent boundaries
        raw_query = 'select id, ST_Area(ST_Intersection((select geom from boundary_polygons where id = %s), geom)) as area_covered from boundary_polygons where id in (%s) order by area_covered desc limit 1'%(max_cbpoly_id, ','.join([str(x) for x in pbpoly_ids]))
        result = db.session.execute(raw_query)
        pb_of_c = result.fetchone()[0]
        
        # Assign that child to max parent
        cb.parent_id = BoundaryPolygons.query.get(pb_of_c).boundary.id
        
    db.session.commit()
    
def smoothen_polygons():
    print 'Smoothening polygons'
    polys = BoundaryPolygons.query.all()
    
    #Smoothen
    for poly in polys:
        print 'Smoothening %s'%poly.id
        raw_query = 'update boundary_polygons set geom = ST_Simplify((select geom from boundary_polygons where id = %s), 0.03) where id = %s'%(poly.id, poly.id)
        db.session.execute(raw_query);
    db.session.commit()
    
def encode_polygons():
    print 'Encoding polygons'
    polys = BoundaryPolygons.query.all()
    encoder = cgpolyencode.GPolyEncoder()
    
    #Encode
    for poly in polys:
        print 'Encoding %s'%poly.id
        poly.encoded_poly = encoder.encode([i[::-1] for i in poly.geom.coords(db.session)[0]])['points']
    db.session.commit()

    
def delete_small_regions():
    print 'Delete small regions'
    
    db.session.execute('delete from boundary_polygons where id in (select id from boundary_polygons where ST_Area(geom)<0.1)')
    db.session.commit()
        
def dump_parentless_cluster():
    sql = '''SELECT id, name from boundaries where level_id = 2 AND parent_id is NULL''';
    
    ret = db.session.execute(sql);
    
    for i in ret:
        print '''UPDATE boundaries SET parent_id =  WHERE id = ''' + str(i[0]) + ''';-- ''' + i[1]

def add_store_to_all_cluster():

    cluster = Boundary.query.filter (Boundary.level_id == 3, Boundary.parent_id != None) #, Boundary.name.like('%Jakarta%'))
    for obj in cluster:
        try:

            #for p in db.session.execute('''select id, ST_Area(geom)<0.1 from boundary_polygons where boundary_id = :id ''', { 'id': obj.id} ):  
                # if p[1] == False:
                    # add_random_outlets_to_poly(1, p[0])
            for p in BoundaryPolygons.query.filter(BoundaryPolygons.boundary_id == obj.id):
                add_random_outlets_to_poly(5, p.id)
        except:
            pass

def add_store_to_region(id, store_per_cluster):

    for obj in Boundary.query.filter_by(parent_id = id):

        for p in BoundaryPolygons.query.filter(BoundaryPolygons.boundary_id == obj.id):
            add_random_outlets_to_poly(store_per_cluster, p.id)

 
# add_outlets()
add_level_polys(1)
add_level_polys(2)
add_level_polys(3)

# # readd_level_polys(1)
# # readd_level_polys(2)

delete_small_regions()
define_hierarchy(2,3)
smoothen_polygons()

db.session.execute('DELETE FROM boundary_polygons where geom is NULL')
db.session.commit()
encode_polygons()




#add_random_outlets_to_poly(2, 6290)    # Add 20 outlets randomly to Aceh Besar
# dump_parentless_cluster()
# smoothen_polygons()
# db.session.execute('DELETE FROM boundary_polygons where geom is NULL')
# db.session.commit()
# encode_polygons()
add_store_to_all_cluster()
db.session.commit()
# add_store_to_region(10, 10)

