# Imports

import jwt
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
import requests
import math
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import kaleido

pd.set_option('display.max_columns', 100000)

# pd.set_option('display.max_rows', 100000)
pd.set_option('display.width', 100000)
pd.set_option('display.max_colwidth', None)

# API keys
# get keys from https://dpn.ceo.getsnworks.com/ceo/developer
dp_pk = 'pk_h7GGLu5SHOMa1gTJpbCGZgWi1H4iX6'
dp_secret = 'sk_P62YquYTjiuGLCcTPjoZckjqFk7QBA'
dp_encoded_jwt = jwt.encode({'pk': dp_pk}, dp_secret, algorithm='HS256')

st_pk = 'pk_cxprrNDEjFDHjZOF1HRxkgnBUOnUiC'
st_secret = 'sk_085yhKYRPUsQVieJ9ss6ovRfljRMn3'
st_encoded_jwt = jwt.encode({'pk': st_pk}, st_secret, algorithm='HS256')


# Function to get number of items for a given property
def getItems(endpoint, jwt):
    per_page = 1
    page = 1
    endpoint = endpoint.format(page, per_page)
    headers = {"Authorization": "Bearer " + jwt}
    response = requests.get(url=endpoint, headers=headers)
    totalItems = response.json()['total_items']
    return totalItems


# Item count endpoints
dp_count_endpoint = """https://dpn.ceo.getsnworks.com/v3/content?dir=desc&grid=false&
              keywords&order=published_at&page={}&per_page={}&status=published&
              type=article&workflow"""
st_count_endpoint = """https://dpn-34s.ceo.getsnworks.com/v3/content?dir=desc&grid=false&
              keywords&order=published_at&page={}&per_page={}&status=published&
              type=article&workflow"""

# Get item counts
dp_items = getItems(dp_count_endpoint, dp_encoded_jwt)
# Endpoints for article scrape
dp_article_endpoint = """https://dpn.ceo.getsnworks.com/v3/content?dir=desc&grid=false&
                keywords&order=published_at&page={}&per_page={}&status=published&
                type=article&workflow"""

st_article_endpoint = """https://dpn-34s.ceo.getsnworks.com/v3/content?dir=desc&grid=false&
                keywords&order=published_at&page={}&per_page={}&status=published&
                type=article&workflow"""


# Function to get articles for a given property
def getArticles(article_endpoint, jwt, numItems, cutoff_date='2022-01-01', source='unknown'):
    perPage = 100  # Pagesize per request
    cutoff_date = pd.to_datetime(cutoff_date)  # '2021-11-1' end of dp dump

    # Empty lists for results
    ids = []
    titles = []
    title_url = []
    content = []
    slugs = []
    contentType = []
    published_dates = []
    srns = []
    authorIds = []

    headers = {"Authorization": "Bearer " + jwt}

    # Scrape loop. Progress bar just indicates max duration
    for i in tqdm(range(math.ceil(numItems / perPage))):

        # Parameters for request
        endpoint = article_endpoint.format(i + 1, perPage)

        # Request send
        res = requests.get(url=endpoint, headers=headers).json()
        # Parse response
        for item in res['items']:
            ids.append(item['id'])
            titles.append(item['title'])
            title_url.append(
                item['published_at'][0:4] + "/" +
                item['published_at'][5:7] + "/" +
                item['title_url'])
            slugs.append(item['slug'])
            srns.append(item['srn'].split(":")[3])
            try:
                authorIds.append(item['user_id'])
            except:
                authorIds.append(None)
            contentType.append(item['type'])
            soup = BeautifulSoup(item['content'], features="html.parser")
            for script in soup(['script', 'style']):
                script.decompose()
            content.append(soup.get_text().replace(u'\xa0', u' ').replace("\n", " "))
            ts = pd.to_datetime(item['published_at'])
            published_dates.append(ts)
        # Break if cutoff date reached
        if ts < cutoff_date:
            break

    articles_df = pd.DataFrame(data={'id': ids,
                                     'type': contentType,
                                     'srn': srns,
                                     'title': titles,
                                     'slug': slugs,
                                     'content': content,
                                     'published_date': published_dates,
                                     "title_url": title_url})
    articles_df = articles_df[articles_df['type'] == 'article']
    articles_df.reset_index(inplace=True, drop=True)
    articles_df['source'] = source

    # for i in articles_df['content'].values:
    #    print(i)
    return articles_df


