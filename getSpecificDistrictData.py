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
vaccinationDataUrl = pd.read_csv('https://raw.githubusercontent.com/govex/COVID-19/master/data_tables/vaccine_data/global_data/time_series_covid19_vaccine_global.csv',sep=',',header=0)
vaccinationDataUrl.info(verbose=False)
vaccinationDataUrl.info()
vaccinationDataUrl.dtypes

importantColumnsVacc=vaccinationDataUrl[["Country_Region", "Date", "Doses_admin","People_partially_vaccinated","People_fully_vaccinated","UID"]]
importantColumnsVacc['Date']=pd.to_datetime(vaccinationDataUrl['Date'],format='%Y-%m-%d')


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
             districtDataByMonth=filteredDistrict.assign(DistrictName=filteredDistrict['Bezirk'],Month=filteredDistrict['Time'].dt.strftime('%m').sort_index(),Year=filteredDistrict['Time'].dt.strftime('%Y').sort_index()).groupby(['DistrictName','Month','Year'])['AnzahlFaelle'].sum()
             districtDataByMonth_FilterYear=districtDataByMonth.filter(like=yeartofilter)
             convertedJson = districtDataByMonth_FilterYear.to_json(orient="table")
             
        elif(dataintervaltofilter=='weekly'):
           districtDataByWeek=filteredDistrict.assign(DistrictName=filteredDistrict['Bezirk'],Week=filteredDistrict['Time'].dt.strftime('%W').sort_index(),Year=filteredDistrict['Time'].dt.strftime('%Y').sort_index()).groupby(['DistrictName','Week','Year'])['AnzahlFaelle'].sum()
           districtDataByWeek_FilterYear=districtDataByWeek.filter(like=yeartofilter)
           convertedJson = districtDataByWeek_FilterYear.to_json(orient="table")
          
        elif(dataintervaltofilter=='yearly'):
           districtDataByYear=filteredDistrict.assign(DistrictName=filteredDistrict['Bezirk'],Year=filteredDistrict['Time'].dt.strftime('%Y').sort_index()).groupby(['DistrictName','Year'])['AnzahlFaelle'].sum()
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
             REffDataByMonth=importantColumnsREFF.assign(Month=importantColumnsREFF['Datum'].dt.strftime('%m').sort_index(),Year=importantColumnsREFF['Datum'].dt.strftime('%Y').sort_index()).groupby(['Month','Year'])['R_eff'].sum()
             REffDataByMonth_FilterYear=REffDataByMonth.filter(like=yeartofilter)
             convertedJsonREff = REffDataByMonth_FilterYear.to_json(orient="table")
             
        elif(dataintervaltofilter=='weekly'):
           REffDataByWeek=importantColumnsREFF.assign(Week=importantColumnsREFF['Datum'].dt.strftime('%W').sort_index(),Year=importantColumnsREFF['Datum'].dt.strftime('%Y').sort_index()).groupby(['Week','Year'])['R_eff'].sum()
           REffDataByWeek_FilterYear=REffDataByWeek.filter(like=yeartofilter)
           convertedJsonREff = REffDataByWeek_FilterYear.to_json(orient="table")
          
        elif(dataintervaltofilter=='yearly'):
           REffDataByYear=importantColumnsREFF.assign(Year=importantColumnsREFF['Datum'].dt.strftime('%Y').sort_index()).groupby(['Year'])['R_eff'].sum()
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
    countryname=''
    year=''
    interval=''
    #get query parameters
    query_parameters = request.args
    # assign param to filter data
    
    countryname=query_parameters.get('countryname')
    year=query_parameters.get('year')
    interval=query_parameters.get('interval')
    
    if 'countryname' in query_parameters:
        countrynametofilter=countryname
        filteredCountry=importantColumnsVacc[importantColumnsVacc['Country_Region'].apply(lambda val:countrynametofilter in val)]
   
    else:
        return 'Error:No country name provided. Please choose a country name.'
    if 'year' in query_parameters:
        yeartofilter=year
    else:
        return 'Error:No year provided. Please choose a year.'
   
    if 'interval' in query_parameters:
        dataintervaltofilter=interval
        
        if(dataintervaltofilter=='monthly'):
             VaccDataByMonth=filteredCountry.assign(Country_Region=filteredCountry['Country_Region'],Month=filteredCountry['Date'].dt.strftime('%m').sort_index(),Year=filteredCountry['Date'].dt.strftime('%Y').sort_index()).groupby(['Country_Region','Month','Year'])['People_fully_vaccinated'].sum()
             VaccDataByMonth_FilterYear=VaccDataByMonth.filter(like=yeartofilter)
             convertedJsonVacc = VaccDataByMonth_FilterYear.to_json(orient="table")
             
        elif(dataintervaltofilter=='weekly'):
           VaccDataByWeek=filteredCountry.assign(Country_Region=filteredCountry['Country_Region'],Week=filteredCountry['Date'].dt.strftime('%W').sort_index(),Year=filteredCountry['Date'].dt.strftime('%Y').sort_index()).groupby(['Country_Region','Week','Year'])['People_fully_vaccinated'].sum()
           VaccDataByWeek_FilterYear=VaccDataByWeek.filter(like=yeartofilter)
           convertedJsonVacc = VaccDataByWeek_FilterYear.to_json(orient="table")
          
        elif(dataintervaltofilter=='yearly'):
           VaccDataByYear=filteredCountry.assign(Country_Region=filteredCountry['Country_Region'],Year=filteredCountry['Date'].dt.strftime('%Y').sort_index()).groupby(['Year'])['People_fully_vaccinated'].sum()
           VaccDataByYear_FilterYear=VaccDataByYear.filter(like=yeartofilter)
           convertedJsonVacc = VaccDataByYear_FilterYear.to_json(orient="table")
           
    else:
        return 'Error:No interval provided. Please choose a data interval.'
    
    parsedJsonVacc = json.loads(convertedJsonVacc)
    json.dumps(parsedJsonVacc) 
    return jsonify(parsedJsonVacc)

app.run()