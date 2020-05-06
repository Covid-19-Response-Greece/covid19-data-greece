"""
@author: Elena Stamatelou
"""
import pandas as pd
# pip install fbprophet
from fbprophet import Prophet
import logging
logging.getLogger('fbprophet').setLevel(logging.WARNING) # remove warning messages in prophet
#import subprocess
#from pathlib import Path    
import datetime as dt
# Define functions
#!pip install PyGithub

# generate GitHub API token

def read_from_github():
    # Input: no 
    # Outputs: the main datasets ready to use
    # Function: reads the files from GitHub
    # Online Github path
    from github.MainClass import Github
    token = 'f1d4c930800cb3e782c1b61b86101c97deefc4c7'
  	# connected to GitHub using my credentials
    g = Github(token)
    # load the repo
    repo = g.get_repo("CSSEGISandData/COVID-19")
    file_list = repo.get_contents("csse_covid_19_data/csse_covid_19_time_series")
    github_dir_path = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/'
    
    file_path_confirmed_US = github_dir_path  + str(file_list[-5]).split('/')[-1].split(".")[0]+ '.csv'
    confirmed_US = pd.read_csv(file_path_confirmed_US, error_bad_lines=False)
    confirmed_US = confirmed_US.drop(['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Combined_Key'], axis=1)
    confirmed_US=confirmed_US.rename(columns = {'Province_State':'Province/State', 
                                          'Country_Region':'Country/Region',
                                          'Long_':'Long'})
    confirmed_info = confirmed_US.groupby(["Province/State"])['Lat','Long','Country/Region'].agg({
            'Lat'      :lambda x: x.mean(),
            'Long'     :lambda x: x.mean(),
            'Country/Region':lambda x: x.unique()
            })
    cases = confirmed_US.drop(columns=['Country/Region', 'Lat', 'Long']).set_index('Province/State')
    cases = cases.groupby(["Province/State"]).sum()
    confirmed_US = confirmed_info.merge(cases, left_index=True, right_index=True).reset_index()    
    confirmed_US = confirmed_US[confirmed_US['Long'].isna() == False]
    confirmed_US = confirmed_US[confirmed_US['Lat'].isna() == False]
    confirmed_US = confirmed_US[confirmed_US['Long'] != 0]
    confirmed_US = confirmed_US[confirmed_US['Lat'] != 0]
    
    file_path_confirmed = github_dir_path  + str(file_list[-4]).split('/')[-1].split(".")[0]+ '.csv'
    confirmed = pd.read_csv(file_path_confirmed, error_bad_lines=False)
    
    confirmed = pd.concat([confirmed_US,confirmed])
     
    file_path_died_US = github_dir_path  + str(file_list[-3]).split('/')[-1].split(".")[0]+ '.csv'
    died_US = pd.read_csv(file_path_died_US, error_bad_lines=False)
    
    died_US = died_US.drop(['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Combined_Key', 'Population'], axis=1)
    died_US=died_US.rename(columns = {'Province_State':'Province/State', 
                                          'Country_Region':'Country/Region',
                                          'Long_':'Long'})
    died_info = died_US.groupby(["Province/State"])['Lat','Long','Country/Region'].agg({
            'Lat'      :lambda x: x.mean(),
            'Long'     :lambda x: x.mean(),
            'Country/Region':lambda x: x.unique()
            })
    deaths = died_US.drop(columns=['Country/Region', 'Lat', 'Long']).set_index('Province/State')
    deaths = deaths.groupby(["Province/State"]).sum()
    died_US = died_info.merge(deaths, left_index=True, right_index=True).reset_index()    
    died_US = died_US[died_US['Long'].isna() == False]
    died_US = died_US[died_US['Lat'].isna() == False]
    died_US = died_US[died_US['Long'] != 0]
    died_US = died_US[died_US['Lat'] != 0]
    
#    
    file_path_died = github_dir_path  + str(file_list[-2]).split('/')[-1].split(".")[0]+ '.csv'
    died = pd.read_csv(file_path_died, error_bad_lines=False)
    
    
    died = pd.concat([died_US,died])

    file_path_recovered = github_dir_path  + str(file_list[-1]).split('/')[-1].split(".")[0]+ '.csv'
    recovered = pd.read_csv(file_path_recovered, error_bad_lines=False)

    # preprocessing to add total column
    confirmed = preprocessing(confirmed)
    died = preprocessing(died)
    recovered = preprocessing(recovered)
    
    # demographics
    population_statistics = pd.read_csv("population_statistics.csv")

    return confirmed, died, recovered, population_statistics

