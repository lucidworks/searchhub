# -*- coding: utf-8 -*-

# Filtered on isBot = True
# i.e JIRA accounts only

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
from sklearn.linear_model import Ridge, RidgeCV, Lasso, LassoCV, ElasticNet, ElasticNetCV 
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor, BaggingRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.metrics import mean_squared_error

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

results = solr.search('_lw_data_source_s:{ml} AND isBot:true'.format(ml=mailing_list),**params)

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
#isbot = [] 
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
    average_length_l.append(sum(a)/len(solr_results.docs))

# x2 - Number of mails containing a question mark in the body field
    num_questions.append(sum(questions)/len(solr_results.docs))

# x3 - Number of mails containing a question mark in the subject field
    num_subject_qs.append(sum(subject_questions)/len(solr_results.docs))        
    
# x4 - Number of mails with variation of 'thanks' in body field
    num_thanks.append(sum(tot1)/len(solr_results.docs))        
        
# x5 - Number of mails with 'fixed' in the body or subject field
    num_fixed.append(sum(tot2)/len(solr_results.docs))        

# x6 - Number of mails with 'commit' or 'committed' in the body or subject fields
    num_commit.append(sum(tot3)/len(solr_results.docs))

# x7 - Number of mails with 'resolved' in the body field
    num_resolved.append(sum(body_resolved)/len(solr_results.docs))

# x8 - Number of mails with 'commented' in the body field
    num_commented.append(sum(body_commented)/len(solr_results.docs))

# x9 - Number of mails with 'reopened'/'re-opened'/'reopening'/'re-opening' in the body field 
    num_reopen.append(sum(tot4)/len(solr_results.docs))         

x1 = average_length_l
x2 = num_questions
x3 = num_subject_qs    
x4 = num_thanks
x5 = num_fixed
x6 = num_commit
x7 = num_resolved
x8 = num_commented         
x9 = num_reopen

#########################################################################################################################################################                                                     

X_full = {'x1':pd.Series(x1,index = active_contribs.keys()),
'x2':pd.Series(x2,index = active_contribs.keys()),
'x3':pd.Series(x3,index = active_contribs.keys()),
'x4':pd.Series(x4,index = active_contribs.keys()),
'x5':pd.Series(x5,index = active_contribs.keys()),
'x6':pd.Series(x6,index = active_contribs.keys()),
'x7':pd.Series(x7,index = active_contribs.keys()),
'x8':pd.Series(x8,index = active_contribs.keys()),
'x9':pd.Series(x9,index = active_contribs.keys())}
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

# Training and test set - target variable
y = pd.DataFrame({'y':pd.Series(active_contribs.values(),index = active_contribs.keys())})
y_train = y.ix[train_select[:int(round(len(active_contribs.keys())*0.75))]].reset_index().y
y_test = y.ix[train_select[int(round(len(active_contribs.keys())*0.75)):]].reset_index().y      

#########################################################################################################################################################

# L1-based feature selection

from sklearn.feature_selection import SelectFromModel

X_full_train.shape
lasso_cv = LassoCV(cv=10,normalize=True).fit(X_full_train,y_train)
model = SelectFromModel(lasso_cv, prefit=True)

# Create dataframe of only those variables non-zero variables selected by Lasso
X = model.transform(X_full)
X = pd.DataFrame(X,index = active_contribs.keys())

# Training and test set - subset as chosen by Lasso regularization
X_train = model.transform(X_full_train)
X_test = model.transform(X_full_test)


#########################################################################################################################################################

# MODEL CONSTRUCTION 

#########################################################################################################################################################

# Building the most accurate statistical model
# We shall use Mean Squared Error to make a judgement of the most accurate model - looking for model with lowest MSE

# Try full models and subset models as chosen by L1 

#########################################################################################################################################################
# Ridge Regression 

# tackles the problem of unstable regression coefficients when predictors are highly correlated

# Ridge regression performs particularly well when there is a subset of true coefficients that are small or even zero. It doesn’t do as
# well when all of the true coefficients are moderately large; however, in this case it can still outperform linear regression over a pretty
# narrow range of (small) λ values

