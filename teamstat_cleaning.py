import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import json
from pandas.io.json import json_normalize

#import raw teamstat file and reorder columns
pd.set_option('display.max_columns',40)
pd.set_option('display.max_colwidth',100)
teamstat=pd.read_csv('mochi_teamstat.csv',parse_dates=['created', 'updated'], infer_datetime_format=True)
teamstat = teamstat[['id', 'created', 'updated', 'team_id', 'journey_id','data']] 
teamstat.set_index('id',inplace=True)
print(teamstat.head())
print(teamstat.info())

#convert iso8601 format to dates
teamstat['created']=pd.to_datetime(teamstat['created']).dt.strftime('%Y-%m-%d')
teamstat['updated']=pd.to_datetime(teamstat['updated']).dt.strftime('%Y-%m-%d')
#print(teamstat[['created','updated']].head())

#convert 'data' jsonb into columns
stdf = teamstat['data'].apply(json.loads)
stdf_df=json_normalize(stdf)
teamstat_data_exploded= teamstat.join(stdf_df).drop(columns=['data'])


#deprecating WEI values
deprecate = 1e18
teamstat_data_exploded['amount_eth_lost'] = teamstat_data_exploded['amount_eth_lost']/deprecate

# Tokens, PoW score global, Journeys quick summary stats

slashed_eth_sum = teamstat_data_exploded['amount_eth_lost'].sum()

print('Total ETH Slashed = ',slashed_eth_sum)
print('Check_in_ratio = ',reporting_ratio)
print(teamstat_data_exploded[['tokens_earned','pearls_of_wisdom','slash_count']].agg('sum'))

#export cleaned teamstat file
teamstat_data_exploded.to_csv('mochi_teamstat_cleaned.csv')