# Article google analytics pull
# Imports
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
import httplib2

# Get new DP articles
dp_articles = getArticles(dp_article_endpoint,
                          dp_encoded_jwt,
                          dp_items,
                          '2022-05-01',
                          'dp')
articles_df = dp_articles
urls = ["/article/" + title_url for title_url in articles_df['title_url']]
articles_df['url'] = ["/article/" + title_url for title_url in articles_df['title_url']]

wdcnt = list(len(str(article).split(' ')) for article in articles_df['content'])  # finds wordcount
articles_df['wordcount'] = wdcnt
# Get per page statistics
# Create service credentials
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    '.analytics-api-1581487025251-ac904d31a17e',
    ['https://www.googleapis.com/auth/analytics.readonly'])

# Create a service object
http = credentials.authorize(httplib2.Http())
service = build('analytics', 'v4', http=http,
                discoveryServiceUrl=('https://analyticsreporting.googleapis.com/$discovery/rest'))


def getViews(pages, viewId, startDate='2006-01-01', endDate='today'):
    response = service.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': viewId,  # Add View ID from GA
                    'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
                    'metrics': [{'expression': 'ga:uniquePageviews'},
                                {'expression': 'ga:pageviews'},
                                {'expression': 'ga:avgTimeOnPage'}],  # If you want to add metrics, add it here!
                    'dimensions': [{"name": "ga:pagePath"}],  # Get Pages
                    "dimensionFilterClauses": [{
                        'filters': {
                            "dimensionName": "ga:pagePath",
                            "operator": "IN_LIST",
                            "expressions": pages
                        }
                    }],
                    'pageSize': 100000
                }]
        }
    ).execute()

    # create two empty lists that will hold our dimentions and sessions data
    data = []

    # Extract Data
    for report in response.get('reports', []):

        rows = report.get('data', {}).get('rows', [])

        for row in rows:
            url = row['dimensions'][0]
            uniquePageViews, pageViews, timeOnPage = row['metrics'][0]['values']  # ?? add new metric here
            data.append((url, uniquePageViews, pageViews, timeOnPage))  # append data here

    return pd.DataFrame(data, columns=['url', 'uniquePageViews', 'pageViews', 'avgTimeOnPage'])  # add new metric here


# returns dataframe of Article Url, Total Users, Users subdivided by Traffic Source/Medium
def getPivot(pages, viewId, startDate='2006-01-01', endDate='today', pivotTag="ga:sourceMedium"):
    response = service.reports().batchGet \
            (
            body={
                "reportRequests":
                    [
                        {
                            "viewId": viewId,
                            'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
                            "metrics": [{'expression': 'ga:pageviews'}],
                            "orderBys": [
                                {
                                    "orderType": "VALUE",
                                    "sortOrder": "DESCENDING",
                                    "fieldName": "ga:pageviews"
                                }],
                            "dimensions": [{"name": "ga:pagePath"}],
                            "dimensionFilterClauses": [{
                                'filters': {
                                    "dimensionName": "ga:pagePath",
                                    "operator": "IN_LIST",
                                    "expressions": pages
                                }
                            }],
                            "pivots":
                                [{"dimensions":
                                      [{"name": pivotTag}],
                                  # ga:dimension3(tags) ga:dimension2(site section) ga:sourceMedium (add dimension here)
                                  "startGroup": 0,
                                  "maxGroupCount": 500,
                                  "metrics":
                                      [{'expression': 'ga:pageviews'}],
                                  }],
                            'pageSize': 100000
                        }
                    ]
            }
        ).execute()

    # formatting data
    data = []
    header = ['url', 'pageViews']
    pivotHeader = []
    for report in response.get('reports', []):
        rows = report.get('data', {}).get('rows', [])

        cols = report.get('columnHeader', {}.get('rows', []))['metricHeader']['pivotHeaders'][0]['pivotHeaderEntries']

        for col in cols:
            pivotHeader.append(col['dimensionValues'][0])
        header = header + pivotHeader

        for row in rows:
            titles = row['dimensions'][0]
            pageViews = int(row['metrics'][0]['values'][0])
            pivotValues = row['metrics'][0]['pivotValueRegions'][0]['values']
            pivotValues = [int(x) for x in pivotValues]
            data.append([titles, pageViews] + pivotValues)

    return pd.DataFrame(data, columns=header), pivotHeader

    # incorporate dates


