from datetime import datetime
import random
import string

import requests


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def addRandomOff():
    username = "lhtvbm"
    password="azerty"
    offname = get_random_string(6)
    km = 25
    meetingPoint = random.randint(1,11)
    endPoint = random.randint(1,11)
    loop = 1
    owner = random.randint(1,9)
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
    username = "lhtvbm"
    password = "azerty"
    url = 'http://127.0.0.1:5000/api/gps/registration'
    myobj = {
        'id_owner':random.randint(1,9),
             'latitude': str(random.randint(10000,50000)),
             'longitude': str(random.randint(10000,50000)),
             'detail' : get_random_string(50)
             }
    x = requests.post(url, json=myobj,auth=(username, password))

    print(x.text)

def addRandomUser():
    mail = get_random_string(5) + "@" + get_random_string(5) + '.' + get_random_string(3)
    username = get_random_string(10)
    password = "azerty"
    kikourou_url="kikourou.fr/"+get_random_string(5)
    url = 'http://127.0.0.1:5000/api/user/registration'
    myobj = {'username': username,
             'password': password,
             'mail':mail,
             'kikourou_url':kikourou_url
             }
    x = requests.post(url, json=myobj)

    print(x.text)

def addRandomParticipant():
    off=random.randint(1,11)
    runner = random.randint(2,20)

    url = 'http://127.0.0.1:5000/api/user/registration'
    myobj = {'off': off,
             'runner': runner,
             }
    x = requests.post(url, json=myobj)

    print(x.text)


def jeuTest(admin=False,user=False,off=False,gps=False,participant=False):
    if admin:
        addRandomUser("admin","azerty","a@a.com","kik",0)
    if user:
        for i in range(0,10):
            addRandomUser()
    if off:
        for i in range(0, 10):
            addRandomOff()
    if gps:
        for i in range(0, 10):
            addRandomGPS()

    if participant:
        addRandomParticipant()



def getOff(id):
    username = "lhtvbm"
    password = "azerty"
    PARAMS = {'id': id}
    url = 'http://127.0.0.1:5000/api/off/'+str(id)
    r = requests.get(url=url,json=PARAMS, auth=(username, password))
    print(r.json())

def getOffsdate(d):
    username = "lhtvbm"
    password = "azerty"
    PARAMS = {'date': d}
    url = 'http://127.0.0.1:5000/api/off/date/'+str(d)
    r = requests.get(url=url,json=PARAMS, auth=(username, password))

    for o in r.json():
        print(o)

def getOffsDist(lat,lon,dist):
    username = "lhtvbm"
    password = "azerty"
    PARAMS = {'date': dist}
    url = 'http://127.0.0.1:5000/api/off/location/'+str(lat)+'/'+str(lon)+'/'+str(dist)
    r = requests.get(url=url,json=PARAMS, auth=(username, password))

    for o in r.json():
        print(o['id_off'])

def getOffOwner(o):
    username = "lhtvbm"
    password = "azerty"
    PARAMS = {'date': o}
    url = 'http://127.0.0.1:5000/api/off/owner/'+str(o)
    r = requests.get(url=url,json=PARAMS, auth=(username, password))

    for o in r.json():
        print(o['id_off'])

def getTest(off=False,offsDate=True,offDist=False,owner=False):
    if off:
        getOff(1)

    if offsDate:
        getOffsdate(1592565879)

    if offDist:
        getOffsDist(45.69896679341558,4.745422049136949,50)

    if owner:
        getOffOwner(9)



getTest(False,False,False,True)

jeuTest(False,False,False,False)