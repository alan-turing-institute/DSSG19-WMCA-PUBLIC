import requests
import xml.etree.ElementTree as ET
from datetime import datetime,timedelta
from utils import *
import csv


# class Trip:
#     def __init__(self, trip_id, total_time, walk_time,
#                  transfer_wait_time, initial_wait_time, transit_time, walk_dist, transit_dist, total_dist,
#                  num_transfers, fare):
#         self.trip_id = trip_id
#         self.total_time = total_time
#         self.walk_time = walk_time
#         self.transfer_wait_time = transfer_wait_time
#         self.initial_wait_time = initial_wait_time
#         self.transit_time = transit_time
#         self.walk_dist = walk_dist
#         self.transit_dist = transit_dist
#         self.total_dist = total_dist
#         self.num_transfers = num_transfers
#         self.fare = fare


def request_otp(host_url, lat_oa, lat_poi, lon_oa, lon_poi, date, time):
    url = host_url + '/otp/routers/default/plan?'
    params = {
        "fromPlace": f"{lat_oa},{lon_oa}",
        "toPlace": f"{lat_poi},{lon_poi}",
        "date": f"{date}",
        "time": f"{time}",
        "mode": "TRANSIT,WALK",
        "arriveBy": "false",
        "numItineraries": "1"}
    # Passing header instructions forces OTP to return xml
    # or json
    # vectorized_resp = np.vectorize(lambda url={'accept': 'application/xml'}: requests.get(url,params,headers={'accept': 'application/xml'}))
    # resp=vectorized_resp(df.URL)
    resp = requests.get(url=url,
                        params=params,
                        headers={'accept': 'application/xml'})
    return resp


def parse_response(response, date, time):
    xml = ET.fromstring(response.content)
    departure_time = None
    arrival_time = None
    total_time = None
    walk_time = None
    transfer_wait_time = None
    transit_time = None
    walk_dist = None
    transit_dist = None
    total_dist = None
    num_transfers = None
    initial_wait_time = None
    fare = None
    query_time = datetime.strptime(' '.join([date, time]), '%Y-%m-%d %H:%M')
    if xml.find('error').find('msg') is not None:
        if xml.find('error').find('message').text in "TOO_CLOSE":
            departure_time = query_time
            arrival_time = query_time
            total_time = 0.0
            walk_time = 0.0
            transfer_wait_time = 0.0
            transit_time = 0.0
            walk_dist = 0.0
            transit_dist = 0.0
            total_dist = 0.0
            num_transfers = 0
            initial_wait_time = 0.0
            print("Too close")
            
    else:
        plan = xml.find('plan')
        for itineraries in plan.findall('itineraries'):
            if itineraries.find(
                    'itineraries') is not None:  # Note that this line discards error xmls, where there was no route
                for itinerary in itineraries.findall('itineraries'):
                    departure_time = datetime.fromtimestamp(float(itinerary.find('startTime').text) / 1000)
                    departure_time += timedelta(hours=1)
                    arrival_time = datetime.fromtimestamp(float(itinerary.find('endTime').text) / 1000)
                    arrival_time += timedelta(hours=1)
                    total_time = float(itinerary.find('duration').text)
                    walk_time = float(itinerary.find('walkTime').text)
                    transfer_wait_time = float(itinerary.find('waitingTime').text)
                    transit_time = float(itinerary.find('transitTime').text)
                    walk_dist = float(itinerary.find('walkDistance').text)
                    num_transfers = int(itinerary.find('transfers').text)

                    for legs in itinerary.findall('legs'):
                        if legs.find(
                                'legs') is not None:
                            for leg in legs.findall('legs'):
                                if total_dist is None:
                                    total_dist = 0.0
                                total_dist = total_dist + float(leg.find('distance').text)
                    if itinerary.find('fare') is not None:
                        fare_obj = itinerary.find('fare')
                        if fare_obj.find('details') is not None:
                            fare = float(fare_obj.find('details').find('regular').find('price').find(
                                'cents').text) / 100

                    # capture the wait time before the first bus arrives

                    initial_wait_time = (departure_time - query_time).total_seconds()
                    transit_dist = total_dist - walk_dist            

    return departure_time, arrival_time, total_time, walk_time, transfer_wait_time, initial_wait_time, transit_time, walk_dist, transit_dist, total_dist, num_transfers, fare
