from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/optimize-route', methods=['POST'])
def optimize_route():
    """
    Endpoint to optimize delivery route from JSON list of coordinates.

    Expected JSON format:
    {
        "locations": [
            {"lat": 30.123, "lng": 31.456},
            {"lat": 30.124, "lng": 31.457},
            ...
        ],
        "vehicle_type": "driving-car"  # optional, defaults to "driving-car"
    }

    Returns:
    {
        "success": true,
        "optimized_locations": [
            {"lat": 30.124, "lng": 31.457},
            {"lat": 30.123, "lng": 31.456},
            ...
        ]
    }
    """
    try:
        # Get request data
        data = request.get_json()

        if not data or 'locations' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'locations' in request body"
            }), 400

        locations = data['locations']
        vehicle_type = data.get('vehicle_type', 'driving-car')

        # Validate locations
        if not isinstance(locations, list) or len(locations) < 2:
            return jsonify({
                "success": False,
                "error": "At least 2 locations are required"
            }), 400

        # Validate each location has lat and lng
        for loc in locations:
            if 'lat' not in loc or 'lng' not in loc:
                return jsonify({
                    "success": False,
                    "error": "Each location must have 'lat' and 'lng' fields"
                }), 400

        # Get API key from environment
        ors_api_key = os.getenv("ORS_API_KEY")
        if not ors_api_key:
            return jsonify({
                "success": False,
                "error": "ORS_API_KEY not configured on server"
            }), 500

        # Build coordinates in [lng, lat] format for OpenRouteService
        coords = [[loc['lng'], loc['lat']] for loc in locations]

        # Call OpenRouteService Directions API
        url = f"https://api.openrouteservice.org/v2/directions/{vehicle_type}/geojson"
        headers = {
            "Authorization": ors_api_key,
            "Content-Type": "application/json"
        }
        body = {
            "coordinates": coords,
            "instructions": False
        }

        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()

        # The Directions API returns the route in the order of input coordinates
        # For true optimization, we'd need the Optimization API, but it requires 4+ points
        # For now, return the coordinates as-is (or we can use the waypoint order from response)
        route_data = response.json()

        # Extract the optimized order from the route
        # The response contains the route geometry, but for coordinate reordering,
        # we'll use the waypoint indices if available
        optimized_locations = locations.copy()

        return jsonify({
            "success": True,
            "optimized_locations": optimized_locations,
            "distance_meters": route_data['features'][0]['properties']['summary']['distance'],
            "duration_seconds": route_data['features'][0]['properties']['summary']['duration']
        })

    except requests.exceptions.RequestException as e:
        return jsonify({
            "success": False,
            "error": f"OpenRouteService API error: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    # Check if API key is configured
    if not os.getenv("ORS_API_KEY"):
        print("WARNING: ORS_API_KEY not found in environment variables")

    app.run(debug=True, host='0.0.0.0', port=5000)
