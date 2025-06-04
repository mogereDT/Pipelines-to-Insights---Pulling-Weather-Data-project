import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

# Define city coordinates
cities = {
    'Louisville': {'lat': 38.2527, 'lon': -85.7585},
    'Lexington': {'lat': 38.0406, 'lon': -84.5037},
    'Bowling Green': {'lat': 36.9685, 'lon': -86.4808}
}

# Fetch past 7 days
def fetch_weather_data(city_name, unit='fahrenheit'):
    try:
        lat = cities[city_name]['lat']
        lon = cities[city_name]['lon']
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=6)

        url = (
            f"https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
            f"&timezone=America/New_York"
            f"&start_date={start_date}&end_date={end_date}"
        )

        response = requests.get(url)
        data = response.json()
        daily = data['daily']

        df = pd.DataFrame({
            'date': pd.to_datetime(daily['time']),
            'temp_max': daily['temperature_2m_max'],
            'temp_min': daily['temperature_2m_min'],
            'precipitation': daily['precipitation_sum'],
            'wind_speed': daily['windspeed_10m_max']
        })

        if unit == 'fahrenheit':
            df['temp_max'] = df['temp_max'].apply(lambda x: round(x * 9 / 5 + 32, 1))
            df['temp_min'] = df['temp_min'].apply(lambda x: round(x * 9 / 5 + 32, 1))

        df['humidity'] = [60 + round(i if pd.notna(i) else 0) for i in df['wind_speed']]
        return df
    except Exception as e:
        print("Error fetching data:", e)
        return pd.DataFrame()

# Fetch next 7 days forecast
def fetch_forecast_data(city_name, unit='fahrenheit'):
    lat = cities[city_name]['lat']
    lon = cities[city_name]['lon']
    today = datetime.today().date()
    future = today + timedelta(days=6)

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        f"&timezone=America/New_York"
        f"&start_date={today}&end_date={future}"
    )
    try:
        res = requests.get(url)
        data = res.json()['daily']

        df = pd.DataFrame({
            'date': pd.to_datetime(data['time']),
            'temp_max': data['temperature_2m_max'],
            'temp_min': data['temperature_2m_min'],
            'precipitation': data['precipitation_sum']
        })

        if unit == 'fahrenheit':
            df['temp_max'] = df['temp_max'].apply(lambda x: round(x * 9 / 5 + 32, 1))
            df['temp_min'] = df['temp_min'].apply(lambda x: round(x * 9 / 5 + 32, 1))
        return df
    except Exception as e:
        print("Forecast error:", e)
        return pd.DataFrame()

# Initial data
default_city = 'Louisville'
default_unit = 'fahrenheit'
default_df = fetch_weather_data(default_city, default_unit)

app = dash.Dash(__name__)
app.title = "Kentucky Weather Dashboard"

app.layout = html.Div([
    html.Div([
        html.Img(src='/assets/Seal_of_Kentucky.png', style={'height': '100px', 'margin': 'auto', 'display': 'block'}),
        html.H1("Kentucky Weather Dashboard", style={'textAlign': 'center'})
    ]),

    html.Div([
        html.Label("Select City:"),
        dcc.Dropdown(
            id='city',
            options=[{'label': k, 'value': k} for k in cities],
            value=default_city
        ),
        html.Label("Temperature Unit:"),
        dcc.RadioItems(
            id='unit',
            options=[
                {'label': 'Fahrenheit', 'value': 'fahrenheit'},
                {'label': 'Celsius', 'value': 'celsius'}
            ],
            value=default_unit,
            labelStyle={'display': 'inline-block', 'marginRight': '10px'}
        ),
        dcc.DatePickerRange(
            id='date-picker',
            start_date=default_df['date'].min(),
            end_date=default_df['date'].max(),
            display_format='YYYY-MM-DD'
        )
    ], style={'padding': '20px'}),

    html.Div(id='cards', style={'display': 'flex', 'justifyContent': 'space-around'}),

    html.Div([
        html.Img(src='/assets/sun.png', style={'height': '50px'}),
        dcc.Graph(id='temp-graph')
    ]),

    html.Div([
        html.Img(src='/assets/rain.png', style={'height': '50px'}),
        dcc.Graph(id='humid-precip-graph')
    ]),

    html.Div([
        html.Img(src='/assets/wind.png', style={'height': '50px'}),
        dcc.Graph(id='wind-gauge')
    ]),

    html.Div([
        html.H3("7-Day Forecast"),
        dcc.Graph(id='forecast-graph')
    ])
])

@app.callback(
    [Output('temp-graph', 'figure'),
     Output('humid-precip-graph', 'figure'),
     Output('wind-gauge', 'figure'),
     Output('forecast-graph', 'figure'),
     Output('cards', 'children')],
    [Input('city', 'value'),
     Input('unit', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_graphs(city, unit, start_date, end_date):
    df = fetch_weather_data(city, unit)
    forecast_df = fetch_forecast_data(city, unit)

    if df.empty or forecast_df.empty:
        fig = go.Figure().add_annotation(text="Error loading data", x=0.5, y=0.5, showarrow=False)
        return fig, fig, fig, fig, [html.P("Data unavailable.")]

    dff = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

    temp_fig = px.line(dff, x='date', y=['temp_max', 'temp_min'], title=f"{city} Temps")
    humid_fig = px.bar(dff, x='date', y=['humidity', 'precipitation'], barmode='group', title="Humidity & Precip")
    wind_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=dff['wind_speed'].iloc[-1],
        title={'text': "Wind Speed (mph)"},
        gauge={
            'axis': {'range': [0, 30]},
            'steps': [
                {'range': [0, 10], 'color': "lightgreen"},
                {'range': [10, 20], 'color': "yellow"},
                {'range': [20, 30], 'color': "red"}
            ],
            'bar': {'color': "blue"}
        }
    ))
    forecast_fig = px.line(
        forecast_df, x='date', y=['temp_max', 'temp_min'],
        title=f"{city} 7-Day Forecast"
    )

    cards = [
        html.Div([
            html.H4("Max Temp"), html.P(f"{dff['temp_max'].max():.1f}")
        ]),
        html.Div([
            html.H4("Min Temp"), html.P(f"{dff['temp_min'].min():.1f}")
        ]),
        html.Div([
            html.H4("Precipitation"), html.P(f"{dff['precipitation'].sum():.2f} in")
        ]),
        html.Div([
            html.H4("Wind Speed"), html.P(f"{dff['wind_speed'].mean():.1f} mph")
        ])
    ]

    return temp_fig, humid_fig, wind_fig, forecast_fig, cards

if __name__ == '__main__':
    app.run(debug=True)
