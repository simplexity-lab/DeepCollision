# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/3 22:04
# @Author  : Chengjie
# @File    : test.py

import requests
import numpy as np

# load scene, just need to load one time
requests.post("http://119.45.188.204:5000/LGSVL/LoadScene?scene=SanFrancisco&road_num=1")

"""
After load the scene using the above code, you can call the status obtain code and environment code for many times.
"""

# get speed only
speed = requests.post("http://192.168.50.81:5000/LGSVL/Status/EGOVehicle/Speed")
print(speed.text)


# change the weather
requests.post("http://119.45.188.204:5000/LGSVL/Control/Weather/Rain?rain_level=Heavy")


# get all the status
r = requests.post("http://192.168.50.81:5000/LGSVL/Status/Environment/State")
a = r.json()

# State returned after one configuration action executed.
state = np.zeros(12)
state[0] = a['x']
state[1] = a['y']
state[2] = a['z']
state[3] = a['rain']
state[4] = a['fog']
state[5] = a['wetness']
state[6] = a['timeofday']
state[7] = a['signal']
state[8] = a['rx']
state[9] = a['ry']
state[10] = a['rz']
state[11] = a['speed']
print(state)
