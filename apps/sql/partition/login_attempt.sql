CREATE OR REPLACE FUNCTION ruther_audit_login_attempt_insert_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_year int;
    v_month int;
    v_tablename varchar;
    v_start_date DATE;
    v_end_date DATE;
    v_attempt_datetime DATE;
BEGIN
    v_attempt_datetime := new.attempt_datetime;
    v_year := date_part('year', v_attempt_datetime);
    v_month := date_part ('month', v_attempt_datetime);
    v_tablename := 'ruther_audit_login_attempt_y' || v_year::varchar || '_m' || v_month::varchar;
    v_start_date := DATE ( v_year::varchar || '-' || v_month::varchar || '-1');
    v_end_date := ( v_start_date + interval '1 month' );

    IF ( EXISTS (SELECT relname FROM pg_class WHERE relname=v_tablename) = FALSE ) THEN
    
    EXECUTE 'CREATE TABLE ' ||  quote_ident(v_tablename) || 
     ' ( CONSTRAINT ' || quote_ident(v_tablename) || '_month CHECK ( attempt_datetime >= DATE ''' ||  to_char(v_start_date, 'YYYY-MM-DD') || ''' AND attempt_datetime < DATE ''' || to_char(v_end_date,'YYYY-MM-DD') || 
     ''' ))  INHERITS (ruther_audit_login_attempt)';
   
    EXECUTE 'CREATE INDEX ' || quote_ident(v_tablename) || '_index ON '|| quote_ident(v_tablename) || '( username )';  

    END IF;

    EXECUTE format('INSERT INTO %I SELECT ($1).*', v_tablename) using NEW;
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER ruther_audit_login_attempt_insert_trigger
    BEFORE INSERT ON ruther_audit_login_attempt
    FOR EACH ROW EXECUTE PROCEDURE ruther_audit_login_attempt_insert_trigger();