

CREATE OR REPLACE FUNCTION aggregate_boundary_sales_force_kpi_day_sum ( int, int, int ) returns void as
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
    v_tablename := 'ruther_sales_force_boundary_kpi_daily'; -- || v_year::varchar || '_m' || v_month::varchar;
    v_start_date := DATE ( v_year::varchar || '-' || v_month::varchar || '-' || v_day::varchar );
    v_end_date := ( v_start_date + interval '1 month' );

    EXECUTE format('INSERT INTO %I ( sales_force_id, sales_force_role_id, boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, target, data_point_count,  calendar_id, raw_date, day_of_week, date_day, date_month, date_year, date_quarter, date_start_of_week, date_end_of_week )
        SELECT k.sales_force_id, k.sales_force_role_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, 
        k.facility_type_id,
        k.kpi_type, SUM(k.kpi), sum(k.actual), sum(k.target), COUNT(k.kpi),
        k.calendar_id, k.raw_date, k.day_of_week, k.date_day, k.date_month, k.date_year, k.date_quarter, k.date_start_of_week, k.date_end_of_week
        FROM ruther_sales_force_facility_kpi_daily k WHERE date_day = $1 AND date_month = $2 AND date_year = $3
        GROUP BY k.sales_force_id, k.sales_force_role_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, k.facility_type_id,
        k.raw_date, k.date_day, k.date_month, k.date_year, k.date_quarter, k.date_start_of_week, k.date_end_of_week, k.kpi_type, k.calendar_id, k.day_of_week', v_tablename) using v_day, v_month, v_year;
    
    
    FOR v_boundary_level_desc in SELECT * FROM boundary_level_desc ORDER BY id DESC
    LOOP
        IF ( v_boundary_level_desc.id != 1 ) THEN
            -- raise NOTICE 'DOING boundary_level_id % to %',v_boundary_level_desc.id::varchar , (v_boundary_level_desc.id - 1)::varchar;
            EXECUTE format('INSERT INTO %I ( sales_force_id, sales_force_role_id, boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, target, data_point_count, calendar_id, raw_date, day_of_week, date_day, date_month, date_year, date_quarter, date_start_of_week, date_end_of_week ) 
                SELECT  k.sales_force_id, k.sales_force_role_id, k.boundary_parent_id, ( $1 - 1 ), b.parent_id, k.facility_type_id,
                k.kpi_type, SUM(k.kpi), sum(k.actual), sum(k.target), SUM(k.data_point_count),
                k.calendar_id, k.raw_date, k.day_of_week, k.date_day, k.date_month, k.date_year, k.date_quarter, k.date_start_of_week, k.date_end_of_week
                FROM ruther_sales_force_boundary_kpi_daily k 
                LEFT JOIN boundaries b on k.boundary_parent_id = b.id WHERE k.boundary_level_id = $1 AND k.date_day = $2 AND k.date_month = $3 AND k.date_year = $4
                GROUP BY k.sales_force_id, k.sales_force_role_id, 
                k.boundary_parent_id, boundary_level_id, b.parent_id,  k.facility_type_id,
                k.kpi_type,
                k.raw_date, k.date_day, k.date_month, k.date_year, k.date_quarter, k.date_start_of_week, k.date_end_of_week,  k.calendar_id, k.day_of_week', v_tablename) using v_boundary_level_desc.id, v_day, v_month, v_year;
        END IF;
    END LOOP;
    
END;
$$
LANGUAGE plpgsql;

-- MONTH BOUNDARY AGGREGATION

-- Aggregate Bounday Month Sum Table based on Month, Year.
-- Automatcially creates, and insert aggregated data to the proper partition table.
-- Bypasses the sum_boundary_product_month trigger for faster performance.
CREATE OR REPLACE FUNCTION aggregate_boundary_sales_force_kpi_month_sum ( int, int ) returns void as
$$
declare
p_month ALIAS FOR $1;
p_year ALIAS FOR $2;
v_tablename varchar;
v_boundary_level_desc boundary_level_desc%rowtype;
BEGIN
    v_tablename := 'ruther_sales_force_boundary_kpi_month';--|| p_year::varchar;

    EXECUTE format('INSERT INTO %I ( sales_force_id, sales_force_role_id, boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, target, data_point_count, date_month, date_year )
        SELECT k.sales_force_id, k.sales_force_role_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, 
        k.facility_type_id,
        k.kpi_type, SUM(k.kpi), sum(k.actual), sum(k.target), COUNT(k.kpi),
        k.date_month, k.date_year
        FROM ruther_sales_force_facility_kpi_daily k WHERE date_month = $1 AND date_year = $2
        GROUP BY  k.sales_force_id, k.sales_force_role_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, k.facility_type_id,
        k.date_month, k.date_year, k.kpi_type', v_tablename) using p_month, p_year;
    FOR v_boundary_level_desc in SELECT * FROM boundary_level_desc ORDER BY id DESC
    LOOP
        IF ( v_boundary_level_desc.id != 1 ) THEN
            -- raise NOTICE 'DOING boundary_level_id % to %',v_boundary_level_desc.id::varchar , (v_boundary_level_desc.id - 1)::varchar;
            EXECUTE format('INSERT INTO %I ( sales_force_id, sales_force_role_id, boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, target, data_point_count, date_month, date_year ) 
                SELECT  k.sales_force_id, k.sales_force_role_id, k.boundary_parent_id, ( $1 - 1 ), b.parent_id,
                k.facility_type_id,
                k.kpi_type, SUM(k.kpi), SUM(k.actual), SUM(k.target), SUM(k.data_point_count),
                k.date_month, k.date_year
                FROM ruther_sales_force_boundary_kpi_month k 
                LEFT JOIN boundaries b on k.boundary_parent_id = b.id WHERE k.boundary_level_id = $1 AND k.date_month = $2 AND k.date_year = $3
                GROUP BY k.sales_force_id, k.sales_force_role_id,
                k.boundary_parent_id, boundary_level_id, b.parent_id, 
                k.facility_type_id,
                k.kpi_type,
                k.date_month, k.date_year', v_tablename) using v_boundary_level_desc.id, p_month, p_year;
        END IF;
    END LOOP;
    
END;
$$
LANGUAGE plpgsql;

-- TO DO: Paritiion the data.
    
---- END MONTH BOUNDARY AGGR



---- START WEEK BOUNDARY AGGR

CREATE OR REPLACE FUNCTION aggregate_boundary_sales_force_kpi_week_sum ( int, int, int ) returns void as
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
    v_tablename := 'ruther_sales_force_boundary_kpi_weekly'; -- || v_year::varchar;
    v_start_date := DATE ( v_year::varchar || '-' || v_month::varchar || '-' || v_day::varchar);
    -- v_end_date := ( v_start_date + interval '1 year' );
    
    v_start_year := DATE ( v_year::varchar || '-1-1');
    v_end_year := v_start_year + interval '1 year';
    

    EXECUTE format('INSERT INTO %I ( sales_force_id, sales_force_role_id, boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, target, data_point_count, date_start_of_week, date_end_of_week )
        SELECT k.sales_force_id, k.sales_force_role_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, 
        k.facility_type_id,
        k.kpi_type, SUM(k.kpi), sum(k.actual), sum(k.target), COUNT(k.kpi),
        k.date_start_of_week, k.date_end_of_week
        FROM ruther_sales_force_facility_kpi_daily k WHERE date_start_of_week = $1 
        GROUP BY  k.sales_force_id, k.sales_force_role_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, k.facility_type_id,
        k.date_start_of_week, k.date_end_of_week, k.kpi_type', v_tablename) using v_start_date;
        
    FOR v_boundary_level_desc in SELECT * FROM boundary_level_desc ORDER BY id DESC
    LOOP
        IF ( v_boundary_level_desc.id != 1 ) THEN
            -- raise NOTICE 'DOING boundary_level_id % to %',v_boundary_level_desc.id::varchar , (v_boundary_level_desc.id - 1)::varchar;
            EXECUTE format('INSERT INTO %I ( sales_force_id, sales_force_role_id, boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, target, data_point_count, date_start_of_week, date_end_of_week ) 
                SELECT k.sales_force_id, k.sales_force_role_id, k.boundary_parent_id, ( $1 - 1 ), b.parent_id, k.facility_type_id,
                k.kpi_type, SUM(k.kpi), sum(k.actual), sum(k.target), SUM(k.data_point_count),
                k.date_start_of_week, k.date_end_of_week
                FROM ruther_sales_force_boundary_kpi_weekly k 
                LEFT JOIN boundaries b on k.boundary_parent_id = b.id WHERE k.boundary_level_id = $1 AND k.date_start_of_week = $2
                GROUP BY  k.sales_force_id, k.sales_force_role_id,
                k.boundary_parent_id, boundary_level_id, b.parent_id,  k.facility_type_id,
                k.kpi_type,
                k.date_start_of_week, k.date_end_of_week', v_tablename) using v_boundary_level_desc.id, v_start_date;
        END IF;
    END LOOP;
    
END;
$$
LANGUAGE plpgsql;

    
---- END WEEK BOUNDARY AGGR


---- SART: YEAR BOUNDARY AGGR

CREATE OR REPLACE FUNCTION aggregate_boundary_sales_force_kpi_year_sum ( int ) returns void as
$$
declare
p_year ALIAS FOR $1;
v_tablename varchar;
v_boundary_level_desc boundary_level_desc%rowtype;
BEGIN
    v_tablename := 'ruther_sales_force_boundary_kpi_year';-- || p_year::varchar;

    EXECUTE format('INSERT INTO %I ( sales_force_id, sales_force_role_id, boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, target, data_point_count, date_year )
        SELECT k.sales_force_id, k.sales_force_role_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, 
        k.facility_type_id,
        k.kpi_type, SUM(k.kpi), SUM(k.actual), SUM(k.target), COUNT(k.kpi),
        k.date_year
        FROM ruther_sales_force_facility_kpi_daily k WHERE date_year = $1
        GROUP BY k.sales_force_id, k.sales_force_role_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, k.facility_type_id,
        k.date_year, k.kpi_type', v_tablename) using p_year;
    FOR v_boundary_level_desc in SELECT * FROM boundary_level_desc ORDER BY id DESC
    LOOP
        IF ( v_boundary_level_desc.id != 1 ) THEN
            -- raise NOTICE 'DOING boundary_level_id % to %',v_boundary_level_desc.id::varchar , (v_boundary_level_desc.id - 1)::varchar;
            EXECUTE format('INSERT INTO %I ( sales_force_id, sales_force_role_id, boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, target, data_point_count, date_year ) 
                SELECT k.sales_force_id, k.sales_force_role_id, k.boundary_parent_id, ( $1 - 1 ), b.parent_id,
                k.facility_type_id,
                k.kpi_type, SUM(k.kpi), SUM(k.actual), SUM(k.target), SUM(k.data_point_count),
                k.date_year
                FROM ruther_sales_force_boundary_kpi_year k 
                LEFT JOIN boundaries b on k.boundary_parent_id = b.id WHERE k.boundary_level_id = $1 AND k.date_year = $2
                GROUP BY k.sales_force_id, k.sales_force_role_id,
                k.boundary_parent_id, boundary_level_id, b.parent_id, 
                k.facility_type_id, k.kpi_type, k.date_year', v_tablename) using v_boundary_level_desc.id, p_year;
        END IF;
    END LOOP;
    
END;
$$
LANGUAGE plpgsql;

---- END: YEAR BOUNDARY AGGR
