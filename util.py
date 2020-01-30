#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 14:43:52 2020

@author: bramante
"""

#......................Utilities for the PLAYGROUNDr app.......................
# Author: James Bramante
# Date: January 24, 2020

#import nltk
#nltk.download('stopwords')
from gensim.models import FastText
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
import pandas as pd
import re

# Text preparation variables
REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;\.\n]') # Symbols to replace in string before model application
BAD_SYMBOLS_RE = re.compile('[^0-9a-z ]') # More symbols to replace, this time with ""
STOPWORDS = set(stopwords.words('english')) # Stop words to remove
lemmatizer = WordNetLemmatizer()

# Model development variables
vector_size = 128
window_size = 5
train_epochs = 5

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


# Method for preparing text for modeling
def process_review(review):
    if "park" not in review['types'] and not any([place_type not in review["name"].lower() for place_type in place_types]):
        out_name = review['name']
        out_text = "This site is not a park"
        out_scores = [0]*num_amenities
        out_address = review['formatted_address']
        out_location = review['geometry']['location']
    
    # If there are no reviews, don't run the model    
    elif 'reviews' not in review.keys():
        out_name = review['name']
        out_text = "No reviews available for this site"
        out_scores = [0]*num_amenities
        out_address = review['formatted_address']
        out_location = review['geometry']['location']
    else:
        # If there are too few reviews, don't run the model
        reviews_text = [text_prepare(rev) for rev in [revi['text'] for revi in review['reviews']] if text_prepare(rev)]
        if len(reviews_text) < min_num_reviews:
            out_name = review['name']
            out_text = "Insufficient (<4) reviews for this site."
            out_scores = [0]*num_amenities
            out_address = review['formatted_address']
            out_location = review['geometry']['location']
        else:
            out_name = review['name']
            out_text = ""
            out_address = review['formatted_address']
            out_location = review['geometry']['location']
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
                    
    out_dict = {
        'name' : out_name,
        'text' : out_text,
        'address' : out_address,
        'scores' : out_scores,
        'amenities' : amenity_names,
        'location' : out_location,
        'distance' : str(0)
                }
    return out_dict

def text_prepare(text):
    text = text.lower()
    text = re.sub(REPLACE_BY_SPACE_RE,' ',text)# replace REPLACE_BY_SPACE_RE symbols by space in text
    text = re.sub(BAD_SYMBOLS_RE, '',text)# delete symbols which are in BAD_SYMBOLS_RE from text
#    text = ' '.join([x for x in text.split() if x not in STOPWORDS])# delete stopwords from text and don't lemmatize
    text = ' '.join([lemmatizer.lemmatize(x) for x in text.split() if x not in STOPWORDS])# delete stopwords from text and lemmatize
    return text

def bag_of_words_vectorize(words,word2index):
    vect = np.zeros([1,len(word2index.keys())])
    for word in words.split():
        if word in word2index.keys():
            vect[0,word2index[word]] += 1
    return vect

def build_fasttext_model(full_database_file):
    review_database = pd.read_json(full_database_file,orient='records',lines='True')
    X_vector_train = []
    for review in list(review_database['reviews']):
        for rev in review.split(r'|||'):
            clean = re.split('[.!?;]',rev)
            X_vector_train += [text_prepare(sent.replace('/n',' ')).split() for sent in clean if sent]
            
    # Train the word2vec model
    # Let's create a basic word2vec model using our full review corpus
    # Parameters
    w2v_model = FastText(min_count=5,
                         window=window_size,
                         size=vector_size,
                         workers=4)
    w2v_model.build_vocab(X_vector_train)
    w2v_model.train(X_vector_train,total_examples=w2v_model.corpus_count,epochs=train_epochs)
    w2v_model.init_sims(replace=True)
    return w2v_model.wv