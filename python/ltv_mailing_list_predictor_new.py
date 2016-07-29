# -*- coding: utf-8 -*-
from __future__ import division
import pysolr
import requests
import itertools
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import scipy
import sys
import matplotlib.pyplot as plt
reload(sys)
sys.setdefaultencoding('utf8')

# Specify Solr shard - We want to take our data from the lucidfind collection - lucidfind_shard1_replica1
solr = pysolr.Solr('http://localhost:8983/solr/lucidfind_shard1_replica1/',timeout=10)

#########################################################################################################################################################

# INPUTS TO SPECIFY PRIOR TO RUNNING

# Specify Mailing List of interest
# e.g let's look at the Lucene dev mailing list            
mailing_list = "mailing-list-lucene-lucene-dev"

# We want to see how well the model performs for predicting the number of mails for a specific contributor.
# For example, let's look at 'Grant Ingersoll (JIRA)'
contributor = 'Grant Ingersoll (JIRA)' 

#########################################################################################################################################################

# Using filter query on hash_id's to filter out those docs without body or subject fields

hash_ids_to_remove = []

# Need to find those docs without body field and delete them
missing_body_docs = solr.search('_lw_data_source_s:{ml} AND -body:[* TO *]'.format(ml=mailing_list),rows=100000)

for i in range(len(missing_body_docs.docs)):
    
    hash_id = str(missing_body_docs.docs[i]['hash_id'])
    hash_del1 = hash_id[3:][:-2] #removing square brackets
    hash_ids_to_remove.append(hash_del1)
            
# Need to find those docs without subject field and delete them
missing_subject_docs = solr.search('_lw_data_source_s:{ml} AND -subject:[* TO *]'.format(ml=mailing_list),rows=100000)

for i in range(len(missing_subject_docs.docs)):
    
    hash_id = str(missing_subject_docs.docs[i]['hash_id'])
    hash_del2 = hash_id[3:][:-2] #removing square brackets
    hash_ids_to_remove.append(hash_del2)

hash_ids_to_remove = str(hash_ids_to_remove)[2:][:-2]
for ch in ["', '"]:
   if ch in hash_ids_to_remove:
      hash_ids_to_remove = hash_ids_to_remove.replace(ch," ")


params = {
  'facet': 'on',
  'facet.field': 'author_facet',
  'facet.limit':  -1
}

results = solr.search('_lw_data_source_s:{ml}'.format(ml=mailing_list),**params)

D = results.facets['facet_fields']['author_facet']

# Turning list D into a dict 
D = dict(itertools.izip_longest(*[iter(D)] * 2, fillvalue=""))

# Creating a dict of all those contributors with 1 or greater mails
active_contribs = {key:value for key, value in D.items() if value > 0}

#Create dependent variable (number of mails sent)
y = active_contribs.values()

#########################################################################################################################################################

# VARIABLE GENERATION

#########################################################################################################################################################

average_length_l = [] 
isbot = [] 
num_questions = [] 
num_subject_qs = [] 
num_thanks = [] 
num_fixed = [] 
num_commit= [] 
num_resolved = [] 
num_commented = [] 
num_reopen = []

