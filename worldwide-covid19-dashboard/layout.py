"""
@author: Elena Stamatelou
"""
import dash_core_components as dcc
import dash_html_components as html

# Create app layout
layout = html.Div(
    [
     dcc.Store(id="aggregate_data"),
     # empty Div to trigger javascript file for graph resizing
     html.Div(id="output-clientside"),
#############################################################
# first container (radioitems, title)        
     html.Div([ 
               html.Div([html.Div([ html.H3( "Coronavirus Dashboard", style={"margin-bottom": "0px", "font-size": "calc(1em + 1vw)"},),
                                    html.H5("An Overview", style={"font-size": "calc(0.7em + 0.7vw)"}),
                                  ])    ], className="one-half column",
                                           id="title",style={  "width": "25%"}),
               dcc.Loading(html.Div([
                                     html.P("Total Population",style={ "width": "10%", "font-size": "calc(0.5em + 0.5vw)"},),
                                     html.Div(id='display_pop_stat',
                                              style={"font-size": "calc(1em + 1vw)","margin-left" : "45%","margin-top" : "-23%", 
                                                      "width": "35%"},)
                                     ],), className="pretty_container three columns",
                                          style={ "width": "21.672%", "margin-left" : "-20%"},
                            ),
               dcc.Loading(children = html.Div([
                         html.P("Population Density",style={ "width": "10%","font-size": "calc(0.5em + 0.5vw)"},),
                         html.Div(id='display_pop_density',
                                  style={"font-size": "calc(1em + 1vw)","margin-left" : "45%","margin-top" : "-23%", "width": "50%"},)
                                                 ],),className="pretty_container three columns",  
                           ),
               dcc.Loading(html.Div([
                         html.P("GDP per capita",style={ "width": "35%", "height":"20%", "font-size": "calc(0.5em + 0.5vw)"},),
                         html.Div(id='display_gdp',
                                  style={"font-size": "calc(1em + 1vw)","margin-left" : "45%","margin-top" : "-22%"},), 
                                     ],),style={ "width": "25%"},
                                         className="pretty_container three columns",
                           )
                ],),                                   
#############################################################             
# second container (map, visualization)     
     html.Div([
               html.Div([
                      html.P("Cases:",  style={"margin-left": "5%"}),
                      dcc.RadioItems(id = 'class-of-cases',
                                     options=[{'label': 'Confirmed', 'value': 'confirmed'},
                                              {'label': 'Recovered', 'value': 'recovered'},
                                              {'label': 'Deaths', 'value': 'died'}],
                                     value='confirmed',  
                                     labelStyle={'display': 'inline-block'}, 
                                     style={"height": "10%", "margin-left": "12%", "margin-top": "-4%"}),
                            # map
                      dcc.Graph(id="main_graph", 
                               style={
#                                       "height": "500px",
                                       "width": "auto", 
                                      },
                                ), 
                      ], className="pretty_container seven columns",style={"height": "100%"}),
               # visualization
               dcc.Loading(children = html.Div([ 
#              
                       html.Div([dcc.Graph(id="individual_graph", 
                                               style={"height": "100%", "width": "auto", 
                                                      "position":"relative", "z-index": "1"},
                                               config={'displayModeBar': False}),
                                     ],),
#                       html.Div([dcc.Graph(id="cases_per_day", 
#                                               style={"height": "250px", "width": "auto", 
#                                                      "position":"relative", "z-index": "2"},
#                                               config={'displayModeBar': False}),
#                                     ],),
                        
#                           ),
                     ],), className="pretty_container five columns",style={"height": "650px"}
                        ),
               ], className="row flex-display",),   
    ], id="mainContainer", style={"display": "flex", "flex-direction": "column"},
)
