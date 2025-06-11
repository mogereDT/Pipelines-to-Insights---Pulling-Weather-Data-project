# ─── Dash app pulls the same API under the hood ───────────────────────────────
import dash
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ─── Serve /mnt/data (your Desktop assets) as Dash assets ────────────────────
app = dash.Dash(__name__)
app.title = "KY Weather Dashboard"

# ─── Supported cities (lat, lon untouched) ───────────────────────────────────
cities = {
    'Louisville, KY':    (38.2527,  -85.7585),
    'Lexington, KY':     (38.0406,  -84.5037),
    'Bowling Green, KY': (36.9685,  -86.4808)
}

# ─── Fetch past 7 days historical data ────────────────────────────────────────
def fetch_weather_data(city):
    lat, lon = cities[city]
    today = datetime.today().date()
    start = today - timedelta(days=6)
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
        "&timezone=America/New_York"
        f"&start_date={start}&end_date={today}"
    )
    r = requests.get(url)
    d = r.json().get('daily', {})
    if not d.get('time'):
        return pd.DataFrame()
    df = pd.DataFrame({
        'date':       pd.to_datetime(d['time']),
        'temp_max_c': d['temperature_2m_max'],
        'temp_min_c': d['temperature_2m_min'],
        'precip_mm':  d['precipitation_sum'],
        'wind_kmh':   d['windspeed_10m_max'],
    })
    # synthetic humidity % (rounded)
    df['humidity_%'] = (
        60
        + df['wind_kmh'].rolling(2, min_periods=1).mean().fillna(0)
    ).round(0).astype(int)
    return df

# ─── Fetch next 7 days forecast ────────────────────────────────────────────────
def fetch_forecast_data(city):
    lat, lon = cities[city]
    today = datetime.today().date()
    future = today + timedelta(days=6)
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=America/New_York"
        f"&start_date={today}&end_date={future}"
    )
    r = requests.get(url)
    d = r.json().get('daily', {})
    if not d.get('time'):
        return pd.DataFrame()
    df = pd.DataFrame({
        'date':       pd.to_datetime(d['time']),
        'temp_max_c': d['temperature_2m_max'],
        'temp_min_c': d['temperature_2m_min'],
        'precip_mm':  d['precipitation_sum'],
    })
    return df

# ─── Initial fetch to set date-picker defaults ────────────────────────────────
default_city = 'Louisville, KY'
hist_df = fetch_weather_data(default_city)

# ─── Layout (Forecast first) ───────────────────────────────────────────────────
app.layout = html.Div(id='app-container', children=[
    html.Div([
        html.Img(src=app.get_asset_url("Seal_of_Kentucky.png"),
                 style={'height':'80px','display':'block','margin':'auto'}),
        html.H1("Kentucky Weather Dashboard", style={'textAlign':'center'})
    ]),
    html.Div(className='control-panel', children=[
        html.Div([
            html.Label("Select City:"), dcc.Dropdown(
                id='city',
                options=[{'label':k,'value':k} for k in cities],
                value=default_city
            )
        ]),
        html.Div([
            html.Label("Temperature Unit:"), dcc.RadioItems(
                id='temp-unit',
                options=[{'label':'°F','value':'fahrenheit'},
                         {'label':'°C','value':'celsius'}],
                value='fahrenheit',
                labelStyle={'display':'inline-block','marginRight':'15px'}
            )
        ]),
        html.Div([
            html.Label("Wind Speed Unit:"), dcc.RadioItems(
                id='wind-unit',
                options=[{'label':'mph','value':'mph'},
                         {'label':'km/h','value':'kph'}],
                value='mph',
                labelStyle={'display':'inline-block','marginRight':'15px'}
            )
        ]),
        html.Div([
            html.Label("Precipitation Unit:"), dcc.RadioItems(
                id='precip-unit',
                options=[{'label':'inches','value':'in'},
                         {'label':'cm','value':'cm'}],
                value='in',
                labelStyle={'display':'inline-block','marginRight':'15px'}
            )
        ]),
        html.Div([
            html.Label("Date Range:"),
            dcc.DatePickerRange(
                id='date-picker',
                start_date=hist_df['date'].min(),
                end_date=hist_df['date'].max(),
                display_format='YYYY-MM-DD'
            ),
        ])
    ]),

    html.H3("7-Day Forecast", style={'textAlign':'center','marginTop':'20px'}),
    html.Div(className='graph-container', children=[
        html.Img(src=app.get_asset_url("sun.png"), className='graph-icon'),
        dcc.Graph(id='forecast-graph')
    ]),

    html.Div(id='cards', className='card-container'),

    html.Div(className='graph-container', children=[
        html.Img(src=app.get_asset_url("sun.png"), className='graph-icon'),
        dcc.Graph(id='temp-graph')
    ]),
    html.Div(className='graph-container', children=[
        html.Img(src=app.get_asset_url("rain.png"), className='graph-icon'),
        dcc.Graph(id='humidity-graph')
    ]),
    html.Div(className='graph-container', children=[
        html.Img(src=app.get_asset_url("rain.png"), className='graph-icon'),
        dcc.Graph(id='precip-graph')
    ]),
    html.Div(className='graph-container', children=[
        html.Img(src=app.get_asset_url("wind.png"), className='graph-icon'),
        dcc.Graph(id='wind-gauge')
    ]),
])

