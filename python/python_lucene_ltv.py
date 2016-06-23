# -*- coding: utf-8 -*-
################################################################
#### Open Source Community Contributor Lifetime Value Model ###
################################################################

# Specific case: Lucene mailing list (mailing-list-lucene-lucene-dev datasource in the lucidfind collection)

import pysolr
import requests
import itertools
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import sys
reload(sys)
sys.setdefaultencoding('utf8')

solr = pysolr.Solr('http://localhost:8983/solr/lucidfind_shard1_replica1/',timeout=10)

# Prior to pulling the lucene data from Solr we have to do a bit of data cleaning,.
# Certain fields that we wish to loop through are non existent in some documents.

# There are 4 docs without a 'body' field - as such providing significantly less information for us to work with
# As these docs represent a very small proportion ofthe total docs we will disgard them
 
# Found these 4 docs by querying q = _lw_data_source_s:"mailing-list-lucene-lucene-dev" AND -body:[* TO *]
# http://localhost:8983/solr/lucidfind_shard1_replica1/select?q=_lw_data_source_s%3A%22mailing-list-lucene-lucene-dev%22+AND+-body%3A%5B*+TO+*%5D&wt=json&indent=true)

#Deleting by hash_id:170849bdc0f7ffa2
#http://localhost:8983/solr/update?stream.body=<delete><query>hash_id:170849bdc0f7ffa2</query></delete>&commit=true
requests.get('http://localhost:8983/solr/lucidfind_shard1_replica1/update?stream.body=%3Cdelete%3E%3Cquery%3Ehash_id%3A170849bdc0f7ffa2%3C/query%3E%3C/delete%3E&commit=true')

#Deleting hash_id:a2fbaf6e779336bb
#http://localhost:8983/solr/update?stream.body=<delete><query>hash_id:a2fbaf6e779336bb</query></delete>&commit=true
requests.get('http://localhost:8983/solr/lucidfind_shard1_replica1/update?stream.body=%3Cdelete%3E%3Cquery%3Ehash_id%3Aa2fbaf6e779336bb%3C/query%3E%3C/delete%3E&commit=true')

#Deleting hash_id:ddfa07e14b5eb842
#http://localhost:8983/solr/update?stream.body=<delete><query>hash_id:ddfa07e14b5eb842</query></delete>&commit=true
requests.get('http://localhost:8983/solr/lucidfind_shard1_replica1/update?stream.body=%3Cdelete%3E%3Cquery%3Ehash_id%3Addfa07e14b5eb842%3C/query%3E%3C/delete%3E&commit=true')

#Deleting hash_id:890c723e69ccc7a4
#http://localhost:8983/solr/update?stream.body=<delete><query>hash_id:890c723e69ccc7a4</query></delete>&commit=true
requests.get('http://localhost:8983/solr/lucidfind_shard1_replica1/update?stream.body=%3Cdelete%3E%3Cquery%3Ehash_id%3A890c723e69ccc7a4%3C/query%3E%3C/delete%3E&commit=true')

#########################################################################################################################
# INTENT TO DO THIS PROCESS BY AUTOMATED MEANS AS OPPOSED TO MANUALLY SEARCHING, FINDING THE hash_id AND SENDING REQUESTS
#########################################################################################################################

# We require subject field present on all docs
# 7 docs without 'subject' field
# Found these 7 docs by querying q = _lw_data_source_s:"mailing-list-lucene-lucene-dev" AND -subject:[* TO *]
# http://localhost:8983/solr/lucidfind_shard1_replica1/select?q=_lw_data_source_s%3A%22mailing-list-lucene-lucene-dev%22+AND+-subject%3A%5B*+TO+*%5D&wt=json&indent=true

# Get rid of these 7 docs - the body field of these docs does not contain anything informative e.g   "body": "<br>\n",

#Deleting by hash_id:117ad464dc7c624
#http://localhost:8983/solr/lucidfind_shard1_replica1/update?stream.body=%3Cdelete%3E%3Cquery%3Ehash_id%3A117ad464dc7c624%3C/query%3E%3C/delete%3E&commit=true

#Deleting hash_id:d33f7649f4986ae1
requests.get('http://localhost:8983/solr/lucidfind_shard1_replica1/update?stream.body=%3Cdelete%3E%3Cquery%3Ehash_id%3Ad33f7649f4986ae1%3C/query%3E%3C/delete%3E&commit=true')

#Deleting hash_id:a161fd5061437587
requests.get('http://localhost:8983/solr/lucidfind_shard1_replica1/update?stream.body=%3Cdelete%3E%3Cquery%3Ehash_id%3Aa161fd5061437587%3C/query%3E%3C/delete%3E&commit=true')

#Deleting hash_id:7b9f313de77dcf40
requests.get('http://localhost:8983/solr/lucidfind_shard1_replica1/update?stream.body=%3Cdelete%3E%3Cquery%3Ehash_id%3A7b9f313de77dcf40%3C/query%3E%3C/delete%3E&commit=true')

#Deleting hash_id:7061d972b3e1228a
requests.get('http://localhost:8983/solr/lucidfind_shard1_replica1/update?stream.body=%3Cdelete%3E%3Cquery%3Ehash_id%3A7061d972b3e1228a%3C/query%3E%3C/delete%3E&commit=true')

