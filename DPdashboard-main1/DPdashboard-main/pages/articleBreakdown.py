import dash
from dash import html, dcc, Input, Output, callback
import data
import plotly.express as px


dp_past_week = data.dp_past_week
dp_past_month = data.dp_past_month
dp_all_time = data.dp_all_time

popularArticle_week = data.popularArticle_week
popularArticle_month = data.popularArticle_month
popularArticles = data.popularArticles
dash.register_page(__name__)

layout = html.Div([

    html.Br(),

    html.Label(['Choose time:'], style={'font-weight': 'bold', "text-align": "center", 'font-family': 'Avenir'}),
    dcc.Dropdown(id='dropdown',
                     options=[
                         {'label': html.Div(['Last Week'], style={'font-family': 'Avenir'}),
                          'value': 'dp_past_week'},
                         {'label': html.Div(['Last Month'], style={'font-family': 'Avenir'}),
                          'value': 'dp_past_month'},
                         {'label': html.Div(['All Time'], style={'font-family': 'Avenir'}),
                          'value': 'dp_all_time'}
                     ],
                     optionHeight=35,  # height/space between dropdown options
                     value='dp_past_week',  # dropdown value selected automatically when page loads
                     disabled=False,  # disable dropdown value selection
                     multi=False,  # allow multiple dropdown values to be selected
                     searchable=True,  # allow user-searching of dropdown values
                     search_value='',  # remembers the value searched in dropdown
                     placeholder='Please select...',  # gray, default text shown when no option is selected
                     clearable=True,  # allow user to removes the selected value
                     style={'width': "100%"}  # use dictionary to define CSS styles of your dropdown
                     ),

    html.Div([
        dcc.Graph(id='scatter')
    ]),

    html.Div([
        html.H4(id = "label"),
        html.Div(id = "table")
        ]),
])

@callback(
    Output(component_id='scatter', component_property='figure'),
    [Input(component_id='dropdown', component_property='value')]
)
def generate_scatter(time_chosen):
    if(time_chosen == 'dp_past_week'):
        df = dp_past_week.iloc[:, [0, 1, 3]]
    elif(time_chosen == 'dp_past_month'):
        df = dp_past_month.iloc[:, [0,1,3]]
    else:
        df = dp_all_time.iloc[:, [0,1,3]]

    fig = px.scatter(df, x= 'avgTime(min)', y= 'pageViews', color_discrete_sequence=px.colors.sequential.RdBu,
                     hover_data =['title'])
    return fig

@callback(
    Output(component_id='label',component_property='children'),
    Output(component_id='table', component_property='children'),
    [Input(component_id='dropdown', component_property='value')]
)
def generate_table(time_chosen):
    if (time_chosen == 'dp_past_week'):
        name = "Popular Articles by Week"
        dataframe = popularArticle_week
    elif (time_chosen == 'dp_past_month'):
        name = "Popular Articles by Month"
        dataframe = popularArticle_month
    else:
        name = "Popular Articles All Time"
        dataframe = popularArticles

    return name,\
        html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
            , style={'font-family': 'Avenir'}
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ], style={'font-family':'Avenir'}) for i in range(0,len(dataframe))
        ])
    ])
