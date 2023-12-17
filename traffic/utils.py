
from collections import defaultdict
import json

def grouped_schedule(data):
    group_data = defaultdict(list)
    if len(data) <0:
        return []
    for result in data:
        group_data[result["route_detail"]['name']].append({'seats':result["seats"], 'vehicle':result['vehicle'],
                        'driver':result['driver'], 'schedule_date': result['schedule_date'],'destination':result['route_detail']['dest']})

    return group_data

def gen_seat(no):
    seats=[{"seat_number":x,"is_available":True} for x in range(1,no+1)]
    return seats