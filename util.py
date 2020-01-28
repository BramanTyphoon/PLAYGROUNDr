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

# Method for preparing text for modeling
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