
-- Aggregate Bounday Day Sum Table based on Month, Year.
-- Automatcially creates, and insert aggregated data to the proper partition table.
-- Bypasses the sum_boundary_product_day trigger for faster performance.
CREATE OR REPLACE FUNCTION aggregate_boundary_day_sum ( int, int, int ) returns void as
$$
declare
v_day ALIAS FOR $1;
v_month ALIAS FOR $2;
v_year ALIAS FOR $3;
v_start_date DATE;
v_end_date DATE;
v_tablename varchar;
v_boundary_level_desc boundary_level_desc%rowtype;
BEGIN
    v_tablename := 'sum_boundary_day_y' || v_year::varchar || '_m' || v_month::varchar;
    v_start_date := DATE ( v_year::varchar || '-' || v_month::varchar || '-' || v_day::varchar );
    v_end_date := ( v_start_date + interval '1 month' );
IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
  
    EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
    ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_raw_date CHECK ( raw_date >= DATE ''' ||  to_char(v_start_date, 'YYYY-MM-DD') || ''' AND raw_date < DATE ''' || to_char(v_end_date,'YYYY-MM-DD') || 
    '''), CONSTRAINT ' || quote_ident(v_tablename) || '_month_year CHECK ( date_month = '|| date_part('month', v_start_date) || ' AND date_year = ' || date_part('year', v_start_date) || ' ))  INHERITS (sum_boundary_day)';
    
    EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_boundary_kpi ON '|| quote_ident(v_tablename) || '( boundary_id, facility_type_id, kpi_type, date_day, date_month, date_year )';  

END IF;

    EXECUTE format('INSERT INTO %I ( boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, data_point_count, calendar_id, raw_date, day_of_week, date_day, date_month, date_year, date_quarter, date_start_of_week, date_end_of_week )
        SELECT k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, 
        k.facility_type_id,
        k.kpi_type, SUM(k.kpi), sum(k.actual), COUNT(k.kpi),
        k.calendar_id, k.raw_date, k.day_of_week, k.date_day, k.date_month, k.date_year, k.date_quarter, k.date_start_of_week, k.date_end_of_week
        FROM ruther_facility_kpi k WHERE date_day = $1 AND date_month = $2 AND date_year = $3
        GROUP BY  k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, k.facility_type_id,
        k.raw_date, k.date_day, k.date_month, k.date_year, k.date_quarter, k.date_start_of_week, k.date_end_of_week, k.kpi_type, k.calendar_id, k.day_of_week
        ORDER BY k.raw_date, k.facility_boundary_id, k.kpi_type', v_tablename) using v_day, v_month, v_year;
    FOR v_boundary_level_desc in SELECT * FROM boundary_level_desc ORDER BY id DESC
    LOOP
        IF ( v_boundary_level_desc.id != 1 ) THEN
            -- raise NOTICE 'DOING boundary_level_id % to %',v_boundary_level_desc.id::varchar , (v_boundary_level_desc.id - 1)::varchar;
            EXECUTE format('INSERT INTO %I ( boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, data_point_count, calendar_id, raw_date, day_of_week, date_day, date_month, date_year, date_quarter, date_start_of_week, date_end_of_week ) 
                SELECT k.boundary_parent_id, ( $1 - 1 ), b.parent_id, k.facility_type_id,
                k.kpi_type, SUM(k.kpi), sum(k.actual), SUM(k.data_point_count),
                k.calendar_id, k.raw_date, k.day_of_week, k.date_day, k.date_month, k.date_year, k.date_quarter, k.date_start_of_week, k.date_end_of_week
                FROM sum_boundary_day k 
                LEFT JOIN boundaries b on k.boundary_parent_id = b.id WHERE k.boundary_level_id = $1 AND k.date_day = $2 AND k.date_month = $3 AND k.date_year = $4
                GROUP BY 
                k.boundary_parent_id, boundary_level_id, b.parent_id,  k.facility_type_id,
                k.kpi_type,
                k.raw_date, k.date_day, k.date_month, k.date_year, k.date_quarter, k.date_start_of_week, k.date_end_of_week,  k.calendar_id, k.day_of_week
                ORDER BY k.raw_date, k.boundary_parent_id, k.kpi_type', v_tablename) using v_boundary_level_desc.id, v_day, v_month, v_year;
        END IF;
    END LOOP;
    
END;
$$
LANGUAGE plpgsql;


-- CREATE OR REPLACE FUNCTION sum_boundary_product_day_insert_trigger()
-- RETURNS TRIGGER AS $$
-- DECLARE
    -- r_year varchar; 
    -- r_month varchar ;
    -- r_day varchar; 
    -- v_tablename varchar;
    -- v_month_begin DATE;
    -- v_month_end DATE;
    -- v_start_date DATE;
    -- v_end_date DATE;
-- BEGIN
    -- r_year:=  date_part('year', NEW.raw_date);
    -- r_month :=  date_part('month', NEW.raw_date);
    -- r_day :=  date_part('day', NEW.raw_date);
    -- v_month_begin := DATE ( r_year ||'-' || r_month || '-' || r_day );
    -- v_month_end := DATE ( v_month_begin + interval '1 month' );
    -- v_tablename := 'sum_boundary_product_day_y' || trim(r_year) || 'm' || trim(r_month);
    -- v_start_date := DATE (trim(r_year) || '-' || trim(r_month) || '-1');
    -- v_end_date := ( v_start_date + interval '1 month' );

    -- IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
    -- EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
    -- ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_raw_date CHECK ( raw_date >= DATE ''' ||  to_char(v_start_date, 'YYYY-MM-DD') || ''' AND raw_date < DATE ''' || to_char(v_end_date,'YYYY-MM-DD') || 
    -- '''), CONSTRAINT ' || quote_ident(v_tablename) || '_month_year CHECK ( date_month = '|| date_part('month', v_start_date) || ' AND date_year = ' || date_part('year', v_start_date) || ' ))  INHERITS (sum_boundary_product_day)';
    -- EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_boundary_product_kpi ON '|| quote_ident(v_tablename) || '( boundary_id, product_id, kpi_type, date_day, date_month, date_year )';  
    -- END IF;

    -- EXECUTE format('INSERT INTO %I SELECT ($1).*', v_tablename) using NEW;
    -- RETURN NULL;
-- END;
-- $$
-- LANGUAGE plpgsql;

-- CREATE TRIGGER sum_boundary_product_day_insert_trigger
    -- BEFORE INSERT ON sum_boundary_product_day
    -- FOR EACH ROW EXECUTE PROCEDURE sum_boundary_product_day_insert_trigger();
