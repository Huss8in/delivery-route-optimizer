# Delivery Route Optimizer

A Python tool to optimize delivery routes using OpenRouteService API. Filters deliveries by area and arranges them in the shortest driving route.

## Features

- Filter deliveries by area name
- Remove duplicate delivery locations
- Optimize route using OpenRouteService Directions API
- Support for different vehicle types (driving-car, cycling-motorbike)
- Export optimized routes to CSV

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your OpenRouteService API key:
   ```
   ORS_API_KEY=your_api_key_here
   ```
   Get your free API key from [OpenRouteService](https://openrouteservice.org/dev/#/signup)

## Usage

Run the example:
```bash
python delivery-route-optimizer.py
```

Or use it in your code:
```python
from delivery_route_optimizer import optimize_delivery_route
import os
from dotenv import load_dotenv

load_dotenv()

df_optimized = optimize_delivery_route(
    csv_file="your_orders.csv",
    area_name="Area Name",
    ors_api_key=os.getenv("ORS_API_KEY"),
    vehicle_type="driving-car",  # or "cycling-motorbike"
    output_csv="optimized_output.csv"
)
```

## CSV Format

Your input CSV should contain at least these columns:
- `deliveryAddress_areaName`: Area/neighborhood name
- `deliveryAddress_lat`: Latitude
- `deliveryAddress_lng`: Longitude

## Requirements

- Python 3.7+
- pandas
- requests
- python-dotenv