for i in range(len(active_contribs.keys())): #looping through the list of (7618) authors 
    
    """as there are some non-english characters in 
    certain contributors names we must change the 
    input string type to utf-8 in such instances"""
    
    if isinstance(active_contribs.keys()[i], str):
        active_contribs.keys()[i] = unicode(active_contribs.keys()[i], "utf-8")
        
    if len(hash_ids_to_remove)==0:
            
        s = '_lw_data_source_s:{ml} AND author:"{author}"'
        solr_results = solr.search(s.format(ml=mailing_list,author=active_contribs.keys()[i]),rows=active_contribs.values()[i])
        author_docs = solr_results.docs

    else:
            
        s = '_lw_data_source_s:{ml} AND author:"{author}"'
        solr_results = solr.search(s.format(ml=mailing_list,author=active_contribs.keys()[i]),rows=active_contribs.values()[i],fq='-hash_id:({HASH})'.format(HASH=hash_ids_to_remove))
        author_docs = solr_results.docs    
    
    a = []
    questions = []
    subject_questions = []
    var_1 = []
    var_2 = []
    var_3 = []
    body_fixed = []
    subject_fixed = []
    body_commit = []
    body_committed = []
    subject_commit = []
    subject_committed = []
    body_resolved = []
    body_commented = []
    body_reopen1 = []
    body_reopen2 = []
    body_reopen3 = []
    body_reopen4 = []

    for j in range(len(author_docs)): #looping through the docs of each author
         
        length = author_docs[j]['length_l']
        a.append(length)

        body = author_docs[j]['body']
        torf1 = '?' in body
        if torf1 == True: 
            questions.append(1)
        else:
            questions.append(0)

        subject = author_docs[j]['subject']
        torf2 = '?' in subject
        if torf2 == True: 
            subject_questions.append(1)
        else:
            subject_questions.append(0)

        torf3 = 'thanks' in body.lower()
        if torf3 == True: 
            var_1.append(1)
        else:
            var_1.append(0)
                        
        torf4 = 'thank' in body.lower()
        if torf4 == True: 
            var_2.append(1)
        else:
            var_2.append(0)

        torf5 = 'thx' in body.lower()
        if torf5 == True: 
            var_3.append(1)
        else:
            var_3.append(0)
                        
        tot1 = var_1 + var_2 + var_3                    

        body = author_docs[j]['body']
        torf6 = 'fixed' in body.lower()
        if torf6 == True: 
            body_fixed.append(1)
        else:
            body_fixed.append(0)
                    
        torf7 = 'fixed' in subject.lower()
        if torf7 == True: 
            subject_fixed.append(1)
        else:
            subject_fixed.append(0)
            
        tot2 = subject_fixed + body_fixed           
 
        torf8 = 'commit' in body.lower()
        if torf8 == True: 
            body_commit.append(1)
        else:
            body_commit.append(0)
                        
        torf9 = 'committed' in body.lower()
        if torf9 == True: 
            body_committed.append(1)
        else:
            body_committed.append(0)
                    
        torf10 = 'commit' in subject.lower()
        if torf10 == True: 
            subject_commit.append(1)
        else:
            subject_commit.append(0)
                        
        torf11 = 'committed' in subject.lower()
        if torf11 == True: 
            subject_committed.append(1)
        else:
            subject_committed.append(0)
            
        tot3 =  body_commit+body_committed+subject_commit+subject_committed 

        torf12 = 'resolved' in body.lower()
        if torf12 == True: 
            body_resolved.append(1)
        else:
            body_resolved.append(0)
            
        torf13 = 'commented' in body.lower()
        if torf13 == True: 
            body_commented.append(1)
        else:
            body_commented.append(0)
            
        torf14 = 'reopened' in body.lower()
        if torf14 == True: 
            body_reopen1.append(1)
        else:
            body_reopen1.append(0)
                        
        torf15 = 're-opened' in body.lower()
        if torf15 == True: 
            body_reopen2.append(1)
        else:
            body_reopen2.append(0)
                        
        torf16 = 'reopening' in body.lower()
        if torf16 == True: 
            body_reopen3.append(1)
        else:
            body_reopen1.append(0)
                    
        torf17 = 're-opening' in subject.lower()
        if torf17 == True: 
            body_reopen4.append(1)
        else:
            body_reopen4.append(0)
            
        tot4 = body_reopen1+body_reopen2+body_reopen3+body_reopen4                          

# x1 - Average length of Mail    
    av_length = sum(a) / len(solr_results.docs)    
    average_length_l.append(av_length)

# x2 - IsBot
    if author_docs[0]['isBot'] == True:
        isbot.append(1)
    elif author_docs[0]['isBot'] == False:
        isbot.append(0)
    
# x3 - Number of mails containing a question mark in the body field
    num_questions.append(sum(questions))

# x4 - Number of mails containing a question mark in the subject field
    num_subject_qs.append(sum(subject_questions))        
    
# x5 - Number of mails with variation of 'thanks' in body field
    num_thanks.append(sum(tot1))        
        
# x6 - Number of mails with 'fixed' in the body or subject field
    num_fixed.append(sum(tot2))        

# x7 - Number of mails with 'commit' or 'committed' in the body or subject fields
    num_commit.append(sum(tot3))

# x8 - Number of mails with 'resolved' in the body field
    num_resolved.append(sum(body_resolved))

# x9 - Number of mails with 'commented' in the body field
    num_commented.append(sum(body_commented))

# x10 - Number of mails with 'reopened'/'re-opened'/'reopening'/'re-opening' in the body field 
    num_reopen.append(sum(tot4))         

x1 = average_length_l
x2 = isbot 
x3 = num_questions
x4 = num_subject_qs    
x5 = num_thanks
x6 = num_fixed
x7 = num_commit
x8 = num_resolved
x9 = num_commented         
x10 = num_reopen

#########################################################################################################################################################  

# Dataframe of dependent and independent variables 

# Dataframe containing all variables
#d = {'y' : pd.Series(y,index = active_contribs.keys()),
#'x1':pd.Series(x1,index = active_contribs.keys()),
#'x2':pd.Series(x2,index = active_contribs.keys()),
#'x3':pd.Series(x3,index = active_contribs.keys()),
#'x4':pd.Series(x4,index = active_contribs.keys()),
#'x5':pd.Series(x5,index = active_contribs.keys()),
#'x6':pd.Series(x6,index = active_contribs.keys()),
#'x7':pd.Series(x7,index = active_contribs.keys()),
#'x8':pd.Series(x8,index = active_contribs.keys()),
#'x9':pd.Series(x9,index = active_contribs.keys()),
#'x10':pd.Series(x10,index = active_contribs.keys())}
#df = pd.DataFrame(d)

#df.corr()
# Variables x1 and x2 displaying v little correlation with y
# Examine models without including them in it

# High degree of multicollinearity present - becomes particularly problematic when we come to look at regression methods
# Unable to satisfactorily separate out the individual effects that highly correlated variables have on the dependent variable. 
# Two highly correlated variables will generally increase or decrease together 
# resultantly difficult to correctly deduce how each of these variables individually affect the response variable.

#########################################################################################################################################################                                                     

