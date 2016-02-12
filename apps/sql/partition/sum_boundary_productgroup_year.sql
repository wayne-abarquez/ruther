-- PRODUCT GROUP Aggregation is more complex than just a single products.
-- Aggregate Bounday Day Sum Table based on Month, Year.
-- Automatcially creates, and insert aggregated data to the proper partition table.
-- Bypasses the sum_boundary_productgroup_year trigger for faster performance.
CREATE OR REPLACE FUNCTION aggregate_boundary_productgroup_year_sum ( int ) returns void as
$$
declare
v_start_date DATE;
v_end_date DATE;
v_tablename varchar;
v_boundary_level_desc boundary_level_desc%rowtype;
BEGIN
    INSERT INTO sum_boundary_productgroup_year ( boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, target, data_point_count, product_group_id, product_group_parent_id, date_year )
        SELECT k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, 
        k.facility_type_id,
        k.kpi_type, SUM(k.kpi), SUM(k.actual), SUM(k.target), COUNT(k.kpi),
        pgm.group_id, pg.parent_id,
         k.date_year
        FROM kpi k 
        LEFT JOIN productgroup_map pgm ON pgm.product_id = k.product_id
        LEFT JOIN product_group pg ON pg.id = pgm.group_id
        WHERE k.date_year = $1
        GROUP BY  k.facility_boundary_id, k.facility_boundary_level_id, k.facility_boundary_parent_id, k.facility_type_id,
        k.date_year, k.kpi_type, pgm.group_id, pg.parent_id
        ORDER BY k.facility_boundary_id, k.kpi_type;
    
    
    FOR v_boundary_level_desc in SELECT * FROM boundary_level_desc ORDER BY id DESC
    LOOP
        IF ( v_boundary_level_desc.id != 1 ) THEN
            -- raise NOTICE 'DOING boundary_level_id % to %',v_boundary_level_desc.id::varchar , (v_boundary_level_desc.id - 1)::varchar;
            INSERT INTO sum_boundary_productgroup_year ( boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi_type, kpi, actual, target, data_point_count, product_group_id, product_group_parent_id, date_year ) 
                SELECT k.boundary_parent_id, ( v_boundary_level_desc.id - 1 ), b.parent_id, k.facility_type_id,
                k.kpi_type, SUM(k.kpi), SUM (k.actual), SUM(k.target), SUM(k.data_point_count), k.product_group_id, k.product_group_parent_id,
                k.date_year
                FROM sum_boundary_productgroup_year k 
                LEFT JOIN boundaries b on k.boundary_parent_id = b.id 
                WHERE k.boundary_level_id = v_boundary_level_desc.id AND k.date_year = $1
                GROUP BY 
                k.boundary_parent_id, boundary_level_id, b.parent_id,  k.facility_type_id,
                k.kpi_type, k.product_group_id, k.product_group_parent_id,
                k.date_year
                ORDER BY k.boundary_parent_id, k.kpi_type;
        END IF;
    END LOOP;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sum_boundary_productgroup_year_insert_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_parent_id int;
    v_tablename varchar;
