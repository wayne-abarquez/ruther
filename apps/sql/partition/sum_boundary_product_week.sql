
-- Aggregate Bounday Day Sum Table based on Month, Year.
-- Automatcially creates, and insert aggregated data to the proper partition table.
-- Bypasses the sum_boundary_product_week trigger for faster performance.
CREATE OR REPLACE FUNCTION aggregate_boundary_product_week_sum ( int, int, int ) returns void as
$$
declare
v_month ALIAS FOR $2;
v_year ALIAS FOR $3;
v_day ALIAS FOR $1;
v_tablename varchar;
v_start_date DATE;
-- v_end_date DATE;

v_start_year DATE;
v_end_year DATE;
v_boundary_level_desc boundary_level_desc%rowtype;
BEGIN
    v_tablename := 'sum_boundary_product_week_y' || v_year::varchar;
    v_start_date := DATE ( v_year::varchar || '-' || v_month::varchar || '-' || v_day::varchar);
    -- v_end_date := ( v_start_date + interval '1 year' );
    
    v_start_year := DATE ( v_year::varchar || '-1-1');
    v_end_year := v_start_year + interval '1 year';
    
IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
  
    EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
    ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_start_of_week CHECK ( date_start_of_week >= DATE ''' ||  to_char(v_start_year, 'YYYY-MM-DD') || ''' AND date_start_of_week < DATE ''' || to_char(v_end_year,'YYYY-MM-DD') || 
    '''))  INHERITS (sum_boundary_product_week)';
    
    EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_boundary_index ON '|| quote_ident(v_tablename) || '( boundary_id, product_id, facility_type_id, kpi_type, date_start_of_week )';  

END IF;

    EXECUTE format('INSERT INTO %I ( boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, target, data_point_count, product_id, date_start_of_week, date_end_of_week )
        SELECT k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, 
        k.facility_type_id,
        k.kpi_type, SUM(k.kpi), sum(k.actual), sum(k.target), COUNT(k.kpi),
        k.product_id,
        k.date_start_of_week, k.date_end_of_week
        FROM kpi k WHERE date_start_of_week = $1 
        GROUP BY  k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, k.facility_type_id,
        k.date_start_of_week, k.date_end_of_week, k.kpi_type, k.product_id
        ORDER BY k.facility_boundary_id, k.kpi_type', v_tablename) using v_start_date;
    FOR v_boundary_level_desc in SELECT * FROM boundary_level_desc ORDER BY id DESC
    LOOP
        IF ( v_boundary_level_desc.id != 1 ) THEN
            -- raise NOTICE 'DOING boundary_level_id % to %',v_boundary_level_desc.id::varchar , (v_boundary_level_desc.id - 1)::varchar;
            EXECUTE format('INSERT INTO %I ( boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, target, data_point_count, product_id, date_start_of_week, date_end_of_week ) 
                SELECT k.boundary_parent_id, ( $1 - 1 ), b.parent_id, k.facility_type_id,
                k.kpi_type, SUM(k.kpi), sum(k.actual), sum(k.target), SUM(k.data_point_count), k.product_id,
                k.date_start_of_week, k.date_end_of_week
                FROM sum_boundary_product_week k 
                LEFT JOIN boundaries b on k.boundary_parent_id = b.id WHERE k.boundary_level_id = $1 AND k.date_start_of_week = $2
                GROUP BY 
                k.boundary_parent_id, boundary_level_id, b.parent_id,  k.facility_type_id,
                k.kpi_type, k.product_id,
                k.date_start_of_week, k.date_end_of_week
                ORDER BY k.boundary_parent_id, k.kpi_type', v_tablename) using v_boundary_level_desc.id, v_start_date;
        END IF;
    END LOOP;
    
END;
$$
LANGUAGE plpgsql;




CREATE OR REPLACE FUNCTION sum_boundary_product_week_insert_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_year int;
    v_tablename varchar;
    v_start_date DATE;
    v_end_date DATE;
    v_start_of_week DATE;
BEGIN
    v_start_of_week := new.date_start_of_week;
    v_year := date_part('year', v_start_date);
    v_tablename := 'sum_boundary_product_week_y' || v_year::varchar;
    v_start_date := DATE ( v_year::varchar || '-1-1');
    v_end_date := ( v_start_date + interval '1 year' );

    IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
        EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
        ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_raw_date CHECK ( date_start_of_week >= DATE ''' ||  to_char(v_start_date, 'YYYY-MM-DD') || ''' AND date_start_of_week < DATE ''' || to_char(v_end_date,'YYYY-MM-DD') || 
        '''))  INHERITS (sum_boundary_product_week)';
    
        EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_boundary_index ON '|| quote_ident(v_tablename) || '( boundary_id, product_id, facility_type_id, kpi_type, date_start_of_week )';  
    END IF;
    --PERFORM add_sum_boundary_product_week_partition_table(r_year, r_month); -- check if partition table exists or not
    -- EXECUTE 'INSERT INTO ' || quote_indent(v_tablename) || ' SELECT ($1).*' using NEW;
    EXECUTE format('INSERT INTO %I SELECT ($1).*', v_tablename) using NEW;
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;



CREATE TRIGGER sum_boundary_product_week_insert_trigger
    BEFORE INSERT ON sum_boundary_product_week
    FOR EACH ROW EXECUTE PROCEDURE sum_boundary_product_week_insert_trigger();