X_full = {'x1':pd.Series(x1,index = active_contribs.keys()),
'x2':pd.Series(x2,index = active_contribs.keys()),
'x3':pd.Series(x3,index = active_contribs.keys()),
'x4':pd.Series(x4,index = active_contribs.keys()),
'x5':pd.Series(x5,index = active_contribs.keys()),
'x6':pd.Series(x6,index = active_contribs.keys()),
'x7':pd.Series(x7,index = active_contribs.keys()),
'x8':pd.Series(x8,index = active_contribs.keys()),
'x9':pd.Series(x9,index = active_contribs.keys()),
'x10':pd.Series(x10,index = active_contribs.keys())}
X_full = pd.DataFrame(X_full)

# divide the data set up into a training and test set 
# 75% Training / 25% Test
# generate a random permuation of the range 0 to 5281 and then pick off the first 3961 for the training set

import numpy.random as npr
npr.seed(123)
train_select = npr.permutation(range(len(active_contribs.keys())))

# Training and test set - all variables

X_full_train = X_full.ix[train_select[:int(round(len(active_contribs.keys())*0.75))],:].reset_index(drop=True)
X_full_test = X_full.ix[train_select[int(round(len(active_contribs.keys())*0.75)):],:].reset_index(drop=True)

#########################################################################################################################################################

# Training and test set - variables x3,x4,x5,x6,x8,x9

X = {'x3':pd.Series(x3,index = active_contribs.keys()),
'x4':pd.Series(x4,index = active_contribs.keys()),
'x5':pd.Series(x5,index = active_contribs.keys()),
'x6':pd.Series(x6,index = active_contribs.keys()),
'x8':pd.Series(x8,index = active_contribs.keys()),
'x9':pd.Series(x9,index = active_contribs.keys())}
X = pd.DataFrame(X)

y = pd.DataFrame({'y':pd.Series(active_contribs.values(),index = active_contribs.keys())})

X_train = X.ix[train_select[:int(round(len(active_contribs.keys())*0.75))],:].reset_index(drop=True)
X_test = X.ix[train_select[int(round(len(active_contribs.keys())*0.75)):],:].reset_index(drop=True)
y_train = y.ix[train_select[:int(round(len(active_contribs.keys())*0.75))]].reset_index().y
y_test = y.ix[train_select[int(round(len(active_contribs.keys())*0.75)):]].reset_index().y      

#########################################################################################################################################################

# MODEL CONSTRUCTION 

#########################################################################################################################################################

# Building the most accurate statistical model
# We shall use Mean Squared Error to make a judgement of the most accurate model - looking for model with lowest MSE

#########################################################################################################################################################

# Ridge Regression

# tackles the problem of unstable regression coefficients when predictors are highly correlated

# Ridge regression performs particularly well when there is a subset of true coefficients that are small or even zero. It doesn’t do as
# well when all of the true coefficients are moderately large; however, in this case it can still outperform linear regression over a pretty
# narrow range of (small) λ values

from sklearn import linear_model
from sklearn.linear_model import Ridge

# Ridge Regression with intercept
ridge_int = Ridge(fit_intercept=True)
ridge_int.fit(X_train, y_train) 
#Predict
ridge_int_test_pred = ridge_int.predict(X_test)
from sklearn.metrics import mean_squared_error
# Compute mean squared error
MSE_ridge_int = mean_squared_error(y_test,ridge_int_test_pred)
# Compute r^2 - coefficient of determination
ridge_int_r2 = ridge_int.score(X_test, y_test)

# Ridge Regression with intercept / all variables
ridge_int_full = Ridge(fit_intercept=True)
ridge_int_full.fit(X_full_train, y_train) 
ridge_int_full_test_pred = ridge_int_full.predict(X_full_test)
from sklearn.metrics import mean_squared_error
MSE_ridge_int_full = mean_squared_error(y_test,ridge_int_full_test_pred)
ridge_int_full_r2 = ridge_int_full.score(X_full_test, y_test)

# Ridge Regression with no intercept
ridge_noint = Ridge(fit_intercept=False, normalize=True)
ridge_noint.fit(X_train, y_train) 
ridge_noint_test_pred = ridge_noint.predict(X_test)
MSE_ridge_noint = mean_squared_error(y_test,ridge_noint_test_pred)
ridge_noint_r2 = ridge_noint.score(X_test, y_test)

# Ridge Regression with no intercept
ridge_noint_full = Ridge(fit_intercept=False)
ridge_noint_full.fit(X_full_train, y_train)
ridge_noint_full_test_pred = ridge_noint_full.predict(X_full_test)
MSE_ridge_noint_full = mean_squared_error(y_test,ridge_noint_full_test_pred)
ridge_noint_full_r2 = ridge_noint_full.score(X_full_test, y_test)

# RidgeCV implements ridge regression with built-in cross-validation of the alpha parameter. 
# The object works in the same way as GridSearchCV except that it defaults to Generalized Cross-Validation (GCV), an efficient form of leave-one-out cross-validation.
# We utilise 10-fold Cross-validation

from sklearn.linear_model import RidgeCV