import datetime as DT

today = DT.date.today()
week_ago = today - DT.timedelta(days=7)
week_ago_str = str(week_ago)
month_ago = today - DT.timedelta(days=31)
month_ago_str = str(month_ago)


def get_duration_engagement(code, pivotTag, time_str='2006-01-01'):
    engagementDP = getViews(urls, code, time_str)
    pivotDP, pivotHeader = getPivot(urls, code, time_str, "today", pivotTag)
    pivotDP.drop(columns='pageViews', inplace=True)  # remove duplicate values (we get pageViews from getViews)
    engagementDP['pageViews'] = pd.to_numeric(
        engagementDP['pageViews'])  # create column for page views and put in data
    engagementDP['avgTime(min)'] = pd.to_numeric(engagementDP['avgTimeOnPage']) / 60
    engagementDP = engagementDP.merge(
        articles_df[['url', 'title', 'published_date', 'wordcount']], on='url')
    engagementDP.reset_index(drop=True)
    engagementDP = engagementDP.merge(pivotDP[pivotDP.columns.to_list()], on='url')

    headers = ['title', 'pageViews', 'wordcount', 'avgTime(min)', 'published_date'] + pivotHeader
    engagementDP = engagementDP.sort_values(
        by='pageViews', ascending=False)[headers].head(100)
    return engagementDP, pivotHeader


def mostPopularPosts(time='2006-01-01'):
    # test getSourceMedium
    test = get_duration_engagement('22050415', 'ga:sourceMedium', time)[0]
    test['avgTime(min)'] = test['avgTime(min)'].round(2)
    return test.sort_values(by=['pageViews'], ascending=False)[:5]  # Top 5 Most Popular Articles


popularArticle_week, popularArticle_month, popularArticles = mostPopularPosts(week_ago_str), mostPopularPosts(
    month_ago_str), mostPopularPosts()


def topTrafficSources(time=month_ago_str):
    # test getSourceMedium
    test = getPivot(urls, '22050415', startDate=time)[0]
    df = test.sum(axis=0)[2:].reset_index()
    df.columns = ["Source/Medium", "Total Traffic"]
    return df.head(5)


def topTags(time=month_ago_str):
    test = getPivot(urls, '22050415', startDate=time, pivotTag='ga:dimension3')
    df = test[0].sum(axis=0).reset_index()
    df.columns = ["Top Tags", "Total Traffic"]
    df['Top Tags'] = df['Top Tags'].apply(lambda x: x.split(','))
    df = df.explode('Top Tags')
    df = df.groupby('Top Tags', as_index=False)['Total Traffic'].sum()
    return df


# Overall Statistics
def getOverallStats(viewId, startDate='2022-01-01', endDate='today'):
    response = service.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': viewId,  # Add View ID from GA
                    'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
                    'metrics': [{'expression': 'ga:uniquePageviews'},
                                {'expression': 'ga:pageViews'},
                                {'expression': 'ga:bounceRate'},
                                {'expression': 'ga:avgTimeOnPage'}],
                }]
        }
    ).execute()

    # Extract Data
    for report in response.get('reports', []):
        results = report.get('data', {}).get('rows', [])[0]['metrics'][0]['values']
        uniquePageViews, pageViews, bounceRate, avgPageTime = results
        return uniquePageViews, pageViews, bounceRate, avgPageTime


