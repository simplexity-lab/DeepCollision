# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/1 11:38
# @Author  : Chengjie
# @File    : replay2.py


import pandas as pd
import socket
import time
from DeepCollision.DQNEnvironment.utils import *


# requests.post("http://192.168.50.81:5000/LGSVL/LoadScene?scene=SanFrancisco&road_num=1")


def get_environment_state():
    r = requests.get("http://192.168.50.81:5000/LGSVL/Status/Environment/State")
    a = r.json()
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

    return state


# action_space = get_action_space()['command']
# scenario_space = get_action_space()['scenario_description']
# N_ACTIONS = action_space['num']
# N_STATES = get_environment_state().shape[0]
# ENV_A_SHAPE = 0
#
# HOST = '192.168.50.51'  # or 'localhost'
# PORT = 6001
# ADDR = (HOST, PORT)
#
# ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# ss.connect(ADDR)

latitude_space = []
check_num = 5  # here depend on observation time: 2s->10, 4s->6, 6s->
latitude_position = 0

position_space = []
position_space_size = 0


def judge_done():
    global latitude_position
    global position_space_size
    global position_space
    judge = False
    position = requests.get("http://192.168.50.81:5000/LGSVL/Status/EGOVehicle/Position").json()
    position_space.append((position['x'], position['y'], position['z']))
    position_space_size = (position_space_size + 1) % check_num
    if len(position_space) == 5:
        start_pos = position_space[0]
        end_pos = position_space[4]
        position_space = []
        dis = pow(
            pow(start_pos[0] - end_pos[0], 2) + pow(start_pos[1] - end_pos[1], 2) + pow(start_pos[2] - end_pos[2], 2),
            0.5)
        if dis < 0.15:
            judge = True
    return judge


# Execute action and get return
def calculate_reward(api_id):
    """
    Function for reward calculating.
    First, interpret action id to real RESTful API and call function -execute_action- to execute current RESTful API;
    then after the execution of RESTful API, the collision information are collected and based on it, we can calculate the reward.
    :param api_id:
    :return:
    """
    global latitude_position
    time_step_probability_list = execute_action(api_id)
    observation = None
    action_reward = 0
    # episode_done = False
    collision_probability = 0
    # Reward is calculated based on collision probability.
    collision_info = (requests.get("http://192.168.50.81:5000/LGSVL/Status/CollisionInfo")).content.decode(
        encoding='utf-8')
    episode_done = judge_done()

    if collision_info != 'None':
        collision_probability = 1
        # episode_done = True
    elif collision_info == "None":
        collision_probability = round(float(
            (requests.get("http://192.168.50.81:5000/LGSVL/Status/CollisionProbability")).content.decode(
                encoding='utf-8')), 3)
        # action_reward = collision_probability.__float__()
    return observation, collision_probability, episode_done, collision_info, time_step_probability_list


# def execute_action(action_id):
#     api = action_space[str(action_id)]
#     probability_list = requests.post(api).json()
#     return probability_list


def get_id(dataX, episode):
    for k in range(len(dataX)):
        if int(dataX['Episode'][k]) == episode:
            return k


def get_actions(scenario_data):
    episode = 0
    episode_actions = []
    all_30_episodes_actions = []

    episode_actions_proc = []
    all_30_episodes_actions_proc = []
    for i in range(get_id(scenario_data, 30)):
        if scenario_data['Episode'][i] == episode:
            episode_actions.append(scenario_data['Action'][i])
            episode_actions_proc.append(scenario_data['Collision_Probability'][i])
        else:
            all_30_episodes_actions.append(episode_actions)
            all_30_episodes_actions_proc.append(episode_actions_proc)
            episode_actions = []
            episode_actions_proc = []
            episode += 1

    # print(all_30_episodes_actions)
    return all_30_episodes_actions, all_30_episodes_actions_proc


file1 = pd.read_csv('Test/data_model_6s_1_with_probability_time_step.csv', sep=',')
file2 = pd.read_csv('Test/data_model_6s_2_with_model4_with_probability_time_step.csv', sep=',')
file3 = pd.read_csv('Test/data_model_6s_3_with_probability_time_step.csv', sep=',')
file4 = pd.read_csv('Test/data_model_6s_4_with_probability_time_step.csv', sep=',')
get_actions(file1)


def replay(road_num, data_file):
    count_ = 0
    # requests.post("http://192.168.50.81:5000/LGSVL/LoadScene?scene=SanFrancisco&road_num=" + str(road_num))
    all_30_episodes_actions, all_30_episodes_actions_proc = get_actions(data_file)
    for i in range(len(all_30_episodes_actions_proc)):
        actions = all_30_episodes_actions[i]
        procs = all_30_episodes_actions_proc[i]
        for j in range(len(actions)):
            laproc = random.uniform(0, procs[j])
            loproc = (procs[j] - laproc) / (1 - laproc)
            max_p = max(laproc, loproc)
            min_p = min(laproc, loproc)
            # if procs[j] - laproc > laproc:
            #     loproc = (procs[j] - laproc) / (1 - laproc)
            # else:
            #     loproc = (procs[j] - laproc) / (1 - laproc)
            if actions[j] in [0, 1, 51] or actions[j] >= 40:
                loproc = max_p
                laproc = min_p
            else:
                laproc = max_p
                loproc = min_p
            if loproc == 1:
                count_ += 1
                print(actions[j], laproc, loproc)
    print(count_)


replay('1', file4)
