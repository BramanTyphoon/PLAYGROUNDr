#!/home/bramante/anaconda3/envs/insight/bin/ python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 17:22:45 2020

@author: bramante
"""

from flask import render_template, request, Flask, jsonify
from GooglePlaces import GooglePlaces
from util import text_prepare, bag_of_words_vectorize
from flask_bootstrap import Bootstrap
import numpy as np
import pickle
import json

# Variables used within the other methods
#API_KEY = 'AIzaSyAUzvGNHIl8i3gY_GC54lJd-NJLq6LbNNA' # Key required for Google API use
API_KEY = input("Provide a Google Places/Maps API KEY:")
gp = GooglePlaces(API_KEY) # Object that interfaces with Google API to pull review data

# Variables useful for map display
init_origin = {"lat": 43.65, "lng": -79.38}
init_zoom = 12


# Define model parameters and load in the model files
num_amenities = 7 # Number of amenities predicted by the classifier
min_num_reviews = 4 # Minimimum number of reviews to accept before running model
amenity_names = ['Playground','Splash pad','Pool','Ice rink','Restroom','Sports field', 'Dog park']
model_file_name = "data/classifier.mod" # Filename containing the classification model
review_database_name = "data/park_reviews_database_20200121.json" # Filename of database containing all park reviews
vectorizer_file_name = "data/BoWmodel.mod"

## Some additional parsing/kluges help the app perform better
# If these words appear in the location name, don't throw out if Google fails
# to label as park
place_types = ['playground','pool', 'dog park', 'recreation centre', 'community centre','recreation center', 'community center', 'sports field']

with open(model_file_name,'rb') as fp:
    clf = pickle.load(fp)
    
with open(vectorizer_file_name,'rb') as fp:
    bow_model = pickle.load(fp)

# Start the app instance
app = Flask(__name__, template_folder="templates")
Bootstrap(app)

@app.route('/')
def index():
    return render_template('mainmap.html', origin=json.dumps(init_origin), zoom=init_zoom,apikey = API_KEY,name = "Location Name", status = "Click on a location", address = "Address", amenities = zip(amenity_names,[False]*num_amenities))

# This route gets called when a user has clicked on a location with a placeid
@app.route('/singlepark', methods=['POST'])
def single_park_amenities():
    placeid = request.form['placeid']
    
    # Extract details with Google API
    reviews = gp.place_reviews(placeid)
    reviews = reviews['result']
    
    # If the place is not a park, don't run the model
    if "park" not in reviews['types'] and not [place_type not in reviews["name"].lower() for place_type in place_types].any():
        out_name = reviews['name']
        out_text = "This site is not a park"
        out_scores = [0]*num_amenities
        out_address = reviews['formatted_address']
    
    # If there are no reviews, don't run the model    
    elif 'reviews' not in reviews.keys():
        out_name = reviews['name']
        out_text = "No reviews available for this site"
        out_scores = [0]*num_amenities
        out_address = reviews['formatted_address']
    else:
        # If there are too few reviews, don't run the model
        reviews_text = [text_prepare(rev) for rev in [revi['text'] for revi in reviews['reviews']] if text_prepare(rev)]
        if len(reviews_text) < min_num_reviews:
            out_name = reviews['name']
            out_text = "Insufficient (<4) reviews for this site."
            out_scores = [0]*num_amenities
            out_address = reviews['formatted_address']
        else:
            out_name = reviews['name']
            out_text = ""
            out_address = reviews['formatted_address']
            # Run the model on the reviews text and return the results
            # Clean the text
            reviews_text = ' '.join(reviews_text)
            # Vectorize the text
            X_vect = bag_of_words_vectorize(reviews_text,bow_model)
            X_vect = X_vect / len(reviews_text.split())
            # Run the classification model
            y_pred = clf.predict(X_vect[0,:].reshape(1,-1))
            out_scores = [str(y_pred[0,ii]) for ii in range(y_pred.shape[1])]
            # If the amenity name appears in the location name, it should
            # probably be at that location
            for ii in range(len(out_scores)):
                if amenity_names[ii].lower() in out_name.lower():
                    out_scores[ii] = str(1)
            
    # Return JSON output
    return jsonify({"results" : [{
            'name' : out_name,
            'text' : out_text,
            'address' : out_address,
            'scores' : out_scores,
            'amenities' : amenity_names
            }]})
        
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)