# Ridge Regression with intercept - using 10-fold cross-validation to get optimal alpha parameter
ridgecv_int = linear_model.RidgeCV(cv=10,normalize=True,fit_intercept=True)
ridgecv_int.fit(X_train, y_train)
ridgecv_int_test_pred = ridgecv_int.predict(X_test)
MSE_ridgecv_int = mean_squared_error(y_test,ridgecv_int_test_pred)
ridgecv_int_r2 = ridgecv_int.score(X_test, y_test)

# Ridge Regression with intercept / all variables - using 10-fold cross-validation to get optimal alpha parameter
ridgecv_int_full = linear_model.RidgeCV(cv=10,normalize=True,fit_intercept=True)
ridgecv_int_full.fit(X_full_train, y_train)
ridgecv_int_full_test_pred = ridgecv_int_full.predict(X_full_test)
MSE_ridgecv_int_full = mean_squared_error(y_test,ridgecv_int_full_test_pred)
ridgecv_int_full_r2 = ridgecv_int_full.score(X_full_test, y_test)

# Ridge Regression without intercept - using 10-fold cross-validation to get optimal alpha parameter
ridgecv_noint = linear_model.RidgeCV(cv=10,normalize=True,fit_intercept=False)
ridgecv_noint.fit(X_train, y_train)
ridgecv_noint_test_pred = ridgecv_noint.predict(X_test)
MSE_ridgecv_noint = mean_squared_error(y_test,ridgecv_noint_test_pred)
ridgecv_noint_r2 = ridgecv_noint.score(X_test, y_test)

# Ridge Regression without intercept - using 10-fold cross-validation to get optimal alpha parameter
ridgecv_noint_full = linear_model.RidgeCV(cv=10,normalize=True,fit_intercept=False)
ridgecv_noint_full.fit(X_full_train, y_train)
ridgecv_noint_full_test_pred = ridgecv_noint_full.predict(X_full_test)
MSE_ridgecv_noint_full = mean_squared_error(y_test,ridgecv_noint_full_test_pred)
ridgecv_noint_full_r2 = ridgecv_noint_full.score(X_full_test, y_test)

######################################################################################################################

# Lasso

# Lasso - with intercept
from sklearn.linear_model import Lasso
lasso = linear_model.Lasso(fit_intercept=True)
lasso.fit(X_train, y_train)
# Predict
lasso_test_pred = lasso.predict(X_test)
# Compute mean squared error
MSE_lasso = mean_squared_error(y_test,lasso.predict(X_test))
# Compute r^2 - coefficient of determination
lasso_r2 = lasso.score(X_test, y_test)

# Lasso - with intercept / all variables
lasso_full = linear_model.Lasso(fit_intercept=True)
lasso_full.fit(X_full_train, y_train)
lasso_full_test_pred = lasso_full.predict(X_full_test)
MSE_lasso_full = mean_squared_error(y_test,lasso_full_test_pred)
lasso_full_r2 = lasso_full.score(X_full_test, y_test)

# Lasso - without intercept
lasso_noint = linear_model.Lasso(fit_intercept=False)
lasso_noint.fit(X_train, y_train)
lasso_noint_test_pred = lasso_noint.predict(X_test)
MSE_lasso_noint = mean_squared_error(y_test,lasso_noint.predict(X_test))
lasso_noint_r2 = lasso_noint.score(X_test, y_test)

# Lasso - without intercept / all variables
lasso_noint_full = linear_model.Lasso(fit_intercept=False)
lasso_noint_full.fit(X_full_train, y_train)
lasso_noint_full_test_pred = lasso_noint_full.predict(X_full_test)
MSE_lasso_noint_full = mean_squared_error(y_test,lasso_noint_full_test_pred)
lasso_noint_full_r2 = lasso_noint_full.score(X_full_test, y_test)

# Using LassoCV function - with intercept
from sklearn.linear_model import LassoCV
lasso_cv = linear_model.LassoCV(cv=10,fit_intercept=True)
lasso_cv.fit(X_train, y_train)
lasso_cv_test_pred = lasso_cv.predict(X_test)
MSE_lasso_cv = mean_squared_error(y_test,lasso_cv.predict(X_test))
lasso_cv_r2 = lasso_cv.score(X_test, y_test)

# LassoCV function - with intercept / all variables
lasso_cv_full = linear_model.LassoCV(cv=10,fit_intercept=True)
lasso_cv_full.fit(X_full_train, y_train)
lasso_cv_full_test_pred = lasso_cv_full.predict(X_full_test)
MSE_lasso_cv_full = mean_squared_error(y_test,lasso_cv_full_test_pred)
lasso_cv_full_r2 = lasso_cv_full.score(X_full_test, y_test)

# Using LassoCV function - without intercept
lasso_cv_noint = linear_model.LassoCV(cv=10,fit_intercept=False)
lasso_cv_noint.fit(X_train, y_train)
lasso_cv_noint_test_pred = lasso_cv_noint.predict(X_test)
MSE_lasso_cv_noint = mean_squared_error(y_test,lasso_cv_noint.predict(X_test))
lasso_cv_noint_r2 = lasso_cv_noint.score(X_test, y_test)

