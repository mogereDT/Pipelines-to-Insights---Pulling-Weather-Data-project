# Kentucky Weather Dashboard

A modern, interactive weather dashboard for Kentucky cities that fetches real-time weather data and presents it through beautiful visualizations. The application provides both historical weather data and future forecasts with an intuitive, dark-themed interface.

![Kentucky Weather Dashboard](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Features

### Data Visualization
- **7-Day Weather Forecast** - Line chart showing temperature predictions
- **Historical Temperature Trends** - Track max/min temperatures over the past week
- **Humidity Monitoring** - Visual representation of humidity levels
- **Precipitation Analysis** - Bar chart showing rainfall amounts
- **Wind Speed Tracking** - Monitor wind patterns over time
- **City Comparison** - Pie chart comparing total precipitation across cities
- **Interactive Map** - Temperature-based visualization of Kentucky cities
- **Detailed Data Table** - Sortable table with all weather metrics

### Interactive Controls
- **City Selection** - Switch between Louisville, Lexington, and Bowling Green
- **Unit Conversion** - Toggle between:
  - Temperature: °F / °C
  - Wind Speed: mph / km/h
  - Precipitation: inches / cm

### Design Features
- Dark theme optimized for data visualization
- Responsive layout that works on all devices
- Kentucky state seal integration
- Weather-themed icons for visual context
- Real-time data fetch timestamp display

## 📋 Requirements

- Python 3.7 or higher
- Internet connection for API access
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Python Dependencies
```
pandas
requests
```

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/kentucky-weather-dashboard.git
   cd kentucky-weather-dashboard
   ```

2. **Install required packages**
   ```bash
   pip install pandas requests
   ```

3. **Add image assets** (optional)
   Place the following images in the project directory:
   - `Seal_of_Kentucky.png` - Kentucky state seal
   - `sun.png` - Sun icon
   - `rain.png` - Rain icon
   - `wind.png` - Wind icon
   
   *Note: The app will work without these images, using placeholders instead.*

## 💻 Usage

1. **Run the application**
   ```bash
   python app.py
   ```

2. **Access the dashboard**
   - The application will automatically open in your default browser
   - If not, navigate to `http://localhost:8000`

3. **Interact with the dashboard**
   - Select different cities using the radio buttons
   - Change units for temperature, wind speed, and precipitation
   - Hover over charts for detailed information
   - Click on map markers for city-specific data

4. **Stop the server**
   - Press `Ctrl+C` in the terminal

## 🏗️ Project Structure

```
kentucky-weather-dashboard/
│
├── app.py              # Main application file
├── README.md           # Project documentation
├── Seal_of_Kentucky.png # Kentucky state seal (optional)
├── sun.png             # Sun weather icon (optional)
├── rain.png            # Rain weather icon (optional)
└── wind.png            # Wind weather icon (optional)
```

## 🔧 Technical Details

### Data Sources
- **Historical Weather Data**: [Open-Meteo Archive API](https://archive-api.open-meteo.com/)
- **Weather Forecasts**: [Open-Meteo Forecast API](https://api.open-meteo.com/)

### Technologies Used
- **Backend**: Python with HTTP server
- **Frontend**: HTML5, CSS3, JavaScript
- **Charting**: Chart.js 3.7.1
- **Mapping**: Leaflet.js 1.7.1
- **Styling**: Custom CSS with CSS variables
- **Icons**: Base64-encoded images

### Key Features Implementation

1. **Single-File Architecture**
   - All assets are embedded as Base64 strings
   - No external file dependencies required
   - Easy distribution and deployment

2. **Real-Time Data Processing**
   - Fetches last 7 days of historical data
   - Retrieves 7-day weather forecast
   - Synthetic humidity calculation based on wind patterns

3. **Dynamic Visualization**
   - Temperature-based color coding on map
   - Responsive chart updates on unit changes
   - Interactive tooltips and legends

4. **Error Handling**
   - Graceful API failure management
   - Image loading fallbacks
   - Request timeout protection

## 🎨 Customization

### Adding New Cities
Edit the `CITIES` dictionary in `app.py`:
```python
CITIES = {
    'Louisville, KY':    (38.2527,  -85.7585),
    'Lexington, KY':     (38.0406,  -84.5037),
    'Bowling Green, KY': (36.9685,  -86.4808),
    # Add new city:
    'Frankfort, KY':     (38.2009,  -84.8733)
}
```

### Changing the Port
Modify the `PORT` variable in `app.py`:
```python
PORT = 8080  # Default is 8000
```

### Styling Modifications
The dashboard uses CSS variables for easy theming. Key variables include:
- `--bg-primary`: Main background color
- `--accent-primary`: Primary accent color
- `--text-primary`: Main text color

## 🐛 Troubleshooting

### Common Issues

1. **"Address already in use" error**
   - Another application is using port 8000
   - Solution: Change the PORT variable or stop the other application

2. **Images not displaying**
   - Image files are not in the correct directory
   - Solution: Ensure all .png files are in the same folder as app.py

3. **No data displayed**
   - API request failed or no internet connection
   - Solution: Check internet connection and try again

4. **Browser doesn't open automatically**
   - System configuration prevents automatic browser launch
   - Solution: Manually navigate to http://localhost:8000

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Contact

For questions or support, please open an issue in the GitHub repository.

---

Made with ❤️ for Kentucky weather enthusiasts