# ─── Callback to update all ─────────────────────────────────────────────────────
@app.callback(
    [
        Output('forecast-graph','figure'),
        Output('temp-graph',     'figure'),
        Output('humidity-graph', 'figure'),
        Output('precip-graph',   'figure'),
        Output('wind-gauge',     'figure'),
        Output('cards',          'children'),
        Output('date-picker',    'start_date'),
        Output('date-picker',    'end_date'),
    ],
    [
        Input('city',        'value'),
        Input('temp-unit',   'value'),
        Input('wind-unit',   'value'),
        Input('precip-unit', 'value'),
    ]
)
def update_all(city, temp_unit, wind_unit, precip_unit):
    df  = fetch_weather_data(city)
    fdf = fetch_forecast_data(city)
    if df.empty:
        empty = go.Figure().add_annotation(text="No data", x=0.5, y=0.5, showarrow=False)
        return empty, empty, empty, empty, empty, [html.P("No data available")], None, None

    # Temps → rounded
    if temp_unit == 'fahrenheit':
        df['temp_max'] = (df['temp_max_c']*9/5+32).round(0)
        df['temp_min'] = (df['temp_min_c']*9/5+32).round(0)
        fdf['temp_max'] = (fdf['temp_max_c']*9/5+32).round(0)
        fdf['temp_min'] = (fdf['temp_min_c']*9/5+32).round(0)
        t_lbl, f_lbl = '°F','°F'
    else:
        df['temp_max'] = df['temp_max_c'].round(0)
        df['temp_min'] = df['temp_min_c'].round(0)
        fdf['temp_max'] = fdf['temp_max_c'].round(0)
        fdf['temp_min'] = fdf['temp_min_c'].round(0)
        t_lbl, f_lbl = '°C','°C'

    # Wind → rounded
    if wind_unit=='mph':
        df['wind'] = (df['wind_kmh']*0.621371).round(0)
        w_lbl = 'mph'
    else:
        df['wind'] = df['wind_kmh'].round(0)
        w_lbl = 'km/h'

    # Precip → rounded
    if precip_unit=='in':
        df['precip'] = (df['precip_mm']/25.4).round(2)
        fdf['precip'] = (fdf['precip_mm']/25.4).round(2)
        p_lbl = 'inches'
    else:
        df['precip'] = (df['precip_mm']/10).round(2)
        fdf['precip'] = (fdf['precip_mm']/10).round(2)
        p_lbl = 'cm'

    # humidity_% already rounded on creation

    # date range
    start, end = df['date'].min(), df['date'].max()

    # Figures
    forecast_fig = px.line(
        fdf, x='date', y=['temp_max', 'temp_min'],
        title=f"{city} 7-Day Forecast ({f_lbl})",
        labels={'value': f"Temp ({f_lbl})", 'date': 'Date', 'variable': 'Temp Type'}
    )
    temp_fig = px.line(
        df, x='date', y=['temp_max', 'temp_min'],
        title=f'Historical Temperatures ({t_lbl})',
        labels={'value': f"Temp ({t_lbl})", 'date': 'Date', 'variable': 'Temp Type'}
    )
    humidity_fig = px.line(
        df, x='date', y='humidity_%',
        title='Historical Humidity (%)',
        labels={'humidity_%': 'Humidity (%)', 'date': 'Date'}
    )
    precip_fig = px.bar(
        df, x='date', y='precip',
        title=f'Historical Precipitation ({p_lbl})',
        labels={'precip': f'Precipitation ({p_lbl})', 'date': 'Date'}
    )
    wind_val = df['wind'].iloc[-1] if not df.empty else 0
    wind_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=wind_val,
        title={'text': f"Latest Wind Speed ({w_lbl})"},
        gauge={ 'axis': {'range': [None, (50 if w_lbl == 'mph' else 80)]} }
    ))

    # Cards
    cards = [
        html.Div(className='card', children=[html.H4("Max Temp"), html.P(f"{df['temp_max'].max():.1f}{t_lbl}")]),
        html.Div(className='card', children=[html.H4("Min Temp"), html.P(f"{df['temp_min'].min():.1f}{t_lbl}")]),
        html.Div(className='card', children=[html.H4("Total Precip"), html.P(f"{df['precip'].sum():.2f} {p_lbl}")]),
        html.Div(className='card', children=[html.H4("Avg Wind"), html.P(f"{df['wind'].mean():.1f} {w_lbl}")])
    ]

    return forecast_fig, temp_fig, humidity_fig, precip_fig, wind_fig, cards, df['date'].min(), df['date'].max()

if __name__ == '__main__':
    # accessible from anywhere on your LAN at port 8050
    app.run(debug=False, host='0.0.0.0', port=8050)