# LassoCV function - with no intercept / all variables
lasso_cv_noint_full = linear_model.LassoCV(cv=10,fit_intercept=False)
lasso_cv_noint_full.fit(X_full_train, y_train)
lasso_cv_noint_full_test_pred = lasso_cv_noint_full.predict(X_full_test)
MSE_lasso_cv_noint_full = mean_squared_error(y_test,lasso_cv_noint_full_test_pred)
lasso_cv_noint_full_r2 = lasso_cv_noint_full.score(X_full_test, y_test)

########################################################################################################################

# Elastic Net

from sklearn.linear_model import ElasticNet

enet = ElasticNet()
enet.fit(X_train, y_train) 
# Predict
enet_pred = enet.predict(X_test)
# Compute mean squared error
MSE_enet = mean_squared_error(y_test,enet.predict(X_test)) 
# Compute r^2 - coefficient of determination
enet_r2 = enet.score(X_test, y_test)  

enet_full = ElasticNet(alpha=1)
enet_full.fit(X_full_train, y_train) 
enet_full_test_pred = enet_full.predict(X_full_test)
MSE_enet_full = mean_squared_error(y_test,enet_full_test_pred)
enet_full_r2 = enet_full.score(X_full_test, y_test) 

from sklearn.linear_model import ElasticNetCV

enet_cv = ElasticNetCV()
enet_cv.fit(X_train, y_train) 
enet_cv_pred = enet_cv.predict(X_test)
MSE_enet_cv = mean_squared_error(y_test,enet_cv.predict(X_test)) 
enet_cv_r2 = enet_cv.score(X_test, y_test)  

enet_cv_full = ElasticNetCV()
enet_cv_full.fit(X_full_train, y_train) 
enet_cv_full_test_pred = enet_cv_full.predict(X_full_test)
MSE_enet_cv_full = mean_squared_error(y_test,enet_cv_full_test_pred)
enet_cv_full_r2 = enet_cv_full.score(X_full_test, y_test) 

#######################################################################################################################

# Support Vector Regression

from sklearn import svm
svr = svm.SVR()
svr.fit(X_train, y_train) 
# Predict
svr_test_pred = svr.predict(X_test)
# Performance 
MSE_svr = mean_squared_error(y_test,svr.predict(X_test))
# Compute r^2 - coefficient of determination
svr_r2 = svr.score(X_test, y_test) 

# Using all variables
svr_full = svm.SVR()
svr_full.fit(X_full_train, y_train) 
svr_full_test_pred = svr_full.predict(X_full_test)
MSE_svr_full = mean_squared_error(y_test,svr_full_test_pred)
svr_full_r2 = svr_full.score(X_full_test, y_test) 

#######################################################################################################################

# Random Forest Regression

from sklearn.ensemble import RandomForestRegressor
rf = RandomForestRegressor()
rf.fit(X_train, y_train) 
# Predict
rf_test_pred = rf.predict(X_test)
# Performance 
MSE_rf = mean_squared_error(y_test,rf.predict(X_test))
# Compute r^2 - coefficient of determination
rf_r2 = rf.score(X_test, y_test)  

rf_full = RandomForestRegressor()
rf_full.fit(X_full_train, y_train) 
rf_full_test_pred = rf_full.predict(X_full_test)
MSE_rf_full = mean_squared_error(y_test,rf_full_test_pred)
rf_full_r2 = rf_full.score(X_full_test, y_test)   

########################################################################################################################

# Bagging

from sklearn.ensemble import BaggingRegressor
bagg = BaggingRegressor()
bagg.fit(X_train, y_train) 
# Predict
bagg_test_pred = bagg.predict(X_test)
# Performance 
MSE_bagg = mean_squared_error(y_test,bagg.predict(X_test))
# Compute r^2 - coefficient of determination
bagg_r2 = bagg.score(X_test, y_test)   

bagg_full = BaggingRegressor()
bagg_full.fit(X_full_train, y_train) 
bagg_full_test_pred = bagg_full.predict(X_full_test)
MSE_bagg_full = mean_squared_error(y_test,bagg_full_test_pred)
bagg_full_r2 = bagg_full.score(X_full_test, y_test)  

########################################################################################################################

# Gradient Boosting Regressor

from sklearn.ensemble import GradientBoostingRegressor
gbr = GradientBoostingRegressor()
gbr.fit(X_train, y_train) 
# Predict
gbr_test_pred = gbr.predict(X_test)
# Performance
MSE_gbr = mean_squared_error(y_test,gbr_test_pred)
# Compute r^2 - coefficient of determination
gbr_r2 = gbr.score(X_test, y_test)  

gbr_full = GradientBoostingRegressor()
gbr_full.fit(X_full_train, y_train) 
gbr_full_test_pred = gbr_full.predict(X_full_test)
MSE_gbr_full = mean_squared_error(y_test,gbr_full_test_pred)
gbr_full_r2 = gbr_full.score(X_full_test, y_test)  

########################################################################################################################

# AdaBoost Regressor

from sklearn.ensemble import AdaBoostRegressor
abr = AdaBoostRegressor()
abr.fit(X_train, y_train) 
abr_test_pred = abr.predict(X_test)
# Performance 
MSE_abr = mean_squared_error(y_test,abr_test_pred)
# Compute r^2 - coefficient of determination
abr_r2 = abr.score(X_test, y_test)  

