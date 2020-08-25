import time
from datetime import datetime
import psycopg2
from psycopg2 import sql
from flask import Flask, request
import requests
import json

app = Flask(__name__)

POSTGRES_USER = 'admin'
POSTGRES_PASSWORD = 'password'
POSTGRES_DB = 'test_db'
POSTGRES_HOST = 'dbhost'
POSTGRES_PORT = '5432'

# Token per le chiamate alla API della world air quality index
# API_TOKEN = "INSERT YOUR API TOKEN HERE"
API_TOKEN = "701db77838d1e5156e628c19086cc420840f0066"
VARIABLE_DICT = {'t' : 'Temperature',
                 'h' : 'Humidity',
                 'p' : 'Pressure',
                 'pm10' : 'PM10',
                 'pm25' : 'PM25',
                 'co' : 'CO',
                 'so2' : 'SO2',
                 'no2' :  'NO2'}

def connect_to_db():
    retries = 5
    connection = None
    record = ""
    while True:
        try:
            connection = psycopg2.connect(user = POSTGRES_USER,
                                  password = POSTGRES_PASSWORD,
                                  host = POSTGRES_HOST,
                                  port = POSTGRES_PORT,
                                  database = POSTGRES_DB)
            cursor = connection.cursor()
            connection.set_session(autocommit=True)
            

        except (Exception, psycopg2.Error) as exc:
            if retries == 0:

                raise exc
            retries -= 1
            print("fail")
            time.sleep(0.5)
        finally:
            if(connection):
                break

    if(connection):
        return connection, cursor

def insert_into_weather_table(conn, cur, data):
    now = datetime.utcnow()
    insert_str = """INSERT INTO weather(
                        station_name,
                        temperature,
                        pressure,
                        humidity,
                        pm10,
                        pm2_5
                        )
                        VALUES (%s,%s,%s,%s,%s,%s)
                        ;"""
    # sql_query = sql.SQL(insert_str)
    cur.execute(insert_str, [ *data ])
    conn.commit()

def get_air_data():
    response = requests.get("https://api.waqi.info/feed/here/?token=" + API_TOKEN)
    print(type(response))
    if response.status_code == 200:
        json_string = response.content.decode()
        valid_json_string = "[" + json_string + "]"
        return json.loads(valid_json_string)[0]
    else:
        return "404 HTTP Error: Not Found!"

def format_history(history):
    data = dict()
    labels = [
        "Index",
        "StationName",
        "Temperature",
        "Pressure",
        "Humidity",
        "PM10",
        "PM25"
    ]

    for idx, val in enumerate(history):
        data[labels[idx]] = val

    formatted = f'''
        <h3>Entry number: {data["Index"]}<h3/>
        <h3>Location: {data["StationName"]}<h3/>
        <br/>
        <table>
            <thead><tr>
              <th>Parameter</th>
              <th>Value</th>
            </tr></thead>
            <tbody>
            <tr><td>Temperature</td><td>{data['Temperature']}\t°C</td></tr>
            <tr><td>Humidity</td><td>{data['Humidity']}\t%</td></tr>
            <tr><td>Pressure</td><td>{data['Pressure']}\thPa</td></tr>
            <tr><td>PM10</td><td>{data['PM10']}\tµg/m3</td></tr>
            <tr><td>PM2.5</td><td>{data['PM25']}\tµg/m3</td></tr>
            </tbody>
        </table><br/>
        '''
    return formatted

@app.route('/')
def home():
    conn, cur = connect_to_db()

    response = get_air_data()
    result_dict = {}
    base_data = response['data']
    city = base_data["city"]["name"]
    geo = base_data["city"]["geo"]
    for key in base_data['iaqi']:
        if key in VARIABLE_DICT:
            result_dict[VARIABLE_DICT[key]] = base_data['iaqi'][key]["v"]

    for key in VARIABLE_DICT:
        if VARIABLE_DICT[key] not in result_dict:
            result_dict[VARIABLE_DICT[key]] = None

    data = [str(base_data["city"]["name"]),
            result_dict['Temperature'],
            result_dict['Pressure'],
            result_dict['Humidity'],
            result_dict['PM10'],
            result_dict['PM10']]
    insert_into_weather_table(conn, cur, data)
    cur.execute("SELECT * FROM weather LIMIT 1;")
    query = cur.fetchone()
    cur.close()
    conn.close()
    result  = f'''
        <h1>Air Polution Checker<h1/>
        <br/>
        <h3>Your location is {city} <br/> Coordinates: {geo}<h3/>
        <br/>
        <table>
            <thead><tr>
              <th>Parameter</th>
              <th>Value</th>
            </tr></thead>
            <tbody>
            <tr><td>Temperature</td><td>{result_dict['Temperature']}\t°C</td></tr>
            <tr><td>Humidity</td><td>{result_dict['Humidity']}\t%</td></tr>
            <tr><td>Pressure</td><td>{result_dict['Pressure']}\thPa</td></tr>
            <tr><td>PM10</td><td>{result_dict['PM10']}\tµg/m3</td></tr>
            <tr><td>PM2.5</td><td>{result_dict['PM25']}\tµg/m3</td></tr>
            <tr><td>CO</td><td>{result_dict['CO']}\tµg/m3</td></tr>
            <tr><td>NO2</td><td>{result_dict['NO2']}\tµg/m3</td></tr>
            <tr><td>SO2</td><td>{result_dict['SO2']}\tµg/m3</td></tr>
            </tbody>
        </table>
        '''
    return result
    # return "{} <br/><br/><br/> version:{}".format(query, version)

@app.route('/history/')
def history():
    query_params = ["measurement_id","station_name",
                    "temperature","pressure",
                    "humidity","pm10","pm2_5"]
    conn, cur = connect_to_db()

    limit = request.args.get('limit', default=1)
    result_string = "<h1>Air Polution Checker History<h1/>"
    
    cur.execute("SELECT * FROM weather ORDER BY measurement_id DESC LIMIT {};".format(int(limit)))
    # cur.execute("""SELECT table_name FROM information_schema.tables
    #    WHERE table_schema = 'public'""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    for res in result:
        res = format_history(res)
        result_string = result_string + "{} <br/> ".format(res)
    return result_string
