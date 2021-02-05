from django.shortcuts import render, get_object_or_404
from .models import Measurement
from .forms import MeasurementModelForm
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from .utils import get_geo, get_center_coordinates, get_zoom, get_ip_address
import folium

def calculate_distance_view (request) :
    
    # initial values 
    distance    = None
    destination = None
    obj         = get_object_or_404(Measurement, id=1)
    form        = MeasurementModelForm(request.POST or None)
    geolocator  = Nominatim(user_agent='gis')
    
    # temp ip address for testing
    ip                      = "66.57.97.8"
    # ip                      = get_ip_address(request)
    country, city, lat, lon = get_geo(ip)
    location                = geolocator.geocode(city)
    
    # Location Coordinates
    pointA                  = (lat, lon)

    # Initial Folium Map
    m = folium.Map(width=800, height=500, location=get_center_coordinates(lat, lon))
    # Location Marker
    folium.Marker([lat, lon], tooltip="Click for more", popup=city["city"], icon=folium.Icon(color="purple")).add_to(m)

    if form.is_valid():
        instance      = form.save(commit=False)
        destination_  = form.cleaned_data.get("destination")
        destination   = geolocator.geocode(destination_)
        
        # Destination Coordinates
        d_lat         = destination.latitude
        d_lon         = destination.longitude
        pointB        = (d_lat, d_lon)
        
        # Distance calculation
        distance      = round(geodesic(pointA, pointB).km, 2)
        
        # Folium Map modification
        m = folium.Map(width=800, height=500, location=get_center_coordinates(lat, lon, d_lat, d_lon), zoom_start=get_zoom( distance ) )
        
        # Location Marker
        folium.Marker([lat, lon], tooltip="Click for more", popup=city["city"], icon=folium.Icon(color="purple")).add_to(m)
        
        # Destination Marker
        folium.Marker([d_lat, d_lon], tooltip="Click for more", popup=destination, icon=folium.Icon(color="red", icon="cloud")).add_to(m)

        # Draw line 
        line = folium.PolyLine(locations=[pointA, pointB], weight=2, color="blue")
        m.add_child(line)
        instance.location    = location
        instance.distance    = distance
        instance.save()

    m = m._repr_html_()

    context = {
        'distance'    : distance,
        'form'        : form,
        'map'         : m,
        'destination' : destination,
    }

    return render(request, "measurements/main.html", context)