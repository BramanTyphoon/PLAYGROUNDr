#!/home/bramante/anaconda3/envs/insight/bin/ python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 17:22:45 2020

@author: bramante
"""

from flask import render_template, request, Flask, jsonify
from GooglePlaces import GooglePlaces
from geopy.distance import geodesic 
from util import process_review
from flask_bootstrap import Bootstrap
import json

# Variables used within the other methods
#API_KEY = 'AIzaSyAUzvGNHIl8i3gY_GC54lJd-NJLq6LbNNA' # Key required for Google API use
API_KEY = input("Provide a Google Places/Maps API KEY:")
search_radius = 1000 #Search radius for location search, in meters
gp = GooglePlaces(API_KEY, search_radius) # Object that interfaces with Google API to pull review data

# Variables useful for map display
init_origin = {"lat": 43.65, "lng": -79.38}
init_zoom = 12
search_query = 'park'

# Start the app instance
app = Flask(__name__, template_folder="templates")
Bootstrap(app)

@app.route('/')
def index():
    return render_template('mainmap.html', origin=json.dumps(init_origin), zoom=init_zoom,apikey = API_KEY,name = "Location Name", status = "Click on a location", address = "Address")

# This route gets called when a user has clicked on a location with a placeid
@app.route('/singlepark', methods=['POST'])
def single_park_amenities():
    placeid = request.form['placeid']
    
    # Extract details with Google API
    reviews = gp.place_reviews(placeid)
    reviews = reviews['result']
    out_dict = {"results" : [process_review(reviews)]}
    return(jsonify(out_dict))
    
    
@app.route('/multipark', methods=['POST'])
def multi_park_amenities():
    lat = float(request.form['lat'])
    lon = float(request.form['lon'])
    print([lat,lon])
    reviews = gp.retrieve_reviews_multi([search_query], [lat,lon])
    out_dicts = []
    out_dists = []
    # For each review, extract details and calculate distance from the search
    # location
    for review in reviews:
        review = review['result']
        details = process_review(review)
        dist = geodesic((lat,lon),(details['location']['lat'],details['location']['lng'])).kilometers
        out_dists.append(dist)
        details['distance'] = str(dist) + ' km'
        out_dicts.append(details)
    # Sort the output locations based on distance to the search location
    out_dicts = sorted(out_dicts,key = lambda i : i['distance'])
    
    return(jsonify({"results" : out_dicts}))
        
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)