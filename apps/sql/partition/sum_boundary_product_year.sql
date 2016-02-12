-- Aggregate Bounday Year Sum Table based on Year.
-- Automatcially creates, and insert aggregated data to the proper partition table.
-- Bypasses the sum_aggregation_boundary_product_year trigger for faster performance.
CREATE OR REPLACE FUNCTION aggregate_boundary_product_year_sum ( int ) returns void as
$$
declare
p_year ALIAS FOR $1;
v_tablename varchar;
v_boundary_level_desc boundary_level_desc%rowtype;
BEGIN
    v_tablename := 'sum_boundary_product_year_y' || p_year::varchar;

IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
  
    EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
    ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_year CHECK ( date_year = ' || p_year::varchar || ' ))  INHERITS (sum_boundary_product_year)';
    
    EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_year_index ON '|| quote_ident(v_tablename) || '( boundary_id, product_id, facility_type_id, kpi_type, date_year )';  
    -- EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_facility_type_index ON '|| quote_ident(v_tablename) || '( boundary_id, product_id, facility_type_id, kpi_type, date_year )';  
END IF;

    EXECUTE format('INSERT INTO %I ( boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, target, data_point_count, product_id, date_year )
        SELECT k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, 
        k.facility_type_id,
        k.kpi_type, SUM(k.kpi), SUM(k.actual), SUM(k.target), COUNT(k.kpi),
        k.product_id,
        k.date_year
        FROM kpi k WHERE date_year = $1
        GROUP BY  k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, k.facility_type_id,
        k.date_year, k.kpi_type, k.product_id
        ORDER BY k.facility_boundary_id, k.kpi_type', v_tablename) using p_year;
    FOR v_boundary_level_desc in SELECT * FROM boundary_level_desc ORDER BY id DESC
    LOOP
        IF ( v_boundary_level_desc.id != 1 ) THEN
            -- raise NOTICE 'DOING boundary_level_id % to %',v_boundary_level_desc.id::varchar , (v_boundary_level_desc.id - 1)::varchar;
            EXECUTE format('INSERT INTO %I ( boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, target, data_point_count, product_id, date_year ) 
                SELECT k.boundary_parent_id, ( $1 - 1 ), b.parent_id,
                k.facility_type_id,
                k.kpi_type, SUM(k.kpi), SUM(k.actual), SUM(k.target), SUM(k.data_point_count), k.product_id,
                k.date_year
                FROM sum_boundary_product_year k 
                LEFT JOIN boundaries b on k.boundary_parent_id = b.id WHERE k.boundary_level_id = $1 AND k.date_year = $2
                GROUP BY 
                k.boundary_parent_id, boundary_level_id, b.parent_id, 
                k.facility_type_id,
                k.kpi_type, k.product_id,
                k.date_year
                ORDER BY k.boundary_parent_id, k.kpi_type', v_tablename) using v_boundary_level_desc.id, p_year;
        END IF;
    END LOOP;
    
END;
$$
LANGUAGE plpgsql;


