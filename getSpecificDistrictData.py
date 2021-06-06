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
print('count of nan values')
print(districtDataUrl.isna().sum())
print(districtDataUrl.isnull().sum(axis = 0))

importantColumns = districtDataUrl[['Time','Bezirk','AnzEinwohner','AnzahlFaelle','AnzahlFaelleSum','AnzahlFaelle7Tage']]

#convert to datetime format of time column for grouping by week,month,year dayfirst=true for correct conversion format(yyyy-mm-dd)
importantColumns['Time']=pd.to_datetime(districtDataUrl['Time'],dayfirst=True)

#R VALUE url

rValueUrl = pd.read_csv('https://www.ages.at/fileadmin/AGES2015/Wissen-Aktuell/COVID19/R_eff.csv',sep=";",decimal=',')
rValueUrl.info(verbose=False)
rValueUrl.info()
rValueUrl.dtypes

importantColumnsREFF = rValueUrl[['Datum','R_eff']]
importantColumnsREFF['Datum']=pd.to_datetime(rValueUrl['Datum'])


#Vaccination data url
vaccinationDataUrl = pd.read_csv('https://info.gesundheitsministerium.gv.at/data/timeline-bundeslaendermeldungen.csv',sep=';')
vaccinationDataUrl.info(verbose=False)
vaccinationDataUrl.info()
vaccinationDataUrl.dtypes

print('count of nan values')
print(vaccinationDataUrl.isna().sum())
print(vaccinationDataUrl.isnull().sum(axis = 0))
#delete the rows where column value is NaN
#vaccinationDataUrl.dropna(axis=0)
importantColumnsVacc=vaccinationDataUrl[["Datum","Name","Bevölkerung","GemeldeteImpfungenLaender"]]
print(importantColumnsVacc.describe())
importantColumnsVacc['Datum']=pd.to_datetime(importantColumnsVacc['Datum'],utc=True)
importantColumnsVacc['Datum']=importantColumnsVacc['Datum'].dt.tz_convert('CET')
print(importantColumnsVacc['Datum'])
print(importantColumnsVacc.describe())

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
        yeartofilter=year
    else:
        return 'Error:No year provided. Please choose a year.'
   
    if 'interval' in query_parameters:
        dataintervaltofilter=interval
        
        if(dataintervaltofilter=='monthly'):
             districtDataByMonth=filteredDistrict.assign(DistrictName=filteredDistrict['Bezirk'],Interval=filteredDistrict['Time'].dt.strftime('%m').sort_index(),Year=filteredDistrict['Time'].dt.strftime('%Y').sort_index()).groupby(['DistrictName','Interval','Year'])['AnzahlFaelle'].sum()
             districtDataByMonth_FilterYear=districtDataByMonth.filter(like=yeartofilter)
             convertedJson = districtDataByMonth_FilterYear.to_json(orient="table")
             
        elif(dataintervaltofilter=='weekly'):
           districtDataByWeek=filteredDistrict.assign(DistrictName=filteredDistrict['Bezirk'],Interval=filteredDistrict['Time'].dt.strftime('%W').sort_index(),Year=filteredDistrict['Time'].dt.strftime('%Y').sort_index()).groupby(['DistrictName','Interval','Year'])['AnzahlFaelle'].sum()
           districtDataByWeek_FilterYear=districtDataByWeek.filter(like=yeartofilter)
           convertedJson = districtDataByWeek_FilterYear.to_json(orient="table")
          
        elif(dataintervaltofilter=='yearly'):
           
           districtDataByYear=filteredDistrict.assign(DistrictName=filteredDistrict['Bezirk'],Interval=filteredDistrict['Time'].dt.strftime('%Y').sort_index()).groupby(['DistrictName','Interval'])['AnzahlFaelle'].sum()
           districtDataByYear_FilterYear=districtDataByYear.filter(like=yeartofilter)
          
           
           convertedJson = districtDataByYear_FilterYear.to_json(orient="table")
           
    else:
        return 'Error:No interval provided. Please choose a data interval.'
   
    
    
    #convertedJson = districtDataByMonth.to_json(orient="table")
    #de-serialize into python obj
    parsedJson = json.loads(convertedJson)
    #serialize into json
    json.dumps(parsedJson) 
    #json op to mime-type application/json
    return jsonify(parsedJson)


@app.route('/api/dropdownvalues/', methods=['GET'])
def get_all_district_names():
 districtnames=districtDataUrl['Bezirk'].unique()
 dataInterval=['weekly','monthly','yearly']
 year=['2020','2021']
 dropdownvalues=[]
 dropdownvalues.append({'districtNames':districtnames.tolist()})
 dropdownvalues.append({'dataInterval':dataInterval})
 dropdownvalues.append({'year':year})
 print(dropdownvalues)
 districtsJson = dropdownvalues
