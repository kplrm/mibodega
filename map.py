import folium
import json
from ipregistry import IpregistryClient, NoCache # Without cache

# Get Client location
# Using ipregistry
client = IpregistryClient("2cc3d6z6ct2weq", cache=NoCache()) # Without cache
ipInfo = client.lookup()
user_latitude = ipInfo.location['latitude']
user_longitude = ipInfo.location['longitude']
user_postal = ipInfo.location['postal']
#print(user_latitude)
#print(user_longitude)
#print(user_postal)
#print(ipInfo)

# Create map object
m = folium.Map(location=[user_latitude,user_longitude],zoom_start=16) # Center point in the map
# Global tooltip
tooltip = 'Ver más'
# Create markers
folium.Marker([52.50086,13.33061], 
               popup='<strong>Bodega1</strong>', # what happens on click
               tooltip=tooltip, # what happens when hover
               icon=folium.Icon(color='orange',icon='shopping-cart')).add_to(m), # icons from glyphicon

# Future: add geojson to create a geofence where the stores can deliver
#overlay = ...load json ....
#folium.GeoJson(overlay,name='coverage_area').add_to(m)

# Generate map
m.save('map.html')