#Deleting hash_id:1d03267c6ed6be23
requests.get('http://localhost:8983/solr/lucidfind_shard1_replica1/update?stream.body=%3Cdelete%3E%3Cquery%3Ehash_id%3A1d03267c6ed6be23%3C/query%3E%3C/delete%3E&commit=true')

#Deleting hash_id:8cfae3c941f08326
requests.get('http://localhost:8983/solr/lucidfind_shard1_replica1/update?stream.body=%3Cdelete%3E%3Cquery%3Ehash_id%3A8cfae3c941f08326%3C/query%3E%3C/delete%3E&commit=true')

####################################################################################################################################

####################################################################################################################################

params = {
  'facet': 'on',
  'facet.field': 'author_facet',
  'facet.limit':  -1
}

results = solr.search('_lw_data_source_s:"mailing-list-lucene-lucene-dev"',**params)

D = results.facets['facet_fields']['author_facet']

# Turning list D into a dict 
D = dict(itertools.izip_longest(*[iter(D)] * 2, fillvalue=""))

# Creating a dict of all those contributors with 1 or greater mails
active_contribs = {key:value for key, value in D.items() if value > 0}

#Create dependent variable (number of mails sent)
y = active_contribs.values()

#############################
# Average Length of Mail (x1)
#############################

# Want to examine if there is a relationship between average length of email and number of emails sent

# to extract average length of email sent by each committer
# we must loop through every author, get the length_l of every email sent, and divide by the total number of emails sent by that person

from __future__ import division

average_length_l = [] 

for i in range(len(active_contribs.keys())): #looping through the list of (5,281) authors 
    
    """as there are some non-english characters in 
    certain contributors names we must change the 
    input string type to utf-8 in such instances"""
    if isinstance(active_contribs.keys()[i], str):
        active_contribs.keys()[i] = unicode(active_contribs.keys()[i], "utf-8")
    s = '_lw_data_source_s:mailing-list-lucene-lucene-dev AND author:"{author}"'
    solr_results = solr.search(s.format(author=active_contribs.keys()[i]),rows=active_contribs.values()[i])
    author_docs = solr_results.docs
    
    a = []
    
    for j in range(len(author_docs)): #looping through the docs of each author
         
        length = author_docs[j]['length_l']
        a.append(length)
        
    av_length = sum(a) / len(solr_results.docs)
    
    average_length_l.append(av_length)

x1 = average_length_l

#################################
# IsBot (x2) - indicator variable
#################################

# Are the mails of that author generated by a bot or not
isbot = [] 

for i in range(len(active_contribs.keys())):
    
    if isinstance(active_contribs.keys()[i], str):
        active_contribs.keys()[i] = unicode(active_contribs.keys()[i], "utf-8")
    s = '_lw_data_source_s:mailing-list-lucene-lucene-dev AND author:"{author}"'
    solr_results = solr.search(s.format(author=active_contribs.keys()[i]),rows=active_contribs.values()[i])
    author_docs = solr_results.docs
    if author_docs[0]['isBot'] == True:
        isbot.append(1)
    elif author_docs[0]['isBot'] == False:
        isbot.append(0)
    
x2 = isbot        

#######################################################
# Number of mails which contain a question in body (x3)
#######################################################

# To get a basic sentiment of whther a contributor is generally asking or answering questions
# We look at the total number of mails containing at least one question for each author

num_questions = [] 

for i in range(len(active_contribs.keys())):
    
    if isinstance(active_contribs.keys()[i], str):
        active_contribs.keys()[i] = unicode(active_contribs.keys()[i], "utf-8")
    s = '_lw_data_source_s:mailing-list-lucene-lucene-dev AND author:"{author}"'
    solr_results = solr.search(s.format(author=active_contribs.keys()[i]),rows=active_contribs.values()[i])
    author_docs = solr_results.docs
    
    questions = []
    
    for j in range(len(solr_results.docs)):
         
        body = author_docs[j]['body']
        torf = '?' in body
        if torf == True: 
            questions.append(1)  
              
    num_questions.append(sum(questions))        

x3 = num_questions
    
##########################################################
# Number of mails which contain a question in subject (x4)
##########################################################            

# A further gauge of whether an author is asking or answering questions
# Number of mails which contain a subject which is a question

num_subject_qs = [] 

for i in range(len(active_contribs.keys())):
    
    if isinstance(active_contribs.keys()[i], str):
        active_contribs.keys()[i] = unicode(active_contribs.keys()[i], "utf-8")
    s = '_lw_data_source_s:mailing-list-lucene-lucene-dev AND author:"{author}"'
    solr_results = solr.search(s.format(author=active_contribs.keys()[i]),rows=active_contribs.values()[i])
    author_docs = solr_results.docs
    
    subject_questions = []
    
    for j in range(len(solr_results.docs)):
         
        body = author_docs[j]['subject']
        torf = '?' in body
        if torf == True: 
            subject_questions.append(1)  
              
    num_subject_qs.append(sum(subject_questions))        

x4 = num_subject_qs
len(x4)             
    
#########################################################################################################################################################

# MORE VARIABLES TO BE ADDED 

#########################################################################################################################################################                                                     

# Dataframe of dependent and independent variables

d = {'y' : pd.Series(y,index = active_contribs.keys()),
'x1':pd.Series(x1,index = active_contribs.keys()),
'x2':pd.Series(x2,index = active_contribs.keys()),
'x3':pd.Series(x3,index = active_contribs.keys()),
'x4':pd.Series(x4,index = active_contribs.keys())}
df = pd.DataFrame(d)



