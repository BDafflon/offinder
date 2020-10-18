from datetime import datetime
import random
import string

import requests


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def addRandomOff():
    username = "zkdtxk"
    password="azerty"
    offname = get_random_string(6)
    km = 25
    meetingPoint = 1
    endPoint = 1
    loop = 1
    owner = 8
    gpx_url = ""
    dplus = 560
    after = 1
    estimateTime = 120
    detail = "Super Off "+get_random_string(6)
    public = 1
    now = datetime.now()

    dateoff = datetime.timestamp(now)


    url = "http://127.0.0.1:5000/api/offs/registration"
    myobj = {'username': username,
            'password': password,
            'offname': offname,
            'km': km,
             'id_endpoint':endPoint,
             'id_meetingpoint':meetingPoint,
            'loop':loop,
             'id_user':owner,
             'gpx_url':gpx_url,
             'dplus':dplus,
             'after':after,
             'estimateTime':estimateTime,
             'detail':detail,
             'public':public,
             'limitParticipants':10,
             'dateoff':dateoff
            }
    print(myobj)
    x = requests.post(url, json=myobj,auth=(username, password))

    print(x.text)

def addRandomGPS():
    username = "zkdtxk"
    password = "azerty"
    url = 'http://127.0.0.1:5000/api/gps/registration'
    myobj = {
        'id_owner':8,
             'latitude': str(random.randint(10000,50000)),
             'longitude': str(random.randint(10000,50000)),
             'detail' : get_random_string(50)
             }
    x = requests.post(url, json=myobj,auth=(username, password))

    print(x.text)

def addRandomUser(username="runneur",password="azerty",mail="a@a.com",kikourou_url="kikourou",rank=2):
    url = 'http://127.0.0.1:5000/api/user/registration'
    myobj = {'username': username,
             'password': password,
             'mail':mail,
             'kikourou_url':kikourou_url
             }
    x = requests.post(url, json=myobj)

    print(x.text)

def jeuTest(admin=False,user=False,off=False,gps=False):
    if admin:
        addRandomUser("admin","azerty","a@a.com","kik",0)
    if user:
        for i in range(0,10):
            addRandomUser(get_random_string(6),"azerty",get_random_string(5)+"@"+get_random_string(5)+'.'+get_random_string(3))
    if off:
        addRandomOff()
    if gps:
        addRandomGPS()

jeuTest(False,False,False,True)