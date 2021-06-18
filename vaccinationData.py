# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 15:31:11 2021

@author: ramya
"""
import pandas as pd
from flask import request, jsonify

#vaccination data url
col_names = ["Country_Region", "Date", "Doses_admin","People_partially_vaccinated","People_fully_vaccinated","Report_Date_String","UID"]

vaccinationDataUrl = pd.read_csv('https://raw.githubusercontent.com/govex/COVID-19/master/data_tables/vaccine_data/global_data/time_series_covid19_vaccine_global.csv',sep=',',header=0)
vaccinationDataUrl.info(verbose=False)
vaccinationDataUrl.info()
vaccinationDataUrl.dtypes

dataValues=vaccinationDataUrl[["Country_Region", "Date", "Doses_admin","People_partially_vaccinated","People_fully_vaccinated","UID"]]
dataValues['Date']=pd.to_datetime(vaccinationDataUrl['Date'],format='%Y-%m-%d')

districtnametofilter='Austria'
filteredDistrict=dataValues[dataValues['Country_Region'].apply(lambda val:districtnametofilter in val)]
vaccDataByMonth=filteredDistrict.assign(Country_Region=dataValues['Country_Region'],Month=dataValues['Date'].dt.strftime('%m').sort_index(),Year=dataValues['Date'].dt.strftime('%Y').sort_index()).groupby(['Country_Region','Month','Year'])['People_fully_vaccinated'].sum()
          
#groupbyCountry=vaccinationDataUrl.groupby(['Country_Region'])
#result=groupbyCountry.apply(lambda val:'Austria' in val )
print(vaccDataByMonth)
print(filteredDistrict)
#df = pd.read_csv(filename, names=col_names)
