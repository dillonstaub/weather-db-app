import requests
import json
import os
import urllib.parse as up
import psycopg2
import logging


def ingestion_handler():
    try:
        check_table_exists()
        minutely_weather = get_minutely_weather()
        query = insert_query_builder(minutely_weather)
        logging.info("Query: \n", query)
        execute_query(query)
        logging.info("Status: ingestion completed successfully")
    except Exception as e:
        logging.error(f"Failed with: {e}")
        raise e


def check_table_exists():
    conn = None
    try:
        check_table_query = """
                                SELECT EXISTS ( 
                                    SELECT FROM 
                                        pg_tables 
                                    WHERE 
                                        schemaname = 'weather_ts' AND 
                                        tablename = 'minutely_weather'
                                    );
                            """
        
        conn = get_conn()
        cur = conn.cursor()

        cur.execute(check_table_query)
        result = cur.fetchall()
        cur.close()
        conn.commit()
        if result[0][0] == False:
            create_table()

    except Exception as e:
        logging.error(f"Failed to check if table exists: {e}")
        raise e
    finally:
        close_conn(conn)


def create_table():
    conn = None
    try:
        create_table_query = """
                                CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
                                CREATE EXTENSION IF NOT EXISTS "timescaledb";
                                CREATE SCHEMA IF NOT EXISTS weather_ts;
                                CREATE TABLE IF NOT EXISTS weather_ts.minutely_weather(
                                    id uuid DEFAULT uuid_generate_v4(),
                                    dt timestamp,
                                    data_type varchar,
                                    value float8,
                                    PRIMARY KEY (dt));
                                SELECT create_hypertable('weather_ts.minutely_weather', 'dt');
                                CREATE INDEX IF NOT EXISTS date_index ON weather_ts.minutely_weather (dt);
                                CREATE INDEX IF NOT EXISTS precip_value_index ON weather_ts.minutely_weather (value);
                            """
        
        conn = get_conn()
        cur = conn.cursor()

        cur.execute(create_table_query)

        cur.close()
        conn.commit()
    except Exception as e:
        logging.error(f"Failed to create table: {e}")
        raise e
    finally:
        close_conn(conn)


def get_minutely_weather():
    try:
        api_key = os.environ["OPENWEATHER_API_KEY"]
        resp = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat=33.44&lon=-94.04&exclude=hourly,daily&appid={api_key}")
        data = json.loads(resp.text)
        return data["minutely"]
    except Exception as e:
        logging.error(f"Failed in get_minutely_weather with: {e}")
        raise e


def insert_query_builder(minutely):
    try:
        query = """ 
                INSERT INTO weather_ts.minutely_weather (
                    dt, 
                    data_type, 
                    value)
                VALUES
                """
        first = True
        for entry in minutely:
            if first:
                value = f"(to_timestamp({entry['dt']}),'precipitation',{entry['precipitation']})\n"
                query += value
                first = False
            else:
                value = f",(to_timestamp({entry['dt']}),'precipitation',{entry['precipitation']})\n"
                query += value
        query += """ON CONFLICT (dt) DO NOTHING;
                    ANALYZE weather_ts.minutely_weather;
                    """
        return query
    except Exception as e:
        logging.error(f"Failed to build query: {e}")
        raise e


def execute_query(query):
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute(query)

        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as e:
        logging.error(f"Exception occurred in execute query with: {e}")
        raise e
    finally:
        close_conn(conn)


def get_conn():
    conn = None
    try:
        up.uses_netloc.append("postgres")
        url = up.urlparse(os.environ["WEATHER_DB_URL"])
        
        conn = psycopg2.connect(dbname="weatherdb",
                                user=url.username,
                                password=url.password,
                                host=url.hostname,
                                port=url.port)
        return conn
    except Exception as e: 
        logging.error(f"Failed to get db connection: {e}")
        close_conn(conn)
        raise e


def close_conn(conn):
    if conn is not None:
            conn.close()


def clear_table():
    query = "TRUNCATE TABLE weather_ts.minutely_weather;"
    execute_query(query)
