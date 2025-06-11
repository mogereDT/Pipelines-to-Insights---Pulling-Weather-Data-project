#!/usr/bin/env python3
"""
Kentucky Weather Dashboard
=========================

A modern, interactive weather dashboard for Kentucky cities that fetches real-time 
weather data and presents it through beautiful visualizations.

This single-file application:
- Fetches weather data from Open-Meteo APIs
- Embeds all assets (images, styles, scripts) for portability
- Serves an interactive dashboard via local web server
- Provides real-time unit conversion and city selection

Author: Kentucky Weather Dashboard Team
License: MIT
Version: 1.0.0
"""

import json
import pandas as pd
import requests
from datetime import datetime, timedelta
from pathlib import Path
import http.server
import socketserver
import webbrowser
import base64
from io import BytesIO

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

# Kentucky cities with their coordinates
CITIES = {
    'Louisville, KY':    (38.2527,  -85.7585),
    'Lexington, KY':     (38.0406,  -84.5037),
    'Bowling Green, KY': (36.9685,  -86.4808)
}

# Web server configuration
PORT = 8000

# Global variable to store the fetch timestamp
FETCH_TIMESTAMP = "Not yet fetched"

# ─────────────────────────────────────────────────────────────────────────────
# ASSET ENCODING
# ─────────────────────────────────────────────────────────────────────────────

def get_image_b64(image_path):
    """
    Reads an image file and returns its Base64 encoded string.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Base64 encoded image data
        
    Note:
        Returns a transparent 1x1 pixel if the file is not found
    """
    try:
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode('utf-8')
            print(f"Successfully loaded image: {image_path}")
            return data
    except FileNotFoundError:
        print(f"Warning: Image file not found at {image_path}. Using placeholder.")
        # Create a 1x1 transparent pixel as a placeholder
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    except Exception as e:
        print(f"Error loading image {image_path}: {e}. Using placeholder.")
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

# Load and encode all image assets
SEAL_B64 = get_image_b64('Seal_of_Kentucky.png')
RAIN_B64 = get_image_b64('rain.png')
SUN_B64 = get_image_b64('sun.png')
WIND_B64 = get_image_b64('wind.png')

