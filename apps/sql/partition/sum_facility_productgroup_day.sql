-- PRODUCT GROUP Aggregation is more complex than just a single products.



-- Aggregate Bounday Day Sum Table based on Month, Year.
-- Automatcially creates, and insert aggregated data to the proper partition table.
-- Bypasses the sum_facility_productgroup_day trigger for faster performance.
CREATE OR REPLACE FUNCTION aggregate_facility_productgroup_day_sum ( int, int, int ) returns void as
$$
declare
v_day ALIAS FOR $1;
v_month ALIAS FOR $2;
v_year ALIAS FOR $3;
v_start_date DATE;
v_end_date DATE;
v_tablename varchar;
BEGIN
    INSERT INTO sum_facility_productgroup_day ( facility_id, facility_boundary_id, facility_boundary_parent_id, facility_boundary_level_id, facility_type_id, kpi_type, kpi, actual, target, data_point_count, product_group_id, product_group_parent_id, calendar_id, raw_date, day_of_week, date_day, date_month, date_year, date_quarter, date_start_of_week, date_end_of_week )
        SELECT k.facility_id, k.facility_boundary_id, k.facility_boundary_parent_id, k.facility_boundary_level_id, 
        k.facility_type_id,
        k.kpi_type, SUM(k.kpi), SUM(k.actual), SUM(k.target), COUNT(k.kpi),
        pgm.group_id, pg.parent_id,
        k.calendar_id, k.raw_date, k.day_of_week, k.date_day, k.date_month, k.date_year, k.date_quarter, k.date_start_of_week, k.date_end_of_week
        FROM kpi k 
        LEFT JOIN productgroup_map pgm ON pgm.product_id = k.product_id
        LEFT JOIN product_group pg ON pg.id = pgm.group_id
        WHERE k.date_day = v_day AND k.date_month = v_month AND k.date_year = v_year
        GROUP BY k.facility_id, k.facility_boundary_id, k.facility_boundary_parent_id, k.facility_boundary_level_id,  k.facility_type_id,
        k.raw_date, k.date_day, k.date_month, k.date_year, k.date_quarter, k.date_start_of_week, k.date_end_of_week, k.kpi_type, pgm.group_id, pg.parent_id, k.calendar_id, k.day_of_week;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sum_facility_productgroup_day_insert_trigger()
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
    v_parent_id int;
