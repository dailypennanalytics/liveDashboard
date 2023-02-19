import dash
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import data
graphData_Now = data.graphData_Now
graphData_OneYear = data.graphData_OneYear
graphData_TwoYears = data.graphData_TwoYears

dash.register_page(__name__,  path='/')

layout = html.Div([

    html.Div([

        html.Br(),
        html.Div(id='output_data'),
        html.Br(),

        html.Label(['Choose metric:'], style={'font-weight': 'bold', "text-align": "center", 'font-family': 'Avenir'}),
        # "label": html.Div(['Montreal'], style={'color': 'Gold', 'font-size': 20})
        dcc.Dropdown(id='dropdown',
                     options=[
                         {'label': html.Div(['Bounce Rate'], style={'font-family': 'Avenir'}), 'value': 'bounceRate'},
                         {'label': html.Div(['Average Time on Page'], style={'font-family': 'Avenir'}),
                          'value': 'avgTimeOnPage'},
                         {'label': html.Div(['Unique Page Views'], style={'font-family': 'Avenir'}),
                          'value': 'uniquePageViews'}
                     ],
                     optionHeight=35,  # height/space between dropdown options
                     value='bounceRate',  # dropdown value selected automatically when page loads
                     disabled=False,  # disable dropdown value selection
                     multi=False,  # allow multiple dropdown values to be selected
                     searchable=True,  # allow user-searching of dropdown values
                     search_value='',  # remembers the value searched in dropdown
                     placeholder='Please select...',  # gray, default text shown when no option is selected
                     clearable=True,  # allow user to removes the selected value
                     style={'width': "100%"}  # use dictionary to define CSS styles of your dropdown
                     ),
        html.Br(),
        html.Label(['Choose time range for the second graph:'],
                   style={'font-weight': 'bold', "text-align": "center", 'font-family': 'Avenir'}),
        dcc.Dropdown(id='dropdown2',
                     options=[
                         {'label': html.Div(['Same as First Graph'], style={'font-family': 'Avenir'}), 'value': 'Same'},
                         {'label': html.Div(['One Year Ago'], style={'font-family': 'Avenir'}),
                          'value': 'One Year Ago'},
                         {'label': html.Div(['Two Years Ago'], style={'font-family': 'Avenir'}),
                          'value': 'Two Years Ago'}
                     ],
                     optionHeight=35,  # height/space between dropdown options
                     value='Same',  # dropdown value selected automatically when page loads
                     disabled=False,  # disable dropdown value selection
                     multi=False,  # allow multiple dropdown values to be selected
                     searchable=True,  # allow user-searching of dropdown values
                     search_value='',  # remembers the value searched in dropdown
                     placeholder='Please select...',  # gray, default text shown when no option is selected
                     clearable=True,  # allow user to removes the selected value
                     style={'width': "100%"}  # use dictionary to define CSS styles of your dropdown
                     ),
    ]),
    html.Br(),
    html.Div([dcc.Graph(id='graph')]),
    html.Br(),
    html.Div([dcc.Graph(id='graph2')]),
])

@callback(

    Output(component_id='graph', component_property='figure'),
    [Input(component_id='dropdown', component_property='value')]
)

def build_graph(column_chosen):
    dff = graphData_Now
    # try making subplots or diff pages??
    fig = px.line(dff, x=graphData_Now.index, y=column_chosen, labels={"date": "Date",
                                                                   "bounceRate": "Bounce Rate (%)",
                                                                   "avgTimeOnPage": "Average Time on Page (s)",
                                                                   "uniquePageViews": "Unique Page Views"})
    fig.update_traces(line_color='#80231c', line_width=5)
    fig.update_layout(title={'text': '<b>DP Analytics Dashboard</b>',
                             'font': {'size': 28}, 'x': 0.5, 'xanchor': 'center'},
                      font_family="Avenir",
                      font_color="blue",
                      title_font_color="#aa1e22",
                      plot_bgcolor="#e8d3d4")
    return fig

@callback(
    Output(component_id='graph2', component_property='figure'),
    [Input(component_id='dropdown', component_property='value'),
     Input(component_id='dropdown2', component_property='value')]
)
def choose_graph(column_chosen, time_chosen):
    if time_chosen == "Same":
        return build_graph2(column_chosen, graphData_Now)
    elif time_chosen == "One Year Ago":
        return build_graph2(column_chosen, graphData_OneYear)
    elif time_chosen == "Two Years Ago":
        return build_graph2(column_chosen, graphData_TwoYears)

def build_graph2(column_chosen, time_chosen):
    dff = time_chosen
    # try making subplots or diff pages??
    fig = px.line(dff, x=time_chosen.index, y=column_chosen, labels={"date": "Date",
                                                                   "bounceRate": "Bounce Rate (%)",
                                                                   "avgTimeOnPage": "Average Time on Page (s)",
                                                                   "uniquePageViews": "Unique Page Views"})
    fig.update_traces(line_color='#80231c', line_width=5)
    fig.update_layout(title={'text': '<b>Time Range Comparison</b>',
                             'font': {'size': 20}, 'x': 0.5, 'xanchor': 'center'},
                      font_family="Avenir",
                      font_color="blue",
                      title_font_color="#aa1e22",
                      plot_bgcolor="#e8d3d4")
    return fig
