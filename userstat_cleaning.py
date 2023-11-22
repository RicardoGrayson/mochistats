import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import json
from pandas.io.json import json_normalize

#import raw userstat file and reorder columns
pd.set_option('display.max_columns',40)
pd.set_option('display.max_colwidth',100)
userstat=pd.read_csv('mochi_userstat.csv',sep='\t',parse_dates=['created','updated'], infer_datetime_format=True)
userstat = userstat[['id', 'created', 'updated', 'user_id', 'community_id','data']] 
userstat.set_index('id',inplace=True)
print(userstat.head())
print(userstat.info())

#convert iso8601 format to dates
userstat['created']=pd.to_datetime(userstat['created']).dt.strftime('%Y-%m-%d')
userstat['updated']=pd.to_datetime(userstat['updated']).dt.strftime('%Y-%m-%d')
#print(userstat[['created','updated']].head())

#convert 'data' jsonb into columns
stdf = userstat['data'].apply(json.loads)
stdf_df=json_normalize(stdf)
userstat_data_exploded= userstat.join(stdf_df).drop(columns=['data'])

#create columns for journey tokens and tokens for rank calcs
df_journeytokens = pd.DataFrame([pd.Series(x) for x in userstat_data_exploded.journey_tokens])
df_journeytokens.columns = ['journey_tokens_{}'.format(x+1) for x in df_journeytokens.columns]
userstat_data_exploded = userstat_data_exploded.join(df_journeytokens)

df_rankcalcs = pd.DataFrame([pd.Series(x) for x in userstat_data_exploded.journey_tokens_for_rank_calcs])
df_rankcalcs.columns = ['journey_tokens_for_rank_calcs_{}'.format(x+1) for x in df_rankcalcs.columns]
userstat_data_exploded = userstat_data_exploded.join(df_rankcalcs)

#remove redundant columns
userstat_data_exploded = userstat_data_exploded.drop(columns=['journey_tokens','journey_tokens_for_rank_calcs','amounted_bonded'])
#print(userstat_data_exploded.head(20))

#deprecating WEI values
deprecate = 1e18
userstat_data_exploded['amount_eth_lost'] = userstat_data_exploded['amount_eth_lost']/deprecate
userstat_data_exploded['amount_withdrawn'] = userstat_data_exploded['amount_withdrawn']/deprecate
userstat_data_exploded['amount_self_bonded'] = userstat_data_exploded['amount_self_bonded']/deprecate
userstat_data_exploded['amount_total_bonded'] = userstat_data_exploded['amount_total_bonded']/deprecate

# Tokens, PoW score global, Journeys quick summary stats
journey_tokens_for_rank_calcs_sum = userstat_data_exploded.iloc[:,31:].sum().sum()
journey_tokens_sum = userstat_data_exploded.iloc[:,17:31].sum().sum()
slashed_eth_sum = userstat_data_exploded['amount_eth_lost'].sum()
eth_bonded_sum = userstat_data_exploded['amount_total_bonded'].sum()
filtered_reporting_ratio = userstat_data_exploded[userstat_data_exploded['check_in_ratio']>0]
reporting_ratio = filtered_reporting_ratio['check_in_ratio'].mean()


print('Journey Tokens for Rank Calcs = ',journey_tokens_for_rank_calcs_sum)
print('Journey Tokens = ',journey_tokens_sum)
print('Total ETH Bonded = ', eth_bonded_sum)
print('Total ETH Slashed = ',slashed_eth_sum)
print('Check_in_ratio = ',reporting_ratio)
print(userstat_data_exploded[['tokens_earned','pearls_of_wisdom','completed_journey_count']].agg('sum'))

#export cleaned userstat file
userstat_data_exploded.to_csv('mochi_userstat_cleaned.csv')
