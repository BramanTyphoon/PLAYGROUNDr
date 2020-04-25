#!/home/bramante/anaconda3/envs/insight/bin/ python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 17:22:45 2020

@author: bramante
"""

from flask import render_template, request, Flask, jsonify
from GooglePlaces import GooglePlaces
from geopy.distance import geodesic 
#from util import process_review
from flask_bootstrap import Bootstrap
import numpy as np
import json

# Variables used within the other methods
# To keep Google API_KEY secret, I've written two ways to enter the API KEY. 
# Either require manual entry when running the server, or have a text file
# containing just the key stored in this file's directory's parent directory
#API_KEY = input("Provide a Google Places/Maps API KEY:")
with open('../API_KEY.txt','r') as fil:
    API_KEY = fil.readline()
search_radius = 5000 #Search radius for location search, in meters
gp = GooglePlaces(API_KEY, search_radius) # Object that interfaces with Google API to pull review data

# Variables useful for map display
init_origin = {"lat": 43.65, "lng": -79.38}
init_zoom = 12
search_query = 'park' #Type of Google Place to search for
max_results = 5#Maximum number of place results to display
max_walk = 1 #Maximum walking distance, in km, from user survey

# Start the application instance
application = Flask(__name__, template_folder="templates")
Bootstrap(application)

@application.route('/')
@application.route('/index',methods=['POST'])
def index():
    if request.form:
        candidate = gp.place_coordinate_by_textquery(request.form['location_field'])
        if candidate['candidates']:
            origin = candidate['candidates'][0]['geometry']['location']
        else:
            origin = init_origin
    else:
        origin = init_origin
    return render_template('mainmap.html', origin=json.dumps(origin), zoom=init_zoom,apikey = API_KEY,name = "Location Name", status = 'Directions: Click on a park to get amenities for that park, click anywhere else to search for nearby parks with the chosen amenities.', address = "Address")

# This route gets called when a user has clicked on a location with a placeid
@application.route('/singlepark', methods=['POST'])
def single_park_amenities():
    placeid = request.form['placeid']
    
    # Extract details with Google API
    reviews = gp.place_reviews(placeid)
    reviews = reviews['result']
    out_dict = {"results" : [process_review(reviews)]}
    return(jsonify(out_dict))
    
    
@application.route('/multipark', methods=['POST'])
def multi_park_amenities():
    lat = float(request.form['lat'])
    lon = float(request.form['lon'])
    options = np.array([1 if x else 0 for x in json.loads(request.form['search'])])

    # Find reviews for all parks within radius of the search location
    reviews = gp.retrieve_reviews_multi([search_query], [lat,lon])
    
    # Sometimes Google has duplicate places. Remove duplicates and combine
    # their reviews before passing to the review handler
    out_names = []
    reviews_no_duplicates = []
    for review in reviews:
        review = review['result']
        if review['name'] not in out_names:
            out_names.append(review['name'])
            reviews_no_duplicates.append(review)
        else:
            if 'reviews' in reviews_no_duplicates[out_names.index(review['name'])].keys():
                if 'reviews' in review.keys():
                    reviews_no_duplicates[out_names.index(review['name'])]['reviews'].extend(review['reviews'])
    
    
    out_dicts = []
    out_dists = []
    out_amens = []
    out_amens_diff = []
    # For each review, extract details and calculate distance from the search
    # location
    for review in reviews_no_duplicates:
        details = process_review(review)
        dist = geodesic((lat,lon),(details['location']['lat'],details['location']['lng'])).kilometers
        out_dists.append(dist)
        out_amens.append(sum([float(x) for x in details['scores']]))
        out_amens_diff.append(sum([x-float(y) if x == 1 else 0 for x,y in zip(options,details['scores'])]))
        details['distance'] = str(dist) + ' km'
        out_dicts.append(details)
        
    # Sort the output locations based on user input amenity requests or
    # distance/number of amenities. We only care about distance if it exceeds
    # some maximum distance our users are willing to walk
    out_dists2 = np.array(out_dists)
    out_dists2[out_dists2<max_walk] = 0
    # If the user doesn't pass us any options or selected all amenities, pass
    # them the results sorted by number of amenities for distance within 
    # maximum walking distance, and by distance otherwise
    if sum(options) == 0 or sum(options)==len(options):
        sorter = np.array(list(zip(list(range(len(out_dists2))),-np.array(out_amens),out_dists2)),dtype=[('index','i4'),('amens','f4'),('dists','f4')])
        sorter = np.sort(sorter,order=['dists','amens'])
    else:
        # If the user supplies desired amenities, sort first by number of 
        # amenities that match the desired list, and then by distance and total 
        # amenities
        sorter = np.array(list(zip(list(range(len(out_dists2))),-np.array(out_amens),out_dists2,out_amens_diff)),dtype=[('index','i4'),('amens','f4'),('dists','f4'),('diff','f4')])
        sorter = np.sort(sorter,order=['diff','dists','amens'])
    
    out_dicts = np.array(out_dicts)
    out_dicts = out_dicts[sorter['index']]
    
    return(jsonify({"results" : list(out_dicts[0:max_results])}))
        
if __name__ == "__main__":
    application.run(host='0.0.0.0',debug=True,port=5000)