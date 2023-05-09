# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify
import os


# Database Setup
os.chdir(os.path.dirname(os.path.realpath(__file__)))
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
measurement = Base.classes.measurement

# Flask Setup
app = Flask(__name__)

# Flask Routes

# Define what to do when a user hits the / route.
@app.route("/")
def home():
    
    # Create session
    session=Session(engine)
    
    # Routes
    content = ("The available routes are:<br>"
        "/api/v1.0/precipitation<br>"
        "/api/v1.0/stations<br>"
        "/api/v1.0/tobs<br>"
        "/api/v1.0/stats/&lt;start&gt;<br>"
        "/api/v1.0/stats/&lt;start&gt;/&lt;end&gt;<br>"
    )
    
    # Close session
    session.close()
    
    # Return routes
    return content


# Define what to do when a user hits the /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create session
    session=Session(engine)
    
    # Starting from the most recent data point in the database. 
    recent_date_str = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]

    # Calculate the date one year from the last date in data set.
    recent_date_dt = dt.date.fromisoformat(recent_date_str)
    year_ago = recent_date_dt - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    date_prcp_data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= year_ago).\
        filter(measurement.date <= recent_date_dt).all()
    
    # Convert query results to a dictionary using date as the key and prcp as the value
    date_prcp_dict = {}
    for result in date_prcp_data:
        date_prcp_dict[result.date] = result.prcp
        
    # Close session
    session.close()
    
    # Return json
    return jsonify (date_prcp_dict) 

# Define what to do when a user hits the /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    
    # Start session
    session=Session(engine)
    
    # Query all unique stations
    results = session.query(measurement.station).distinct().all()
    
    # Convert query to list
    all_stations = []
    for station in results:
        station_dict = {}
        station_dict["stations"] = station[0]
        all_stations.append(station_dict)
    
    # Close session
    session.close()
    
    # Return json
    return jsonify(all_stations)

# Define what to do when a user hits the /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    
    # Start session
    session = Session(engine)
    
    # Starting from the most recent data point in the database. 
    recent_date_str = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]

    # Calculate the date one year from the last date in data set.
    recent_date_dt = dt.date.fromisoformat(recent_date_str)
    year_ago = recent_date_dt - dt.timedelta(days=365)
    
    # Query the last 12 months of temperature observation data
    tobs_data = session.query(measurement.tobs).\
    filter(measurement.station == 'USC00519281').\
    filter(measurement.date >= year_ago).\
    filter(measurement.date <= recent_date_dt).all()
    
    # Convert query results to a list of dictionaries
    most_active_tobs = []
    for temperature in tobs_data:
        temperature_dict = {}
        temperature_dict["temperature"] = temperature[0]
        most_active_tobs.append(temperature_dict)
    
    # Close the session
    session.close()
    
    # Return the JSON of the list of dictionaries
    return jsonify(most_active_tobs)

# Define what to do when a user hits the /api/v1.0/<start> route
@app.route("/api/v1.0/stats/<start>")
@app.route("/api/v1.0/stats/<start>/<end>")
def stats(start, end=None):
    
    # Start session
    session = Session(engine)

    # Convert start date to datetime object
    start_date = dt.date.fromisoformat(start)
    
    # Query TMIN, TAVG, and TMAX for dates greater than or equal to the start date
    if end:
        end_date = dt.date.fromisoformat(end)
        start_end_stats = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= start_date).\
            filter(measurement.date <= end_date).\
            first()
    else: 
        start_end_stats = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start_date).\
                first()
            
    keys = ["tobs_min","tobs_avg", "tobs_max"]
    dict_builder = zip(keys, start_end_stats)
    results = {k:v for (k,v) in dict_builder}

    
    # Close the session
    session.close()
    
    # Return the JSON
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)