
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
import plotly.io as pio
pio.renderers.default = 'browser'

rValueUrl = pd.read_csv('https://www.ages.at/fileadmin/AGES2015/Wissen-Aktuell/COVID19/R_eff.csv',sep=";")
rValueUrl.info(verbose=False)
rValueUrl.info()
rValueUrl.dtypes


parseddatetime=pd.to_datetime(rValueUrl['Datum'],dayfirst=True)
print(parseddatetime)

# =============================================================================
# placesroundup=rValueUrl['R_eff']
# print(placesroundup)
# =============================================================================

# Create figure
fig = go.Figure()
fig.add_trace(go.Scatter(x=parseddatetime, y=rValueUrl['R_eff']))
# Add range slider
fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label="1m",
                     step="month",
                     stepmode="backward"),
                dict(count=6,
                     label="6m",
                     step="month",
                     stepmode="backward"),
                dict(count=1,
                     label="YTD",
                     step="year",
                     stepmode="todate"),
                dict(count=1,
                     label="1y",
                     step="year",
                     stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        )
    ), title='R_effective Value in  Austria'
)
fig.show()


