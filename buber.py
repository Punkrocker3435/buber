﻿"""
Filename: buber.py

### Description: ###
An application to provide information onspecific bus numbers
through Colchester, Essex, UK

This will be done with the help of the transportapi
https://developer.transportapi.com/

Map plotting is via folium and teh following tutorial
https://www.geeksforgeeks.org/python-plotting-google-map-using-folium-package/?ref=rp

### Basic Decomposition: - "Eat the elephant one bite at a time" ###
1. Hold API key and Program ID so we dont need to keep entering it or URLS - DONE
2. Retreive data for the Number 65 bus heading outbound - DONE
3. Take user input for bus number. Only allow then to enter the buses we have supplied - DONE
    3.1 If user enter an incorrect bus number twice offer them the option to find the bus number by final destination
4. User enters a bus number. We are only using a subset of buses for Colchester. "64", "65", "67", "88", "104".
We have atcocodes for these stops and can define start and end points
5. User enters a destination - Program tells user what bus goes there and when the next departure is (from Town Center)
6. Display data to user on a map. - Milestone 1

### Questions the app should be able to answer ###
1. When is the next bus - enter bus number return next bus time for town center location
2. Given a location display what busses go there. if you select a bus then display the time of the next bus

### Future work if we have time ###
1. Make a windows graphical app
2. Make an android graphical app
3. Deploy ity to a virtual android phone and run it

Tools/Frameworks
1. Kivy Framework - https://realpython.com/mobile-app-kivy-python/
2. Android dev app - https://developer.android.com/studio

TRANSPORT API
1. This URL identifies One particular bus service, identified by line and operator - Function bus_service(bus_number)
It can be used to get the BUS_START and BUS_END of the journey
RETURNS: bus_number, outbound, inbound

'https://transportapi.com/v3/uk/bus/services/FESX:65.json?app_id=9e91c41c&app_key=ebaa5b9461f7f42778146f909073d17a'


2. Bus departures at a given bus stop (live) - Function next_bus_live()
By passing in the atcocode for the bus stop you can get live departure information for that stop
##PARAMETERS TO PROVIDE
atcocode

##INTERESTING VALUES IN RETURENED DATA
line_name, direction, status, best_departure_estimate

This returns any bus operating company utilising that stop
Data is returned in a dictionary of x lists where x is the number of buses that use that stop

First part of data recieved from url pull

{'65': [{'mode': 'bus', 'line': '65', 'line_name': '65', 'direction': 'Highwoods Tesco', 'operator': 'FESX',
'date': '2020-05-19', 'expected_departure_date': '2020-05-19', 'aimed_departure_time': '09:32',
'expected_departure_time': '09:30', 'best_departure_estimate': '09:30',
'status': {'cancellation': {'value': False, 'reason': None}}, 'source': 'FirstTicketerNationwide', 'dir': 'outbound',
'operator_name': 'First Essex',
'id': <URL>>

'https://transportapi.com/v3/uk/bus/stop/1500AA20/live.json?app_id=9e91c41c&app_key=ebaa5b9461f7f42778146f909073d17a&group=route&nextbuses=yes'

3. Bus departures at a given bus stop (timetabled) - Function next_bus_timetabled()
This URL gives you the timetabled information for that particulatr stop
##PARAMETERS TO PROVIDE
date, time, atcocode

https://transportapi.com/v3/uk/bus/stop/1500AA20/2020-05-15/07:10/timetable.json?app_id=9e91c41c&app_key=ebaa5b9461f7f42778146f909073d17a&group=route

4. The route of one specific bus - Function bus_route()
This gives every stop the bus will make between its atcocode bust stop and the final destination

##PARAMETERS TO PROVIDE
date, time, atcocode

https://transportapi.com/v3/uk/bus/route/FESX/65/outbound/1500AA20/2020-05-15/07:10/timetable.json?app_id=9e91c41c&app_key=ebaa5b9461f7f42778146f909073d17a&edge_geometry=false&stops=ALL

"""
# Import Libraries we need
import urllib3
import json
import pandas as pd
import folium
import sys

# Constants
APP_ID = '9e91c41c'
API_KEY = 'ebaa5b9461f7f42778146f909073d17a'
BASE_URL = 'https://transportapi.com/v3/uk/bus/'

def main():

    # Ask the user to input a bus number
    what_bus = input("What bus do you want?: ")

    # Validate if it is a service we support
    bus = validate_bus(what_bus)
    # DEBUG - TO BE REMOVED
    print("From validate_bus() we got " + str(bus))
    # only work on valid bus routes supported by our application
    if bus != "Unsupported service":
        # Get some information on the bus_service
        bus_serv, outbound, inbound = bus_service(bus)
        print("From bus_service(): Bus Number " + bus_serv + " , Traveling from: " + outbound + ", Traveling to: " + inbound)
    else:
        sys.exit("Unsupported service at this time. Goodbye")
        
    stop, lat, long = bus_route(what_bus)
    print("DEBUG 0: Returned from  bus_route(). Last Stop is " + stop + " , " + str(lat) + " , " +  str(long))

