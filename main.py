from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    MetricType,
    RunReportRequest,
    
)
#"C://Users//anmol//Downloads//analytics-api-1581487025251-ac904d31a17e.txt"
import os
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C://Users//anmol//Downloads//analytics-api-1581487025251-ac904d31a17e.txt"
def run_sample(property_id):
    namelist = []
    viewlist = []
    """Runs the sample."""
    # TODO(developer): Replace this variable with your Google Analytics 4
    #  property ID before running the sample.
    namelist, viewlist = run_report(property_id)
    return namelist, viewlist


def run_report(property_id):
    """Runs a report of active users grouped by country."""
    client = BetaAnalyticsDataClient()

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="fullPageUrl")],
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date="2023-08-01", end_date="2023-08-15")],
    )
    response = client.run_report(request)
    namelist, viewlist = print_run_report_response(response)
    return namelist, viewlist

def print_run_report_response(response):
    namelist = []
    viewlist = []
    # """Prints results of a runReport call."""
    # print(f"{response.row_count} rows received")
    # for dimensionHeader in response.dimension_headers:
    #     print(f"Dimension header name: {dimensionHeader.name}")
    # for metricHeader in response.metric_headers:
    #     metric_type = MetricType(metricHeader.type_).name
    #     print(f"Metric header name: {metricHeader.name} ({metric_type})")
    for rowIdx, row in enumerate(response.rows):
        #print(f"\nRow {rowIdx}")
        for i, dimension_value in enumerate(row.dimension_values):
            dimension_name = response.dimension_headers[i].name
            #print(f"{dimension_name}: {dimension_value.value}")
            namelist.append(dimension_value.value)

        for i, metric_value in enumerate(row.metric_values):
            metric_name = response.metric_headers[i].name
            #print(f"{metric_name}: {metric_value.value}")
            viewlist.append(metric_value.value)
    return namelist, viewlist

DPID = "344298334"
ST34ID = "372418130"
dpnamelist, dpviewlist = run_sample(DPID)
streetnamelist, streetviewlist = run_sample(ST34ID)
df34 = pd.DataFrame()
df34['Name'] = streetnamelist
df34['Views'] = streetviewlist
df34  = df34.drop(0)
df34 = df34.reset_index()
del df34['index']
df34v2 = df34.iloc[:10]
for i in range(len(list(df34v2['Name']))):
    df34v2['Name'][i] = str(df34v2['Name'][i])[29:]
    df34v2['Views'][i] = int(df34v2['Views'][i])
dp = pd.DataFrame()
dp['Name'] = dpnamelist
dp['Views'] = dpviewlist
dp  = dp.drop(0)
dp = dp.reset_index()
del dp['index']
dpv2 = dp.iloc[:10]
for i in range(len(list(dp['Name']))):
    dp['Name'][i] = str(dp['Name'][i])[22:]
    dp['Views'][i] = int(dp['Views'][i])
fig = px.histogram(dpv2, x='Name', y='Views')
fig.update_layout(autosize=False,
    width=1500,
    height=1000,

    xaxis= go.layout.XAxis(linecolor = 'black',
                          linewidth = 1,
                          mirror = True),

    yaxis= go.layout.YAxis(linecolor = 'black',
                          linewidth = 1,
                          mirror = True),

    margin=go.layout.Margin(
        l=50,
        r=50,
        b=100,
        t=100,
        pad = 4
    ))
fig.write_image(file='dpstatsimage.png', format='png')
fig.show()
fig = px.histogram(df34v2, x='Name', y='Views')
fig.update_layout(autosize=False,
    width=1500,
    height=1000,

    xaxis= go.layout.XAxis(linecolor = 'black',
                          linewidth = 1,
                          mirror = True),

    yaxis= go.layout.YAxis(linecolor = 'black',
                          linewidth = 1,
                          mirror = True),

    margin=go.layout.Margin(
        l=50,
        r=50,
        b=100,
        t=100,
        pad = 4
    ))
fig.write_image(file='34thstreetimage.png', format='png')
fig.show()
