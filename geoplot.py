import re
import json
import pandas as pd
@@ -26,7 +25,6 @@
# HTML template for Cesium visualization
# This template defines the structure and behavior of the Cesium-based visualization.
# It includes functions for interpolating colors, determining pixel sizes, and processing time-series data.

geoplot_template = """
<!doctype html>
<html lang="en">
@@ -41,9 +39,11 @@
  <body>
    <div id="cesiumContainer"></div>
    <script>
      // Setup Cesium viewer
      Cesium.Ion.defaultAccessToken = '$accessToken';
      const viewer = new Cesium.Viewer('cesiumContainer');
      // Interpolate between two colors based on a factor
      function interpolateColor(color1, color2, factor) {
        const result = new Cesium.Color();
        result.red = color1.red + factor * (color2.red - color1.red);
@@ -53,16 +53,19 @@
        return result;
      }
      // Get color based on value (between blue and red)
      function getColor(value, min, max) {
        const factor = (value - min) / (max - min);
        return interpolateColor(Cesium.Color.BLUE, Cesium.Color.RED, factor);
      }
      // Get pixel size based on value
      function getPixelSize(value, min, max) {
        const factor = (value - min) / (max - min);
        return 100 * (1 + factor);
      }
      // Process GeoJSON data to build a time-series map
      function processTimeSeriesData(geoJsonData) {
        const timeSeriesMap = new Map();
        let minValue = Infinity;
@@ -86,6 +89,7 @@
        return { timeSeriesMap, minValue, maxValue };
      }
      // Create Cesium entities for the time series
      function createTimeSeriesEntities(timeSeriesData, startTime, stopTime) {
        const dataSource = new Cesium.CustomDataSource('AgentTorch Simulation');
@@ -105,6 +109,7 @@
            },
          });
          // Add each time sample
          timeSeries.forEach(({ time, value, coordinates }) => {
            const position = Cesium.Cartesian3.fromDegrees(coordinates[0], coordinates[1]);
            entity.position.addSample(time, position);
@@ -121,6 +126,7 @@
        return dataSource;
      }
      // Load and visualize the time series data
      const geoJsons = $data;
      const start = Cesium.JulianDate.fromIso8601('$startTime');
      const stop = Cesium.JulianDate.fromIso8601('$stopTime');
@@ -133,6 +139,7 @@
      viewer.timeline.zoomTo(start, stop);
      // Load all GeoJSON datasets
      for (const geoJsonData of geoJsons) {
        const timeSeriesData = processTimeSeriesData(geoJsonData);
        const dataSource = createTimeSeriesEntities(timeSeriesData, start, stop);
@@ -144,17 +151,12 @@
</html>
"""

# Helper function to extract nested property from state based on path
# This function uses the get_by_path utility to navigate nested dictionaries.

# Helper function to extract nested property from the simulation state
def read_var(state, var):
    """Helper to extract nested property from state based on path."""
    return get_by_path(state, re.split("/", var))

# GeoPlot class
# This class encapsulates the logic for generating GeoJSON and HTML visualizations.
# It takes configuration and visualization options as input.

# GeoPlot class for generating visualization outputs
class GeoPlot:
    def __init__(self, config, options):
        """Initialize GeoPlot with config and visualization options."""
@@ -173,24 +175,21 @@ def __init__(self, config, options):
            options["visualization_type"],
        )

    # Render the trajectory to a GeoJSON and HTML visualization
    # This method processes the state trajectory to generate GeoJSON features and an HTML file.
    # It extracts coordinates and property values, generates timestamps, and constructs GeoJSON features.

    def render(self, state_trajectory):
        """Render the trajectory to a GeoJSON and HTML visualization."""
        """Render the trajectory to GeoJSON and HTML visualization."""
        coords, values = [], []
        name = self.config["simulation_metadata"]["name"]
        geodata_path, geoplot_path = f"{name}.geojson", f"{name}.html"

        # Extract coordinates and property values from final states
        # Extract final state coordinates and properties
        for i in range(0, len(state_trajectory) - 1):
            final_state = state_trajectory[i][-1]
            coords = np.array(read_var(final_state, self.entity_position)).tolist()
            values.append(
                np.array(read_var(final_state, self.entity_property)).flatten().tolist()
            )

        # Start time for the simulation
        start_time = pd.Timestamp.utcnow()

        # Generate timestamps spaced by step_time
@@ -204,7 +203,7 @@ def render(self, state_trajectory):

        geojsons = []

        # Construct GeoJSON features for each coordinate
        # Construct GeoJSON features for visualization
        for i, coord in enumerate(coords):
            features = []
            for time, value_list in zip(timestamps, values):
@@ -221,14 +220,11 @@ def render(self, state_trajectory):
                })
            geojsons.append({"type": "FeatureCollection", "features": features})

        # Write GeoJSON file
        # Write GeoJSON output file
        with open(geodata_path, "w", encoding="utf-8") as f:
            json.dump(geojsons, f, ensure_ascii=False, indent=2)

        # Fill the HTML template with real data and token
        # The HTML file is generated by substituting values into the Cesium template.
        # It includes the Cesium token, start and stop times, GeoJSON data, and visualization type.

        # Generate HTML file by substituting template values
        tmpl = Template(geoplot_template)
        with open(geoplot_path, "w", encoding="utf-8") as f:
            f.write(
@@ -240,3 +236,4 @@ def render(self, state_trajectory):
                    "visualType": self.visualization_type,
                })
            )

