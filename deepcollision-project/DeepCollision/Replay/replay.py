# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/1 1:09
# @Author  : Chengjie
# @File    : replay.py


import pandas as pd
import socket
import time
# from StrategyForLiveTCM.DQNEnvironment.utils import *
import requests
import json
import numpy as np

HOST = '192.168.1.236'
PORT = 6009
ADDR = (HOST, PORT)
ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.connect(ADDR)

requests.post("http://192.168.1.236:5000/LGSVL/LoadScene?scene=SanFrancisco&road_num=1")


def get_action_space():
    # json_file = open('../../RESTfulAPIProcess/RESTful_API_old.json', 'r')
    json_file = open('/home/chengjie/LiveTCM/LCJ/LGSVLProject/RESTfulAPIProcess/RESTful_API.json', 'r')
    content = json_file.read()
    restful_api = json.loads(s=content)
    return restful_api


def get_environment_state():
    r = requests.get("http://192.168.1.236:5000/LGSVL/Status/Environment/State")
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


action_space = get_action_space()['command']
scenario_space = get_action_space()['scenario_description']
N_ACTIONS = action_space['num']
N_STATES = get_environment_state().shape[0]
ENV_A_SHAPE = 0

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
    position = requests.get("http://192.168.1.236:5000/LGSVL/Status/EGOVehicle/Position").json()
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
    collision_info = (requests.get("http://192.168.1.236:5000/LGSVL/Status/CollisionInfo")).content.decode(
        encoding='utf-8')
    episode_done = judge_done()

    if collision_info != 'None':
        collision_probability = 1
        # episode_done = True
    elif collision_info == "None":
        collision_probability = round(float(
            (requests.get("http://192.168.1.236:5000/LGSVL/Status/CollisionProbability")).content.decode(
                encoding='utf-8')), 3)
        # action_reward = collision_probability.__float__()
    return observation, collision_probability, episode_done, collision_info, time_step_probability_list


def execute_action(action_id):
    api = action_space[str(action_id)]
    probability_list = requests.post(api).json()
    return probability_list


def get_id(dataX, episode):
    for k in range(len(dataX)):
        if int(dataX['Episode'][k]) == episode:
            return k


def create_two_dim_array(sample_size):
    array = []
    for i in range(sample_size):
        array.append([])
    return array


# def get_actions(scenario_data):
#     episode = 0
#     episode_actions = []
#     all_30_episodes_actions = []
#
#     episode_actions_proc = []
#     all_30_episodes_actions_proc = []
#     for i in range(len(scenario_data)):
#         if scenario_data['Episode'][i] == episode:
#             episode_actions.append(scenario_data['Action'][i])
#             episode_actions_proc.append(scenario_data['Collision_Probability'][i])
#         else:
#             all_30_episodes_actions.append(episode_actions)
#             all_30_episodes_actions_proc.append(episode_actions_proc)
#             episode_actions = []
#             episode_actions_proc = []
#             episode += 1
#
#     # print(all_30_episodes_actions)
#     return all_30_episodes_actions, all_30_episodes_actions_proc

def get_actions(scenario_data):
    action_array = create_two_dim_array(20)

    for i in range(len(scenario_data)):
        # print(scenario_data['Episode'][i], scenario_data['Action'][i])
        action_array[scenario_data['Episode'][i]].append(scenario_data['Action'][i])

    return action_array


title = ["Episode", "Step", "State", "Action", "Action_Description", "Reward", "Reward_Info",
         "Ego_Vehicle_Ops_Value", "Ego_Vehicle_Pose", "Obstacle_Info", "Traffic_Light", "Realistic", "Done"]
df_title = pd.DataFrame([title])


def replay(road_num, data_file, new_filename):
    df_title.to_csv(new_filename, mode='w', header=False, index=False)

    # all_30_episodes_actions, all_30_episodes_actions_proc = get_actions(data_file)
    all_30_episodes_actions = get_actions(data_file)
    # for i in range(len(all_30_episodes_actions_proc)):
    for i in range(len(all_30_episodes_actions)):
        print('-----------Episode: {}-----------'.format(i))
        requests.post("http://192.168.1.236:5000/LGSVL/Episode?episode={}".format(str(i)))
        actions = all_30_episodes_actions[i]
        # actions = [2, 2, 2, 2, 2]
        requests.post("http://192.168.1.236:5000/LGSVL/LoadScene?scene=SanFrancisco&road_num=" + str(road_num))
        for j in range(len(actions)):
            r = requests.get("http://192.168.1.236:5000/LGSVL/Status/Environment/State")
            state = r.json()

            api = action_space[str(actions[j])]
            action_des = scenario_space[str(actions[j])]
            print('Step: {}, Action: {}, Action_Description: {}'.format(j, actions[j], action_des))

            ss.send(json.dumps(['start']).encode('utf-8'))
            measure_list = requests.post(api).json()
            ss.send(json.dumps(['stop']).encode('utf-8'))

            probability = np.array(measure_list['probability']).max()

            realistic = requests.get("http://192.168.1.236:5000/LGSVL/Status/Realistic").json()
            # print('realistic constraints: ', realistic)
            """
            Processing start
            """
            cmd_res_size = ss.recv(1024)
            length = int(cmd_res_size.decode())
            ss.send(json.dumps(['confirmed']).encode('utf-8'))
            received_size = 0
            received_data = b''
            while received_size < length:
                cmd_res = ss.recv(1024)
                received_size += len(cmd_res)
                received_data += cmd_res
            received_data = json.loads(received_data.decode('utf-8'))
            state_arr = received_data['state_arr']
            pose_arr = received_data['pose_arr']
            obstacle_arr = received_data['obstacle_arr']
            traffic_light = received_data['traffic_light']
            """
            Processing end
            """

            pd.DataFrame([[i, j, state, actions[j], scenario_space[str(actions[j])], probability, measure_list,
                           state_arr, pose_arr, obstacle_arr, traffic_light,
                           realistic, False if j < len(actions) - 1 else True]]). \
                to_csv(new_filename, mode='a', header=False, index=False)

            # _, probability, done, _, probability_list_in_one_action = calculate_reward(actions[j])
            # requests.get("http://192.168.1.236:5000/LGSVL/Status/EGOVehicle/Speed")


# data = pd.read_csv(filepath_or_buffer='./Model_DeepTest/Strategy_Model_Road1_6s.csv', sep=',')
#
# actions = get_actions(data)
# print(actions, len(actions))


if __name__ == '__main__':

    roads = {'4': 'Road4'}
    for k in roads.keys():
        fn = './Model/Strategy_Model_{}_6s.csv'.format(roads[k])
        new_path = './Model/Model_{}_6s.csv'.format(roads[k])
        print('processing {} ...'.format(fn))
        data = pd.read_csv(filepath_or_buffer=fn, sep=',')
        replay(k, data, new_path)
