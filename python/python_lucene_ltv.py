    # -*- coding: utf-8 -*-
################################################################
#### Open Source Community Contributor Lifetime Value Model ###
################################################################

# Specific case: Lucene mailing list (mailing-list-lucene-lucene-dev datasource in the lucidfind collection)

import pysolr
import requests
import itertools
from __future__ import division
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import scipy
import sys
import matplotlib.pyplot as plt
reload(sys)
sys.setdefaultencoding('utf8')

solr = pysolr.Solr('http://localhost:8983/solr/lucidfind_shard1_replica1/',timeout=10)

# Prior to pulling the lucene data from Solr we have to do a bit of data cleaning,.
# Certain fields that we wish to loop through are non existent in some documents.

# There are 4 docs without a 'body' field - as such providing significantly less information for us to work with
# As these docs represent a very small proportion ofthe total docs we will disgard them

###

 # Delete Documents From Solr Index By Query
 
#### 
     
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
# INTEND TO DO THIS PROCESS BY AUTOMATED MEANS AS OPPOSED TO MANUALLY SEARCHING, FINDING THE hash_id AND SENDING REQUESTS
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

#########################################################################################################################################################

#############################
# Average Length of Mail (x1)
#############################

# Want to examine if there is a relationship between average length of email and number of emails sent

# to extract average length of email sent by each committer
# we must loop through every author, get the length_l of every email sent, and divide by the total number of emails sent by that person

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

#########################################################################################################################################################

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
   
#########################################################################################################################################################

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

#########################################################################################################################################################
        
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
         
        subject = author_docs[j]['subject']
        torf = '?' in subject
        if torf == True: 
            subject_questions.append(1)  
              
    num_subject_qs.append(sum(subject_questions))        

x4 = num_subject_qs
    
#########################################################################################################################################################

# Generally, a contributor who asks questions will contain some kind of variation of thank you in their mail
# Count how many emails from an author contains some kind of variation of thank you

###########################################################################
# Number of mails which contain some form of "thanks" in body field (x5)
###########################################################################  

num_thanks = [] 

for i in range(len(active_contribs.keys())):
    
    if isinstance(active_contribs.keys()[i], str):
        active_contribs.keys()[i] = unicode(active_contribs.keys()[i], "utf-8")
    s = '_lw_data_source_s:mailing-list-lucene-lucene-dev AND author:"{author}"'
    solr_results = solr.search(s.format(author=active_contribs.keys()[i]),rows=active_contribs.values()[i])
    author_docs = solr_results.docs
    
    var_1 = []
    var_2 = []
    var_3 = []
  
    for j in range(len(solr_results.docs)):
         
        body = author_docs[j]['body']
        torf = 'thanks' in body.lower()
        if torf == True: 
            var_1.append(1)
            
        torf2 = 'thank' in body.lower()
        if torf2 == True: 
            var_2.append(1)

        torf3 = 'thx' in body.lower()
        if torf3 == True: 
            var_3.append(1)
            
        tot = var_1 + var_2 + var_3            
              
    num_thanks.append(sum(tot))        

x5 = num_thanks


#########################################################################################################################################################

#FIXED

# the mention of "fixed" in either the subject or body fields

##################################################################
# Number of mails which contain "fixed" in body/subject field (x6)
##################################################################

num_fixed = [] 

for i in range(len(active_contribs.keys())):
    
    if isinstance(active_contribs.keys()[i], str):
        active_contribs.keys()[i] = unicode(active_contribs.keys()[i], "utf-8")
    s = '_lw_data_source_s:mailing-list-lucene-lucene-dev AND author:"{author}"'
    solr_results = solr.search(s.format(author=active_contribs.keys()[i]),rows=active_contribs.values()[i])
    author_docs = solr_results.docs
    
    body_fixed = []
    subject_fixed = []
  
    for j in range(len(solr_results.docs)):
         
        body = author_docs[j]['body']
        torf = 'fixed' in body.lower()
        if torf == True: 
            body_fixed.append(1)
        
        subject = author_docs[j]['subject']
        torf2 = 'fixed' in subject.lower()
        if torf2 == True: 
            subject_fixed.append(1)

        tot = subject_fixed + body_fixed           
              
    num_fixed.append(sum(tot))        

