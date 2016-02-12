import os, sys, logging, datetime, time, random, simplejson, argparse

sys.path.append('../')

from app import db


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="WARNING!!!! This scripts will drop schema public and re-create it, before creating the ruther tables schema. Make sure you don't have any data.")
    parser.add_argument('--postgis', dest='postgis', action='store',
                       help='Path to your postgis installation')

    parser.add_argument('--db-name', dest='db_name', action='store',
                       help='your pgsql password')

    parser.add_argument('--username', dest='username', action='store',
                       help='your pgsql username')

    parser.add_argument('--password', dest='password', action='store',
                       help='your pgsql password')
                       
    parser.add_argument('--force', dest='force', action='store',
                       help='Yes, I want to destroy my existing tables, and data. NO REFUNDS!!!')

    db_uri = 'postgresql://%(creds)slocalhost:5432/%(db_name)s'
    args = parser.parse_args()
    db_name = 'ruther'
    if args.db_name:
        db_name = args.db_name
              

    creds = ''
    if args.username and args.password:
        creds = args.username + ':' + args.password +  '@'
    elif args.username:
        creds = args.username + '@'
 
    if args.postgis:
        if not os.path.isfile(os.path.join(args.postgis, 'postgis.sql')):
            print 'Unable to find ' + os.path.join(args.postgis, 'postgis.sql')
            
        if not os.path.isfile(os.path.join(args.postgis, 'spatial_ref_sys.sql')):
            print 'Unable to find ' + os.path.join(args.postgis, 'spatial_ref_sys.sql')
        
        if not (os.path.isfile(os.path.join(args.postgis, 'postgis.sql')) or os.path.isfile(os.path.join(args.postgis, 'spatial_ref_sys.sql'))):
            parser.print_help()
            sys.exit(0)

    if args.force:
        # app = Flask (__name__)
        # app.config.from_object('config')
        # app.config['DEBUG'] = os.environ.get('DEBUG',False)
        # app.config['SQLALCHEMY_DATABASE_URI'] = db_uri % { 'creds' : creds, 'db_name' : db_name }

        # db = SQLAlchemy(app)

        db.session.execute('''drop schema public cascade; create schema public;''')
        db.session.commit()
        
        f = open( os.path.join(args.postgis, 'postgis.sql') )
        s  = f.read()
        f.close()
        db.session.execute(s)
        # db.session.execute('''\\i %(file)s;''' % { 'file': os.path.join(args.postgis, 'postgis.sql') })
        
        f = open( os.path.join(args.postgis, 'spatial_ref_sys.sql') )
        s  = f.read()
        f.close()
        db.session.execute(s)
        
        # partition_sql_path = os.path.join('../sql/partition')
        # for filename in os.listdir(partition_sql_path):
            # if filename.endswith(".sql"):
                # f = open( os.path.join(partition_sql_path, filename) )
                # s  = f.read()
                # f.close()
                # db.session.execute(s)
                
        # db.session.execute('''\\i %(file)s;''' % { 'file': os.path.join(args.postgis, 'spatial_ref_sys.sql') })
        db.create_all()



    else:
        parser.print_help()
        sys.exit(0)
# db.session.execute('''
# create or replace function add_KPI_partition_table(varchar, date, date) returns void as
# $$
# begin

# IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=$1) = FALSE ) THEN
    # EXECUTE 'CREATE TABLE ' || 
    # $1 || 
    # ' (CHECK ( date >= DATE \'\'\' || 
    # $2 || 
    # \'\'\' AND date < DATE \'\'\' || 
    # $3 || 
    # \'\'\')) INHERITS (kpi)';
    
    # EXECUTE 'CREATE INDEX ' ||
    # $1 ||
    # '_date ON ' || 
    # $1 || 
    # ' (date)';
# END IF;
# END;

# $$
# language 'plpgsql';


# CREATE OR REPLACE FUNCTION KPI_insert_trigger()
# RETURNS TRIGGER AS $$
# DECLARE
    # r_year varchar; 
    # r_month varchar ;
    # r_day varchar; 
    # v_tablename varchar;
    # v_month_begin DATE;
    # v_month_end DATE;
# BEGIN
    # r_year:=  date_part('year', NEW.date);
    # r_month :=  date_part('month', NEW.date);
    # r_day :=  date_part('day', NEW.date);
    # v_month_begin := DATE ( r_year ||'-' || r_month || '-' || r_day );
    # v_month_end := DATE ( v_month_begin + interval '1 month' );
    # v_tablename := 'kpi_y' || r_year || 'm' || r_month;
    
    # PERFORM add_KPI_partition_table(v_tablename, v_month_begin, v_month_end); -- check if partition table exists or not
    # -- EXECUTE 'INSERT INTO ' || quote_indent(v_tablename) || ' SELECT ($1).*' using NEW;
    # EXECUTE format('INSERT INTO %I SELECT ($1).*', v_tablename) using NEW;
    # RETURN NEW;
# END;
# $$
# LANGUAGE plpgsql;

# CREATE TRIGGER KPI_insert_trigger
    # BEFORE INSERT ON KPI
    # FOR EACH ROW EXECUTE PROCEDURE KPI_insert_trigger();
    
# ''')

# db.session.commit()
    
# if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    # api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    # api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
# else:
    # api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))
