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
finallist=[]
# read loacl csv file for coordinates
df = pd.read_csv (r'AustrianCityCoordinates-WarnLevel.csv')   

# =============================================================================

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/api/warnLevelRegion/', methods=['GET'])

def api_warningLevelRegion():

 date=''
 query_parameters = request.args
 date=query_parameters.get('date')
 if 'date' in query_parameters:
  datetofilter=date
 else:
  return 'Error:No date provided. Please choose a date.'
  
 for warnLevelObjects in entiredata:
   warnLevelObjects['Stand']=warnLevelObjects['Stand'][0:10]
   filteredData = [d for d in entiredata if d['Stand'] == datetofilter]

 for warnLevelData in filteredData:
  for region in warnLevelData['Warnstufen']:
   if region['Name'] is not None:
    df1=df[df['cityName']==region['Name']]
    if not df1.empty:
     toJson=df1.to_json(orient="table")
     convertedJson=json.loads(toJson)
     json.dumps(convertedJson)
     finallist.append(convertedJson)
   #print(convertedJson)
 return jsonify(finallist)
app.run()
