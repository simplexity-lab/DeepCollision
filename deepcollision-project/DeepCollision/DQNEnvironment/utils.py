import json

import requests
import numpy as np
import math
import random

import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple
from itertools import count
from PIL import Image

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T

# T.Resize(144, interpolation=Image.CUBIC),  # (size * height / width, size)
resize = T.Compose([T.ToPILImage(),

                    T.ToTensor()])

# if gpu is to be used
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device = torch.device("cpu")

"""
Input extraction
"""


def get_current_state():
    r = requests.get("http://192.168.1.239:5000/LGSVL/Status/CenterCamera")

    image = np.ascontiguousarray(r.json()['index'], dtype=np.float32)  # 内存连续，加速运算
    print(image.shape)

    # Transpose it into torch order (CHW)
    print('transposing')
    image = image.transpose((2, 0, 1))
    print(image.shape)
    image = torch.from_numpy(image)
    # print('image shape: ', image.shape)
    # print('resize shape: ', np.array(resize(image)).shape)
    return resize(image).unsqueeze(0).to(device)


def get_action_space():
    # json_file = open('../../RESTfulAPIProcess/RESTful_API_old.json', 'r')
    json_file = open('D:/RTCM COPY/Autonomous Car/LGSVL/LGSVLProject/RESTfulAPIProcess/RESTful_API.json', 'r')
    content = json_file.read()
    restful_api = json.loads(s=content)
    return restful_api


# Display
def show_iteration(iteration):
    print('-------------------------------------------------')
    print('+                 iteration: ', iteration, '                +')
    print('-------------------------------------------------')


if __name__ == '__main__':
    init_state = get_current_state()
    print(init_state.shape)
    get_action_space()

    print(hyperparameters['GAMMA'])
