import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    
    return (
        f"SQL Alchemy: Surf's Up<br/>"
        f"Available Routes:<br/>"
        f"<a href='http://127.0.0.1:5000/api/v1.0/precipitation'>Precipitation</a><br/>"
        f"<a href='http://127.0.0.1:5000/api/v1.0/stations'>Stations</a><br/>"
        f"<a href='http://127.0.0.1:5000/api/v1.0/tobs'>tobs</a><br/>"
        f"<a href='http://127.0.0.1:5000/api/v1.0/<start>'>Enter a start date of your trip:use date format YYYY-MM-DD</a><br/>"
        f"<a href='http://127.0.0.1:5000/api/v1.0/<start>/<end>'>Enter a start and end date of trip duration:use date format YYYY-MM-DD</a>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a Dictionary using date as the key and prcp as the value."""

    #Get the last date from the database
    last_date= session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    
    # Calculate the date 1 year ago from the last data point in the database then convert datetime to date
    year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d")- dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    one_yr_data = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=year_ago).all()
    
    session.close()

 
    """Return the JSON representation of your dictionary."""
    prcp_dict = list(np.ravel(one_yr_data))
   
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    station_query = session.query(Station.station).all()

    session.close()
    
    stations = list(np.ravel(station_query))

    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(stations))

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """query for the dates and temperature observations from a year from the last data point."""
    #Get the last date from the database
    last_date= session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    
    # Calculate the date 1 year ago from the last data point in the database then convert datetime to date
    year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d")- dt.timedelta(days=365)

    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    results = session.query(Measurement.tobs).filter(Measurement.date >= year_ago).all()

    session.close()

    tobs_list = list(np.ravel(results))
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def trip_start(start):
    """ Return a JSON list of the minimum temperature, the average temperature,"""
    """ and the max temperature for a given start or start-end range."""
    """ Calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""

    session = Session(engine)

    temp_results = session.query(func.min(Measurement.tobs).label('TMIN'),\
        func.avg(Measurement.tobs).label('TAVG'),\
        func.max(Measurement.tobs).label('TMAX'),\
        Measurement.date).filter(Measurement.date >= start).all()

    session.close()
    
    # temp_list = list(np.ravel(temp_results))
    temp_list = []
    for row in temp_results:
        temp_dict = {}
        temp_dict['Start Date'] = start
        temp_dict['TMIN'] = row.TMIN
        temp_dict['TAVG'] = row.TAVG
        temp_dict['TMAX'] = row.TMAX
        temp_list.append(temp_dict)
    
    return jsonify(temp_list)


@app.route("/api/v1.0/<start>/<end>")
def trip_duration(start,end):

    """ Return a JSON list of the minimum temperature, the average temperature,"""
    """ and the max temperature for a given start or start-end range."""
    """ Calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""

    session = Session(engine)

    temp_results = session.query(func.min(Measurement.tobs).label('TMIN'),
    func.avg(Measurement.tobs).label('TAVG'),\
    func.max(Measurement.tobs).label('TMAX'))\
    .filter(Measurement.date >= start)\
    .filter(Measurement.date <= end).all()

    session.close()
    
    trip_temps_list = []
    for row in temp_results:
        trip_temps_dict = {}
        trip_temps_dict['Start Date'] = start
        trip_temps_dict['End Date'] = end
        trip_temps_dict['TMIN'] = row.TMIN
        trip_temps_dict['TAVG'] = row.TAVG
        trip_temps_dict['TMAX'] = row.TMAX
        trip_temps_list.append(trip_temps_dict)
    
    return jsonify(trip_temps_list)


if __name__ == '__main__':
    app.run(debug=True)
