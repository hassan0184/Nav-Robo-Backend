import math


def haversine_distance(lat1, lon1, lat2, lon2):
    radius = 6371 # km
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    return d

def closest_robot(current_rider,i,current_latitude,current_longitude,closest_location,closest_distance):

    if i.get('is_available') == True:
        if i.get('rider_list'):
            if current_rider not in i.get('rider_list'):
                latitude=i.get('position').latitude
                longitude=i.get('position').longitude
                distance = haversine_distance(current_latitude, current_longitude, latitude, longitude)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_location = i
        else:
            latitude=i.get('position').latitude
            longitude=i.get('position').longitude
            distance = haversine_distance(current_latitude, current_longitude, latitude, longitude)
            if distance < closest_distance:
                closest_distance = distance
                closest_location = i
            
    return closest_location,closest_distance