import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

####################################################
# Database setup
####################################################
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# Reflecting existing database into a new model
Base = automap_base()
# Reflecting the tables
Base.prepare(engine, reflect=True)

# Saving reference tables
Measurement = Base.classes.measurement
Station = Base.classes.station

####################################################
# Creating Flask
####################################################
app = Flask(__name__)

####################################################
# Flask Routes
####################################################
@app.route('/')
def welcome():
    '''List of all available routes'''
    return (
        f'Available Routes: <br/>'
        f'/api/v1.0/precipitation <br/>'
        f'/api/v1.0/stations <br/>'
        f'/api/v1.0/tobs <br/>'
        f'/api/v1.0/start/2016-10-11 <br/>'
        f'/api/v1.0/start/2016-10-11/end/2017-08-23'
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Creating session
    session = Session(engine)

    '''Convert query results from last 12 months to a dictionary using date as the key and prcp as the value'''
    # Finding the most recent date
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year = dt.date.fromisoformat(most_recent) - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year).order_by(Measurement.date).all()

    session.close()

    # Creating a dictionary from row data
    all_precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['prcp'] = prcp
        all_precipitation.append(prcp_dict)
    
    return jsonify(all_precipitation)

@app.route('/api/v1.0/stations')
def stations():
    # Creating session
    session = Session(engine)

    '''List of all stations from the dataset'''
    results = session.query(Station.station).all()

    session.close()

    # Converting list into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route('/api/v1.0/tobs')
def tobs():
    # Creating a session
    session = Session(engine)

    '''Query dates and temperature observations of the most active station for the previous year of data'''
    # Finding the most recent date
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year = dt.date.fromisoformat(most_recent) - dt.timedelta(days=365)

    # Finding most active station
    most_active = session.query(Station.id, func.count(Measurement.station)).group_by(Measurement.station).\
        filter(Station.station == Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    query = session.query(Measurement.date, Measurement.tobs).\
        filter(Station.station == Measurement.station).\
        filter(Station.id == most_active).filter(Measurement.date >= one_year).all()
    
    session.close()

    # Creating a dictionary from row data
    all_temperature = []
    for date, temp in query:
        temp_dict = {}
        temp_dict['date'] = date
        temp_dict['temperature'] = temp
        all_temperature.append(temp_dict)

    return jsonify(all_temperature)

@app.route('/api/v1.0/start/<start>')
def min_max_avg(start):
    # Creating a session
    session = Session(engine)

    '''Calculate t_min, t_max, and t_avg for all dates greater than or eqal to the start date'''
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

   # Creating a dictionary from row data
    temp_stats = []
    for min, max, avg in results:
        temp_dict = {}
        temp_dict['Start Date'] = start
        temp_dict['Min Temp'] = min
        temp_dict['Max Temp'] = max
        temp_dict['Avg Temp'] = round(avg, 2)
        temp_stats.append(temp_dict)
    
    return jsonify(temp_stats)

@app.route('/api/v1.0/start/<start>/end/<end>')
def min_max_avg2(start, end):
    # Creating a session
    session = Session(engine)

    '''Calculate t_min, t_max, and t_avg for all dates greater than or eqal to the start date'''
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Creating a dictionary from row data
    temp_stats = []
    for min, max, avg in results:
        temp_dict = {}
        temp_dict['Start Date'] = start
        temp_dict['End Date'] = end
        temp_dict['Min Temp'] = min
        temp_dict['Max Temp'] = max
        temp_dict['Avg Temp'] = round(avg, 2)
        temp_stats.append(temp_dict)
    
    return jsonify(temp_stats)


if __name__ == '__main__':
    app.run(debug=True)