def getRange(viewId, daySpan, spans):
    # daySpan: Number of days to aggregate over (eg, 7 for week)
    # of spans to calculate statistics for (eg, 4 for a month)
    stats = {}
    for i in range(spans):
        start = today - DT.timedelta(days=daySpan * (i + 1))
        end = today - DT.timedelta(days=daySpan * (i))
        stats[str(end)] = getOverallStats(viewId,
                                          startDate=str(start),
                                          endDate=str(end))
    dpRange = pd.DataFrame(stats)
    dpRangeT = dpRange.T
    dpRangeT.columns = ['uniquePageViews', 'pageViews', 'bounceRate', 'avgTimeOnPage']
    return dpRangeT


def getRangeOneYearAgo(viewId, daySpan, spans):
    # daySpan: Number of days to aggregate over (eg, 7 for week)
    # of spans to calculate statistics for (eg, 4 for a month)
    current_year = DT.date.today().year
    current_month = DT.date.today().month
    current_day = DT.date.today().day
    last_year = current_year - 1
    a = DT.date(current_year, current_month, current_day)  # current date
    b = DT.date(last_year, current_month, current_day)  # same date, but last year
    delta = a - b
    stats = {}
    for i in range(spans):
        start = b - DT.timedelta(days=daySpan * (i + 1))
        end = b - DT.timedelta(days=daySpan * (i))
        stats[str(end)] = getOverallStats(viewId,
                                          startDate=str(start),
                                          endDate=str(end))
    dpRange = pd.DataFrame(stats)
    dpRangeT = dpRange.T
    dpRangeT.columns = ['uniquePageViews', 'pageViews', 'bounceRate', 'avgTimeOnPage']
    return dpRangeT


def getRangeTwoYearsAgo(viewId, daySpan, spans):
    # daySpan: Number of days to aggregate over (eg, 7 for week)
    # of spans to calculate statistics for (eg, 4 for a month)
    current_year = DT.date.today().year
    current_month = DT.date.today().month
    current_day = DT.date.today().day
    one_week_ago = current_day - 7
    a = DT.date(current_year, current_month, current_day)  # current day
    b = DT.date(current_year, current_month, one_week_ago)  # same date, but two years ago
    delta = a - b

    stats = {}
    for i in range(spans):
        start = today - DT.timedelta(days=delta.days) - DT.timedelta(days=daySpan * (i + 1))
        end = today - DT.timedelta(days=delta.days) - DT.timedelta(days=daySpan * (i))
        stats[str(end)] = getOverallStats(viewId,
                                          startDate=str(start),
                                          endDate=str(end))
    dpRange = pd.DataFrame(stats)
    dpRangeT = dpRange.T
    dpRangeT.columns = ['uniquePageViews', 'pageViews', 'bounceRate', 'avgTimeOnPage']
    return dpRangeT


# print(dp_articles)

dp_past_week, headerPastWeek = get_duration_engagement('22050415', 'ga:sourceMedium', week_ago_str)
dp_past_month, headerPastMonth = get_duration_engagement('22050415', 'ga:sourceMedium', month_ago_str)
dp_all_time, headerAllTime = get_duration_engagement('22050415', 'ga:sourceMedium')

dpOverallStats = getRange('22050415', 7, 16)
dpOverallStats = dpOverallStats.rename_axis('date')
dpOverallStats.index = pd.to_datetime(dpOverallStats.index)
topDataWeekly, topDataMonthly = topTrafficSources(week_ago_str), topTrafficSources(month_ago_str)
topTagsWeekly, topTagsMonthly = topTags(week_ago_str), topTags(month_ago_str)

# print(dpOverallStats)
# print("AAAAAAAAAAAAAAAAAAAAAAA")
# print(type(dpOverallStats))
# print(type(dp_past_week))
# print(dp_past_week)
# print(dp_past_week.head(10))
# clean data
graphData_Now = dpOverallStats.groupby(pd.Grouper(level='date', freq='W')).mean()
graphData_Now = graphData_Now.round(decimals=2)

