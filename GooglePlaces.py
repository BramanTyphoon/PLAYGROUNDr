#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
...............Google Places API utilities for PLAYGROUNDr web app.............
Author: James Bramante
Date: January 15, 2020

This module contains the GooglePlaces class for interfacing with Google Places 
API.
"""

#..Use the Google Places API to extract reviews and photos from map locations..
import requests
import json
import os

class GooglePlaces(object):
    """A utility class used to interface with Google Places API
    
    Attributes
    ----------
    search_filename : str
        filename of text log file to record Google Places Photo URLs
    DEFAULT_RADIUS : float
        search radius in meters to use as a default if not supplied to init
    search_radius : float
        search radius to use for location-based queries
    apiKey : str
        Google Cloud API key with access to Google Places
        
    Methods
    -------
    place_id_by_coordinate(self, query, location, radius=()):
        Find a Google PlaceID given a text search query and coordinates
    place_id_by_textquery(self, query):
        Find a Google PlaceID given just a text search query
    place_id_by_textquery(self, query):
        Find a Google PlaceID given just a text search query
    place_coordinate_by_textquery(self, query):
        Find location coordinates given just a text search query
    places_by_coordinate(self, typ, location, radius=()):
        Find multiple Google PlaceIDs given a location type and coordinates
    places_by_textquery(self, query, location, radius=()):
        Find multiple Google PlaceIDs given a text query and coordinates
    place_details(self, place_id):
        Find Google Place Details given a PlaceID
    place_reviews(self, place_id):
        Find Google Place Reviews given a PlaceID
    place_photos(self, place_id):
        Find just photos for a location given a Google PlaceID
    retrieve_reviews(self, query, location=()):
        Retrieve Google Places reviews given text query and optional coords
    retrieve_reviews_multi(self, query, location=()):
        Retrieve Google Places reviews for multiple locations
    retrieve_photo(self, photo_element):
        Given a Google photo element, returns the url for photo retrieval
    retrieve_photo_url_from_location(self,query,location):
        Retrieve Google Places photos given text query and optional coords
    save_photo_url_from_location(self,search_text,output_folder):
        Retrieve and save Google Places photos given text query and folder
    """
    
    search_filename = "search_path.txt"
    DEFAULT_RADIUS = 500 #Default search radius, in meters
    
    def __init__(self, apiKey, search_radius=DEFAULT_RADIUS):
        """
        Parameters
        ----------
        apiKey : str
            required Google Cloud api key with access to Google Places
        search_radius : float, optional
            radius within which to conduct location-based searches. The 
            default is DEFAULT_RADIUS.

        Returns
        -------
        None.

        """
        
        super(GooglePlaces, self).__init__()
        self.search_radius = search_radius
        self.apiKey = apiKey
        
    def place_id_by_coordinate(self, query, location, radius=()):
        """Find a Google PlaceID given a text search query and coordinates

        Parameters
        ----------
        query : str
            search query. e.g. keywords describing a park
        location : [float,float]
            a two-index lat/lon list or tuple
        radius : float, optional
            search radius, in meters, within which to search.

        Returns
        -------
        results : JSON dict
            JSON dict of Google Places output

        """
        
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
        """Find a Google PlaceID given just a text search query

        Parameters
        ----------
        query : str
            search query. e.g. keywords describing a park

        Returns
        -------
        results : JSON dict
            JSON dict of Google Places output

        """
        
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
        """Find location coordinates given just a text search query

        Parameters
        ----------
        query : str
            search query. e.g. keywords describing a park

        Returns
        -------
        results : JSON dict
            JSON dict of Google Places geometry output

        """
        
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
        """Find multiple Google PlaceIDs given a location type and coordinates

        Parameters
        ----------
        typ : str
            location type used by Google to index its locations. N.B. only some
            are searchable (refer to Google Places documentation)
        location : [float,float]
            a two-index lat/lon list or tuple
        radius : float, optional
            search radius, in meters, within which to search.

        Returns
        -------
        results : JSON dict
            JSON dict of Google Places output

        """
        
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
        """Find multiple Google PlaceIDs given a text query and coordinates

        Parameters
        ----------
        query : str
            search query. e.g. keywords describing a park
        location : [float,float]
            a two-index lat/lon list or tuple
        radius : float, optional
            search radius, in meters, within which to search.

        Returns
        -------
        results : JSON dict
            JSON dict of Google Places output

        """
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
        """Find Google Place Details given a PlaceID

        Parameters
        ----------
        place_id : str
            Google PlaceID for the desired location

        Returns
        -------
        results : JSON dict
            JSON dict of Google Places Details output (photos, address, name)

        """
        
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
        """Find Google Place Reviews given a PlaceID

        Parameters
        ----------
        place_id : str
            Google PlaceID for the desired location

        Returns
        -------
        results : JSON dict
            JSON dict of Google Places Details output (geometry, reviews,
                                                       address, name, type)

        """
        
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
        """Find just photos for a location given a Google PlaceID
        
        Parameters
        ----------
        place_id : str
            Google PlaceID for the desired location
            
        Returns
        -------
        results : JSON dict
            JSON dict of photo details for the requested location
        """
        
        endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
                'place_id' : place_id,
                'fields' : 'photo',
                'key' : self.apiKey
                }
        res = requests.get(endpoint_url,params = params)
        results = json.loads(res.content)['result']['photos']
        return results
    
    def retrieve_reviews(self, query, location=()):
        """Retrieve Google Places reviews given text query and optional coords
        
        Contains a request for a place_id and uses it to request reviews

        Parameters
        ----------
        query : str
            text search query to find a location
        location : [float, float], optional
            lat/lon list or tuple of float location coordinates

        Returns
        -------
        reviews : JSON dict
            JSON dict containing all of the reviews

        """
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
        """Retrieve Google Places reviews for multiple locations
        
        Contains a request for many PlaceIDs and uses them to request reviews

        Parameters
        ----------
        query : str
            text search query to find a location
        location : [float, float], optional
            lat/lon list or tuple of float location coordinates

        Returns
        -------
        reviews : list
            list of JSON dicts containing all of the reviews for multiple locs
            
        """

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
        """Given a Google photo element, returns the url for photo retrieval
        
        Parameters
        ----------
        photo_element : str
            Google-provided unique reference for a Google Places photo
        
        Returns
        -------
        str
            a url at which the photo can be retrieved
        
        """
        endpoint_url = "https://maps.googleapis.com/maps/api/place/photo"
        params = {
                'photoreference' : photo_element['photo_reference'],
                'maxwidth' : photo_element['width'],
                'key' : self.apiKey
                }
        res = requests.get(endpoint_url,params = params)
        return res.url
    
    def retrieve_photo_url_from_location(self,query,location):
        """Retrieve Google Places photos given text query and optional coords
        
        Contains a request for a place_id and uses it to request photo urls

        Parameters
        ----------
        query : str
            text search query to find a location
        location : [float, float], optional
            lat/lon list or tuple of float location coordinates

        Returns
        -------
        tuple
            tuple of the PlaceID and the URLs of the photos associated with it

        """
        
        candidates = self.place_id_by_coordinates(query,location,self.search_radius)
        place_id = candidates['candidates'][0]['place_id']
        photos = self.place_photos(place_id)
        photo_urls = []
        for photo in photos:
            photo_urls += [self.retrieve_photo(photo)]
        return (place_id, photo_urls)
    
    def save_photo_url_from_location(self,search_text,output_folder):
        """Retrieve and save Google Places photos given text query and folder
        
        Contains a request for a place_id and uses it to download photos

        Parameters
        ----------
        query : str
            text search query to find a location
        output_folder : str
            location to which photos should be saved

        Returns
        -------
        None.
        
        """

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