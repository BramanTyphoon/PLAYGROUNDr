#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
......................Utilities for the PLAYGROUNDr app.......................
Author: James Bramante
Date: January 24, 2020

This script can be imported as a module and contains utility methods for the 
PLAYGROUNDr web app to process Google Reviews and implement NLP models

This script requires gensim, nltk, numpy, pandas, and pickle for pickled models
"""
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
amenity_names = ['Playground','Sports field','Pool','Splash pad','Ice rink', 'Dog park']
model_file_name = "data/classifier.mod" # Filename containing the classification model
vectorizer_file_name = "data/TFIDFmodel.mod"

## Some additional parsing/kluges help the app perform better
# If these words appear in the location name, don't throw out if Google fails
# to label as park
place_types = ['playground','pool', 'dog park', 'dog run', 'rink', 'recreation centre', 'community centre','recreation center', 'community center', 'sports field']

# Load the string encoder model and amenity classification model
with open(model_file_name,'rb') as fp:
    clf = pickle.load(fp)
    
with open(vectorizer_file_name,'rb') as fp:
    tfidf_model = pickle.load(fp)


def process_review(review):
    """Apply a classification model to review text to predict amenities
    

    Parameters
    ----------
    review : dict
        JSON dict output from Google Places request for reviews. The first 
        name should be 'results', and its value should contain all other info

    Returns
    -------
    out_dict : dict
        Dictionary containing all of the location information from the Google
        Places request, plus predictions for which amenities are at that
        location
        
    """
    
    # Set default outputs
    out_name = review['name']
    out_text = ""
    out_scores = [0]*num_amenities
    out_address = review['formatted_address']
    out_location = review['geometry']['location']
    
    if "park" not in review['types'] and not any([place_type in review["name"].lower() for place_type in place_types]):
        out_text = "This site is not a park; results may be invalid."
    
    # If there are no reviews, don't run the model    
    if 'reviews' not in review.keys():
        out_name = review['name']
        out_text = "No reviews available for this site"
    else:
        # If there are too few reviews, don't run the model
        reviews_text = [text_prepare(rev) for rev in [revi['text'] for revi in review['reviews']] if text_prepare(rev)]
        if len(reviews_text) < min_num_reviews:
            out_name = review['name']
            out_text = "Insufficient (<4) reviews for this site."
        else:
            out_name = review['name']
            # Run the model on the reviews text and return the results
            # Clean the text
            reviews_text = ' '.join(reviews_text)
            # Vectorize the text
            X_vect = tfidf_vectorize(reviews_text,tfidf_model)
            # Run the classification model
            y_pred = [clf[ii].predict(X_vect[0,:])[0] for ii in range(len(clf))]
            out_scores = [str(y_pred[ii]) for ii in range(len(y_pred))]
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
    """Prepares (formats, lemmatizes) text input prior to vectorization

    Parameters
    ----------
    text : str
        A review document (a string containing one or more reviews)

    Returns
    -------
    text : str
    
    """
    
    text = text.lower()
    text = re.sub(REPLACE_BY_SPACE_RE,' ',text)# replace REPLACE_BY_SPACE_RE symbols by space in text
    text = re.sub(BAD_SYMBOLS_RE, '',text)# delete symbols which are in BAD_SYMBOLS_RE from text
#    text = ' '.join([x for x in text.split() if x not in STOPWORDS])# delete stopwords from text and don't lemmatize
    text = ' '.join([lemmatizer.lemmatize(x) for x in text.split() if x not in STOPWORDS])# delete stopwords from text and lemmatize
    return text

def bag_of_words_vectorize(words,word2index):
    """
    Vectorizes text input using a bag of words model

    Parameters
    ----------
    words : str
        A review document (a string containing one or more reviews)
    word2index : dict
        Vector of word : index pairs for every word in a vocabulary

    Returns
    -------
    vect : numpy.array
        An array containing counts for every word in a vocabulary

    """
    vect = np.zeros([1,len(word2index.keys())])
    for word in words.split():
        if word in word2index.keys():
            vect[0,word2index[word]] += 1
    return vect

def tfidf_vectorize(words,tfidf):
    """
    Vectorizes text using a Term Frequency-Inverse Document Frequency model

    Parameters
    ----------
    words : str
        A review document (a string containing one or more reviews)
    tfidf : sklearn.TfidfVectorizer
        A vectorizer that takes a list of strings as input documents

    Returns
    -------
    numpy.array
        An array containing TF-IDF values for the input review document

    """
    return tfidf.transform([words])

def build_fasttext_model(full_database_file):
    """
    Trains a word2vec model from scratch

    Parameters
    ----------
    full_database_file : pandas.DataFrame
        Precisely formatted Pandas database containing a large number of 
        reviews

    Returns
    -------
    gensim.models.Word2Vec
        A word2vec vectorizer

    """
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