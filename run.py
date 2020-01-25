#!/home/bramante/anaconda3/envs/insight/bin/ python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 17:22:45 2020

@author: bramante
"""

from flask import render_template, request, Flask
#from flask_bootstrap import Bootstrap
from GooglePlaces import GooglePlaces
from util import text_prepare, build_fasttext_model
import numpy as np
import pickle
import json

# Variables used within the other methods
API_KEY = 'AIzaSyAUzvGNHIl8i3gY_GC54lJd-NJLq6LbNNA' # Key required for Google API use
gp = GooglePlaces(API_KEY) # Object that interfaces with Google API to pull review data

# Variables useful for map display
init_origin = {"lat": 43.65, "lng": -79.38}
init_zoom = 12


# Define model parameters and load in the model files
num_amenities = 7 # Number of amenities predicted by the classifier
min_num_reviews = 4 # Minimimum number of reviews to accept before running model
amenity_names = ['Playground','Splash pad','Pool','Ice rink','Restroom','Sports field', 'Dog park']
model_file_name = "data/NBCmodel.mod" # Filename containing the classification model
review_database_name = "data/park_reviews_database_20200121.json" # Filename of database containing all park reviews

with open(model_file_name,'rb') as fp:
    clf = pickle.load(fp)
    
w2v_model = build_fasttext_model(review_database_name)

# Start the app instance
app = Flask(__name__, template_folder="templates")
#Bootstrap(app)

@app.route('/')
def index():
    return render_template('mainmap.html', origin=json.dumps(init_origin), zoom=init_zoom,apikey = API_KEY,name = "Location Name", status = "Click on a location", address = "Address", amenities = zip(amenity_names,[False]*num_amenities))

# This route gets called when a user has clicked on a location with a placeid
@app.route('/park_amenities')
def park_amenity():
    # Extract Google Places details for the placeid
    placeid = request.args.get('placeid')
    inlon = float(request.args.get('inlon'))
    inlat = float(request.args.get('inlat'))
    zoom = float(request.args.get('zoom'))
    
    reviews = gp.place_reviews(placeid)
    reviews = reviews['result']
    
    # If the place is not a park, don't run the model
    if "park" not in reviews['types']:
        out_name = reviews['name']
        out_text = "This site is not a park"
        out_amenities = [0]*num_amenities
        out_address = reviews['formatted_address']
    
    # If there are no reviews, don't run the model    
    elif 'reviews' not in reviews.keys():
        out_name = reviews['name']
        out_text = "No reviews available for this site"
        out_amenities = [0]*num_amenities
        out_address = reviews['formatted_address']
    else:
        # If there are too few reviews, don't run the model
        reviews_text = [text_prepare(rev) for rev in [revi['text'] for revi in reviews['reviews']] if text_prepare(rev)]
        if len(reviews_text) < min_num_reviews:
            out_name = reviews['name']
            out_text = "Insufficient (<4) reviews for this site."
            out_amenities = [0]*num_amenities
            out_address = reviews['formatted_address']
        else:
            out_name = reviews['name']
            out_text = ""
            out_address = reviews['formatted_address']
            # Run the model on the reviews text and return the results
            # Clean the text
            reviews_text = ' '.join(reviews_text)
            # Vectorize the text
            X_vect = np.zeros([1,w2v_model['test'].shape[0]])
            for word in reviews_text.split():
                X_vect += w2v_model[word]
            X_vect = X_vect / len(reviews_text.split())
            # Run the classification model
            y_pred = clf.predict(X_vect[0,:].reshape(1,-1))
            out_amenities = [y_pred[0,ii] for ii in range(y_pred.shape[1])]
    
    return render_template('mainmap.html',origin=json.dumps({"lat": inlat,"lng": inlon}), zoom=float(zoom),apikey=API_KEY, name = out_name, status = out_text, address = out_address, amenities = zip(amenity_names,[x == 1 for x in out_amenities]))
        
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)