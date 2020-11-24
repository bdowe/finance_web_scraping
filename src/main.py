import pandas as pd
import requests as re
# import plotly.graph_objects as go

resp = re.get('https://financialmodelingprep.com/api/v3/income-statement/AAPL?limit=120&apikey=demo')
resp = resp.json()

sample_year = resp[0]
df = pd.DataFrame(list(sample_year.items()))
df.head()