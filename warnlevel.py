import numpy as np
import pandas as pd
import flask 
from flask import request, jsonify
import json
from collections import Counter
import geocoder
import requests

#read json file for warn level
response = requests.get("https://corona-ampel.gv.at/sites/corona-ampel.gv.at/files/assets/Warnstufen_Corona_Ampel_aktuell.json") 
entiredata=json.loads(response.text)
# read loacl csv file for coordinates
df = pd.read_csv (r'AustrianCitiesWithLatLong.csv')  


# for entry in df.iterrows():
#     print(entry[1]['cityName'])
#     print("Separation")
 

#=============================================================================
finallist=[]
locationLongLatDict ={}
#print(type(entiredata))
for warnLevelObjects in entiredata:
 warnLevelObjects['Stand']=warnLevelObjects['Stand'][0:10]
 if warnLevelObjects['Stand']== '2021-06-10':
        #print(warnLevelObjects)
  for region in warnLevelObjects['Warnstufen']:
   if region['Name'] is not None:
    for entry in df.iterrows():
         if entry[1]['name'] == region['Name']:
          locationLongLatDict['cityName'] =region['Name']
          locationLongLatDict['latitude'] =entry[1]['lang']
          locationLongLatDict['longitude'] =entry[1]['long']
          locationLongLatDict['Warnstufe'] =region['Warnstufe']
          print(locationLongLatDict)
          finallist.append(locationLongLatDict)
          print(finallist)
# =============================================================================
 app = flask.Flask(__name__)
 app.config["DEBUG"] = True
# # 
 @app.route('/api/warnLevelRegion/', methods=['GET'])

 def api_warningLevelRegion():
  date=''
  query_parameters = request.args
  date=query_parameters.get('date')
  if 'date' in query_parameters:
   datetofilter=date
  else:
   return 'Error:No date provided. Please choose a date.'
  finallist=[]
  locationLongLatDict ={}
  for warnLevelObjects in entiredata:
   warnLevelObjects['Stand']=warnLevelObjects['Stand'][0:10]
   if warnLevelObjects['Stand']== datetofilter:
    for region in warnLevelObjects['Warnstufen']:
     if region['Name'] is not None:
      for entry in df.iterrows():
         if entry[1]['name'] == region['Name']:
          locationLongLatDict['cityName'] =region['Name']
          locationLongLatDict['latitude'] =entry[1]['lang']
          locationLongLatDict['longitude'] =entry[1]['long']
          locationLongLatDict['Warnstufe'] =region['Warnstufe']
          print(locationLongLatDict)
          finallist.append(locationLongLatDict)
          response = jsonify(finallist)
  return response
app.run()
