from enum import Enum


import random
import string
from math import radians, sin, atan2, sqrt, cos


def distance_between_coord(lat1,lon1,lat2,lon2):
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

class Rank(Enum):
    ADMIN=0
    APP=1
    USER=2

def api_endpoint():
    return {"api_version":1,"end_point":{"photo":{"add_photo":"/api/photo/<int:id_off>","get_photo":"/api/photo/<int:id>","get_photo_off":"/api/photo/off/<int:id>"},"team":{"registration":"/api/team/registration","add_teamate":"/api/team/addteamate/<int:idteam>","remove_teamate":"/api/team/remove/<int:idteam>","get_teamate":"/api/team/teamate/<int:idteam>"},"gps":{"get_gps_point":"/api/gps/<int:id>","get_gps_point_by_owner":"/api/gps/owner/<int:id>","registration":"/api/gps/registration","update_gps_point":"/api/gps/<int:id>"},"off":{"get_off":"/api/off/<int:id>","get_off_by_date":"/api/off/date/<str:date>","get_off_by_location":"/api/off/location/<str:lat>/<str:lon>","get_off_by_owner":"/api/off/owner/<int:user>","get_off_by_participant":"/api/off/participant/<int:id>","get_off_by_team":"/api/off/team/<int:id>","registration":"/api/off/registration","update_off_data":"/api/off/<int:id>"},"user":{"get_user":"/api/user/<int:id>","registration":"/api/user/registration","update_user_data":"/api/user/<int:id>"}},"get_session_token":"/api/token"}


