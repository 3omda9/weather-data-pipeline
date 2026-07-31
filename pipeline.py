import requests
import pandas as pd
from datetime import datetime


def fetch_weather_data():
    # Fetching 7-day forecast for Grenoble, France
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 45.1885,   # Grenoble Latitude
        "longitude": 5.7245,   # Grenoble Longitude
        "hourly": "temperature_2m,precipitation",
        "timezone": "Europe/Paris"
    }
    
    print("Connecting to Open-Meteo API...")
    
    try:
        # 1. Network Request with 10s Timeout
        response = requests.get(url, params=params, timeout=10)
        
        # 2. Check HTTP status (4xx / 5xx)
        response.raise_for_status()
        
        # 3. Parse JSON response
        data = response.json()

    # --- DEFENSIVE ERROR HANDLING ---
    except requests.exceptions.Timeout:
        print("Error: The request timed out. Open-Meteo server is taking too long to respond.")
        return None
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: Server returned status code {response.status_code}. Detail: {err}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"Network Error: Unable to connect to API. Detail: {err}")
        return None
    except ValueError:
        print("Data Error: API response was not valid JSON.")
        return None

    # --- DATA VALIDATION ---
    if "hourly" not in data or "time" not in data["hourly"]:
        print("Validation Error: API response missing expected 'hourly' schema.")
        return None

    # --- EXTRACTION & TRANSFORMATION ---
    hourly_data = data["hourly"]
    times = hourly_data.get("time", [])
    temperatures = hourly_data.get("temperature_2m", [])
    precipitation = hourly_data.get("precipitation", [])
    
    records = []
    for i in range(len(times)):
        records.append({
            "Datetime": times[i],
            "Temperature (C)": temperatures[i] if i < len(temperatures) else None,
            "Precipitation (mm)": precipitation[i] if i < len(precipitation) else None
        })

    df = pd.DataFrame(records)

    # --- DATETIME CLEANUP ---
    if not df.empty and "Datetime" in df.columns:
        # Convert strings to Pandas Datetime objects
        dt_series = pd.to_datetime(df["Datetime"], errors="coerce")
        # Format cleanly as YYYY-MM-DD HH:MM for both CSV export and terminal output
        df["Datetime"] = dt_series.dt.strftime("%Y-%m-%d %H:%M")

    return df


if __name__ == "__main__":
    df_weather = fetch_weather_data()
    
    if df_weather is not None and not df_weather.empty:
        today_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"grenoble_weather_{today_date}.csv"

        # 1. Export Clean CSV
        df_weather.to_csv(filename, index=False)

        # 2. Compute Summary Insights
        try:
            temps = pd.to_numeric(df_weather["Temperature (C)"], errors="coerce")
            precip = pd.to_numeric(df_weather["Precipitation (mm)"], errors="coerce").fillna(0)
            
            start = df_weather["Datetime"].min()
            end = df_weather["Datetime"].max()
            avg_temp = temps.mean()
            min_temp = temps.min()
            max_temp = temps.max()
            total_precip = precip.sum()
            rainy_hours = int((precip > 0).sum())

            print(f"\nExtracted {len(df_weather)} hourly records for {start} to {end}.")
            print(f"Average: {avg_temp:.1f}°C — Low: {min_temp:.1f}°C, High: {max_temp:.1f}°C")
            print(f"Total expected precipitation: {total_precip:.1f} mm across {rainy_hours} hour(s).")

            if total_precip == 0 or rainy_hours == 0:
                print("Summary: Dry conditions expected; no precipitation forecast.")
            elif total_precip < 2:
                print("Summary: Light showers possible during the forecast period.")
            else:
                print("Summary: Noticeable precipitation expected — plan accordingly.")

        except Exception as e:
            print(f"Success! Data saved to {filename} (Summary calculation skipped: {e})")

        print(f"\nSaved to: {filename}")
        print("\nData Preview:")
        print(df_weather.head().to_string(index=False))

    else:
        print("Pipeline Execution Failed. No data was returned from the weather API.")