import pandas as pd
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def optimize_delivery_route(csv_file, area_name, ors_api_key, vehicle_type="driving-car", output_csv=None):
    """
    Filters deliveries by area, removes duplicates, and returns the delivery addresses
    arranged in shortest driving route using OpenRouteService.

    Uses Optimization API for 4+ points, Directions API for <=3 points.

    Args:
        csv_file (str): Path to the input CSV.
        area_name (str): deliveryAddress_areaName to filter.
        ors_api_key (str): Your ORS API key.
        vehicle_type (str): "driving-car" or "cycling-motorbike".
        output_csv (str, optional): Path to save optimized CSV.

    Returns:
        pd.DataFrame: DataFrame of optimized delivery addresses.
    """
    # Load CSV and filter by area
    df = pd.read_csv(csv_file)
    df_filtered = df[df["deliveryAddress_areaName"] == area_name].drop_duplicates(
        subset=["deliveryAddress_lat", "deliveryAddress_lng"]
    ).reset_index(drop=True)

    if df_filtered.empty:
        print(f"No deliveries found for area: {area_name}")
        return pd.DataFrame()

    # Build coordinates
    coords = [[row["deliveryAddress_lng"], row["deliveryAddress_lat"]] for _, row in df_filtered.iterrows()]
    
    # Use Directions API for small datasets
    url = "https://api.openrouteservice.org/v2/directions/" + vehicle_type + "/geojson"
    headers = {"Authorization": ors_api_key, "Content-Type": "application/json"}
    body = {"coordinates": coords, "instructions": False}

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()

    df_route = df_filtered.copy()

    # if len(coords) <= 3:
    #     # Use Directions API for small datasets
    #     url = "https://api.openrouteservice.org/v2/directions/" + vehicle_type + "/geojson"
    #     headers = {"Authorization": ors_api_key, "Content-Type": "application/json"}
    #     body = {"coordinates": coords, "instructions": False}

    #     response = requests.post(url, headers=headers, json=body)
    #     response.raise_for_status()

    #     df_route = df_filtered.copy()
    # else:
    #     # Use Optimization API for larger datasets
    #     jobs = [{"id": i, "location": coord} for i, coord in enumerate(coords)]
    #     vehicles = [{"id": 1, "profile": vehicle_type, "start": coords[0], "end": None}]
    #     payload = {"jobs": jobs, "vehicles": vehicles}
    #     headers = {"Authorization": ors_api_key, "Content-Type": "application/json"}
    #     url = "https://api.openrouteservice.org/optimization"

    #     response = requests.post(url, headers=headers, data=json.dumps(payload))
    #     response.raise_for_status()
    #     data = response.json()

    #     steps = data["routes"][0]["steps"]
    #     ordered_indices = [step["job"] for step in steps if "job" in step]
    #     df_route = df_filtered.iloc[ordered_indices].reset_index(drop=True)

    if output_csv:
        df_route.to_csv(output_csv, index=False)
        print(f"Optimized CSV saved to {output_csv}")

    return df_route


# ===========================
# Example usage
# ===========================
if __name__ == "__main__":
    # Get API key from environment variable
    ORS_API_KEY = os.getenv("ORS_API_KEY")

    if not ORS_API_KEY:
        raise ValueError("ORS_API_KEY not found in environment variables. Please set it in .env file.")

    # Optimize route for El Rehab area
    df_optimized = optimize_delivery_route(
        csv_file="el_rehab_orders.csv",
        area_name="El Rehab",
        ors_api_key=ORS_API_KEY,
        # vehicle_type="cycling-motorbike",  # Use "driving-car" (default) or "cycling-motorbike"
        output_csv="el_rehab_orders_optimized.csv"
    )

    print(df_optimized)