BEGIN
    r_year:=  date_part('year', NEW.raw_date);
    r_month :=  date_part('month', NEW.raw_date);
    r_day :=  date_part('day', NEW.raw_date);
    v_month_begin := DATE ( r_year ||'-' || r_month || '-' || r_day );
    v_month_end := DATE ( v_month_begin + interval '1 month' );
    v_tablename := 'sum_facility_productgroup_day_y' || trim(r_year) || 'm' || trim(r_month);
    v_start_date := DATE (trim(r_year) || '-' || trim(r_month) || '-1');
    v_end_date := ( v_start_date + interval '1 month' );

    IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
    EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
    ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_raw_date CHECK ( raw_date >= DATE ''' ||  to_char(v_start_date, 'YYYY-MM-DD') || ''' AND raw_date < DATE ''' || to_char(v_end_date,'YYYY-MM-DD') || 
    '''), CONSTRAINT ' || quote_ident(v_tablename) || '_month_year CHECK ( date_month = '|| date_part('month', v_start_date) || ' AND date_year = ' || date_part('year', v_start_date) || ' ))  INHERITS (sum_facility_productgroup_day)';
    EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_day_index ON '|| quote_ident(v_tablename) || '( facility_id, product_group_id, kpi_type, date_day, date_month, date_year )';  
    EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_raw_date_index ON '|| quote_ident(v_tablename) || '( facility_id, product_group_id, kpi_type, raw_date )';  
    END IF;
    
    -- just in case if the INSERT is for an existing row, then just update.
    IF ( EXISTS ( SELECT id FROM sum_facility_productgroup_day where product_group_id = NEW.product_group_id and raw_date = NEW.raw_date and facility_id = NEW.facility_id AND kpi_type = NEW.kpi_type) = FALSE ) THEN
        EXECUTE format('INSERT INTO %I SELECT ($1).*', v_tablename) using NEW;
    ELSE
        UPDATE sum_facility_productgroup_day 
            SET kpi = ( kpi + NEW.kpi ), actual = ( actual + NEW.actual), target = (target + NEW.target), data_point_count = ( data_point_count + NEW.data_point_count ) 
            WHERE product_group_id = NEW.product_group_id AND raw_date = NEW.raw_date AND facility_id = NEW.facility_id AND kpi_type = NEW.kpi_type;
    END IF;
    
    -- aggregate the value upwards if possible.
    IF ( NEW.product_group_parent_id is not NULL) THEN
        SELECT INTO v_parent_id parent_id FROM product_group WHERE id = NEW.product_group_parent_id ;
        IF ( EXISTS ( SELECT id FROM sum_facility_productgroup_day where product_group_id = NEW.product_group_parent_id and raw_date = NEW.raw_date and facility_id = NEW.facility_id and facility_type_id = NEW.facility_type_id AND kpi_type = NEW.kpi_type) = FALSE ) THEN
            INSERT INTO sum_facility_productgroup_day ( facility_id,  facility_boundary_id, facility_boundary_parent_id, facility_boundary_level_id, facility_type_id, kpi, actual, target, kpi_type, data_point_count, product_group_id, product_group_parent_id, calendar_id, raw_date, day_of_week, date_day, date_month, date_year, date_quarter, date_start_of_week, date_end_of_week ) 
            SELECT NEW.facility_id, NEW.facility_boundary_id, NEW.facility_boundary_parent_id, NEW.facility_boundary_level_id, NEW.facility_type_id, NEW.kpi, NEW.actual, NEW.target, NEW.kpi_type, NEW.data_point_count, NEW.product_group_parent_id, v_parent_id, NEW.calendar_id, NEW.raw_date, NEW.day_of_week, NEW.date_day, NEW.date_month, NEW.date_year, NEW.date_quarter, NEW.date_start_of_week, NEW.date_end_of_week;
        ELSE
            UPDATE sum_facility_productgroup_day 
            SET kpi = ( kpi + NEW.kpi ), actual = ( actual + NEW.actual ), target = (target + NEW.target), data_point_count = ( data_point_count + NEW.data_point_count ) 
            WHERE product_group_id = NEW.product_group_parent_id AND raw_date = NEW.raw_date AND facility_id = NEW.facility_id AND kpi_type = NEW.kpi_type;
        END IF;
    END IF;
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sum_facility_productgroup_day_update_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_parent_id int;
BEGIN
    -- aggregate the value upwards if possible.
    IF ( NEW.product_group_parent_id is not NULL) THEN
        SELECT INTO v_parent_id parent_id FROM product_group WHERE id = NEW.product_group_parent_id ;
        IF ( EXISTS ( SELECT id FROM sum_facility_productgroup_day where product_group_id = NEW.product_group_parent_id and raw_date = NEW.raw_date and facility_id = NEW.facility_id AND kpi_type = NEW.kpi_type) = FALSE ) THEN
            INSERT INTO sum_facility_productgroup_day ( facility_id, facility_boundary_id, facility_boundary_parent_id, facility_boundary_level_id,  facility_type_id, kpi, actual, target, kpi_type, data_point_count, product_group_id, product_group_parent_id, calendar_id, raw_date, day_of_week, date_day, date_month, date_year, date_quarter, date_start_of_week, date_end_of_week ) 
            SELECT NEW.facility_id, NEW.facility_boundary_id, NEW.facility_boundary_parent_id, NEW.facility_boundary_level_id, NEW.facility_type_id, NEW.kpi, NEW.actual, NEW.target, NEW.kpi_type, NEW.data_point_count, NEW.product_group_parent_id, v_parent_id, NEW.calendar_id, NEW.raw_date, NEW.day_of_week, NEW.date_day, NEW.date_month, NEW.date_year, NEW.date_quarter, NEW.date_start_of_week, NEW.date_end_of_week;
        ELSE
            UPDATE sum_facility_productgroup_day 
            SET kpi = ( kpi + NEW.kpi ), actual = ( actual + NEW.actual ), target = (target + NEW.target), data_point_count = ( data_point_count + NEW.data_point_count ) 
            WHERE product_group_id = NEW.product_group_parent_id AND raw_date = NEW.raw_date AND facility_id = NEW.facility_id AND kpi_type = NEW.kpi_type;
        
        END IF;
    END IF;
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER sum_facility_productgroup_day_insert_trigger
    BEFORE INSERT ON sum_facility_productgroup_day
    FOR EACH ROW EXECUTE PROCEDURE sum_facility_productgroup_day_insert_trigger();
    
CREATE TRIGGER sum_facility_productgroup_day_update_trigger
    BEFORE UPDATE ON sum_facility_productgroup_day
    FOR EACH ROW EXECUTE PROCEDURE sum_facility_productgroup_day_update_trigger();