x6 = num_fixed

#########################################################################################################################################################

#COMMIT

# the mention of commit in either the subject or body fields

##########################################################################################################
# Number of mails which contain variation of 'commit'/'committer'/'comitted' in body or subject field (x7)
##########################################################################################################

num_commit= [] 

for i in range(len(active_contribs.keys())):
    
    if isinstance(active_contribs.keys()[i], str):
        active_contribs.keys()[i] = unicode(active_contribs.keys()[i], "utf-8")
    s = '_lw_data_source_s:mailing-list-lucene-lucene-dev AND author:"{author}"'
    solr_results = solr.search(s.format(author=active_contribs.keys()[i]),rows=active_contribs.values()[i])
    author_docs = solr_results.docs
    
    body_commit = []
    body_committer = []
    body_committed = []
    subject_commit = []
    subject_committed = []
    subject_committer = []
  
    for j in range(len(solr_results.docs)):
         
        body = author_docs[j]['body']
        torf = 'commit' in body.lower()
        if torf == True: 
            body_commit.append(1)
            
        torf2 = 'committer' in body.lower()
        if torf2 == True: 
            body_committer.append(1)
            
        torf3 = 'committed' in body.lower()
        if torf3 == True: 
            body_committed.append(1)
        
        subject = author_docs[j]['subject']
        torf4 = 'commit' in subject.lower()
        if torf4 == True: 
            subject_commit.append(1)
            
        torf5 = 'committer' in subject.lower()
        if torf5 == True: 
            subject_committer.append(1)
            
        torf6 = 'committed' in subject.lower()
        if torf6 == True: 
            subject_committed.append(1)

        tot =  body_commit+body_committer+body_committed+subject_commit+subject_committed+subject_committer         
              
    num_commit.append(sum(tot))        

x7 = num_commit



# MORE VARIABLES TO BE ADDED 

#########################################################################################################################################################                                                     

# Dataframe of dependent and independent variables 

# Dataframe containing all variables
d = {'y' : pd.Series(y,index = active_contribs.keys()),
'x1':pd.Series(x1,index = active_contribs.keys()),
'x2':pd.Series(x2,index = active_contribs.keys()),
'x3':pd.Series(x3,index = active_contribs.keys()),
'x4':pd.Series(x4,index = active_contribs.keys()),
'x5':pd.Series(x5,index = active_contribs.keys()),
'x6':pd.Series(x6,index = active_contribs.keys()),
'x7':pd.Series(x7,index = active_contribs.keys())}
df = pd.DataFrame(d)

df.corr()
# Variables x1 and x2 displaying v little correlation with y

# Sorting Dataframe by index of names ascending
# df3 = df.sort_index(axis=0, ascending=True)

# Dataframe containing x3,x4,x5,x6,x7
d2 = {'y' : pd.Series(y,index = active_contribs.keys()),
'x3':pd.Series(x3,index = active_contribs.keys()),
'x4':pd.Series(x4,index = active_contribs.keys()),
'x5':pd.Series(x5,index = active_contribs.keys()),
'x6':pd.Series(x6,index = active_contribs.keys()),
'x7':pd.Series(x7,index = active_contribs.keys())}
df2 = pd.DataFrame(d2)

df2.corr()
# High degree of multicollinearity present - becomes particularly problematic when we come to look at regression methods
# Unable to satisfactorily separate out the individual effects that highly correlated variables have on the dependent variable. 
# Two highly correlated variables will generally increase or decrease together 
# resultantly difficult to correctly deduce how each of these variables individually affect the response variable.

#########################################################################################################################################################                                                     

# Training and test set - variables x3,x4,x5,x6,x7

