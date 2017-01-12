#!/usr/bin/python

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import requests
import os
import argparse
import json
import time
import sys
import urllib2

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = ""
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_videos(id_string):
    print("Getting video details")
    video_details = []
    video_information = youtube.videos().list(
        id= id_string,
        part="snippet, id"
    ).execute()
    for video in video_information["items"]:
        video_details.append({
            "publishedOnDate":video["snippet"]["publishedAt"],
            "datasource_label":"youtube_parser", 
            "project_label":"youtube",
            "description":video["snippet"]["description"].encode('utf-8'),
            "content":video["snippet"]["description"].encode('utf-8'),
            "title":video["snippet"]["title"].encode('utf-8'), 
            "url":("https://www.youtube.com/watch?v=" + video["id"]).encode('utf-8'), 
            "_lw_data_source_s":"website-lucidworks-youtube-lucidworks",
            "site_search_s":"video"
        })
    return video_details

def get_id_string(search_response):
    print("Getting Id String!")
    id_vals = [d["id"] for d in search_response]
    id_string = ""
    for id_val in id_vals: 
        if id_val["kind"] == "youtube#video":
            id_string += id_val["videoId"]+ ","
    return id_string

def get_all_ids(final_video_details, search_response):
    # Call the search.list method to retrieve results matching the specified
    # query term.
    print("Getting all ids")
    id_string = get_id_string(search_response["items"])
    video_details = get_videos(id_string)
    final_video_details += video_details
    nextPageToken = search_response.get("nextPageToken", [])
    if nextPageToken == []:
        return final_video_details
    else:
        print ("Getting the next page of results!")
        search_response = youtube.search().list(
            channelId="UCPItOdfUk_tjlvqggkY-JsA",
            part="id",
            maxResults=25,
            pageToken=nextPageToken
        ).execute()
        return get_all_ids(final_video_details, search_response)

if __name__ == "__main__":
    print("Starting the service")
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    print ("finished making youtube")
    search_response = youtube.search().list(
        channelId="UCPItOdfUk_tjlvqggkY-JsA",
        part="id",
        maxResults=25,
    ).execute()
    print("finished getting search_response")
    final_video_details = []
    final_list = get_all_ids(final_video_details, search_response)
    print(len(final_list))
    json_vids = json.dumps(final_list)
    headers = {'content-type': 'application/json'}
    r = requests.post("http://localhost:8983/solr/lucidfind/update/json?commit=true", data = json_vids, headers=headers)
    r.raise_for_status()
    print("Successfully sent data to solr!")