BEGIN

    v_tablename := 'sum_boundary_productgroup_year_y' || NEW.date_year::varchar;


    IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
    EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
    ' ( CONSTRAINT ' || quote_ident(v_tablename) || 'year CHECK ( date_year = ' || new.date_year::varchar || ' ))  INHERITS (sum_boundary_productgroup_year)';
    EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_year_index ON '|| quote_ident(v_tablename) || '( boundary_id, product_group_id, facility_type_id, kpi_type, date_year )';  

    END IF;
    
    -- just in case if the INSERT is for an existing row, then just update.
    IF ( EXISTS ( SELECT id FROM sum_boundary_productgroup_year where product_group_id = NEW.product_group_id AND date_year = NEW.date_year and boundary_id = NEW.boundary_id and facility_type_id = NEW.facility_type_id AND kpi_type = NEW.kpi_type) = FALSE ) THEN
        EXECUTE format('INSERT INTO %I SELECT ($1).*', v_tablename) using NEW;
    ELSE
        UPDATE sum_boundary_productgroup_year 
            SET kpi = ( kpi + NEW.kpi ), actual = ( actual + NEW.actual), target = (target + NEW.target), data_point_count = ( data_point_count + NEW.data_point_count ) 
            WHERE product_group_id = NEW.product_group_id AND date_year = NEW.date_year AND boundary_id = NEW.boundary_id AND facility_type_id = NEW.facility_type_id AND kpi_type = NEW.kpi_type;

    END IF;
    
    -- aggregate the value upwards if possible.
    IF ( NEW.product_group_parent_id is not NULL) THEN
        SELECT INTO v_parent_id parent_id FROM product_group WHERE id = NEW.product_group_parent_id ;
        IF ( EXISTS ( SELECT id FROM sum_boundary_productgroup_year where product_group_id = NEW.product_group_parent_id AND date_year = NEW.date_year and boundary_id = NEW.boundary_id and facility_type_id = NEW.facility_type_id AND kpi_type = NEW.kpi_type) = FALSE ) THEN
            INSERT INTO sum_boundary_productgroup_year ( boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi, actual, target, kpi_type, data_point_count, product_group_id, product_group_parent_id, date_year ) 
            SELECT NEW.boundary_id, NEW.boundary_level_id, NEW.boundary_parent_id, NEW.facility_type_id, NEW.kpi, NEW.actual, NEW.target, NEW.kpi_type, NEW.data_point_count, NEW.product_group_parent_id, v_parent_id, NEW.date_year;
        ELSE
            UPDATE sum_boundary_productgroup_year 
            SET kpi = ( kpi + NEW.kpi ), actual = ( actual + NEW.actual), target = (target + NEW.target), data_point_count = ( data_point_count + NEW.data_point_count ) 
            WHERE product_group_id = NEW.product_group_parent_id AND date_year = NEW.date_year AND boundary_id = NEW.boundary_id AND facility_type_id = NEW.facility_type_id AND kpi_type = NEW.kpi_type;
        
        END IF;
    END IF;
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sum_boundary_productgroup_year_update_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_parent_id int;
BEGIN
    -- aggregate the value upwards if possible.
    IF ( NEW.product_group_parent_id is not NULL) THEN
        SELECT INTO v_parent_id parent_id FROM product_group WHERE id = NEW.product_group_parent_id ;
        IF ( EXISTS ( SELECT id FROM sum_boundary_productgroup_year where product_group_id = NEW.product_group_parent_id AND date_year = NEW.date_year and boundary_id = NEW.boundary_id and facility_type_id = NEW.facility_type_id AND kpi_type = NEW.kpi_type) = FALSE ) THEN
            INSERT INTO sum_boundary_productgroup_year ( boundary_id, boundary_level_id, boundary_parent_id, facility_type_id, kpi, actual, target, kpi_type, data_point_count, product_group_id, product_group_parent_id, date_year ) 
            SELECT NEW.boundary_id, NEW.boundary_level_id, NEW.boundary_parent_id, NEW.facility_type_id, NEW.kpi, NEW.actual, NEW.target, NEW.kpi_type, NEW.data_point_count, NEW.product_group_parent_id, v_parent_id, NEW.date_year;
        ELSE
            UPDATE sum_boundary_productgroup_year 
            SET kpi = ( kpi + NEW.kpi ), actual = ( actual + NEW.actual ), target = (target + NEW.target), data_point_count = ( data_point_count + NEW.data_point_count ) 
            WHERE product_group_id = NEW.product_group_parent_id AND date_year = NEW.date_year AND boundary_id = NEW.boundary_id AND facility_type_id = NEW.facility_type_id AND kpi_type = NEW.kpi_type;
        
        END IF;
    END IF;
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER sum_boundary_productgroup_year_insert_trigger
    BEFORE INSERT ON sum_boundary_productgroup_year
    FOR EACH ROW EXECUTE PROCEDURE sum_boundary_productgroup_year_insert_trigger();
    
CREATE TRIGGER sum_boundary_productgroup_year_update_trigger
    BEFORE UPDATE ON sum_boundary_productgroup_year
    FOR EACH ROW EXECUTE PROCEDURE sum_boundary_productgroup_year_update_trigger();