dpOverallStats_OneYear = getRangeOneYearAgo('22050415', 7, 16)
dpOverallStats_OneYear = dpOverallStats_OneYear.rename_axis('date')
dpOverallStats_OneYear.index = pd.to_datetime(dpOverallStats_OneYear.index)
graphData_OneYear = dpOverallStats_OneYear.groupby(pd.Grouper(level='date', freq='W')).mean()
graphData_OneYear = graphData_OneYear.round(decimals=2)

dpOverallStats_TwoYears = getRangeTwoYearsAgo('22050415', 7, 16)
dpOverallStats_TwoYears = dpOverallStats_TwoYears.rename_axis('date')
dpOverallStats_TwoYears.index = pd.to_datetime(dpOverallStats_TwoYears.index)
graphData_TwoYears = dpOverallStats_TwoYears.groupby(pd.Grouper(level='date', freq='W')).mean()
graphData_TwoYears = graphData_TwoYears.round(decimals=2)

# print(graphData_Now,graphData_OneYear,graphData_TwoYears)

# print(get_duration_engagement('22050415', 'ga:sourceMedium', week_ago_str))
# print(type(get_duration_engagement('22050415', 'ga:sourceMedium', week_ago_str)))

titlelist = list(dp_past_week.head(10)['title'])
viewlistweek = list(dp_past_week.head(10)['pageViews'])

print(titlelist)
lst = [titlelist, viewlistweek]
df2 = pd.DataFrame({'title': titlelist, 'views': viewlistweek})

test, test2 = getPivot(urls, '22050415', week_ago_str, pivotTag='ga:dimension3')
print("Test 1:")
test = test.head(500)
print(test)
for col in test.columns:
    print(col)
print("Test 2:")
print(test2)
sportslist = []
newslist = []
opinionlist = []
print(len(test2))
for i in range(len(test2)):
    if "news" in test2[i]:
        newslist.append(i)
    if "opinion" in test2[i]:
        opinionlist.append(i)
    if "sport" in test2[i]:
        sportslist.append(i)
print(len(newslist))
print(len(opinionlist))
print(len(sportslist))
pageviewlist = test['pageViews']
namelist = test['url']
newsviewlist = []
opinionviewlist = []
sportsviewlist = []
newsnamelist = []
opinionnamelist = []
sportsnamelist = []
for i in range(len(newslist)):
    newsviewlist.append(pageviewlist[i])
    newsnamelist.append(namelist[i])
for i in range(len(opinionlist)):
    opinionviewlist.append(pageviewlist[i])
    opinionnamelist.append(namelist[i])
for i in range(len(sportslist)):
    sportsviewlist.append(pageviewlist[i])
    sportsnamelist.append(namelist[i])
dnews = {'Name':newsnamelist, 'Views': newsviewlist}
dopinion = {'Name':opinionnamelist, 'Views':opinionviewlist}
dsports = {'Name':sportsnamelist, 'Views': sportsviewlist}
dfnews = pd.DataFrame(dnews)
dfopinion = pd.DataFrame(dopinion)
dfsports = pd.DataFrame(dsports)
dfnews = dfnews.sort_values(by=['Views'], ascending=False).head(10)
dfopinion = dfopinion.sort_values(by=['Views'], ascending=False).head(10)
dfnews = dfsports.sort_values(by=['Views'], ascending=False).head(10)
print(dfnews)
print(dfsports)
print(dfopinion)

fig = px.histogram(df2, x="title", y='views')
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
fig.write_image(file='staff_plot.png', format='png')
print("AAAA")
fig.show()
fig = px.histogram(dfnews, x="title", y='views')
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
fig.write_image(file='staff_plot2.png', format='png')
print("AAAA")
fig.show()
fig = px.histogram(dfopinion, x="title", y='views')
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
fig.write_image(file='staff_plot3.png', format='png')
print("AAAA")
fig.show()
fig = px.histogram(dfsports, x="title", y='views')
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
fig.write_image(file='staff_plot4.png', format='png')
print("AAAA")
fig.show()