# Ridge Regression without intercept - using 10-fold cross-validation to get optimal alpha parameter (L1 selected subset)
ridgecv_noint = RidgeCV(cv=10,normalize=True,fit_intercept=False).fit(X_train, y_train)
ridgecv_noint_test_pred = ridgecv_noint.predict(X_test)
MSE_ridgecv_noint = mean_squared_error(y_test,ridgecv_noint_test_pred)
ridgecv_noint_r2 = ridgecv_noint.score(X_test, y_test)

# Ridge Regression without intercept - using 10-fold cross-validation to get optimal alpha parameter (all variables)
ridgecv_noint_full = RidgeCV(cv=10,normalize=True,fit_intercept=False).fit(X_full_train, y_train)
ridgecv_noint_full_test_pred = ridgecv_noint_full.predict(X_full_test)
MSE_ridgecv_noint_full = mean_squared_error(y_test,ridgecv_noint_full_test_pred)
ridgecv_noint_full_r2 = ridgecv_noint_full.score(X_full_test, y_test)

######################################################################################################################
# LassoCV (L1 selected subset)
lasso_cv_noint = LassoCV(cv=10,fit_intercept=False,normalize=True).fit(X_train, y_train)
lasso_cv_noint_test_pred = lasso_cv_noint.predict(X_test)
MSE_lasso_cv_noint = mean_squared_error(y_test,lasso_cv_noint.predict(X_test))
lasso_cv_noint_r2 = lasso_cv_noint.score(X_test, y_test)

# LassoCV function - with no intercept / all variables
lasso_cv_noint_full = LassoCV(cv=20,fit_intercept=False,normalize=True).fit(X_full_train, y_train)
lasso_cv_noint_full_test_pred = lasso_cv_noint_full.predict(X_full_test)
MSE_lasso_cv_noint_full = mean_squared_error(y_test,lasso_cv_noint_full_test_pred)
lasso_cv_noint_full_r2 = lasso_cv_noint_full.score(X_full_test, y_test)

########################################################################################################################
# Elastic Net (L1 selected subset)
enet_cv = ElasticNetCV(fit_intercept=False,normalize=True).fit(X_train, y_train) 
enet_cv_pred = enet_cv.predict(X_test)
MSE_enet_cv = mean_squared_error(y_test,enet_cv.predict(X_test)) 
enet_cv_r2 = enet_cv.score(X_test, y_test)  

# Elastic Net (all variables)
enet_cv_full = ElasticNetCV(fit_intercept=False,normalize=True).fit(X_full_train, y_train) 
enet_cv_full_test_pred = enet_cv_full.predict(X_full_test)
MSE_enet_cv_full = mean_squared_error(y_test,enet_cv_full_test_pred)
enet_cv_full_r2 = enet_cv_full.score(X_full_test, y_test) 

#######################################################################################################################
# Support Vector Regression (L1 selected subset)
svr = SVR().fit(X_train, y_train) 
svr_test_pred = svr.predict(X_test)
MSE_svr = mean_squared_error(y_test,svr.predict(X_test))
svr_r2 = svr.score(X_test, y_test) 

# Support Vector Regression (all variables)
svr_full = SVR().fit(X_full_train, y_train) 
svr_full_test_pred = svr_full.predict(X_full_test)
MSE_svr_full = mean_squared_error(y_test,svr_full_test_pred)
svr_full_r2 = svr_full.score(X_full_test, y_test) 

#######################################################################################################################
# Random Forest Regression (L1 selected subset)
rf = RandomForestRegressor().fit(X_train, y_train) 
rf_test_pred = rf.predict(X_test) 
MSE_rf = mean_squared_error(y_test,rf.predict(X_test))
rf_r2 = rf.score(X_test, y_test)  

# Random Forest Regression (all variables)
rf_full = RandomForestRegressor().fit(X_full_train, y_train) 
rf_full_test_pred = rf_full.predict(X_full_test)
MSE_rf_full = mean_squared_error(y_test,rf_full_test_pred)
rf_full_r2 = rf_full.score(X_full_test, y_test)   

########################################################################################################################
# Bagging (L1 selected subset)
bagg = BaggingRegressor().fit(X_train, y_train) 
bagg_test_pred = bagg.predict(X_test)
MSE_bagg = mean_squared_error(y_test,bagg.predict(X_test))
bagg_r2 = bagg.score(X_test, y_test)   

