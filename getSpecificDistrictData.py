# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 15:07:15 2021

@author: ramya
"""

import pandas as pd
import flask 
from flask import request, jsonify

import json

#district data url
districtDataUrl = pd.read_csv('https://covid19-dashboard.ages.at/data/CovidFaelle_Timeline_GKZ.csv',sep=";")
districtDataUrl.info(verbose=False)
districtDataUrl.info()
districtDataUrl.dtypes


importantColumns = districtDataUrl[['Time','Bezirk','AnzEinwohner','AnzahlFaelle','AnzahlFaelleSum','AnzahlFaelle7Tage']]

#convert to datetime format of time column for grouping by week,month,year
importantColumns['Time']=pd.to_datetime(districtDataUrl['Time'],dayfirst=True)

#R VALUE 

rValueUrl = pd.read_csv('https://www.ages.at/fileadmin/AGES2015/Wissen-Aktuell/COVID19/R_eff.csv',sep=";",decimal=',')
rValueUrl.info(verbose=False)
rValueUrl.info()
rValueUrl.dtypes

importantColumnsREFF = rValueUrl[['Datum','R_eff']]
importantColumnsREFF['Datum']=pd.to_datetime(rValueUrl['Datum'])

#API
app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<p>District data: pass parameters district name, year  and interval  to get json view of data</p>"

# A route to return all the json data.
@app.route('/api/positivecasesbydistrict/', methods=['GET'])
def api_DistrictPositiveCases_Filter():
    districtname=''
    year=''
    interval=''
    #get query parameters
    query_parameters = request.args
    # assign param to filter data
    districtname=query_parameters.get('districtname')
    year=query_parameters.get('year')
    interval=query_parameters.get('interval')
    
    
    
    if 'districtname' in query_parameters:
        districtnametofilter=districtname
        filteredDistrict=importantColumns[importantColumns['Bezirk'].apply(lambda val:districtnametofilter in val)]
   
    else:
        return 'Error:No district name provided. Please choose a district name.'
    if 'year' in query_parameters:
        yeartofilter=str(year)
    else:
        return 'Error:No year provided. Please choose a year.'
    if 'interval' in query_parameters:
        dataintervaltofilter=interval
        
        if(dataintervaltofilter=='monthly'):
             districtDataByMonth=filteredDistrict.assign(DistrictName=filteredDistrict['Bezirk'],Month=filteredDistrict['Time'].dt.strftime('%m').sort_index(),Year=filteredDistrict['Time'].dt.strftime('%Y').sort_index()).groupby(['DistrictName','Month','Year'])['AnzahlFaelle'].sum()
             convertedJson = districtDataByMonth.to_json(orient="table")
             
        elif(dataintervaltofilter=='weekly'):
           districtDataByWeek=filteredDistrict.assign(DistrictName=filteredDistrict['Bezirk'],Week=filteredDistrict['Time'].dt.strftime('%W').sort_index(),Year=filteredDistrict['Time'].dt.strftime('%Y').sort_index()).groupby(['DistrictName','Week','Year'])['AnzahlFaelle'].sum()
           convertedJson = districtDataByWeek.to_json(orient="table")
          
        elif(dataintervaltofilter=='yearly'):
           districtDataByYear=filteredDistrict.assign(DistrictName=filteredDistrict['Bezirk'],Year=filteredDistrict['Time'].dt.strftime('%Y').sort_index()).groupby(['DistrictName','Year'])['AnzahlFaelle'].sum()
           convertedJson = districtDataByYear.to_json(orient="table")
           
    else:
        return 'Error:No interval provided. Please choose a data interval.'
   
    
    
    #convertedJson = districtDataByMonth.to_json(orient="table")
    #de-serialize into python obj
    parsedJson = json.loads(convertedJson)
    #serialize into json
    json.dumps(parsedJson) 
    #json op to mime-type application/json
    return jsonify(parsedJson)


@app.route('/api/alldistrictnames/', methods=['GET'])
def get_all_district_names():
 districtnames=districtDataUrl['Bezirk'].unique()
 print(districtnames)
 districtsJson = districtnames.tolist()
 json.dumps(districtsJson) 
 return jsonify(districtsJson)

@app.route('/REff', methods=['GET'])
def REffhome():
    return "<p>R_Effective data: R effective value for austria grouped by week month and year</p>"

# A route to return all the json data.
@app.route('/api/R_eff_Austria/', methods=['GET'])
def api_REffectiveValue_Filter():
    
    year=''
    interval=''
    #get query parameters
    query_parameters = request.args
    # assign param to filter data
    
    year=query_parameters.get('year')
    interval=query_parameters.get('interval')
    
    if 'year' in query_parameters:
        yeartofilter=str(year)
    else:
        return 'Error:No year provided. Please choose a year.'
    if 'interval' in query_parameters:
        dataintervaltofilter=interval
        
        if(dataintervaltofilter=='monthly'):
             REffDataByMonth=importantColumnsREFF.assign(Month=importantColumnsREFF['Datum'].dt.strftime('%m').sort_index(),Year=importantColumnsREFF['Datum'].dt.strftime('%Y').sort_index()).groupby(['Month','Year'])['R_eff'].sum()
             convertedJsonREff = REffDataByMonth.to_json(orient="table")
             
        elif(dataintervaltofilter=='weekly'):
           REffDataByWeek=importantColumnsREFF.assign(Week=importantColumnsREFF['Datum'].dt.strftime('%W').sort_index(),Year=importantColumnsREFF['Datum'].dt.strftime('%Y').sort_index()).groupby(['Week','Year'])['R_eff'].sum()
           convertedJsonREff = REffDataByWeek.to_json(orient="table")
          
        elif(dataintervaltofilter=='yearly'):
           REffDataByYear=importantColumnsREFF.assign(Year=importantColumnsREFF['Datum'].dt.strftime('%Y').sort_index()).groupby(['Year'])['R_eff'].sum()
           convertedJsonREff = REffDataByYear.to_json(orient="table")
           
    else:
        return 'Error:No interval provided. Please choose a data interval.'
    
    parsedJsonREff = json.loads(convertedJsonREff)
    json.dumps(parsedJsonREff) 
    return jsonify(parsedJsonREff)



app.run()