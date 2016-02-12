-- Aggregate Bounday Month Sum Table based on Month, Year.
-- Automatcially creates, and insert aggregated data to the proper partition table.
-- Bypasses the sum_boundary_product_month trigger for faster performance.
CREATE OR REPLACE FUNCTION aggregate_boundary_month_sum ( int, int ) returns void as
$$
declare
p_month ALIAS FOR $1;
p_year ALIAS FOR $2;
v_tablename varchar;
v_boundary_level_desc boundary_level_desc%rowtype;
BEGIN
    v_tablename := 'sum_boundary_month_y' || p_year::varchar;

IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
  
    EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
    ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_year CHECK ( date_year = ' || p_year::varchar || ' ))  INHERITS (sum_boundary_month)';
    
    EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_boundary_index ON '|| quote_ident(v_tablename) || '( boundary_id, facility_type_id, kpi_type, date_month, date_year )';  

END IF;

    EXECUTE format('INSERT INTO %I ( boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, data_point_count, date_month, date_year )
        SELECT k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, 
        k.facility_type_id,
        k.kpi_type, SUM(k.kpi), sum(k.actual), COUNT(k.kpi),
        k.date_month, k.date_year
        FROM ruther_facility_kpi k WHERE date_month = $1 AND date_year = $2
        GROUP BY  k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, k.facility_type_id,
        k.date_month, k.date_year, k.kpi_type
        ORDER BY k.facility_boundary_id, k.kpi_type', v_tablename) using p_month, p_year;
    FOR v_boundary_level_desc in SELECT * FROM boundary_level_desc ORDER BY id DESC
    LOOP
        IF ( v_boundary_level_desc.id != 1 ) THEN
            -- raise NOTICE 'DOING boundary_level_id % to %',v_boundary_level_desc.id::varchar , (v_boundary_level_desc.id - 1)::varchar;
            EXECUTE format('INSERT INTO %I ( boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, data_point_count, date_month, date_year ) 
                SELECT k.boundary_parent_id, ( $1 - 1 ), b.parent_id,
                k.facility_type_id,
                k.kpi_type, SUM(k.kpi), SUM(k.actual), SUM(k.data_point_count),
                k.date_month, k.date_year
                FROM sum_boundary_product_month k 
                LEFT JOIN boundaries b on k.boundary_parent_id = b.id WHERE k.boundary_level_id = $1 AND k.date_month = $2 AND k.date_year = $3
                GROUP BY 
                k.boundary_parent_id, boundary_level_id, b.parent_id, 
                k.facility_type_id,
                k.kpi_type,
                k.date_month, k.date_year
                ORDER BY k.boundary_parent_id, k.kpi_type', v_tablename) using v_boundary_level_desc.id, p_month, p_year;
        END IF;
    END LOOP;
    
END;
$$
LANGUAGE plpgsql;


-- CREATE OR REPLACE FUNCTION sum_boundary_product_month_insert_trigger()
-- RETURNS TRIGGER AS $$
-- DECLARE
    -- v_tablename varchar;
    -- v_month int;
    -- v_year int;
-- BEGIN
    -- v_month := new.date_month;
    -- v_year := new.date_year;
    -- v_tablename := 'sum_boundary_product_month_y' || v_year::varchar;


    -- IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
    
    -- EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
    -- ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_year CHECK ( date_year = ' || v_year::varchar|| ' ))  INHERITS (sum_boundary_product_month)';
   
    -- EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_boundary_product_kpi_index ON '|| quote_ident(v_tablename) || '( boundary_id, product_id, kpi_type, date_month, date_year )';  
    
    -- END IF;

    -- EXECUTE format('INSERT INTO %I SELECT ($1).*', v_tablename) using NEW;
    -- RETURN NULL;
-- END;
-- $$
-- LANGUAGE plpgsql;



-- CREATE TRIGGER sum_boundary_product_month_insert_trigger
    -- BEFORE INSERT ON sum_boundary_product_month
    -- FOR EACH ROW EXECUTE PROCEDURE sum_boundary_product_month_insert_trigger();
