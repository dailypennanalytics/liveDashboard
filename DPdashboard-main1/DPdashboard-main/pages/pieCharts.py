import dash
from dash import html, dcc, Input, Output, callback
import data
import plotly.express as px
import plotly.io as pio
#
# @callback(
#     Output(component_id='graph', component_property='figure'),
#     [Input(component_id='names', component_property='name')]
# )
dash.register_page(__name__)
topDataWeekly = data.topDataWeekly
topDataMonthly = data.topDataMonthly
topTagsWeekly = data.topTagsWeekly
topTagsMonthly = data.topTagsMonthly

@callback(
    Output(component_id='pieChart', component_property='figure'),
    Output(component_id='pieChart2', component_property='figure'),
    [Input(component_id='dropdown', component_property='value')]
)
def choose_graph(time_chosen):
    if(time_chosen == "weekly"):
        return build_graph(topDataWeekly),build_graph(topTagsWeekly)
    elif(time_chosen == "monthly"):
        return build_graph(topDataMonthly), build_graph(topTagsMonthly)


def build_graph(dataframe):
    df = dataframe
    #try making subplots or diff pages??
    fig = px.pie(data_frame=df, values= df.columns[1], names= df.columns[0],
                 color_discrete_sequence=px.colors.sequential.RdBu,
                 title=df.columns.to_list()[0])
    # fig.update_layout(title={'text': '<b>DP Analytics Dashboard</b>',
    #                          'font': {'size': 28}, 'x': 0.5, 'xanchor': 'center'},
    #                   font_family="Avenir")

    return fig

layout = html.Div([
    html.H4('Pie Chart Visualizations'),
dcc.Dropdown(id='dropdown',
                     options=[
                         {'label': html.Div(['Last Week'], style={'font-family': 'Avenir'}),
                          'value': 'weekly'},
                         {'label': html.Div(['Last Month'], style={'font-family': 'Avenir'}),
                          'value': 'monthly'},
                     ],
                     optionHeight=35,  # height/space between dropdown options
                     value='weekly',  # dropdown value selected automatically when page loads
                     disabled=False,  # disable dropdown value selection
                     multi=False,  # allow multiple dropdown values to be selected
                     searchable=True,  # allow user-searching of dropdown values
                     search_value='',  # remembers the value searched in dropdown
                     placeholder='Please select...',  # gray, default text shown when no option is selected
                     clearable=True,  # allow user to removes the selected value
                     style={'width': "100%"}  # use dictionary to define CSS styles of your dropdown
                     ),
    html.Div([dcc.Graph(id = 'pieChart')]),
    html.Div([dcc.Graph(id = 'pieChart2')])
])
