-- Aggregate Bounday Month Sum Table based on Month, Year.
-- Automatcially creates, and insert aggregated data to the proper partition table.
-- Bypasses the sum_aggregation_boundary_week trigger for faster performance.
CREATE OR REPLACE FUNCTION aggregate_facility_week_sum ( int, int, int ) returns void as
$$
declare

v_tablename varchar;
v_year ALIAS FOR $3;
v_month ALIAS FOR $2;
v_day ALIAS FOR $1;
v_start_date DATE;
-- v_end_date DATE;

v_start_year DATE;
v_end_year DATE;
BEGIN
    v_tablename := 'sum_facility_week_y' || v_year::varchar;
    v_start_date := DATE ( v_year::varchar || '-' || v_month::varchar || '-' || v_day::varchar);
    -- v_end_date := ( v_start_date + interval '1 year' );
    
    v_start_year := DATE ( v_year::varchar || '-1-1');
    v_end_year := v_start_year + interval '1 year';
        
    IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
      
        EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
        ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_start_of_week CHECK ( date_start_of_week >= DATE ''' || to_char(v_start_year, 'YYYY-MM-DD') ||''' AND date_start_of_week < DATE '''|| to_char(v_end_year, 'YYYY-MM-DD') ||'''))  INHERITS (sum_facility_week)';
        
        EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_facility_index ON '|| quote_ident(v_tablename) || '( facility_id, kpi_type, date_start_of_week )';  
        EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_facility_type_index ON '|| quote_ident(v_tablename) || '( facility_type_id,  kpi_type, date_start_of_week )';  

    END IF;

    EXECUTE format('INSERT INTO %I ( facility_id, facility_type_id, facility_boundary_id, facility_boundary_level_id, facility_boundary_parent_id, kpi_type, kpi, actual, data_point_count, date_start_of_week, date_end_of_week )
        SELECT k.facility_id, k.facility_type_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, 
        k.kpi_type, SUM(k.kpi), SUM(k.actual), COUNT(k.kpi),
        k.date_start_of_week, k.date_end_of_week
        FROM ruther_facility_kpi k WHERE date_start_of_week = $1
        GROUP BY  k.facility_id, k.facility_type_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id,
        date_start_of_week, date_end_of_week, k.kpi_type
        ORDER BY k.facility_boundary_id, k.kpi_type', v_tablename) using v_start_date;
   
END;
$$
LANGUAGE plpgsql;


-- CREATE OR REPLACE FUNCTION sum_aggregation_facility_week_insert_trigger()
-- RETURNS TRIGGER AS $$
-- DECLARE
    -- v_year int;
    -- v_tablename varchar;
    -- v_start_date DATE;
    -- v_end_date DATE;
    -- v_start_of_week DATE;
-- BEGIN
    -- v_start_of_week := new.date_start_of_week;
    -- v_year := date_part('year', v_start_date);
    -- v_tablename := 'sum_facility_week_y' || v_year::varchar;
    -- v_start_date := DATE ( v_year::varchar || '-1-1');
    -- v_end_date := ( v_start_date + interval '1 year' );

    -- IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
    
    -- EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
     -- ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_start_of_week CHECK ( date_start_of_week >= DATE ''' ||  to_char(v_start_date, 'YYYY-MM-DD') || ''' AND date_start_of_week < DATE ''' || to_char(v_end_date,'YYYY-MM-DD') || 
     -- ' ))  INHERITS (sum_facility_week)';
   
    -- EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_facility_index ON '|| quote_ident(v_tablename) || '( facility_id, kpi_type, date_start_of_week )';  
    -- EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_facility_type_index ON '|| quote_ident(v_tablename) || '( facility_type_id, kpi_type, date_start_of_week )';   
    -- END IF;

    -- EXECUTE format('INSERT INTO %I SELECT ($1).*', v_tablename) using NEW;
    -- RETURN NULL;
-- END;
-- $$
-- LANGUAGE plpgsql;

-- CREATE TRIGGER sum_aggregation_facility_week_insert_trigger
    -- BEFORE INSERT ON sum_facility_week
    -- FOR EACH ROW EXECUTE PROCEDURE sum_aggregation_facility_week_insert_trigger();