X = {'x3':pd.Series(x3,index = active_contribs.keys()),
'x4':pd.Series(x4,index = active_contribs.keys()),
'x5':pd.Series(x5,index = active_contribs.keys()),
'x6':pd.Series(x6,index = active_contribs.keys()),
'x7':pd.Series(x7,index = active_contribs.keys())}
X = pd.DataFrame(X)

y = {'y':pd.Series(y,index = active_contribs.keys())}
y = pd.DataFrame(y)

# divide the data set up into a training and test set 
# 75% Training / 25% Test
# generate a random permuation of the range 0 to 5281 and then pick off the first 3961 for the training set

import numpy.random as npr
npr.seed(123)
train_select = npr.permutation(range(len(active_contribs.keys())))
X_train = X.ix[train_select[:int(round(len(active_contribs.keys())*0.75))],:].reset_index(drop=True)
X_test = X.ix[train_select[int(round(len(active_contribs.keys())*0.75)):],:].reset_index(drop=True)
y_train = y.ix[train_select[:int(round(len(active_contribs.keys())*0.75))]].reset_index().y
y_test = y.ix[train_select[int(round(len(active_contribs.keys())*0.75)):]].reset_index().y      

#########################################################################################################################################################

                                                     
#########################################################################################################################################################                                                     

# Training and test set - all variables

X_full = {'x1':pd.Series(x1,index = active_contribs.keys()),
'x2':pd.Series(x2,index = active_contribs.keys()),
'x3':pd.Series(x3,index = active_contribs.keys()),
'x4':pd.Series(x4,index = active_contribs.keys()),
'x5':pd.Series(x5,index = active_contribs.keys()),
'x6':pd.Series(x6,index = active_contribs.keys()),
'x7':pd.Series(x7,index = active_contribs.keys())}
X_full = pd.DataFrame(X_full)

y = {'y':pd.Series(active_contribs.values(),index = active_contribs.keys())}
y = pd.DataFrame(y)

npr.seed(123)
train_select = npr.permutation(range(len(active_contribs.keys())))
X_full_train = X_full.ix[train_select[:int(round(len(active_contribs.keys())*0.75))],:].reset_index(drop=True)
X_full_test = X_full.ix[train_select[int(round(len(active_contribs.keys())*0.75)):],:].reset_index(drop=True)
y_train = y.ix[train_select[:int(round(len(active_contribs.keys())*0.75))]].reset_index().y
y_test = y.ix[train_select[int(round(len(active_contribs.keys())*0.75)):]].reset_index().y      

#########################################################################################################################################################                                                       

#########################################################################################################################################################

# OLS Regression

import statsmodels.formula.api as smf
mod = smf.ols("y ~ x1 + x2 + x3 + x4 + x5 + x6 + x7", df).fit()
mod.summary()
# The condition number is large, 1.26e+05. 
# Indication that there is indeed strong multicollinearity or other numerical problems.

mod2 = smf.ols("y ~ x3 +x4 +x5 + x6 + x7", df2).fit()
mod2.summary()

######################################################

# Ridge Regression

# tackles the problem of unstable regression coefficients when predictors are highly correlated

from sklearn.linear_model import Ridge

ridge = Ridge(fit_intercept=False, normalize=True)
ridge.fit(X_train, y_train) 
ridge.score(X_train, y_train, sample_weight=None)
ridge.coef_ 
ridge_test_pred = ridge.predict(X_test)
# Plot
fig = plt.figure()
plt.plot(y_test,ridge_test_pred,'kx')
plt.plot(plt.xlim(), plt.ylim(), ls="--")
# Compute mean squared error
MSE_ridge = mean_squared_error(y_test,ridge_test_pred)
# 1984.4930

#RidgeCV implements ridge regression with built-in cross-validation of the alpha parameter. 
#The object works in the same way as GridSearchCV except that it defaults to Generalized Cross-Validation (GCV), an efficient form of leave-one-out cross-validation:

