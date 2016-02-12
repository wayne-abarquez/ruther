-- Aggregate Bounday Year Sum Table based on Year.
-- Automatcially creates, and insert aggregated data to the proper partition table.
-- Bypasses the sum_aggregation_boundary_year trigger for faster performance.
CREATE OR REPLACE FUNCTION aggregate_facility_year_sum ( int ) returns void as
$$
declare
v_tablename varchar;
v_year ALIAS FOR $1;
BEGIN
    v_tablename := 'sum_facility_year_y' || v_year::varchar;

IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
  
    EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
    ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_year CHECK ( date_year = ' || v_year::varchar || ' ))  INHERITS (sum_facility_year)';
    
    EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_facility_index ON '|| quote_ident(v_tablename) || '( facility_id,  kpi_type, date_year )';  
    EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_facility_type_index ON '|| quote_ident(v_tablename) || '( facility_type_id,  kpi_type, date_year )';  

END IF;

    EXECUTE format('INSERT INTO %I ( facility_id, facility_type_id, facility_boundary_id, facility_boundary_level_id, facility_boundary_parent_id, kpi_type, kpi, actual, data_point_count, date_year )
        SELECT k.facility_id, k.facility_type_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, 
        k.kpi_type, SUM(k.kpi), SUM(k.actual), COUNT(k.kpi),
        k.date_year
        FROM ruther_facility_kpi k WHERE date_year = $1
        GROUP BY  k.facility_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, k.facility_type_id,
        k.date_year, k.kpi_type
        ORDER BY k.facility_boundary_id, k.kpi_type', v_tablename) using v_year;
END;
$$
LANGUAGE plpgsql;


-- CREATE OR REPLACE FUNCTION sum_facility_product_year_insert_trigger()
-- RETURNS TRIGGER AS $$
-- DECLARE
    -- v_tablename varchar;

    -- v_year int;

-- BEGIN
    -- v_year := new.date_year;
    -- v_tablename := 'sum_facility_product_year_y' || v_year::varchar;

    -- IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
    
        -- EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
        -- ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_year CHECK ( date_year = ' || date_part('year', v_start_date) || ' ))  INHERITS (sum_facility_product_year)';
       
        -- EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_facility_index ON '|| quote_ident(v_tablename) || '( facility_id, product_id, kpi_type, date_month, date_year )';  
        -- EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_facility_type_index ON '|| quote_ident(v_tablename) || '( facility_type_id, product_id, kpi_type, date_month, date_year )';   
    -- END IF;

    -- EXECUTE format('INSERT INTO %I SELECT ($1).*', v_tablename) using NEW;
    -- RETURN NULL;
-- END;
-- $$
-- LANGUAGE plpgsql;



-- CREATE TRIGGER sum_facility_product_year_insert_trigger
    -- BEFORE INSERT ON sum_facility_product_year
    -- FOR EACH ROW EXECUTE PROCEDURE sum_facility_product_year_insert_trigger();
