from enum import Enum


class Rank(Enum):
    ADMIN=0
    APP=1
    USER=2

def api_endpoint():
    return {"api_version":1,"get_session_token":"/api/token","end_point":{"user":{"get_user":"/api/user/<int:id>","registration":"/api/user/registration","update_user_data":"/api/user/<int:id>"},"off":{"registration":"/api/off/registration","get_off":"/api/off/<int:id>","get_off_by_location":"/api/off/location/<str:lat>/<str:lon>","get_off_by_date":"/api/off/date/<str:date>","get_off_by_owner":"/api/off/owner/<int:user>","get_off_by_participant":"/api/off/participant/<int:id>","update_off_data":"/api/off/<int:id>"},"gps":{"registration":"/api/gps/registration","get_gps_point_by_owner":"/api/gps/owner/<int:id>","get_gps_point":"/api/gps/<int:id>","update_gps_point":"/api/gps/<int:id>"}}}