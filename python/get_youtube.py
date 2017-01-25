#!/usr/bin/python

import requests
import os
import argparse
import json
import time
import sys
import urllib2
import math
from server import app

#TODO: convert this to work w/ the Fusion backend instead of one off
if __name__ == "__main__":
    # Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
    # tab of
    #   https://cloud.google.com/console
    # Please ensure that you have enabled the YouTube Data API for your project.
    DEVELOPER_KEY = app.config.get("YOUTUBE_DEVELOPER_KEY")
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    YOUTUBE_CHANNEL_ID = "UCPItOdfUk_tjlvqggkY-JsA" #Lucidworks video channel
    YOUTUBE_MAX_RESULTS = "30"
    
    FUSION_UI_URL = app.config['FUSION_URLS'][0]
    FUSION_INDEXING_API = "apollo/index-pipelines/default/collections/"
    FUSION_COLLECTION = app.config.get("FUSION_COLLECTION", "lucidfind")
    FUSION_USERNAME = app.config.get("FUSION_ADMIN_USERNAME", "admin")
    FUSION_PASSWORD = app.config.get("FUSION_ADMIN_PASSWORD")

    yt_search_url = "https://www.googleapis.com/"
    yt_search_url += YOUTUBE_API_SERVICE_NAME + "/" 
    yt_search_url += YOUTUBE_API_VERSION + "/" 
    yt_search_url += "search?"
    yt_search_url += "key=" + DEVELOPER_KEY
    yt_search_url += "&channelId=" + YOUTUBE_CHANNEL_ID
    yt_search_url += "&part=snippet,id"
    yt_search_url += "&maxResults=" + YOUTUBE_MAX_RESULTS
    
    yt_detail_url = "https://www.googleapis.com/"
    yt_detail_url += YOUTUBE_API_SERVICE_NAME + "/" 
    yt_detail_url += YOUTUBE_API_VERSION + "/" 
    yt_detail_url += "videos?"
    yt_detail_url += "key=" + DEVELOPER_KEY
    yt_detail_url += "&part=snippet"
    yt_detail_url += "&id="
    
    fusion_url = FUSION_UI_URL
    fusion_url += FUSION_INDEXING_API
    fusion_url += FUSION_COLLECTION
    fusion_url += "/index"

    r = requests.get(yt_search_url)
    r.raise_for_status()
    id_list = []
    video_list = []
    
    for page in range(0, int(math.ceil(float(r.json()["pageInfo"]["totalResults"])/r.json()["pageInfo"]["resultsPerPage"]))):
        print "Parsing page " + str(page)
        yt_search_response = r.json()
        video_string = ''
        for i in range(0, len(r.json()["items"])):
            if('videoId' not in r.json()["items"][i]["id"]):
                print "Item is not a video"
            else:
                video_string += ',' + r.json()["items"][i]["id"]["videoId"]
        
        r = requests.get(yt_detail_url + video_string)
        r.raise_for_status()
            
        for i in range(0, len(r.json()["items"])):
            video = r.json()["items"][i]
            video_list.append({
                "publishedOnDate":video["snippet"]["publishedAt"],
                "datasource_label":"youtube_parser", 
                "project_label":"YouTube",
                "description":video["snippet"]["description"].encode('utf-8'),
                "content":video["snippet"]["description"].encode('utf-8'),
                "title":video["snippet"]["title"].encode('utf-8'), 
                "suggest":video["snippet"]["title"].encode('utf-8'), 
                "id":("https://www.youtube.com/watch?v=" + video["id"]).encode('utf-8'), 
                "_lw_data_source_s":"website-lucidworks-youtube-lucidworks",
                "site_search_s":"video",
                "isBot":"false"
            })
            
        #setup for next page
        nextPageToken = yt_search_response.get("nextPageToken", [])
        if nextPageToken:
            next_request = yt_search_url + "&pageToken=" + yt_search_response["nextPageToken"]
            r = requests.get(next_request)
            r.raise_for_status()
        
        headers = {'content-type': 'application/json'}
        print "Sending video list to {0}".format(fusion_url)
        #REPLACE WITH Fusion backend support
        fusion_update = requests.post(fusion_url, data=json.dumps(video_list), headers=headers, auth=(FUSION_USERNAME, FUSION_PASSWORD))
        print("Successfully sent page {0} to Fusion: {1}".format(page, fusion_update))