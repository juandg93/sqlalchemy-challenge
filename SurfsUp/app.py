# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func,inspect
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt
import numpy as np


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base = automap_base()

Base.prepare(engine, reflect=True)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

# Precipitation route

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session (link) from Python to the DB
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    # Close the session
    session.close()
    # Convert list of tuples into normal list
    precipitation_dict = dict(results)
    return jsonify(precipitation_dict)

# station route

@app.route("/api/v1.0/stations")
def stations():
    # Create a session (link) from Python to the DB
    session = Session(engine)
    # Query all stations
    results = session.query(Station.station).all()
    # Close the session
    session.close()
    # Convert list of tuples into normal list
    stations = list(np.ravel(results))
    return jsonify(stations)


# TOBS route
@app.route("/api/v1.0/tobs")
def tobs():
    # Create a session (link) from Python to the DB
    session = Session(engine)
    # Query the last year of temperature observations for the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).first().station
    last_date = session.query(func.max(Measurement.date)).filter(Measurement.station == most_active_station).scalar()
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    # Close the session
    session.close()
    # Convert list of tuples into normal list
    tobs = list(np.ravel(results))
    return jsonify(tobs)

# TIME routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start(start, end=None):
    # Create a session (link) from Python to the DB
    session = Session(engine)

    try:
        # Convert string dates to datetime objects
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')

        if end:
            end_date = dt.datetime.strptime(end, '%Y-%m-%d')
            
        # Perform a query to retrieve the temperature observations
        if not end:
            results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).all()
        else:
            results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).\
                filter(Measurement.date <= end_date).all()
            
        # Close the session
        session.close()
        
        # Convert list of tuples into normal list
        temps = list(np.ravel(results))
        return jsonify(temps)
    
    except ValueError:
        session.close()  # Closing session... even on error
        return jsonify({"Error": "Make sure you're entering the dates in correct format - Example: http://127.0.0.1:5000/api/v1.0/2016-01-20/2017-01-20"}), 404



if __name__ == '__main__':
    app.run(debug=True)