# Bagging (all variables)
bagg_full = BaggingRegressor().fit(X_full_train, y_train) 
bagg_full_test_pred = bagg_full.predict(X_full_test)
MSE_bagg_full = mean_squared_error(y_test,bagg_full_test_pred)
bagg_full_r2 = bagg_full.score(X_full_test, y_test)  

########################################################################################################################
# Gradient Boosting Regressor (L1 selected subset)
gbr = GradientBoostingRegressor().fit(X_train, y_train) 
gbr_test_pred = gbr.predict(X_test)
MSE_gbr = mean_squared_error(y_test,gbr_test_pred)
gbr_r2 = gbr.score(X_test, y_test)  

# Gradient Boosting Regressor (all variables)
gbr_full = GradientBoostingRegressor().fit(X_full_train, y_train) 
gbr_full_test_pred = gbr_full.predict(X_full_test)
MSE_gbr_full = mean_squared_error(y_test,gbr_full_test_pred)
gbr_full_r2 = gbr_full.score(X_full_test, y_test)  

########################################################################################################################
# AdaBoost Regressor (L1 selected subset)
abr = AdaBoostRegressor().fit(X_train, y_train) 
abr_test_pred = abr.predict(X_test)
MSE_abr = mean_squared_error(y_test,abr_test_pred)
abr_r2 = abr.score(X_test, y_test)  

# AdaBoost Regressor (all variables)
abr_full = AdaBoostRegressor().fit(X_full_train, y_train) 
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

# Creating stribg of those variables selected by L1-regularization
string = ""
for i in range(X_train.shape[1]):
    if lasso_cv.coef_[i] != 0:
        string+=("""x{num}, """.format(num=i+1))   

                                                                                                                                                                                                                                                                                          
