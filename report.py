import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import json
from pandas.io.json import json_normalize

#import raw report file 
pd.set_option('display.max_columns',40)
pd.set_option('display.max_colwidth',100)
report=pd.read_csv('mochi_report.csv',parse_dates=['created','updated','checkin_date'], infer_datetime_format=True)
report = userstat[['id', 'created', 'updated', 'user_id', 'community_id','data']] 
report.set_index('id',inplace = True)
print(report.head())
print(report.info())
#print(userstat['data'].head())

#convert datetime data
report['created']=pd.to_datetime(report['created']).dt.strftime('%Y-%m-%d')
report['updated']=pd.to_datetime(report['updated']).dt.strftime('%Y-%m-%d')
report['checkin_date']=pd.to_datetime(report['checkin_date']).dt.strftime('%Y-%m-%d')

#convert 'details' jsonb into columns
reportdf = report['details'].apply(json.loads)
reportdf_df=json_normalize(reportdf)
report_data_exploded = report.join(reportdf_df).drop(columns=['details'])
print(report_data_exploded.head())

#create columns for answers and prompts
df_answers = pd.DataFrame([pd.Series(x) for x in report_data_exploded.answers])
df_answers.columns = ['answers_{}'.format(x+1) for x in df_answers.columns]
report_data_exploded = report_data_exploded.join(df_answers)

df_prompts = pd.DataFrame([pd.Series(x) for x in report_data_exploded.prompts])
df_prompts.columns = ['prompts_{}'.format(x+1) for x in df_prompts.columns]
report_data_exploded = report_data_exploded.join(df_prompts)
report_data_exploded = report_data_exploded.drop(columns=['answers', 'prompts'])

#quick summary stats
tokens_awarded = report_data_exploded['token_award_amount'].sum()
#slashed_eth = report_data_exploded['player_slash_amount'].sum()+report_data_exploded['team_slash_amount'].sum()
print('Reported Tokens awarded = ', tokens_awarded)
#print('Reported ETH Slash Total = ', slashed_eth)
print('Total Unique Journeys = ', report_data_exploded['journey_id'].nunique())

#export cleaned report file
report_data_exploded.to_csv('mochi_report_cleaned.csv')