# districtsJson = districtnames.tolist()
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
        yeartofilter=year
    else:
        return 'Error:No year provided. Please choose a year.'
    if 'interval' in query_parameters:
        dataintervaltofilter=interval
        
        if(dataintervaltofilter=='monthly'):
             REffDataByMonth=importantColumnsREFF.assign(Interval=importantColumnsREFF['Datum'].dt.strftime('%m').sort_index(),Year=importantColumnsREFF['Datum'].dt.strftime('%Y').sort_index()).groupby(['Interval','Year'])['R_eff'].sum()
             REffDataByMonth_FilterYear=REffDataByMonth.filter(like=yeartofilter)
             convertedJsonREff = REffDataByMonth_FilterYear.to_json(orient="table")
             
        elif(dataintervaltofilter=='weekly'):
           REffDataByWeek=importantColumnsREFF.assign(Interval=importantColumnsREFF['Datum'].dt.strftime('%W').sort_index(),Year=importantColumnsREFF['Datum'].dt.strftime('%Y').sort_index()).groupby(['Interval','Year'])['R_eff'].sum()
           REffDataByWeek_FilterYear=REffDataByWeek.filter(like=yeartofilter)
           convertedJsonREff = REffDataByWeek_FilterYear.to_json(orient="table")
          
        elif(dataintervaltofilter=='yearly'):
           REffDataByYear=importantColumnsREFF.assign(Interval=importantColumnsREFF['Datum'].dt.strftime('%Y').sort_index()).groupby(['Interval'])['R_eff'].sum()
           REffDataByYear_FilterYear=REffDataByYear.filter(like=yeartofilter)
           convertedJsonREff = REffDataByYear_FilterYear.to_json(orient="table")
           
    else:
        return 'Error:No interval provided. Please choose a data interval.'
    
    parsedJsonREff = json.loads(convertedJsonREff)
    json.dumps(parsedJsonREff) 
    return jsonify(parsedJsonREff)


@app.route('/Vaccination', methods=['GET'])
def Vaccination():
    return "<p>Vaccination data: Vaccination data for countries grouped by week month and year</p>"

# A route to return all the json data.
@app.route('/api/Vaccination/', methods=['GET'])
def api_Vaccination_Filter():
    statename=''
    year=''
    interval=''
    #get query parameters
    query_parameters = request.args
    # assign param to filter data
    
    statename=query_parameters.get('statename')
    year=query_parameters.get('year')
    interval=query_parameters.get('interval')
    
    if 'statename' in query_parameters:
        countrynametofilter=statename
        filteredCountry=importantColumnsVacc[importantColumnsVacc['Name'].apply(lambda val:countrynametofilter in val)]
   
    else:
        return 'Error:No country name provided. Please choose a country name.'
    if 'year' in query_parameters:
        yeartofilter=year
    else:
        return 'Error:No year provided. Please choose a year.'
   
    if 'interval' in query_parameters:
        dataintervaltofilter=interval
        
        if(dataintervaltofilter=='monthly'):
             VaccDataByMonth=filteredCountry.assign(Country_Region=filteredCountry['Name'],Interval=filteredCountry['Datum'].dt.strftime('%m').sort_index(),Year=filteredCountry['Datum'].dt.strftime('%Y').sort_index()).groupby(['Country_Region','Bevölkerung','Interval','Year'])['GemeldeteImpfungenLaender'].sum()
             VaccDataByMonth_FilterYear=VaccDataByMonth.filter(like=yeartofilter)
             convertedJsonVacc = VaccDataByMonth_FilterYear.to_json(orient="table")
             
        elif(dataintervaltofilter=='weekly'):
           VaccDataByWeek=filteredCountry.assign(Country_Region=filteredCountry['Name'],Interval=filteredCountry['Datum'].dt.strftime('%W').sort_index(),Year=filteredCountry['Datum'].dt.strftime('%Y').sort_index()).groupby(['Country_Region','Bevölkerung','Interval','Year'])['GemeldeteImpfungenLaender'].sum()
           VaccDataByWeek_FilterYear=VaccDataByWeek.filter(like=yeartofilter)
           convertedJsonVacc = VaccDataByWeek_FilterYear.to_json(orient="table")
          
        elif(dataintervaltofilter=='yearly'):
           VaccDataByYear=filteredCountry.assign(Country_Region=filteredCountry['Name'],Interval=filteredCountry['Datum'].dt.strftime('%Y').sort_index()).groupby(['Country_Region','Bevölkerung','Interval'])['GemeldeteImpfungenLaender'].sum()
           VaccDataByYear_FilterYear=VaccDataByYear.filter(like=yeartofilter)
           convertedJsonVacc = VaccDataByYear_FilterYear.to_json(orient="table")
           
    else:
        return 'Error:No interval provided. Please choose a data interval.'
    
    parsedJsonVacc = json.loads(convertedJsonVacc)
    json.dumps(parsedJsonVacc) 
    return jsonify(parsedJsonVacc)

@app.route('/api/coordinates/', methods=['GET'])
def get_coordinates():
 coordinates = {'Region': ['Burgenland','Kärnten','Niederösterreich','Oberösterreich','Salzburg','Steiermark','Tirol','Vorarlberg','Wien'],
        'latitude': [47.15373,46.72171,48.10761820136797,48.02698076818874,47.809238125614016,47.359788001288564, 47.25372006444835, 47.24972136421407, 48.2082],
        'longitude':[16.26889,14.18093,15.799985593898148,13.97202152046062,13.05569498271758, 14.46895105653989,11.60217196740872,9.979392299039727,16.3738]
        }

 df = pd.DataFrame(coordinates, columns = ['Region', 'latitude','longitude'])
 df_json=df.to_json(orient="table")
 parsedJsonCoordinates= json.loads(df_json)
 json.dumps(parsedJsonCoordinates) 
 return jsonify(parsedJsonCoordinates)
 
app.run()