import numpy as np
import torch
print(torch.__version__)
b = np.array([[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
              [[13, 14, 15, 16], [17, 18, 19, 20], [21, 22, 23, 24]],
              [[25, 26, 27, 28], [29, 30, 31, 32], [33, 34, 35, 36]],
              ])
#
# a = [1, 2]
# print(a)
# print(b, b.shape)
# print(b[:, 0], b[:, 0].shape)
# print(b[:, [0]], b[:, [0]].shape)
# print(b[:, [[0]]], b[:, [[0]]].shape)
# import requests
# requests.post("http://192.168.50.81:5000/LGSVL/LoadScene?scene=SanFrancisco&road_num=1")


import requests

requests.post("http://119.45.188.204:5000/LGSVL/LoadScene?scene=SanFrancisco&road_num=1")

all_state = requests.post("http://119.45.188.204:5000/LGSVL/Status/Environment/State")
print(all_state.text)