from sklearn.linear_model import RidgeCV
ridgecv = linear_model.RidgeCV(cv=10,normalize=True)
ridgecv.fit(X_train, y_train)
ridgecv.coef_ 
# Predict
ridgecv_test_pred = ridgecv.predict(X_test)
# Plot
fig = plt.figure()
plt.plot(y_test,ridgecv_test_pred,'kx')
plt.plot(plt.xlim(), plt.ylim(), ls="--")
# Looks better than previous

# Compute mean squared error
MSE_ridgecv = mean_squared_error(y_test,ridgecv_test_pred)
# 1932.9572

# Using all variables
ridgecv_full = linear_model.RidgeCV(cv=10)
ridgecv_full.fit(X_full_train, y_train)
ridgecv_full.coef_ 
# Predict
ridgecv_full_test_pred = ridgecv_full.predict(X_full_test)
# Plot
fig = plt.figure()
plt.plot(y_test,ridgecv_full_test_pred,'kx')
plt.plot(plt.xlim(), plt.ylim(), ls="--")
# Compute mean squared error
MSE_ridgecv_full = mean_squared_error(y_test,ridgecv_full_test_pred)
# 1936.8783






ridge = linear_model.Ridge(normalize=True)
alphas = np.logspace(2,10, n_alphas)

scores = list()
scores_std = list()

for alpha in alphas:
    Ridge.alpha = alpha
    this_scores = cross_validation.cross_val_score(ridge, X_train, y_train, n_jobs=1)
    scores.append(np.mean(this_scores))
    scores_std.append(np.std(this_scores))

plt.semilogx(alphas, scores)
# Error lines showing +/- std. errors of the scores
plt.semilogx(alphas, np.array(scores) + np.array(scores_std) / np.sqrt(len(X)),'b--')
plt.semilogx(alphas, np.array(scores) - np.array(scores_std) / np.sqrt(len(X)),'b--')
plt.ylabel('CV score')
plt.xlabel('alpha')
plt.axhline(np.max(scores), linestyle='--', color='.5')
optimal_alpha_ridge = alphas[scores.index(np.max(scores))]
plt.axvline(optimal_alpha_ridge, linestyle='--', color='.5')


###############################################################################
# Plot Ridge coefficients as a function of the regularization

# Compute paths

n_alphas = 200
alphas = np.logspace(2, 10, n_alphas)
ridge = linear_model.Ridge(fit_intercept=True)

coefs = []
for a in alphas:
    ridge.set_params(alpha=a)
    ridge.fit(X_full_train, y_train)
    coefs.append(ridge.coef_)

# Display results

ax = plt.gca()
ax.set_color_cycle(['b', 'r', 'g', 'c', 'k', 'y', 'm'])

ax.plot(alphas, coefs)
ax.set_xscale('log')
ax.set_xlim(ax.get_xlim()[::-1])  # reverse axis
plt.xlabel('alpha')
plt.ylabel('weights')
plt.title('Ridge coefficients as a function of the regularization')
plt.axis('tight')
plt.show()
             
##############################
#Lasso            

# Selecting optimal alpha 
from sklearn import cross_validation, linear_model
lasso = linear_model.Lasso()
alphas = np.logspace(-4, 6, n_alphas)

scores = list()
scores_std = list()

for alpha in alphas:
    lasso.alpha = alpha
    this_scores = cross_validation.cross_val_score(lasso, X_train, y_train, n_jobs=1)
    scores.append(np.mean(this_scores))
    scores_std.append(np.std(this_scores))

plt.semilogx(alphas, scores)
# Error lines showing +/- std. errors of the scores
plt.semilogx(alphas, np.array(scores) + np.array(scores_std) / np.sqrt(len(X)),'b--')
plt.semilogx(alphas, np.array(scores) - np.array(scores_std) / np.sqrt(len(X)),'b--')
plt.ylabel('CV score')
plt.xlabel('alpha')
plt.axhline(np.max(scores), linestyle='--', color='.5')
optimal_alpha_lasso = alphas[scores.index(np.max(scores))]
plt.axvline(optimal_alpha_lasso, linestyle='--', color='.5')

