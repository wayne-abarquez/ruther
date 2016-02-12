-- THIS IS THE FUNCTIONS, and TRIGGER to dynamically partition rows for KPI tables.

create or replace function add_KPI_partition_table( varchar, varchar ) returns void as
$$
declare
v_start_date DATE;
v_end_date DATE;
v_tablename varchar;
begin
    v_tablename := 'kpi_y' || trim($1) || '_m' || trim($2);
    v_start_date := DATE (trim($1) || '-' || trim($2) || '-1');
    v_end_date := ( v_start_date + interval '1 month' );
IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
    EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
    ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_raw_date CHECK ( raw_date >= DATE ''' ||  to_char(v_start_date, 'YYYY-MM-DD') || ''' AND raw_date < DATE ''' || to_char(v_end_date,'YYYY-MM-DD') || 
    '''), CONSTRAINT ' || quote_ident(v_tablename) || '_month_year CHECK ( date_month = '|| date_part('month', v_start_date) || ' AND date_year = ' || date_part('year', v_start_date) || ' ))  INHERITS (kpi)';
    
    EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_date_product_facility_index ON '|| quote_ident(v_tablename) || '( raw_date, product_id, facility_boundary_id )';  
END IF;
END;

$$
language 'plpgsql';


CREATE OR REPLACE FUNCTION KPI_insert_trigger()
RETURNS TRIGGER AS $$
DECLARE
    r_year varchar; 
    r_month varchar ;
    r_day varchar; 
    v_tablename varchar;
    v_month_begin DATE;
    v_month_end DATE;
    v_start_date DATE;
    v_end_date DATE;
BEGIN
    r_year:=  date_part('year', NEW.raw_date);
    r_month :=  date_part('month', NEW.raw_date);
    r_day :=  date_part('day', NEW.raw_date);
    v_month_begin := DATE ( r_year ||'-' || r_month || '-' || r_day );
    v_month_end := DATE ( v_month_begin + interval '1 month' );
    v_tablename := 'kpi_y' || trim(r_year) || 'm' || trim(r_month);
    v_start_date := DATE (trim(r_year) || '-' || trim(r_month) || '-1');
    v_end_date := ( v_start_date + interval '1 month' );
    IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
    EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
    ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_raw_date CHECK ( raw_date >= DATE ''' ||  to_char(v_start_date, 'YYYY-MM-DD') || ''' AND raw_date < DATE ''' || to_char(v_end_date,'YYYY-MM-DD') || 
    '''), CONSTRAINT ' || quote_ident(v_tablename) || '_month_year CHECK ( date_month = '|| date_part('month', v_start_date) || ' AND date_year = ' || date_part('year', v_start_date) || ' ))  INHERITS (kpi)';
    
    EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_date_product_facility_index ON '|| quote_ident(v_tablename) || '( raw_date, product_id, facility_boundary_id )';  
    END IF;
    -- PERFORM add_KPI_partition_table(r_year, r_month); -- check if partition table exists or not
    -- EXECUTE 'INSERT INTO ' || quote_indent(v_tablename) || ' SELECT ($1).*' using NEW;
    EXECUTE format('INSERT INTO %I SELECT ($1).*', v_tablename) using NEW;
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER KPI_insert_trigger
    BEFORE INSERT ON KPI
    FOR EACH ROW EXECUTE PROCEDURE KPI_insert_trigger();
