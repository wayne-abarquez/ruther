-- Aggregate Bounday Month Sum Table based on Month, Year.
-- Automatcially creates, and insert aggregated data to the proper partition table.
-- Bypasses the sum_aggregation_boundary_month trigger for faster performance.
CREATE OR REPLACE FUNCTION aggregate_facility_month_sum ( int, int ) returns void as
$$
declare

v_tablename varchar;
p_month ALIAS FOR $1;
p_year ALIAS FOR $2;
BEGIN
    v_tablename := 'sum_facility_month_y' || p_year::varchar;

    IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
      
        EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
        ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_year CHECK ( date_year = ' || p_year::varchar || ' ))  INHERITS (sum_facility_month)';
        
        EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_facility_index ON '|| quote_ident(v_tablename) || '( facility_id, kpi_type, date_month, date_year )';  
        EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_facility_type_index ON '|| quote_ident(v_tablename) || '( facility_type_id, kpi_type, date_month, date_year )';  

    END IF;

    EXECUTE format('INSERT INTO %I ( facility_id, facility_type_id, facility_boundary_id, facility_boundary_level_id, facility_boundary_parent_id, kpi_type, kpi, actual, data_point_count, date_month, date_year )
        SELECT k.facility_id, k.facility_type_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, 
        k.kpi_type, SUM(k.kpi), SUM(k.actual), COUNT(k.kpi),
        k.date_month, k.date_year
        FROM ruther_facility_kpi k WHERE date_month = $1 AND date_year = $2
        GROUP BY  k.facility_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, k.facility_type_id,
        k.date_month, k.date_year, k.kpi_type
        ORDER BY k.facility_boundary_id, k.kpi_type', v_tablename) using p_month, p_year;
   
END;
$$
LANGUAGE plpgsql;


-- CREATE OR REPLACE FUNCTION sum_facility_product_month_insert_trigger()
-- RETURNS TRIGGER AS $$
-- DECLARE
    -- v_tablename varchar;
    -- v_month int;
    -- v_year int;
-- BEGIN
    -- v_month := new.date_month;
    -- v_year := new.date_year;

    -- v_tablename := 'sum_facility_product_month_y' || v_year::varchar;

    -- IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
    
    -- EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
    -- ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_year CHECK ( date_year = ' || v_year::varchar || ' ))  INHERITS (sum_facility_product_month)';
   
    -- EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_facility_index ON '|| quote_ident(v_tablename) || '( facility_id, product_id, kpi_type, date_month, date_year )';  
    -- EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_facility_type_index ON '|| quote_ident(v_tablename) || '( facility_type_id, product_id, kpi_type, date_month, date_year )';   
    -- END IF;

    -- EXECUTE format('INSERT INTO %I SELECT ($1).*', v_tablename) using NEW;
    -- RETURN NULL;
-- END;
-- $$
-- LANGUAGE plpgsql;



-- CREATE TRIGGER sum_facility_product_month_insert_trigger
    -- BEFORE INSERT ON sum_facility_product_month
    -- FOR EACH ROW EXECUTE PROCEDURE sum_facility_product_month_insert_trigger();