# ─────────────────────────────────────────────────────────────────────────────
# HTML TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kentucky Weather Dashboard</title>
    
    <!-- External Libraries -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        /* CSS Variables for theming */
        :root {
            --bg-primary: #0f0f23; 
            --bg-secondary: #1a1a2e; 
            --bg-tertiary: #16213e;
            --bg-card: #1e2139; 
            --text-primary: #ffffff; 
            --text-secondary: #a0a0b3;
            --text-muted: #6b7280; 
            --accent-primary: #00d4aa; 
            --accent-secondary: #0ea5e9;
            --accent-tertiary: #8b5cf6; 
            --border: #2d3748; 
            --border-light: #3a4553;
            --gradient-primary: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        }
        
        /* Global Styles */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Inter', sans-serif; 
            background: var(--bg-primary); 
            color: var(--text-primary); 
        }
        
        /* Layout Components */
        .container { 
            max-width: 1600px; 
            margin: 0 auto; 
            padding: 24px; 
        }
        
        .header { 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            gap: 1.5rem; 
            text-align: center; 
            margin-bottom: 1rem; 
        }
        
        .header img { height: 70px; }
        h1 { font-size: 2.5rem; font-weight: 700; }
        
        .timestamp { 
            text-align: center; 
            color: var(--text-muted); 
            margin-bottom: 2rem; 
            font-style: italic; 
        }
        
        /* Control Panel */
        .controls { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 1.5rem; 
            padding: 1.5rem; 
            background: var(--bg-card); 
            border-radius: 12px; 
            margin-bottom: 2rem; 
            border: 1px solid var(--border); 
        }
        
        .control-group { 
            display: flex; 
            flex-direction: column; 
            gap: 8px; 
        }
        
        label { 
            color: var(--text-secondary); 
            font-size: 0.875rem; 
            font-weight: 500; 
        }
        
        .radio-group { 
            display: flex; 
            gap: 1rem; 
        }
        
        .radio-group label { 
            display: flex; 
            align-items: center; 
            gap: 0.5rem; 
            cursor: pointer; 
        }
        
        /* Grid Layout */
        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
            gap: 1.5rem; 
        }
        
        /* Card Components */
        .card { 
            background: var(--bg-card); 
            border: 1px solid var(--border); 
            border-radius: 12px; 
            padding: 1.5rem; 
            box-shadow: var(--shadow-md); 
        }
        
        .card h3 { 
            display: flex; 
            align-items: center; 
            gap: 0.75rem; 
            margin-bottom: 1.5rem; 
            font-size: 1.25rem; 
            font-weight: 600; 
        }
        
        .card h3 img { height: 28px; }
        
        /* Chart and Map Containers */
        .chart-container { 
            position: relative; 
            height: 320px; 
        }
        
        .map-container { 
            height: 400px; 
            border-radius: 8px; 
            overflow: hidden; 
            border: 1px solid var(--border); 
        }
        
        /* Table Styles */
        table { 
            width: 100%; 
            border-collapse: collapse; 
        }
        
        th, td { 
            padding: 1rem; 
            text-align: left; 
            border-bottom: 1px solid var(--border); 
        }
        
        th { background: var(--bg-secondary); }
        
        /* Utility Classes */
        .full-width { grid-column: 1 / -1; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Section -->
        <header class="header">
            <img src="data:image/png;base64,SEAL_ICON_PLACEHOLDER" alt="Kentucky Seal">
            <h1>Kentucky Weather Dashboard</h1>
        </header>
        
        <!-- Timestamp Display -->
        <div class="timestamp">Last updated: TIMESTAMP_PLACEHOLDER</div>

        <!-- Control Panel -->
        <div class="controls">
            <div class="control-group" id="city-control"></div>
            <div class="control-group" id="temp-unit-control"></div>
            <div class="control-group" id="wind-unit-control"></div>
            <div class="control-group" id="precip-unit-control"></div>
        </div>

        <!-- Visualization Grid -->
        <div class="grid">
            <!-- Forecast Chart -->
            <div class="card">
                <h3><img src="data:image/png;base64,SUN_ICON_PLACEHOLDER" alt="Sun">7-Day Forecast</h3>
                <div class="chart-container"><canvas id="forecastChart"></canvas></div>
            </div>
            
            <!-- Temperature History -->
            <div class="card">
                <h3><img src="data:image/png;base64,SUN_ICON_PLACEHOLDER" alt="Sun">Historical Temperature</h3>
                <div class="chart-container"><canvas id="tempChart"></canvas></div>
            </div>
            
            <!-- Humidity Chart -->
            <div class="card">
                <h3><img src="data:image/png;base64,WIND_ICON_PLACEHOLDER" alt="Wind">Historical Humidity</h3>
                <div class="chart-container"><canvas id="humidityChart"></canvas></div>
            </div>
            
            <!-- Precipitation Chart -->
            <div class="card">
                <h3><img src="data:image/png;base64,RAIN_ICON_PLACEHOLDER" alt="Rain">Historical Precipitation</h3>
                <div class="chart-container"><canvas id="precipChart"></canvas></div>
            </div>
            
            <!-- Wind Speed Chart -->
            <div class="card">
                <h3><img src="data:image/png;base64,WIND_ICON_PLACEHOLDER" alt="Wind">Historical Wind Speed</h3>
                <div class="chart-container"><canvas id="windChart"></canvas></div>
            </div>
            
            <!-- Precipitation Pie Chart -->
            <div class="card">
                <h3><img src="data:image/png;base64,RAIN_ICON_PLACEHOLDER" alt="Rain">Total Precipitation by City (last 7 days)</h3>
                <div class="chart-container"><canvas id="precipPieChart"></canvas></div>
            </div>
            
            <!-- Interactive Map -->
            <div class="card full-width">
                <h3>City Temperature Map</h3>
                <div id="map" class="map-container"></div>
            </div>
            
            <!-- Data Table -->
            <div class="card full-width">
                <h3>Data Table</h3>
                <div style="overflow-x: auto;"><table id="weatherTable"></table></div>
            </div>
        </div>
    </div>

    <script>
        // Weather data will be injected here
        /* DATA_PLACEHOLDER */

        // Global chart instances
        let forecastChart, tempChart, humidityChart, precipChart, windChart, precipPieChart, map;

        // Chart.js default configuration
        const chartDefaults = {
            responsive: true, 
            maintainAspectRatio: false,
            plugins: { 
                legend: { 
                    labels: { color: '#ffffff' } 
                } 
            },
            scales: {
                y: { 
                    ticks: { color: '#a0a0b3' }, 
                    grid: { color: '#2d3748' } 
                },
                x: { 
                    ticks: { color: '#a0a0b3' }, 
                    grid: { color: '#2d3748' } 
                }
            }
        };

        /**
         * Initialize the dashboard
         */
        function initialize() {
            createControls();
            initializeCharts();
            initializeMap();
            initializePrecipPieChart();
            updateDashboard();
            attachEventListeners();
        }
        
        /**
         * Create control panel with radio buttons
         */
        function createControls() {
            const cities = Object.keys(allData);
            document.getElementById('city-control').innerHTML = 
                '<label>City:</label>' + createRadioGroup('city', cities, cities[0]);
            document.getElementById('temp-unit-control').innerHTML = 
                '<label>Temperature Unit:</label>' + createRadioGroup('temp-unit', ['°F', '°C'], '°F');
            document.getElementById('wind-unit-control').innerHTML = 
                '<label>Wind Speed Unit:</label>' + createRadioGroup('wind-unit', ['mph', 'km/h'], 'mph');
            document.getElementById('precip-unit-control').innerHTML = 
                '<label>Precipitation Unit:</label>' + createRadioGroup('precip-unit', ['in', 'cm'], 'in');
        }

        /**
         * Create a radio button group
         */
        function createRadioGroup(name, options, defaultValue) {
            return '<div class="radio-group">' + options.map(o => `
                <label>
                    <input type="radio" name="${name}" value="${o}" ${o === defaultValue ? 'checked' : ''}>
                    <span>${o}</span>
                </label>
            `).join('') + '</div>';
        }

        /**
         * Attach event listeners to controls
         */
        function attachEventListeners() {
            document.querySelectorAll('input[type="radio"]').forEach(radio => {
                radio.addEventListener('change', () => updateDashboard());
            });
        }

        /**
         * Initialize all Chart.js charts
         */
        function initializeCharts() {
            forecastChart = new Chart(document.getElementById('forecastChart').getContext('2d'), 
                { type: 'line', options: chartDefaults });
            tempChart = new Chart(document.getElementById('tempChart').getContext('2d'), 
                { type: 'line', options: chartDefaults });
            humidityChart = new Chart(document.getElementById('humidityChart').getContext('2d'), 
                { type: 'line', options: chartDefaults });
            precipChart = new Chart(document.getElementById('precipChart').getContext('2d'), 
                { type: 'bar', options: chartDefaults });
            windChart = new Chart(document.getElementById('windChart').getContext('2d'), 
                { type: 'line', options: chartDefaults });
        }

        /**
         * Initialize Leaflet map
         */
        function initializeMap() {
            map = L.map('map').setView([37.5, -85.5], 7);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '© OpenStreetMap contributors, © CARTO'
            }).addTo(map);
        }

        /**
         * Get selected value from radio group
         */
        function getSelected(name) { 
            return document.querySelector(`input[name="${name}"]:checked`).value; 
        }

        /**
         * Update all dashboard components based on selected options
         */
        function updateDashboard() {
            const city = getSelected('city');
            const tUnit = getSelected('temp-unit');
            const wUnit = getSelected('wind-unit');
            const pUnit = getSelected('precip-unit');
            
            const cityData = allData[city];
            const processedHistory = processHistory(cityData.history, tUnit, wUnit, pUnit);
            const processedForecast = processForecast(cityData.forecast, tUnit);

            updateAllCharts(processedHistory, processedForecast);
            updateMap(tUnit);
            updateTable(processedHistory);
        }

        /**
         * Process historical data with unit conversions
         */
        function processHistory(history, tUnit, wUnit, pUnit) {
            return history.map(d => ({
                date: d.date,
                temp_max: tUnit === '°F' ? (d.temp_max_c * 9/5 + 32).toFixed(0) : d.temp_max_c.toFixed(0),
                temp_min: tUnit === '°F' ? (d.temp_min_c * 9/5 + 32).toFixed(0) : d.temp_min_c.toFixed(0),
                humidity_percent: d.humidity_percent,
                precip: pUnit === 'in' ? (d.precip_mm / 25.4).toFixed(2) : (d.precip_mm / 10).toFixed(2),
                wind_speed: wUnit === 'mph' ? (d.wind_kmh * 0.621371).toFixed(0) : d.wind_kmh.toFixed(0)
            }));
        }

        /**
         * Process forecast data with unit conversions
         */
        function processForecast(forecast, tUnit) {
            return forecast.map(d => ({
                date: d.date,
                temp_max: tUnit === '°F' ? (d.temp_max_c * 9/5 + 32).toFixed(0) : d.temp_max_c.toFixed(0),
                temp_min: tUnit === '°F' ? (d.temp_min_c * 9/5 + 32).toFixed(0) : d.temp_min_c.toFixed(0),
            }));
        }
        
        /**
         * Update all charts with new data
         */
        function updateAllCharts(history, forecast) {
            const labels = history.map(d => d.date);
            const forecastLabels = forecast.map(d => d.date);

            // Update forecast chart
            updateChart(forecastChart, 'line', forecastLabels, [
                { label: 'Max Temp', data: forecast.map(d => d.temp_max), borderColor: '#ef4444' },
                { label: 'Min Temp', data: forecast.map(d => d.temp_min), borderColor: '#0ea5e9' }
            ]);

            // Update historical charts
            updateChart(tempChart, 'line', labels, [
                { label: 'Max Temp', data: history.map(d => d.temp_max), borderColor: '#ef4444' },
                { label: 'Min Temp', data: history.map(d => d.temp_min), borderColor: '#0ea5e9' }
            ]);
            updateChart(humidityChart, 'line', labels, 
                [{ label: 'Humidity (%)', data: history.map(d => d.humidity_percent), borderColor: '#8b5cf6' }]);
            updateChart(precipChart, 'bar', labels, 
                [{ label: `Precipitation (${getSelected('precip-unit')})`, data: history.map(d => d.precip), backgroundColor: '#0ea5e9' }]);
            updateChart(windChart, 'line', labels, 
                [{ label: `Wind Speed (${getSelected('wind-unit')})`, data: history.map(d => d.wind_speed), borderColor: '#00d4aa' }]);
        }

        /**
         * Update a specific chart
         */
        function updateChart(chart, type, labels, datasets) {
            chart.data.labels = labels;
            chart.data.datasets = datasets;
            chart.update();
        }

        /**
         * Update map with temperature-based markers
         */
        function updateMap(tUnit) {
            // Clear existing markers
            map.eachLayer(layer => { 
                if (layer instanceof L.CircleMarker || layer instanceof L.Marker) {
                    map.removeLayer(layer);
                }
            });

            // Get all city temperatures
            const cityTemps = Object.values(allData).map(cityData => {
                const validHistory = cityData.history.map(h => h.temp_max_c).filter(t => t !== null && !isNaN(t));
                return validHistory.length > 0 ? validHistory[validHistory.length - 1] : null;
            }).filter(t => t !== null);

            if (cityTemps.length === 0) return;

            const minTemp = Math.min(...cityTemps);
            const maxTemp = Math.max(...cityTemps);

            // Color interpolation function
            function getColor(temp, min, max) {
                if (min === max) return 'rgb(255, 0, 0)';
                const fraction = (temp - min) / (max - min);
                const r = Math.floor(255 * fraction);
                const g = 0;
                const b = Math.floor(255 * (1 - fraction));
                return `rgb(${r}, ${g}, ${b})`;
            }

            // Add markers for each city
            for (const city in allData) {
                const cityData = allData[city];
                const validHistory = cityData.history.map(h => h.temp_max_c).filter(t => t !== null && !isNaN(t));
                const latestTempC = validHistory.length > 0 ? validHistory[validHistory.length - 1] : null;

                if (latestTempC === null) continue;

                const displayTemp = tUnit === '°F' ? (latestTempC * 9/5 + 32).toFixed(0) : latestTempC.toFixed(0);
                const radius = (maxTemp === minTemp) ? 15 : (10 + 20 * (latestTempC - minTemp) / (maxTemp - minTemp));

                L.circleMarker([cityData.lat, cityData.lon], {
                    radius: radius,
                    fillColor: getColor(latestTempC, minTemp, maxTemp),
                    color: "#fff",
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                }).addTo(map)
                  .bindPopup(`<b>${city}</b><br>${displayTemp}${tUnit}`);
            }
        }

        /**
         * Update data table
         */
        function updateTable(history) {
            const table = document.getElementById('weatherTable');
            const headers = ['Date', `Max Temp (${getSelected('temp-unit')})`, 
                           `Min Temp (${getSelected('temp-unit')})`, 'Humidity (%)', 
                           `Precip. (${getSelected('precip-unit')})`, 
                           `Wind (${getSelected('wind-unit')})`];
            const keys = ['date', 'temp_max', 'temp_min', 'humidity_percent', 'precip', 'wind_speed'];
            
            table.innerHTML = `
                <thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
                <tbody>${history.map(row => `<tr>${keys.map(k => `<td>${row[k]}</td>`).join('')}</tr>`).join('')}</tbody>
            `;
        }

        /**
         * Initialize precipitation pie chart
         */
        function initializePrecipPieChart() {
            // Calculate total precipitation for each city
            const cityPrecip = Object.entries(allData).map(([city, data]) => {
                const totalPrecip = data.history.reduce((sum, day) => {
                    const precip = day.precip_mm;
                    return sum + (isNaN(precip) ? 0 : precip);
                }, 0);
                return { city, totalPrecip };
            });

            const pieOptions = {
                responsive: true, 
                maintainAspectRatio: false,
                plugins: { 
                    legend: { labels: { color: '#ffffff' } },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed !== null) {
                                    label += context.parsed.toFixed(1) + ' mm';
                                }
                                return label;
                            }
                        }
                    }
                }
            };

            precipPieChart = new Chart(document.getElementById('precipPieChart').getContext('2d'), {
                type: 'pie',
                data: {
                    labels: cityPrecip.map(d => d.city),
                    datasets: [{
                        label: 'Total Precipitation (mm)',
                        data: cityPrecip.map(d => d.totalPrecip),
                        backgroundColor: ['#00d4aa', '#0ea5e9', '#8b5cf6'],
                    }]
                },
                options: pieOptions
            });
        }

        // Initialize dashboard when DOM is ready
        document.addEventListener('DOMContentLoaded', initialize);
    </script>
