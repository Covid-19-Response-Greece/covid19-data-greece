"""
@author: Elena Stamatelou
"""
import dash
import numpy as np
import math
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import app_functions
# remove logging messages from flask
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


[confirmed, died, recovered, population_statistics] = app_functions.read_from_github()
#print("read_main_files",dt.datetime.now())
#app_functions.save(confirmed, died, recovered)
#print("save_main_files",dt.datetime.now())
#[confirmed, died, recovered, population_statistics] = app_functions.read_files()

#### CALLBACKS ###
def register_callbacks(app):
# map                      
 @app.callback(
    Output("main_graph", "figure"),
    [Input("main_graph", "selectedData"),
    Input('class-of-cases', 'value'),
    ],
 )
 def make_main_figure(selectedData, class_of_cases): 
    traces = []
    ### Add Countries ###
#    event_data = dict(
#                    type="scattermapbox",
#                    lon = confirmed["Long"],
#                    lat = confirmed["Lat"],
#                    text = confirmed["Country/Region"],
#                    name = confirmed["Country/Region"],
#                    hoverinfo="text + name",
#                    customdata=confirmed["Country/Region"],
#                    marker=go.scattermapbox.Marker(size=4,opacity=0.5,color = '#000000'))        
#    traces.append(event_data)      
    trace_name =  confirmed["Country/Region"].unique() 
    
    for event in trace_name:
        event_data = dict(
            type = 'scattermapbox',
            lat = confirmed.loc[confirmed["Country/Region"] == event,'Lat'],
            lon = confirmed.loc[confirmed["Country/Region"] == event,'Long'],
            text = confirmed.loc[confirmed["Country/Region"] == event,'Province/State'],
            hoverinfo='text' + event,
            customdata=confirmed.loc[confirmed["Country/Region"] == event,'Country/Region'],
            name = event,
            marker = go.scattermapbox.Marker(size=4, color = 'orange', opacity = 0.5)  
        )
        traces.append(event_data)
    
    ## Define the selected case ##
    if class_of_cases == 'confirmed':
        display = np.log(confirmed["total"]+1)
        text = "Confirmed"
    if class_of_cases == 'recovered':
        display = np.log(recovered["total"]+1)
        text = "Recovered"
    if class_of_cases == 'died':
        display = np.log(died["total"]+1)
        text = "Died"
    
    ## Heat map ##
    event_data = dict(type="scattermapbox",
                      lon = confirmed["Long"], lat = confirmed["Lat"],
                      customdata = display,
                      hoverinfo='skip', 
                      marker=go.scattermapbox.Marker(size=4,opacity=0, color = 'orange'),
                      )        
    traces.append(event_data)
    
    event_data = dict(type="densitymapbox",  
                          lon = confirmed["Long"], lat = confirmed["Lat"],
                          z = display, radius = 10,

                          hoverinfo='skip',
                          opacity=1,
                          )     
    traces.append(event_data) 
    # overlay heatmap when a rectange area is selected 
    if selectedData!=None:
        lat=[]
        lon=[]
        size=[]
        for point in selectedData['points']:
                lon.append(point['lon'])
                lat.append(point['lat'])
                size.append(point['customdata'])
        # add colored points in the selected area
        event_data = dict(type="scattermapbox",
                      lon = lon, lat = lat,
                       customdata = size,
                      hoverinfo='skip', showlegend = False,
                      marker=go.scattermapbox.Marker(size=5,opacity=1,color ='#4c8bf5' ),
                      )        
        traces.append(event_data)
        # add heatmap
        event_data = dict(type="densitymapbox", 
                          lon = lon, lat = lat,
                          z = size, radius = 20,
                          hoverinfo='skip',
                          customdata = size,
                          opacity=1,
                          )     
        traces.append(event_data)  
        
    # Create map layout
    mapbox_access_token = "pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w"
    layout = dict(
            autosize=True,
            automargin=True,
            margin=dict(l=30, r=30, b=30, t=60),
            hovermode="closest",
            plot_bgcolor="#F9F9F9",
            paper_bgcolor="#F9F9F9",
            showlegend = False,
            title="Coronavirus outbreak map: " +  text + " Cases" ,
            mapbox=dict(
                    accesstoken=mapbox_access_token,
                    style="light",
                    center=dict(lon=10, lat=20),
                    zoom = 0.5,
                    width="50%",
                    height="80%", 
                    ),
                            )
    # create the figure 
    figure = dict(data=traces, layout=layout,showscale = False)
    return figure