# ridgecv_noint
if min(MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_ridgecv_noint:
    y_prediction = ridgecv_noint.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a ridge regression model without an intercept, where the optimal alpha value has been selected by 10-fold cross-validation, built with variables {insert_string}.
    
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables {insert_string}optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables {insert_string}) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables {insert_string}) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables {insert_string}) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables {insert_string}) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables {insert_string}) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(insert_string=string,MSE=MSE_ridgecv_noint, contrib=contributor, mail_list=mailing_list, r2=ridgecv_noint_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    
    
    
# ridgecv_noint_full
elif min(MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_ridgecv_noint_full:
    y_prediction = ridgecv_noint_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a ridge regression model without an intercept, where the optimal alpha value has been selected by 10-fold cross-validation, built with all 9 variables.
    
    Where:
    
    x1: Average length of mail sent by contributor
    x2: Number of mails containing a question in the body field
    x3: Number of mails containing a question in the subject field
    x4: Number of mails containing some form of "thanks" in the body field
    x5: Number of mails containing "fixed" in the body or subject fields
    x6: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x7: Number of mails that mention 'resolved' in the body field
    x8: number of mails that mention 'commented' in the body field
    x9: number of mails with 'reopened' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Lasso model w/o intercept (variables {insert_string}; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables {insert_string}optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables {insert_string}) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables {insert_string}) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables {insert_string}) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables {insert_string}) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables {insert_string}) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(insert_string=string,MSE=MSE_ridgecv_noint_full, contrib=contributor, mail_list=mailing_list, r2=ridgecv_noint_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    

# lasso_cv_noint
elif min(MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_lasso_cv_noint:
    y_prediction = lasso_cv_noint.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model ia a lasso model without an intercept, where the optimal alpha value is selcted by 10-fold CV, built with variables {insert_string}.

    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables {insert_string}optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables {insert_string}) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables {insert_string}) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables {insert_string}) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables {insert_string}) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables {insert_string}) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(insert_string=string, MSE=MSE_lasso_cv_noint, contrib=contributor, mail_list=mailing_list, r2=lasso_cv_noint_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    


# lasso_cv_noint_full
elif min(MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_lasso_cv_noint_full:
    y_prediction = lasso_cv_noint_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model ia a lasso model without an intercept, where the optimal alpha value is selcted by 10-fold CV. Built using all 9 variables. 
    
    Where:
    
    x1: Average length of mail sent by contributor
    x2: Number of mails containing a question in the body field
    x3: Number of mails containing a question in the subject field
    x4: Number of mails containing some form of "thanks" in the body field
    x5: Number of mails containing "fixed" in the body or subject fields
    x6: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x7: Number of mails that mention 'resolved' in the body field
    x8: number of mails that mention 'commented' in the body field
    x9: number of mails with 'reopened' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/o intercept (variables {insert_string} alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Elastic net regression model (variables {insert_string}optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables {insert_string}) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables {insert_string}) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables {insert_string}) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables {insert_string}) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables {insert_string}) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(insert_string=string,MSE=MSE_lasso_cv_noint_full, contrib=contributor, mail_list=mailing_list, r2=lasso_cv_noint_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    


# enet_cv
elif min(MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_enet_cv:
    y_prediction = enet_cv.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is an elatic net regression model, where the optimal values for alpha and the L1-ratio are selected by 10-fold CV. Built with variables {insert_string}.

    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables {insert_string}) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables {insert_string}) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables {insert_string}) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables {insert_string}) : MSE = {MSE_abr1}
        - AdaBoost regressor model (variables {insert_string}) : MSE = {MSE_abr1}""".format(insert_string=string, MSE=MSE_enet_cv, contrib=contributor, mail_list=mailing_list, r2=enet_cv_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    
        

# enet_cv_full

elif min(MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_enet_cv_full:
    y_prediction = enet_cv_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is an elatic net regression model, where the optimal values for alpha and the L1-ratio are selected by 10-fold CV. Built with all 10 variables.
    
    Where:
    
    x1: Average length of mail sent by contributor
    x2: Number of mails containing a question in the body field
    x3: Number of mails containing a question in the subject field
    x4: Number of mails containing some form of "thanks" in the body field
    x5: Number of mails containing "fixed" in the body or subject fields
    x6: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x7: Number of mails that mention 'resolved' in the body field
    x8: number of mails that mention 'commented' in the body field
    x9: number of mails with 'reopened' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/ intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_full1}
        - Elastic net regression model (variables {insert_string}optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Support Vector Regression model (variables {insert_string}) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables {insert_string}) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables {insert_string}) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables {insert_string}) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables {insert_string}) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(insert_string=string,MSE=MSE_enet_cv_full, contrib=contributor, mail_list=mailing_list, r2=enet_cv_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet_cv1=MSE_enet_cv, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    
    
# svr    
elif min(MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_svr:
    y_prediction = svr.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is support vector regression model, built with variables {insert_string}. 
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables {insert_string}optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables {insert_string}) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables {insert_string}) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables {insert_string}) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables {insert_string}) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(insert_string=string,MSE=MSE_svr, contrib=contributor, mail_list=mailing_list, r2=svr_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full,MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    
    

# svr_full

elif min(MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_svr_full:
    y_prediction = svr_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a support vector regression model, built with all 9 variables. 
    
    Where:
    
    x1: Average length of mail sent by contributor
    x2: Number of mails containing a question in the body field
    x3: Number of mails containing a question in the subject field
    x4: Number of mails containing some form of "thanks" in the body field
    x5: Number of mails containing "fixed" in the body or subject fields
    x6: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x7: Number of mails that mention 'resolved' in the body field
    x8: number of mails that mention 'commented' in the body field
    x9: number of mails with 'reopened' in the body field
                    
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables {insert_string}optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables {insert_string}) : MSE = {MSE_svr1}
        - Random forest model (variables {insert_string}) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables {insert_string}) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables {insert_string}) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables {insert_string}) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(insert_string=string,MSE=MSE_svr_full, contrib=contributor, mail_list=mailing_list, r2=svr_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr,MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    
    
# rf
elif min(MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_rf:
    y_prediction = rf.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a random forest model built with variables {insert_string}.
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables {insert_string}optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables {insert_string}) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables {insert_string}) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables {insert_string}) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables {insert_string}) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(insert_string=string, MSE=MSE_rf, contrib=contributor, mail_list=mailing_list, r2=rf_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full,MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    

# rf_full    
elif min(MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_rf_full:
    y_prediction = rf_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a random forest model built with all 9 variables. 
    
    Where:
    
    x1: Average length of mail sent by contributor
    x2: Number of mails containing a question in the body field
    x3: Number of mails containing a question in the subject field
    x4: Number of mails containing some form of "thanks" in the body field
    x5: Number of mails containing "fixed" in the body or subject fields
    x6: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x7: Number of mails that mention 'resolved' in the body field
    x8: number of mails that mention 'commented' in the body field
    x9: number of mails with 'reopened' in the body field
                    
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables {insert_string}optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables {insert_string}) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables {insert_string}) : MSE = {MSE_rf1}
        - Bagging model (variables {insert_string}) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables {insert_string}) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables {insert_string}) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(insert_string=string,MSE=MSE_rf_full, contrib=contributor, mail_list=mailing_list, r2=rf_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf,MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    
   

# bagg
elif min(MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_bagg:
    y_prediction = bagg.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a bagging model built with variables {insert_string}.
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables {insert_string}optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables x3,x4,x5,x6,x8,x9) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables {insert_string}) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables {insert_string}) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables {insert_string}) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(insert_string=string, MSE=MSE_bagg, contrib=contributor, mail_list=mailing_list, r2=bagg_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full,MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    

    
# bagg_full            
elif min(MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_bagg_full:
    y_prediction = bagg_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a bagging model built with all 9 variables. 
    
    Where:
    
    x1: Average length of mail sent by contributor
    x2: Number of mails containing a question in the body field
    x3: Number of mails containing a question in the subject field
    x4: Number of mails containing some form of "thanks" in the body field
    x5: Number of mails containing "fixed" in the body or subject fields
    x6: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x7: Number of mails that mention 'resolved' in the body field
    x8: number of mails that mention 'commented' in the body field
    x9: number of mails with 'reopened' in the body field
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables {insert_string}optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables {insert_string}) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables {insert_string}) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables {insert_string}) : MSE = {MSE_bagg1}
        - Gradient boosting regressor model (variables {insert_string}) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables {insert_string}) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(insert_string=string,MSE=MSE_bagg_full, contrib=contributor, mail_list=mailing_list, r2=bagg_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg,MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    
    

# gbr:
elif min(MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_gbr:
    y_prediction = gbr.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a gradient boosting regression model built with variables {insert_string}.
          
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables {insert_string}optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables {insert_string}) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables {insert_string}) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables {insert_string}) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables {insert_string}) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(insert_string=string, MSE=MSE_gbr, contrib=contributor, mail_list=mailing_list, r2=gbr_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    


# gbr_full:
elif min(MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_gbr_full:
    y_prediction = gbr_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is a gradient boosting regression model built with all 9 variables. 
    
    Where:
    
    x1: Average length of mail sent by contributor
    x2: Number of mails containing a question in the body field
    x3: Number of mails containing a question in the subject field
    x4: Number of mails containing some form of "thanks" in the body field
    x5: Number of mails containing "fixed" in the body or subject fields
    x6: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x7: Number of mails that mention 'resolved' in the body field
    x8: number of mails that mention 'commented' in the body field
    x9: number of mails with 'reopened' in the body field
                    
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables {insert_string}optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables {insert_string}) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables {insert_string}) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables {insert_string}) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables {insert_string}) : MSE = {MSE_gbr1} 
        - AdaBoost regressor model (variables {insert_string}) : MSE = {MSE_abr1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(insert_string=string,MSE=MSE_gbr_full, contrib=contributor, mail_list=mailing_list, r2=gbr_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr,MSE_abr1=MSE_abr, MSE_abr_full1=MSE_abr_full))    
    

# abr:
elif min(MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_abr:
    y_prediction = abr.predict((X.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is an AdaBoost regression model built with variables {insert_string}. 

    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables {insert_string}optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables {insert_string}) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables {insert_string}) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables {insert_string}) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables {insert_string}) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (all variables) : MSE = {MSE_abr_full1}""".format(insert_string=string, MSE=MSE_abr, contrib=contributor, mail_list=mailing_list, r2=abr_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full,MSE_abr_full1=MSE_abr_full))    
 