# Using LassoCV func

from sklearn.linear_model import LassoCV
lasso_cv = linear_model.LassoCV(cv=10)
lasso_cv.fit(X_train, y_train)
lasso_cv.coef_ # Has set some of them to zero
# Predict
lasso_cv_test_pred = lasso_cv.predict(X_test)
# Plot
fig = plt.figure()
plt.plot(y_test,lasso_cv_test_pred,'kx')
plt.plot(plt.xlim(), plt.ylim(), ls="--")
# Compute mean squared error
MSE_lasso_cv = mean_squared_error(y_test,lasso_cv.predict(X_test))
# 3624.3137

# Using all variables - no change
lasso_cv_full = linear_model.LassoCV(cv=10)
lasso_cv_full.fit(X_full_train, y_train)
lasso_cv_full.coef_ # Has set some of them to zero
# Predict
lasso_cv_full_test_pred = lasso_cv_full.predict(X_full_test)
# Plot
fig = plt.figure()
plt.plot(y_test,lasso_cv_full_test_pred,'kx')
plt.plot(plt.xlim(), plt.ylim(), ls="--")
# Compute mean squared error
MSE_lasso_cv_full = mean_squared_error(y_test,lasso_cv_full_test_pred)
# 3624.3137

############################################################
# Support Vector Regression

from sklearn import svm
svr = svm.SVR()
svr.fit(X_train, y_train) 
# Predict
svr_test_pred = svr.predict(X_test)
# Plot
fig = plt.figure()
plt.plot(y_test,svr_test_pred,'kx')
plt.plot(plt.xlim(), plt.ylim(), ls="--")
# Performance 
MSE_svr = mean_squared_error(y_test,svr.predict(X_test)) 
# 114834.4193

# Using all variables
svr_full = svm.SVR()
svr_full.fit(X_full_train, y_train) 
# Predict
svr_full_test_pred = svr_full.predict(X_full_test)
# Plot
fig = plt.figure()
plt.plot(y_test,svr_full_test_pred,'kx')
plt.plot(plt.xlim(), plt.ylim(), ls="--")
# Performance 
MSE_svr_full = mean_squared_error(y_test,svr_full_test_pred) 
# 115866.6992668

############################################################
# Random Forest Regression

from sklearn.ensemble import RandomForestRegressor
rf = RandomForestRegressor()
rf.fit(X_train, y_train) 
# Predict
rf_test_pred = rf.predict(X_test)
# Plot
fig = plt.figure()
plt.plot(y_test,rf_test_pred,'kx')
plt.plot(plt.xlim(), plt.ylim(), ls="--")
# Performance 
MSE_rf = mean_squared_error(y_test,rf.predict(X_test)) 
# 9284.1081

rf_full = RandomForestRegressor()
rf_full.fit(X_full_train, y_train) 
# Predict
rf_full_test_pred = rf_full.predict(X_full_test)
# Plot
fig = plt.figure()
plt.plot(y_test,rf_full_test_pred,'kx')
plt.plot(plt.xlim(), plt.ylim(), ls="--")
# Performance 
MSE_rf_full = mean_squared_error(y_test,rf_full_test_pred) 
# 10547.9287

############################################################
# Bagging

from sklearn.ensemble import BaggingRegressor
bagg = BaggingRegressor()
bagg.fit(X_train, y_train) 
# Predict
bagg_test_pred = bagg.predict(X_test)
# Plot
fig = plt.figure()
plt.plot(y_test,bagg_test_pred,'kx')
plt.plot(plt.xlim(), plt.ylim(), ls="--")
# Performance 
MSE_bagg = mean_squared_error(y_test,bagg.predict(X_test)) 
# 7965.2756

