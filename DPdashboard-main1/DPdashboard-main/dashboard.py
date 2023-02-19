import data
import dash
from dash import Dash, html, dcc
graphData_Now = data.graphData_Now
graphData_OneYear = data.graphData_OneYear
graphData_TwoYears = data.graphData_TwoYears


app = Dash(__name__, use_pages=True)

app.layout = html.Div([
    html.H1('Welcome to DP Analytics!', style={'font-family': 'Avenir', 'textAlign': 'center'}),

    html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']} - {page['path']}", href=page["relative_path"], style={'font-family': 'Avenir'}
                )
            )
            for page in dash.page_registry.values()
        ]
    ),

    dash.page_container
])

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False, port=8051)