# abr_full             
elif min(MSE_ridgecv_noint, MSE_ridgecv_noint_full, MSE_lasso_cv_noint, MSE_lasso_cv_noint_full, MSE_enet_cv, MSE_enet_cv_full, MSE_svr, MSE_svr_full, MSE_rf, MSE_rf_full, MSE_bagg, MSE_bagg_full, MSE_gbr, MSE_gbr_full, MSE_abr, MSE_abr_full) == MSE_abr_full:
    y_prediction = abr_full.predict((X_full.ix[contributor]).reshape(1,-1))
    squared_error = pow((y_prediction-y_value),2)

    print ("""The chosen model is an AdaBoost regression model built with all 9 variables. 
    
    Where:
    
    x1: Average length of mail sent by contributor
    x2: Number of mails containing a question in the body field
    x3: Number of mails containing a question in the subject field
    x4: Number of mails containing some form of "thanks" in the body field
    x5: Number of mails containing "fixed" in the body or subject fields
    x6: Number of mails containing a variation of 'commit'/'comitted' in the body or subject fields
    x7: Number of mails that mention 'resolved' in the body field
    x8: number of mails that mention 'commented' in the body field
    x9: number of mails with 'reopened' in the body field
                    
    The MSE for this model is {MSE}.
    
    The associated coefficient of determination (R^2) of the prediction is {r2}.
    
    The predicted number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_1} mails.
    The actual number of mails sent by {contrib} over the course of his/her lifetime to the {mail_list} is {num_of_mails_2} mails.
    
    The squared error for this prediction is {se}.
    
    ===================================================================================================================================
    
    Other models taken into consideration, and their respective MSE values were:
        
        - Ridge regression model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint1}
        - Ridge regression model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_ridgecv_noint_full1}
        - Lasso model w/o intercept (variables {insert_string}alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint1}
        - Lasso model w/o intercept (all variables; alpha selected by 10-fold CV) : MSE = {MSE_lasso_cv_noint_full1}
        - Elastic net regression model (variables {insert_string}optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv1}
        - Elastic net regression model (all variables; optimal alpha and l1_ratio paramters selected by 10-fold CV) : MSE = {MSE_enet_cv_full1}
        - Support Vector Regression model (variables {insert_string}) : MSE = {MSE_svr1}
        - Support Vector Regression model (all variables) : MSE = {MSE_svr_full1}
        - Random forest model (variables {insert_string}) : MSE = {MSE_rf1}
        - Random forest model (all varibles) : MSE = {MSE_rf_full1}
        - Bagging model (variables {insert_string}) : MSE = {MSE_bagg1}
        - Bagging model (all variables) : MSE = {MSE_bagg_full1}
        - Gradient boosting regressor model (variables {insert_string}) : MSE = {MSE_gbr1} 
        - Gradient boosting regressor model (all variables) : MSE = {MSE_gbr_full1}
        - AdaBoost regressor model (variables {insert_string}) : MSE = {MSE_abr1}""".format(insert_string=string,MSE=MSE_abr_full, contrib=contributor, mail_list=mailing_list, r2=abr_full_r2, num_of_mails_1=str(y_prediction)[2:][:-1], num_of_mails_2=y_value, se=str(squared_error)[2:][:-1],MSE_ridgecv_noint1=MSE_ridgecv_noint,MSE_ridgecv_noint_full1=MSE_ridgecv_noint_full,MSE_lasso_cv_noint1=MSE_lasso_cv_noint,MSE_lasso_cv_noint_full1=MSE_lasso_cv_noint_full,MSE_enet_cv1=MSE_enet_cv,MSE_enet_cv_full1=MSE_enet_cv_full, MSE_svr1=MSE_svr, MSE_svr_full1=MSE_svr_full, MSE_rf1=MSE_rf, MSE_rf_full1=MSE_rf_full, MSE_bagg1=MSE_bagg, MSE_bagg_full1=MSE_bagg_full, MSE_gbr1=MSE_gbr, MSE_gbr_full1=MSE_gbr_full, MSE_abr1=MSE_abr))