abr_full = AdaBoostRegressor()
abr_full.fit(X_full_train, y_train) 
abr_full_test_pred = abr_full.predict(X_full_test)
MSE_abr_full = mean_squared_error(y_test,abr_full_test_pred)
abr_full_r2 = abr_full.score(X_full_test, y_test) 
 
########################################################################################################################

# MODEL PERFORMANCE

########################################################################################################################
########################################################################################################################

# Testing the performance of the best model, chosen as the model with the lowest MSE

# One can look at how the chosen model performs on predicting the number of mails sent by a specific contributor.
# Specify the contributor who you wish to predict for.

# Actual number of mails sent by Contributor
y_value = y.ix[contributor][0]   
    
# MSE_ridge_int

if min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_ridge_int:
    y_prediction = ridge_int.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a ridge regression model with an intercept; built with variables x3, x4, x5, x6, x8 and x9. 
    
    Where:
    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the bocdy field
    x6: Number of mails containing "fixed" in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_ridge_int, contrib=contributor, mail_list=mailing_list, r2=ridge_int_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))

# MSE_ridge_int_full

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_ridge_int_full:
    y_prediction = ridge_int_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a ridge regression model with an intercept; built with all 10 variables. 
    
    Where:
    
    x1: Average length of mail sent by contributor
    x2: IsBot - Indicator variable on whether the author is a Bot or not    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x7: Number of mails containing a variation of 'commit'/'committer'/'comitted' in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
    x10: number of mails with 'reopened' in the body field          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_ridge_int_full, contrib=contributor, mail_list=mailing_list, r2=ridge_int_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int1=MSE_ridge_int,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    

# MSE_ridge_noint

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_ridge_noint:
    y_prediction = ridge_noint.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a ridge regression model without an intercept; built with variables x3, x4, x5, x6, x8 and x9. 
    
    Where:
    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the bocdy field
    x6: Number of mails containing "fixed" in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_ridge_noint, contrib=contributor, mail_list=mailing_list, r2=ridge_noint_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    


#MSE_ridge_noint_full

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_ridge_noint_full:
    y_prediction = ridge_noint_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a ridge regression model without an intercept; built with all 10 variables. 
    
    Where:
    
    x1: Average length of mail sent by contributor
    x2: IsBot - Indicator variable on whether the author is a Bot or not    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x7: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
    x10: number of mails with 'reopened' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_ridge_noint_full, contrib=contributor, mail_list=mailing_list, r2=ridge_noint_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    

# MSE_ridgecv_int

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_ridgecv_int:
    y_prediction = ridgecv_int.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a ridge regression model with an intercept, where the optimal alpha value has been selected by 10-fold cross-validation, built with variables x3, x4, x5, x6, x8 and x9.
    
    Where:
        
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field

    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_ridgecv_int, contrib=contributor, mail_list=mailing_list, r2=ridgecv_int_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1], MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    


# MSE_ridgecv_int_full

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_ridgecv_int_full:
    y_prediction = ridgecv_int_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a ridge regression model with an intercept, where the optimal alpha value has been selected by 10-fold cross-validation, built with all the variables.
    
    Where:
      
    x1: Average length of mail sent by contributor
    x2: IsBot - Indicator variable on whether the author is a Bot or not    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x7: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
    x10: number of mails with 'reopened' in the body field
    
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_ridgecv_int_full, contrib=contributor, mail_list=mailing_list, r2=ridgecv_int_full, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1], MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    

#MSE_ridgecv_noint

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_ridgecv_noint:
    y_prediction = ridgecv_noint.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a ridge regression model without an intercept, where the optimal alpha value has been selected by 10-fold cross-validation, built with variables x3, x4, x5, x6, x8 and x9.
    
    Where:
      
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
    
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_ridgecv_noint, contrib=contributor, mail_list=mailing_list, r2=ridgecv_noint_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1], MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    
    
    
# MSE_ridgecv_noint_full

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_ridgecv_noint_full:
    y_prediction = ridgecv_noint_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a ridge regression model without an intercept, where the optimal alpha value has been selected by 10-fold cross-validation, built with all 10 variables.
    
    Where:
      
    x1: Average length of mail sent by contributor
    x2: IsBot - Indicator variable on whether the author is a Bot or not    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x7: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
    x10: number of mails with 'reopened' in the body field

    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_ridgecv_noint_full, contrib=contributor, mail_list=mailing_list, r2=ridgecv_noint_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1], MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    

# MSE_lasso

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_lasso:
    y_prediction = lasso.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a lasso model with an intercept, built with variables x3, x4, x5, x6, x8 and x9.
    
    Where:
      
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field

    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_lasso, contrib=contributor, mail_list=mailing_list, r2=lasso_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    


# MSE_lasso_full

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_lasso_full:
    y_prediction = lasso_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a lasso model with an intercept, built with all 10 variables.
    
    Where:
      
    x1: Average length of mail sent by contributor
    x2: IsBot - Indicator variable on whether the author is a Bot or not    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x7: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
    x10: number of mails with 'reopened' in the body field

    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_lasso_full, contrib=contributor, mail_list=mailing_list, r2=lasso_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1], MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    

