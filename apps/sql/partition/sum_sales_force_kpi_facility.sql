CREATE OR REPLACE FUNCTION aggregate_facility_sales_force_week_sum (int, int, int ) returns void as
$$
declare

v_tablename varchar;
v_year ALIAS FOR $3;
v_month ALIAS FOR $2;
v_day ALIAS FOR $1;
v_start_date DATE;
v_end_date DATE;

v_start_year DATE;
v_end_year DATE;
BEGIN
    v_tablename := 'ruther_sales_force_facility_kpi_weekly'; --- || v_year::varchar;
    v_start_date := DATE ( v_year::varchar || '-' || v_month::varchar || '-' || v_day::varchar);
    -- v_end_date := ( v_start_date + interval '1 year' );
    v_start_year := DATE ( v_year::varchar || '-1-1');
    v_end_year := v_start_year + interval '1 year';

    EXECUTE format('INSERT INTO %I ( sales_force_id, sales_force_role_id, facility_id, facility_type_id, facility_boundary_id, facility_boundary_level_id, facility_boundary_parent_id, kpi_type, kpi, actual, target, data_point_count, date_start_of_week, date_end_of_week )
        SELECT k.sales_force_id, k.sales_force_role_id, k.facility_id, k.facility_type_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, 
        k.kpi_type, SUM(k.kpi), SUM(k.actual), SUM(k.target), COUNT(k.kpi),
        k.date_start_of_week, k.date_end_of_week
        FROM ruther_sales_force_facility_kpi_daily k WHERE date_start_of_week = $1
        GROUP BY  k.sales_force_id, k.sales_force_role_id, k.facility_id, k.facility_type_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id,
        date_start_of_week, date_end_of_week, k.kpi_type', v_tablename) using v_start_date;

END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION aggregate_facility_sales_force_kpi_month_sum ( int, int ) returns void as
$$
declare

v_tablename varchar;
p_month ALIAS FOR $1;
p_year ALIAS FOR $2;
BEGIN
    v_tablename := 'ruther_sales_force_facility_kpi_month'; -- || p_year::varchar;

    EXECUTE format('INSERT INTO %I ( sales_force_id, sales_force_role_id, facility_id, facility_type_id, facility_boundary_id, facility_boundary_level_id, facility_boundary_parent_id, kpi_type, kpi, actual, target, data_point_count, date_month, date_year )
        SELECT k.sales_force_id, k.sales_force_role_id, k.facility_id, k.facility_type_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, 
        k.kpi_type, SUM(k.kpi), SUM(k.actual), SUM(k.target), COUNT(k.kpi),
        k.date_month, k.date_year
        FROM ruther_sales_force_facility_kpi_daily k WHERE date_month = $1 AND date_year = $2
        GROUP BY k.sales_force_id, k.sales_force_role_id, k.facility_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, k.facility_type_id,
        k.date_month, k.date_year, k.kpi_type', v_tablename) using p_month, p_year;
   
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION aggregate_facility_sales_force_kpi_year_sum ( int ) returns void as
$$
declare
v_tablename varchar;
v_year ALIAS FOR $1;
BEGIN
    v_tablename := 'ruther_sales_force_facility_kpi_year' ; --|| v_year::varchar;

    EXECUTE format('INSERT INTO %I ( sales_force_id, sales_force_role_id, facility_id, facility_type_id, facility_boundary_id, facility_boundary_level_id, facility_boundary_parent_id, kpi_type, kpi, actual, target, data_point_count, date_year )
        SELECT k.sales_force_id, k.sales_force_role_id, k.facility_id, k.facility_type_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, 
        k.kpi_type, SUM(k.kpi), SUM(k.actual), SUM(k.target), COUNT(k.kpi),
        k.date_year
        FROM ruther_sales_force_facility_kpi_daily k WHERE date_year = $1
        GROUP BY k.sales_force_id, k.sales_force_role_id, k.facility_id, k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, k.facility_type_id,
        k.date_year, k.kpi_type', v_tablename) using v_year;
END;
$$
LANGUAGE plpgsql;