def save(confirmed, died, recovered):
    # save the files
    a = dt.datetime.now()
    confirmed.to_csv("time_series_19-covid-Confirmed.csv",index=False)
    died.to_csv("time_series_19-covid-Deaths.csv",index=False)
    recovered.to_csv("time_series_19-covid-Recovered.csv",index=False)
    print("save_main_files",dt.datetime.now()-a)
    return

def read_files():
    # Input: no 
    # Outputs: the main datasets ready to use
    # Function: reads the files 
    ## Confirmed ##  
    confirmed = pd.read_csv("time_series_19-covid-confirmed.csv")
    confirmed = preprocessing(confirmed)
    ## Died ##
    died = pd.read_csv("time_series_19-covid-Deaths.csv")
    died = preprocessing(died)
    ## Recovered ##
    recovered = pd.read_csv("time_series_19-covid-Recovered.csv")
    recovered = preprocessing(recovered)
   
    population_statistics = pd.read_csv("population_statistics.csv")
    return confirmed, died, recovered, population_statistics

def preprocessing(df):
    # Inputs: Inputs datasets of confirmed, died,and recovered cases
    # Ouputs: Preprocessed datasets
    # Function: Creates an extra column with the total number of cases per country/row
    number = df.drop(['Province/State', 'Country/Region', 'Lat' ,'Long'], axis=1)
    number.loc[:,'total'] = number.sum(axis=1)
    df = pd.concat([df,number.total],axis = 1)
    return df

def selected_countries_df(df, selected_countries):
    # Inputs: All the dataset and the selected countries (an area is selected in the map)
    # Outputs:The data of the selected countries 
    # Function: Filters the dataset
    a = dt.datetime.now()
    selected_countries_data_all = pd.DataFrame()
    for i in range(len(selected_countries)):
                  selected_data = df[df['Country/Region'] == selected_countries[i]]
                  selected_countries_data_all = pd.concat([selected_countries_data_all, selected_data])
                 
    selected_countries_data_all = selected_countries_data_all.drop(['Province/State', 'Country/Region', 'Lat' ,'Long', 'total'], axis=1).reset_index(drop=True)
    selected_countries_data_all.loc['total',:]= selected_countries_data_all.sum(axis=0)
    selected_countries_data_all = selected_countries_data_all.T
    selected_countries_data_all = selected_countries_data_all.reset_index()
    selected_countries_data_all['index'] = pd.to_datetime(selected_countries_data_all['index'])
    print("Filters the dataset",dt.datetime.now()-a)

    return selected_countries_data_all

def predictions(df):
    # Input: time series dataframe with two columns (date, values)
    # Output: predictions
    # Function: applies prophet forecast method 
    a = dt.datetime.now()
    predictions = df[['index','total']]
    predictions.columns = ['ds', 'y']
#    predictions = predictions.iloc[:-1,:]
    # create the model
#    m = Prophet(yearly_seasonality=True)
    # add monthly seasonality
#    m.add_seasonality(name="monthly",period=30.5,fourier_order=5)
    m = Prophet(changepoint_prior_scale=0.2, changepoint_range=0.98,uncertainty_samples=0, yearly_seasonality=False, seasonality_mode='additive')
    m.add_seasonality(name="monthly",period=30.5,fourier_order=5)
    # predict
    m.fit(predictions)
    future = m.make_future_dataframe(periods=5)
    fcst = m.predict(future)
    fcst['yhat'] = fcst['yhat'].astype(int)
    print("Predict",dt.datetime.now()-a)
    return fcst
    
def difference_prediction_actual(df, fcst):
    actual = df[['index','total']]
    actual.columns = ['ds', 'y']
    forecasted = fcst[['ds','yhat']]
    actual_and_forecasted = pd.merge(left=actual, right=forecasted, left_on='ds', right_on='ds')
    actual_and_forecasted['difference'] = abs((actual_and_forecasted['y'] - actual_and_forecasted['yhat'])/actual_and_forecasted['y'])
    mape = actual_and_forecasted['difference'].sum() / len(actual_and_forecasted)
    return mape