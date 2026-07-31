# API-to-CSV Data Pipeline (Weather Data)

A robust Python data extraction script that consumes the Open-Meteo REST API, handles HTTP and network errors, parses nested JSON responses, normalizes the data into a Pandas DataFrame, and exports the results as a clean CSV file.

## Business Value
This project demonstrates the ability to reliably extract data from external APIs and convert it into a usable tabular format. It includes:
* **Error Handling:** Validates HTTP status codes and API responses to prevent silent failures.
* **Data Transformation:** Flattens complex JSON structures into clean, analytical tables.
* **Production Ready:** Uses standard libraries (`requests`, `pandas`) for reliable execution.

## How to Run
1. Install requirements: `pip install -r requirements.txt`
2. Run the pipeline: `python pipeline.py`
3. Check the root folder for the output `grenoble_weather_forecast.csv`