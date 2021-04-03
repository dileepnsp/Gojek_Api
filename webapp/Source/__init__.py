import flask
from flask import request, jsonify
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import os.path
import ssl
import json
from s2 import s2
app = flask.Flask(__name__)
app.config["DEBUG"] = True

gcp_project = "weighty-flag-307702"
class Gcp_connect:
    def __init__(self):
        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(my_path, "../Config/weighty-flag-307702-26125390e609.json")
        print(path)
        #self.credentials = service_account.Credentials.from_service_account_file('Config\weighty-flag-307702-26125390e609.json')
        self.credentials = service_account.Credentials.from_service_account_file(path)
        self.client = bigquery.Client(credentials=self.credentials, project=gcp_project)
    def get_client(self):
        return self.client

#Get GCP Client
def get_gcp_client():
    return Gcp_connect().get_client()

gcp_client=get_gcp_client()

@app.route('/', methods=['GET'])
def home():
    return "<h1>Gojek Taxi API.</h1>"

#
@app.route('/total_trips', methods=['GET'])
def total_trips():
    query_parameters = request.args
    start_date= query_parameters.get('start')
    end_date = query_parameters.get('end')
    print(start_date)
    print(end_date)
    query_res  = gcp_client.query("""select date, total_trips from  (
        SELECT CAST(DATE(trip_start_timestamp) as DATE) as date, count(*) as total_trips   from
    `bigquery-public-data.chicago_taxi_trips.taxi_trips` where CAST(DATE(trip_start_timestamp) as DATE)  between
    '"""+start_date+"' and '"+end_date+"'  group   by  CAST(DATE(trip_start_timestamp) as DATE))a order  by  date""")
    # to store results in dataframe
    results = []  # empty dataframe
    for row in query_res:
        results.append({"date":str(row.date),"total_trips":row.total_trips})
    return {"data": results}

@app.route('/avg_speed_24hrs', methods=['GET'])

def avg_speed_24hrs():

    query_parameters = request.args
    date= query_parameters.get('date')

    query_res=gcp_client.query("""select 
    avg(trip_miles / (TIMESTAMP_DIFF(trip_end_timestamp, trip_start_timestamp, minute) / 60)) as average_speed
    from     `bigquery-public-data.chicago_taxi_trips.taxi_trips`    where
    abs(DATE_DIFF(DATE    '"""+date+"', CAST(DATE(trip_end_timestamp)    AS    DATE), DAY)) < 1 and " \
                                    "trip_end_timestamp != trip_start_timestamp""")

    results = []  # empty dataframe
    for row in query_res:
        results.append({"average_speed":row.average_speed})
    return {"data": results}

@app.route('/average_fare_heatmap', methods=['GET'])

def avg_fare_heatmap():
    query_parameters = request.args
    date= query_parameters.get('date')
    query_res = gcp_client.query("""select pickup_location,avg(fare) as avg_fare from `bigquery-public-data.chicago_taxi_trips.taxi_trips`
    where pickup_location is not null and CAST(DATE(trip_start_timestamp) AS DATE) = '"""+date+"' group by pickup_location""")

    results = []  # empty dataframe
    for row in query_res:
        results.append({"s2id":row.pickup_location,"fare":row.avg_fare})
    return {"data": results}

def calculate_s2id(point,radius ):
    latlong = s2.LatLngFromDegrees(point.Latitude, point.Longitude)
    s2Point = s2.PointFromLatLng(latlong)
    EarthRadiusInMeter=10
    angle = s2.Angle(radius / EarthRadiusInMeter)
    sphereCap = s2.CapFromCenterAngle(s2Point, angle)
    region = s2.Region(sphereCap)
    rc = s2.RegionCoverer(MaxLevel=16, MinLevel=16)
    cellUnion = rc.Covering(region)
    stringCellIDs=[]
    for cellID in cellUnion:
        stringCellIDs.append(int(cellID))
    return stringCellIDs

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

if __name__ == "__main__":
    app.run()