# MSE_lasso_noint

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_lasso_noint:
    y_prediction = lasso_noint.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a Lasso model with no intercept, built with variables x3, x4, x5, x6, x8 and x9.
    
    Where:
    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field

    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_lasso_noint, contrib=contributor, mail_list=mailing_list, r2=lasso_noint_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1], MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    


# MSE_lasso_noint_full

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_lasso_noint_full:
    y_prediction = lasso_noint_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a lasso model, without an intercept, built with all 10 variables.
    
    Where:
      
    x1: Average length of mail sent by contributor
    x2: IsBot - Indicator variable on whether the author is a Bot or not    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x7: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
    x10: number of mails with 'reopened' in the body field

    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_lasso_noint_full, contrib=contributor, mail_list=mailing_list, r2=lasso_noint_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1], MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    


# MSE_lasso_cv

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_lasso_cv:
    y_prediction = lasso_cv.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model ia a lasso model with an intercept, where the optimal alpha value is selcted by 10-fold CV. Built with variables x3, x4, x5, x6, x8 and x9. 
    
    Where:
     
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field

    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_lasso_cv, contrib=contributor, mail_list=mailing_list, r2=lasso_cv_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1], MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    


# MSE_lasso_cv_full

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_lasso_cv_full:
    y_prediction = lasso_cv_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model ia a lasso model with an intercept, where the optimal alpha value is selcted by 10-fold CV. Built with all 10 variables. 
    
    Where:
     
    x1: Average length of mail sent by contributor
    x2: IsBot - Indicator variable on whether the author is a Bot or not    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x7: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
    x10: number of mails with 'reopened' in the body field

    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_lasso_cv_full, contrib=contributor, mail_list=mailing_list, r2=lasso_cv_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    


# MSE_lasso_cv_noint

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_lasso_cv_noint:
    y_prediction = lasso_cv_noint.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model ia a lasso model without an intercept, where the optimal alpha value is selcted by 10-fold CV. Built with variables x3, x4, x5, x6, x8 and x9. 
    
    Where:
       
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field

    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_lasso_cv_noint, contrib=contributor, mail_list=mailing_list, r2=lasso_cv_noint_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1], MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    


# MSE_lasso_cv_noint_full

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_lasso_cv_noint_full:
    y_prediction = lasso_cv_noint_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model ia a lasso model without an intercept, where the optimal alpha value is selcted by 10-fold CV. Built using all 10 variables. 
    
    Where:
       
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x7: Number of mails containing a variation of 'commit'/'committer'/'comitted' in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field

    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_lasso_cv_noint_full, contrib=contributor, mail_list=mailing_list, r2=lasso_cv_noint_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1], MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    


# MSE_enet

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_enet:
    y_prediction = enet.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is an elastic net regression model, built with variables x3, x4, x5, x6, x8 and x9.
    
    Where:
      
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field

    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_enet, contrib=contributor, mail_list=mailing_list, r2=enet_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1], MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    

# MSE_enet_full

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_enet_full:
    y_prediction = enet_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is an elastic net regression model, built with variables all 10 variables.
    
    Where:
        
    x1: Average length of mail sent by contributor
    x2: IsBot - Indicator variable on whether the author is a Bot or not    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x7: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
    x10: number of mails with 'reopened' in the body field
    
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_enet_full, contrib=contributor, mail_list=mailing_list, r2=enet_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1], MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    