def validate_bus(what_bus):
    # Function to validate we have a valid bus for our application
    # Evaluate the user input
    # Is the users bus selection in our buses list? if yes, then procced
    # These are only First Essex buses
    buses = ["64", "65", "67", "70", "74B", "88", "104"]

    if what_bus in buses:
        print("The number " + str(what_bus) + " is a bus service we support")
        return what_bus
    else:
        print("We do not support bus service number " + str(what_bus) + " at this time")
        return "Unsupported service"

def bus_service(bus_number):

    bus_num = bus_number
    # Try out retrieving a URL via urllib3
    # Use %s to pass in the Constants and Variables to make up the URL
    url = BASE_URL + '/services/FESX:%s.json?app_id=%s&app_key=%s' % (bus_num, APP_ID, API_KEY)
    http = urllib3.PoolManager()

    # Request our data, and decode the json data returned
    response = http.request('GET', url)
    bus_service_dict = json.loads(response.data.decode('utf-8'))
    outbound = bus_service_dict['directions'][0]['destination']['description']
    inbound = bus_service_dict['directions'][1]['destination']['description']

    # Return the bus number and its endpoints
    return bus_num, outbound, inbound

def next_bus_live():
    # URL to retrieve data. This may need more paramaters to be passed in. Currently only APP_ID and API_KEY
    url = BASE_URL + '/stop/1500AA20/live.json?app_id=%s&app_key=%s&group=route&nextbuses=yes' % ( APP_ID, API_KEY)

    http = urllib3.PoolManager()

    # Request our data, and decode the json data returned
    response = http.request('GET', url)
    next_bus_live_dict = json.loads(response.data.decode('utf-8'))
    print(next_bus_live_dict)


def next_bus_timetabled():
    # URL to retrieve data. This may need more paramaters to be passed in. Currently only APP_ID and API_KEY
    url = BASE_URL + '/stop/1500AA20/2020-05-15/07:10/timetable.json?app_id=%s&app_key=%s' % (APP_ID, API_KEY)

    http = urllib3.PoolManager()

    # Request our data, and decode the json data returned
    response = http.request('GET', url)
    next_bus_timetabled_dict = json.loads(response.data.decode('utf-8'))
    print(next_bus_timetabled_dict)

def bus_route(bus_number):

    bus = bus_number
    # Try out retrieving a URL via urllib3
    # Use %s to pass in the Constants and Variables to make up the URL
    url = BASE_URL + '/route/FESX/%s/inbound/1500IM2456B/2020-05-21/19:25/timetable.json?app_id=%s&app_key=%s' \
                     '&edge_geometry=false&stops=ALL' % (bus, APP_ID, API_KEY)

    http = urllib3.PoolManager()

    # Request our data, and decode the json data returned
    response = http.request('GET', url)
    bus_route_dict = json.loads(response.data.decode('utf-8'))
    x = 0
    # iterate through our dictionary giving us the bus stop names and their
    # lat and long so we can plot them on a map.
    #while x < len(bus_route_dict['stops']):
    #    print(x)
    for stop in bus_route_dict['stops']:
        bus_stand = stop['stop_name']
        lat = stop['latitude']
        long = stop['longitude']
        print("DEBUG 4: " + bus_stand + " , " + str(lat) + " , " + str(long))
        map_it(bus_stand, lat, long)
    return bus_stand, lat, long

def map_it(bus_stand, lat, long):

    # Folium mapping
    stop = bus_stand
    latitude = lat
    longitude = long

    #while True:
    print("DEBUG 5: " + stop + " , " + str(latitude) + " , " + str(longitude))
    #for stop in my_dict['stops']:


        #testing out folium
        ##route_65 = folium.Map(location=[stop['latitude'], stop['longitude']], zoom_start=20)
        # Pass a string in popup parameter
        ##folium.Marker([stop['latitude'], stop['longitude']], popup=stop['stop_name']).add_to(route_65)
        # Save the output to an html file
        ##route_65.save(" route_65.html ")

        # Import location csv data into pandas
        ##df_location = pd.read_csv('location.csv')
        # Check we got it
        ##print(df_location.head())

        # Prep data for the map
        #locations = df_location[['lat', 'long']]
        #locationlist = locations.values.tolist()
        #print(len(locationlist))

        # Now build the map
        #route_65 = folium.Map(location=[51.89518, 0.89575 ], zoom_start=14)
        #for point in range(0, len(locationlist)):
            #folium.Marker(locationlist[point], popup=stop['stop_name']).add_to(route_65)
            #route_65.save(" route_65.html ")


if __name__ == '__main__':
    main()