bagg_full = BaggingRegressor()
bagg_full.fit(X_full_train, y_train) 
# Predict
bagg_full_test_pred = bagg_full.predict(X_full_test)
# Plot
fig = plt.figure()
plt.plot(y_test,bagg_full_test_pred,'kx')
plt.plot(plt.xlim(), plt.ylim(), ls="--")
# Performance 
MSE_bagg_full = mean_squared_error(y_test,bagg_full_test_pred)
# 8853.3803 

############################################################
# Gradient Boosting Regressor

from sklearn.ensemble import GradientBoostingRegressor
gbr = GradientBoostingRegressor()
gbr.fit(X_train, y_train) 
# Predict
gbr_test_pred = gbr.predict(X_test)
# Plot
fig = plt.figure()
plt.plot(y_test,gbr_test_pred,'kx')
plt.plot(plt.xlim(), plt.ylim(), ls="--")
# Performance 
MSE_gbr = mean_squared_error(y_test,gbr_test_pred) 
# 7697.7107


# Fit regression model
params = {'n_estimators': 500, 'max_depth': 4, 'min_samples_split': 1,
          'learning_rate': 0.01, 'loss': 'ls'}
gbr = GradientBoostingRegressor(**params)

gbr.fit(X_train, y_train)
MSE_gbr = mean_squared_error(y_test,gbr_test_pred) 
print("MSE: %.4f" % MSE_gbr)

# Plot training deviance

# compute test set deviance
test_score = np.zeros((params['n_estimators'],), dtype=np.float64)

for i, y_pred in enumerate(gbr.staged_predict(X_test)):
    test_score[i] = gbr.loss_(y_test, y_pred)

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.title('Deviance')
plt.plot(np.arange(params['n_estimators']) + 1, gbr.train_score_, 'b-',
         label='Training Set Deviance')
plt.plot(np.arange(params['n_estimators']) + 1, test_score, 'r-',
         label='Test Set Deviance')
plt.legend(loc='upper right')
plt.xlabel('Boosting Iterations')
plt.ylabel('Deviance')


# Plot feature importance
feature_importance = gbr.feature_importances_
# make importances relative to max importance
feature_importance = 100.0 * (feature_importance / feature_importance.max())
sorted_idx = np.argsort(feature_importance)
pos = np.arange(sorted_idx.shape[0]) + .5
plt.subplot(1, 2, 2)
plt.barh(pos, feature_importance[sorted_idx], align='center')
plt.yticks(pos, X.feature_names[sorted_idx])
plt.xlabel('Relative Importance')
plt.title('Variable Importance')
plt.show()


gbr_full = GradientBoostingRegressor()
gbr_full.fit(X_train, y_train) 
# Predict
gbr_full_test_pred = gbr_full.predict(X_test)
# Plot
fig = plt.figure()
plt.plot(y_test,gbr_full_test_pred,'kx')
plt.plot(plt.xlim(), plt.ylim(), ls="--")
# Performance 
MSE_gbr_full = mean_squared_error(y_test,gbr_full_test_pred) 
# 7774.6173

############################################################

# AdaBoost Regressor
from sklearn.ensemble import AdaBoostRegressor
abr = AdaBoostRegressor()
abr.fit(X_train, y_train) 
# Predict
abr_test_pred = abr.predict(X_test)
# Plot
fig = plt.figure()
plt.plot(y_test,abr_test_pred,'kx')
plt.plot(plt.xlim(), plt.ylim(), ls="--")
# Performance 
MSE_abr = mean_squared_error(y_test,abr_test_pred) 
# 9109.4165

abr_full = AdaBoostRegressor()
abr_full.fit(X_full_train, y_train) 
# Predict
abr_full_test_pred = abr_full.predict(X_full_test)
# Plot
fig = plt.figure()
plt.plot(y_test,abr_full_test_pred,'kx')
plt.plot(plt.xlim(), plt.ylim(), ls="--")
# Performance 
MSE_abr_full = mean_squared_error(y_test,abr_full_test_pred)
# 9293.1306 