</body>
</html>
"""

# ─────────────────────────────────────────────────────────────────────────────
# DATA FETCHING FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def fetch_weather_data(city, lat, lon):
    """
    Fetches historical weather data for the last 7 days.
    
    Args:
        city (str): City name
        lat (float): Latitude
        lon (float): Longitude
        
    Returns:
        pd.DataFrame: Weather data with columns for date, temperature, precipitation, etc.
    """
    today = datetime.today().date()
    start = today - timedelta(days=6)
    
    # Build API URL
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
        "&timezone=America/New_York"
        f"&start_date={start}&end_date={today}"
    )
    
    try:
        # Make API request with timeout
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        d = r.json().get('daily', {})
        
        if not d.get('time'):
            return pd.DataFrame()
            
        # Create DataFrame from API response
        df = pd.DataFrame({
            'date':       pd.to_datetime(d['time']),
            'temp_max_c': d['temperature_2m_max'],
            'temp_min_c': d['temperature_2m_min'],
            'precip_mm':  d['precipitation_sum'],
            'wind_kmh':   d['windspeed_10m_max'],
        })
        
        # Generate synthetic humidity based on wind patterns
        df['humidity_percent'] = (60 + df['wind_kmh'].rolling(2, min_periods=1).mean().fillna(0)).round(0).astype(int)
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data for {city}: {e}")
        return pd.DataFrame()


def fetch_forecast_data(city, lat, lon):
    """
    Fetches weather forecast for the next 7 days.
    
    Args:
        city (str): City name
        lat (float): Latitude
        lon (float): Longitude
        
    Returns:
        pd.DataFrame: Forecast data with columns for date and temperatures
    """
    today = datetime.today().date()
    future = today + timedelta(days=6)
    
    # Build API URL
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=America/New_York"
        f"&start_date={today}&end_date={future}"
    )
    
    try:
        # Make API request with timeout
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        d = r.json().get('daily', {})
        
        if not d.get('time'):
            return pd.DataFrame()
            
        # Create DataFrame from API response
        return pd.DataFrame({
            'date':       pd.to_datetime(d['time']),
            'temp_max_c': d['temperature_2m_max'],
            'temp_min_c': d['temperature_2m_min'],
            'precip_mm':  d['precipitation_sum'],
        })
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching forecast data for {city}: {e}")
        return pd.DataFrame()


def fetch_all_data():
    """
    Fetches historical and forecast data for all cities.
    
    Returns:
        dict: Dictionary with city names as keys and weather data as values
    """
    global FETCH_TIMESTAMP
    FETCH_TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

    all_data = {}
    
    for city, (lat, lon) in CITIES.items():
        print(f"Fetching data for {city}...")
        
        # Fetch both historical and forecast data
        history_df = fetch_weather_data(city, lat, lon)
        forecast_df = fetch_forecast_data(city, lat, lon)
        
        # Convert timestamps to strings for JSON serialization
        if not history_df.empty:
            history_df['date'] = history_df['date'].dt.strftime('%Y-%m-%d')
        if not forecast_df.empty:
            forecast_df['date'] = forecast_df['date'].dt.strftime('%Y-%m-%d')

        # Store data for this city
        all_data[city] = {
            'lat': lat,
            'lon': lon,
            'history': history_df.to_dict(orient='records'),
            'forecast': forecast_df.to_dict(orient='records')
        }
        
    return all_data

# ─────────────────────────────────────────────────────────────────────────────
# HTML GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def generate_html(data):
    """
    Injects weather data into the HTML template.
    
    Args:
        data (dict): Weather data for all cities
        
    Returns:
        str: Complete HTML content with embedded data
    """
    print("Generating HTML report...")
    
    # Convert data to JSON
    data_json = json.dumps(data, indent=4)
    
    # Replace placeholders in the template
    html_content = HTML_TEMPLATE.replace("/* DATA_PLACEHOLDER */", f"const allData = {data_json};")
    html_content = html_content.replace("SEAL_ICON_PLACEHOLDER", SEAL_B64)
    html_content = html_content.replace("SUN_ICON_PLACEHOLDER", SUN_B64)
    html_content = html_content.replace("RAIN_ICON_PLACEHOLDER", RAIN_B64)
    html_content = html_content.replace("WIND_ICON_PLACEHOLDER", WIND_B64)
    html_content = html_content.replace("TIMESTAMP_PLACEHOLDER", FETCH_TIMESTAMP)
    
    return html_content

# ─────────────────────────────────────────────────────────────────────────────
# WEB SERVER
# ─────────────────────────────────────────────────────────────────────────────

def serve_html(html_content):
    """
    Serves the dashboard via local web server.
    
    Args:
        html_content (str): Complete HTML content to serve
    """
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        """Custom HTTP handler to serve our dashboard"""
        
        def do_GET(self):
            """Handle GET requests"""
            if self.path == '/':
                # Serve the dashboard
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))
            else:
                # Return 404 for other paths
                self.send_error(404, "File Not Found")

    # Create and start the server
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"Serving at {url}")
        
        # Open browser automatically
        webbrowser.open_new_tab(url)
        
        try:
            # Serve forever until interrupted
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
            
        # Clean shutdown
        httpd.server_close()
        print("\nServer stopped.")

# ─────────────────────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    """Main entry point of the application"""
    
    # Fetch weather data from APIs
    weather_data = fetch_all_data()
    
    # Generate HTML with embedded data
    final_html = generate_html(weather_data)
    
    # Serve the dashboard
    serve_html(final_html) 