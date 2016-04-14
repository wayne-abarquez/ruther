ruther
======
---
####Installation notes:


PostGIS - http://postgis.net/docs/manual-2.0/postgis_installation.html

####Setting up ruther db:

#####Create a new database
```
sudo su postgres  
createdb -E UNICODE ruther  
createlang plpgsql ruther  
psql -d ruther -f /usr/share/postgresql/9.1/contrib/postgis-2.0/postgis.sql  
psql -d ruther -f /usr/share/postgresql/9.1/contrib/postgis-2.0/spatial_ref_sys.sql  
```

#####Create a new user (if a user named 'ruther' does not exist already)
```
createuser -P ruther
```

#####Grant permissions to user 'ruther' on the new database
```
psql ruther  
grant all on database ruther to ruther;  
grant all on spatial_ref_sys to ruther;  
grant all on geometry_columns to ruther;  
\q
```

#####Create tables
```
python db_create.py
```