# Main graph -> individual graph == outbreak through time 
 @app.callback(
    [Output("individual_graph", "figure"), 
    Output('display_pop_stat', 'children'), 
    Output('display_pop_density', 'children'), 
    Output('display_gdp', 'children'),],  
    [Input("main_graph", "clickData"),    
    Input("main_graph", "selectedData"), ])   
 def make_individual_figure(main_graph_hover, selectedData):
    ctx = dash.callback_context # saves the latest action
    
    # in case of click--> display data of one country
    if ctx.triggered[0]['prop_id'] == "main_graph.clickData":
        selected_countries = []
        for point in ctx.triggered[0]['value']['points']:
            selected_countries = [str(point['customdata'])]
            title_countries =  ": "  + point['customdata']
            # related data
            confirmed_selected = app_functions.selected_countries_df(confirmed,selected_countries)
            died_selected = app_functions.selected_countries_df(died,selected_countries)
            recovered_selected = app_functions.selected_countries_df(recovered,selected_countries)
            if ((population_statistics["Country"] == point['customdata']).any() == True):
                # general info
                population = population_statistics[population_statistics["Country"] == point['customdata']]['Population'].values[0]
                population_density = population_statistics[population_statistics["Country"] == point['customdata']]['Density'].values[0]
                gdp = population_statistics[population_statistics["Country"] == point['customdata']]['GDP'].values[0]
            
            # predictions
            confirmed_predictions = app_functions.predictions(confirmed_selected) 
            confirmed_difference = app_functions.difference_prediction_actual(confirmed_selected, confirmed_predictions)
            print("confirmed difference",confirmed_difference)
            died_predictions = app_functions.predictions(died_selected) 
            died_difference = app_functions.difference_prediction_actual(died_selected, died_predictions)
            print("died difference",died_difference)           
            recovered_predictions = app_functions.predictions(recovered_selected) 
            recovered_difference = app_functions.difference_prediction_actual(recovered_selected, recovered_predictions)
            print("recovered difference",recovered_difference)
            
    # in case of area selection          
    if ctx.triggered[0]['prop_id'] == "main_graph.selectedData": 
        # display all the cases if no region is selected
        if selectedData is None:
            selected_countries = confirmed['Country/Region']
            
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            
            selected_countries = list(set(selected_countries))
           
            title_countries = ": All countries"
            # related data
            confirmed_selected = app_functions.selected_countries_df(confirmed,selected_countries)
            died_selected = app_functions.selected_countries_df(died,selected_countries)
            recovered_selected = app_functions.selected_countries_df(recovered,selected_countries)
            
            # general info
            population = 7770853
            population_density = 15
            gdp = 18381
            
            # predictions
            confirmed_predictions = app_functions.predictions(confirmed_selected) 
            confirmed_difference = app_functions.difference_prediction_actual(confirmed_selected, confirmed_predictions)
            print("confirmed difference",confirmed_difference)
            died_predictions = app_functions.predictions(died_selected) 
            died_difference = app_functions.difference_prediction_actual(died_selected, died_predictions)
            print("died difference",died_difference)
            recovered_predictions = app_functions.predictions(recovered_selected) 
            recovered_difference = app_functions.difference_prediction_actual(recovered_selected, recovered_predictions)
            print("recovered difference",recovered_difference)
            
        # display the cases in the selected rectangle 
        if selectedData is not None:     
           selected_countries = []
           population = 0
           population_density = 0
           gdp = 0
           for point in selectedData['points']:
               if type(point['customdata']) == str :
                   selected = point['customdata']
                   selected_countries.append(selected)                 
                   selected_countries = list(set(selected_countries))
                   if ((population_statistics["Country"] == point['customdata']).any() == True):
                       # general info
                       population = population + population_statistics[population_statistics["Country"] == point['customdata']]['Population'].values[0]
                       population_density = population_density + population_statistics[population_statistics["Country"] == point['customdata']]['Density'].values[0]
                       gdp = population_statistics[population_statistics["Country"] == point['customdata']]['GDP'].values[0]
           title_countries = ""
           
           # related data
           confirmed_selected = app_functions.selected_countries_df(confirmed,selected_countries)
           died_selected = app_functions.selected_countries_df(died,selected_countries)
           recovered_selected = app_functions.selected_countries_df(recovered,selected_countries)
           
           # predictions
           confirmed_predictions = app_functions.predictions(confirmed_selected) 
           confirmed_difference = app_functions.difference_prediction_actual(confirmed_selected, confirmed_predictions)
           print("confirmed difference",confirmed_difference)
           died_predictions = app_functions.predictions(died_selected) 
           died_difference = app_functions.difference_prediction_actual(died_selected, died_predictions)
           print("died difference",died_difference)           
           recovered_predictions = app_functions.predictions(recovered_selected) 
           recovered_difference = app_functions.difference_prediction_actual(recovered_selected, recovered_predictions)
           print("recovered difference",recovered_difference)
               
    # create the figure
    data=[
          go.Scatter(x=confirmed_selected['index'], y=confirmed_selected['total'], 
                     mode='lines+markers',marker_color='#F4B400',legendgroup="group1", name='confirmed'), 
          go.Scatter(x=died_selected['index'], y=died_selected['total'], 
                      mode='lines+markers', marker_color='#DB4437',legendgroup="group2", name='died'), 
          go.Scatter(x=recovered_selected['index'], y=recovered_selected['total'], 
                     mode='lines+markers',marker_color='#4285F4 ', name='recovered'), 
          go.Scatter(x=confirmed_predictions.ds, y=confirmed_predictions.yhat, 
                     mode='lines',marker_color='#6b6e6f',legendgroup="group", name= "pred-confirmed", showlegend=False), 
          go.Scatter(x=died_predictions.ds, y=died_predictions.yhat, 
                     mode='lines',marker_color='#6b6e6f', legendgroup="group", name= "pred-died",showlegend=False,), 
          go.Scatter(x=recovered_predictions.ds, y=recovered_predictions.yhat, 
                     mode='lines',marker_color='#6b6e6f', legendgroup="group", name= "pred-recovered", showlegend=False,), 
                     ]
    
    # create figure layout            
    layout_individual = go.Layout(title = "Coronavirus spread" + title_countries,
                                  xaxis_title="days",
                                  yaxis_title="cases", 
                                  legend=dict(x=0,y=1.0,bgcolor='rgba(255, 255, 255, 0)',bordercolor='rgba(255, 255, 255, 0)'),
                                  paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)', 
                                  xaxis=dict(showgrid=False))  

    figure = dict(data = data, layout = layout_individual)
    
    ## general info
    ## output population number 
    digits = int(math.log10(population))+1
    if (digits>=4) & (digits<=6):
        population = int((population/1000))
        unit = 'M'
    elif digits<=3:
        unit = 'T'
    elif digits>=7:
        population = int(population/1000000)
        unit = 'B'
    output_population_number = '{} {}'.format(population, unit)
    
    ## output population density 
    output_population_density = '{} Km2'.format(population_density)
    gdp = int(gdp)
    output_gdp = '{} $'.format(gdp)

    return figure, output_population_number,output_population_density, output_gdp  