# MSE_enet_cv

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_enet_cv:
    y_prediction = enet_cv.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is an elatic net regression model, where the optimal values for alpha and the L1-ratio are selected by 10-fold CV. Built with variables x3, x4, x5, x6, x8 and x9.
    
    Where:
       
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field

    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x7,x8,x9) : MSE = {MSE_abr1}""".format(MSE=MSE_enet_cv, contrib=contributor, mail_list=mailing_list, r2=enet_cv_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1], MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    
        

# MSE_enet_cv_full

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_enet_cv_full:
    y_prediction = enet_cv_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is an elatic net regression model, where the optimal values for alpha and the L1-ratio are selected by 10-fold CV. Built with all 10 variables.
    
    Where:
    
    x1: Average length of mail sent by contributor
    x2: IsBot - Indicator variable on whether the author is a Bot or not    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x7: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
    x10: number of mails with 'reopened' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_enet_cv_full, contrib=contributor, mail_list=mailing_list, r2=enet_cv_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    
    
# MSE_svr    

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_svr:
    y_prediction = svr.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is support vector regression model, built with variables x3, x4, x5, x6, x8 and x9. 
    
    Where:
    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the bocdy field
    x6: Number of mails containing "fixed" in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_svr, contrib=contributor, mail_list=mailing_list, r2=svr_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full,MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    
    

# MSE_svr_full

elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_svr_full:
    y_prediction = svr_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a support vector regression model, built with all 10 variables. 
    
    Where:
    
    x1: Average length of mail sent by contributor
    x2: IsBot - Indicator variable on whether the author is a Bot or not    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x7: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
    x10: number of mails with 'reopened' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_svr_full, contrib=contributor, mail_list=mailing_list, r2=svr_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr,MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    
    

#MSE_rf
elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_rf:
    y_prediction = rf.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a random forest model built with variables x3, x4, x5, x6, x8 and x9. 
    
    Where:
    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the bocdy field
    x6: Number of mails containing "fixed" in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_rf, contrib=contributor, mail_list=mailing_list, r2=rf_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full,MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    

    
# MSE_rf_full    
elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_rf_full:
    y_prediction = rf_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a random forest model built with all 10 variables. 
    
    Where:
    
    x1: Average length of mail sent by contributor
    x2: IsBot - Indicator variable on whether the author is a Bot or not    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x7: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
    x10: number of mails with 'reopened' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_rf_full, contrib=contributor, mail_list=mailing_list, r2=rf_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf,MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    
   

# MSE_bagg
elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_bagg:
    y_prediction = bagg.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a bagging model built with variables x3, x4, x5, x6, x8 and x9. 
    
    Where:
    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the bocdy field
    x6: Number of mails containing "fixed" in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_bagg, contrib=contributor, mail_list=mailing_list, r2=bagg_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full,MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    

    
# MSE_bagg_full            
elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_bagg_full:
    y_prediction = bagg_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a bagging model built with all 10 variables. 
    
    Where:
    
    x1: Average length of mail sent by contributor
    x2: IsBot - Indicator variable on whether the author is a Bot or not    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x7: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
    x10: number of mails with 'reopened' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_bagg_full, contrib=contributor, mail_list=mailing_list, r2=bag_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg,MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    
    

# MSE_gbr:
elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_gbr:
    y_prediction = gbr.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a gradient boosting regression model built with variables x3, x4, x5, x6, x8 and x9. 
    
    Where:
    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the bocdy field
    x6: Number of mails containing "fixed" in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_gbr, contrib=contributor, mail_list=mailing_list, r2=gbr_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    


# MSE_gbr_full:
elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_gbr_full:
    y_prediction = gbr_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a gradient boosting regression model built with all 10 variables. 
    
    Where:
    
    x1: Average length of mail sent by contributor
    x2: IsBot - Indicator variable on whether the author is a Bot or not    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x7: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
    x10: number of mails with 'reopened' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_gbr_full, contrib=contributor, mail_list=mailing_list, r2=gbr_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr,MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    
    

# MSE_abr:
elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_abr:
    y_prediction = abr.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is an AdaBoost regression model built with variables x3, x4, x5, x6, x8 and x9. 
    
    Where:
    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the bocdy field
    x6: Number of mails containing "fixed" in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(MSE=MSE_abr, contrib=contributor, mail_list=mailing_list, r2=abr_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full,MSE_abr_full1=MSE_abr_full))    
 
    
       
# MSE_abr_full             
elif min(MSE_ridge_int, MSE_ridge_int_full, MSE_ridge_noint, MSE_ridge_noint_full, MSE_ridgecv_int, MSE_ridgecv_int_full, MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso, MSE_lasso_full, MSE_lasso_noint, MSE_lasso_noint_full, MSE_lasso_cv, MSE_lasso_cv_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet, MSE_enet_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_abr_full:
    y_prediction = abr_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is an AdaBoost regression model built with all 10 variables. 
    
    Where:
    
    x1: Average length of mail sent by contributor
    x2: IsBot - Indicator variable on whether the author is a Bot or not    
    x3: Number of mails containing a question in the body field
    x4: Number of mails containing a question in the subject field
    x5: Number of mails containing some form of "thanks" in the body field
    x6: Number of mails containing "fixed" in the body or subject fields
    x7: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x8: Number of mails that mention 'resolved' in the body field
    x9: number of mails that mention 'commented' in the body field
    x10: number of mails with 'reopened' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_int1}
        - Ridge regression model w/ intercept (all variables) : MSE = {MSE_ridge_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_ridge_noint1}
        - Ridge regression model w/o intercept (all variables) : MSE = {MSE_ridge_noint_full1}
        - Ridge regression model w/ intercept, (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int1}
        - Ridge regression model w/ intercept, (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_int_full1}
        - Ridge regression model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso1}
        - Lasso model w/ intercept (all variables) : MSE = {MSE_lasso_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_lasso_noint1}
        - Lasso model w/o intercept (all variables) : MSE = {MSE_lasso_noint_full1}
        - Lasso model w/ intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Lasso model w/o intercept (variables x3,x4,x5,x6,x8,x9; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_enet1}
        - Elastic net regression model (all variables) : MSE = {MSE_enet_full1}
        - Elastic net regression model (variables x3,x4,x5,x6,x8,x9; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_abr1}""".format(MSE=MSE_abr_full, contrib=contributor, mail_list=mailing_list, r2=abr_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridge_int1=MSE_ridge_int,MSE_ridge_int_full1=MSE_ridge_int_full,MSE_ridge_noint1=MSE_ridge_noint,MSE_ridge_noint_full1=MSE_ridge_noint_full,MSE_ridgecv_int1=MSE_ridgecv_int,MSE_ridgecv_int_full1=MSE_ridgecv_int_full,MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso1=MSE_lasso,MSE_lasso_full1=MSE_lasso_full,MSE_lasso_noint1=MSE_lasso_noint,MSE_lasso_noint_full1=MSE_lasso_noint_full,MSE_lasso_cv1=MSE_lasso_cv,MSE_lasso_cv_full1=MSE_lasso_cv_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet1=MSE_enet,MSE_enet_full1=MSE_enet_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr))
