#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 16:19:49 2020

@author: bramante
"""

#..Use the Google Places API to extract reviews and photos from map locations..
import requests
import json
import os

class GooglePlaces(object):
    
    search_filename = "search_path.txt"
    DEFAULT_RADIUS = 500 #Default search radius, in meters
    
    def __init__(self, apiKey, search_radius=DEFAULT_RADIUS):
        super(GooglePlaces, self).__init__()
        self.search_radius = search_radius
        self.apiKey = apiKey
        
    def place_id_by_coordinate(self, query, location, radius=()):
        if not radius:
            radius = self.search_radius
        endpoint_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
                'input' : query,
                'inputtype' : 'textquery',
                'locationbias' : 'circle:{}@{},{}'.format(radius,location[0],location[1]),
                'key' : self.apiKey
                }
        res = requests.get(endpoint_url,params = params)
        results = json.loads(res.content)
        return results
    
    def place_id_by_textquery(self, query):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
                'input' : query,
                'inputtype' : 'textquery',
                'key' : self.apiKey
                }
        res = requests.get(endpoint_url,params = params)
        results = json.loads(res.content)
        return results
    
    def place_coordinate_by_textquery(self, query):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
                'input' : query,
                'inputtype' : 'textquery',
                'fields' : 'geometry',
                'key' : self.apiKey
                }
        res = requests.get(endpoint_url,params = params)
        results = json.loads(res.content)
        return results
    
    def places_by_coordinate(self, typ, location, radius=()):
        if not radius:
            radius = self.search_radius
        endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
                'type' : typ,
                'location' : '{},{}'.format(location[0],location[1]),
                'radius' : radius,
                'key' : self.apiKey
                }
        res = requests.get(endpoint_url,params = params)
        results = json.loads(res.content)
        return results
    
    def places_by_textquery(self, query, location, radius=()):
        if not radius:
            radius = self.search_radius
        endpoint_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
                'query' : query,
                'inputtype' : 'textquery',
                'location' : '{},{}'.format(radius,location[0],location[1]),
                'radius' : radius,
                'key' : self.apiKey
                }
        res = requests.get(endpoint_url,params = params)
        results = json.loads(res.content)
        return results
    
    def place_details(self, place_id):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
                'place_id' : place_id,
                'fields' : ",".join(['photo','formatted_address','name']),
                'key' : self.apiKey
                }
        res = requests.get(endpoint_url,params = params)
        results = json.loads(res.content)
        return results
    
    def place_reviews(self, place_id):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
                'place_id' : place_id,
                'language' : 'en',
                'fields' : ",".join(['geometry','review','formatted_address','name','place_id','type']),
                'key' : self.apiKey
                }
        res = requests.get(endpoint_url,params = params)
        results = json.loads(res.content)
        return results
    
    def place_photos(self, place_id):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
                'place_id' : place_id,
                'fields' : 'photo',
                'key' : self.apiKey
                }
        res = requests.get(endpoint_url,params = params)
        results = json.loads(res.content)['result']['photos']
        return results
    
    def retrieve_reviews(self, query, location=[]):
        find_fail_text = '{"html_attributions": [], "result": {"formatted_address": "nan", "geometry" : {"location" : "", "viewport": "nan"},"name": "nan", "place_id": "nan","types": ["Query Not Found"]}}'
        if location:
            candidates = self.place_id_by_coordinate(query,location,self.search_radius)
        else:
            candidates = self.place_id_by_textquery(query)
        if candidates['candidates']:
            reviews = self.place_reviews(candidates['candidates'][0]['place_id'])
        else:
            reviews = json.loads(find_fail_text)
        return reviews
    
    def retrieve_reviews_multi(self, query, location=()):
        find_fail_text = '{"html_attributions": [], "result": {"formatted_address": "nan", "geometry" : {"location" : "", "viewport": "nan"},"name": "nan", "place_id": "nan","types": ["Query Not Found"]}}'
        if isinstance(query,list):
            candidates = self.places_by_coordinate(query[0],location,self.search_radius)
        else:
            candidates = self.places_by_textquery(query,location,self.search_radius)
        if candidates['results']:
            reviews = [self.place_reviews(candidates['results'][ii]['place_id']) for ii in range(len(candidates['results']))]
        else:
            reviews = [json.loads(find_fail_text)]
        return reviews
        
    
    def retrieve_photo(self, photo_element):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/photo"
        params = {
                'photoreference' : photo_element['photo_reference'],
                'maxwidth' : photo_element['width'],
                'key' : self.apiKey
                }
        res = requests.get(endpoint_url,params = params)
        return res.url
    
    def retrieve_photo_url_from_location(self,search_text,location):
        candidates = self.place_id_by_coordinates(search_text,location,self.search_radius)
        place_id = candidates['candidates'][0]['place_id']
        photos = self.place_photos(place_id)
        photo_urls = []
        for photo in photos:
            photo_urls += [self.retrieve_photo(photo)]
        return (place_id, photo_urls)
    
    def save_photo_url_from_location(self,search_text,output_folder):
        (place_id, photo_urls) = self.retrieve_photo_url_from_location(search_text)
        with open(os.path.join(output_folder,self.search_filename),'w') as txtfile:
            txtfile.write("Location searched: {}\n".format(search_text))
            txtfile.write("Place ID: {}\n".format(place_id))
            txtfile.write("Photo URLs:\n")
            txtfile.writelines(photo_urls)
        
#workflow
#res = requests.get("https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=neutaconkanut%20park&inputtype=textquery&key=")
#results = json.loads(res.content)
#res = requests.get("https://maps.googleapis.com/maps/api/place/details/json?place_id={}&fields=photo&key=".format(results['candidates'][0]['place_id']))
#results2 = json.loads(res.content)
#results_photos = results2['result']['photos']
#res = requests.get("https://maps.googleapis.com/maps/api/place/photo?photoreference={}&maxwidth={}&key=".format(results_photos[0]['photo_reference'],results_photos[0]['width']))
#urllib.request.urlretrieve(res.url,"test.jpg")