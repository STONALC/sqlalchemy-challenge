# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
import numpy as np
import pandas as pd
import datetime as dt
import os

#################################################
# Database Setup
#################################################
os.chdir(os.path.dirname(os.path.realpath(__file__)))
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask HTML Routes
#################################################
@app.route("/")
def home():
    html = """
    /<br>
    /api/v1.0/precipitation<br>
    /api/v1.0/stations<br>
    /api/v1.0/tobs<br>
    /api/v1.0/tstats/&lt;start&gt;<br>
    /api/v1.0/tstats/&lt;start&gt;/&lt;end&gt;<br>
    """
    return html    

#################################################
# Flask API Routes
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    # Calculate the date one year from the last date in the data set
    last_12_months_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_12_months_date).\
        order_by(Measurement.date).all()
    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    precip_df = {date: prcp for date, prcp in precip_data}
    return jsonify(precip_df)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Query to get all stations
    station_data = session.query(Station.station).all()
    session.close()

    # Convert the query results to a list
    stations = list(np.ravel(station_data))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Find the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(desc(func.count(Measurement.station))).first()

    # Calculate the date one year ago from the last data point in the dataset
    last_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query the dates and temperature observations of the most active station for the previous year of data
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station[0]).\
        filter(Measurement.date >= one_year_ago).all()
    session.close()

    # Convert the query results to a dictionary
    tobs_data = {date: tobs for date, tobs in results}
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    session = Session(engine)
    if not end:
        end = dt.date.today().strftime("%Y-%m-%d")
    
    # Query the temperature data
    results = session.query(func.min(Measurement.tobs), 
                            func.avg(Measurement.tobs), 
                            func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start).\
                    filter(Measurement.date <= end).all()
    session.close()

    temp_data = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    return jsonify(temp_data)

if __name__ == "__main__":
    app.run(debug=True)
