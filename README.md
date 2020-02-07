# PLAYGROUNDr
A web-app to identify park amenities from Google Reviews. This project was developed as part of the Insight Data Science Program over four weeks in 2020.

## Motivation
Determining what amenities (e.g. playgrounds, sports fields, dog parks) exist in parks can require a surprising amount of online research, involving poring over satellite imagery, Google reviews, and search results. Even most city governments don't have a comprehensive centralized database of all their parks' facilities. PLAYGROUNDr saves you time by doing this research work for you.

## Installation
Fork or clone the app to your local machine. The app can be run locally using the following command from the PLAYGROUNDr directory.
```
flask run.py
```
The web-app will then be accessible by default in any internet browser at 0.0.0.0:5000 (localhost, port 5000). Alternatively, the app can be run off a server using gunicorn and nginx.

Running the web-app requires a viable [Google API key](https://developers.google.com/maps/documentation/javascript/get-api-key) with access to Google Places and Google Maps APIs.

## How does it work?
### Model description
Underneath the Flask application, PLAYGROUNDr applies a series of logistic regressions to Google reviews accessed through the Google Places API. There is one logistic regression trained for each amenity listed in the app's search options: Playground, Sports Field, Pool, Splash Pad, Ice Rink, and off-leash Dog Park. 

The logistic regression models were trained with Google reviews sampled from over 900 parks in Toronto, Ontario, Canada, for which a comprehensive [database of amenities](https://open.toronto.ca/dataset/parks-and-recreation-facilities/) was available. The models use the 2,000 most frequent tokens in a unigram+bigram vocabulary, embedded/vectorized using term frequency inverse document frequency (TF-IDF) trained on Google reviews sampled from roughly 20,000 parks from comprehensive databases belonging to [Pennsylvania](https://newdata-dcnr.opendata.arcgis.com/datasets/pennsylvania-local-park-boundaries), [Rhode Island](https://esri-boston-office.hub.arcgis.com/datasets/0e2070ec0e844d10b291147a080b522f_0/data?geometry=-72.763%2C41.646%2C-70.504%2C42.004), and [Florida](http://geodata.myflorida.com/datasets/c5b766ec085440738425724c451701aa_0), whose amenity listings were not as comprehensive as the Toronto database.

### Model training
Plots of cross-validated training and test precision for the models can be found in the Jupyter notebook [PLAYGROUNDr_model_training.ipynb](PLAYGROUNDr_model_training.ipynb). Google Places API's terms of service preclude caching data acquired through the API. Therefore, the data used to train the models is not included in this repository, and the Jupyter notebook is meant to be static.

### Files
* [wsgi.py](wsgi.py) - Drives run.py for Gunicorn HTTP server
* [run.py](run.py) - Creates the Flask app that handles server requests from the webpage
* [util.py](util.py) - Contains functions used by the app to apply the models to reviews
* [GooglePlaces.py](GooglePlaces.py) - A class used to interface with Google Places/Details API
* [mainmap.html](templates/mainmap.html) - HTML template with the embedded Google map and Javascript/AJAX to handle communication between Flask server and users.
* [classifier.mod](data/classifier.mod) - A pickled list of logistic regression models applied to Google Reviews
* [TFIDFmodel.mod](data/TFIDFmodel.mod) - A pickled TFIDF vectorizer that feeds into the classification models

## Built with

* [Google Maps Javascript API](https://developers.google.com/maps/documentation/javascript/tutorial) - API used to embed Google Maps and extract location coordinates and place ids.
* [Flask](https://palletsprojects.com/p/flask/) - Python-based web application framework

Dependencies can be found in [requirements.txt](requirements.txt). Packages used include geopy, json, numpy, nltk, pickle, pandas, re, requests, gensim (for a legacy function not actually used in the current version of the app).

## Authors
* James Bramante - initial work - [BramanTyphoon](https://github.com/BramanTyphoon)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments
* [GooglePlaces.py](GooglePlaces.py) was modeled off of [code](https://python.gotrained.com/google-places-api-extracting-location-data-reviews/) by [Majid Alizadeh](https://python.gotrained.com/author/majid-alizadeh/)


