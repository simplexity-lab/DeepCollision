from DeepCollision.DQNEnvironment.utils import get_action_space
import random
import requests
import pandas as pd
import time
import numpy as np


# Execute action
def execute_action(api_id):
    api = action_space[str(api_id)]
    requests.post(api)


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
    execute_action(api_id)
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
    return observation, collision_probability, episode_done, collision_info


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


# initialize the environment
# requests.post("http://192.168.50.81:5000/LGSVL/LoadScene?scene=SanFrancisco")
requests.post("http://192.168.50.81:5000/LGSVL/LoadScene?scene=SanFrancisco&road_num=" + '1')

action_space = get_action_space()['command']
action_space_size = action_space['num']

title = ["Episode", "State", "Action", "Reward", "Done"]
df_title = pd.DataFrame([title])
file_name = str(int(time.time()))
df_title.to_csv('../ExperimentData/Analysis/Data_Random/random_8s_road1_' + file_name + '.csv', mode='w', header=False, index=None)

iteration = 0
step = 0
while True:
    # Random select action to execute

    s = get_environment_state()
    api_id = random.randint(0, action_space_size - 1)
    _, probability, done, _ = calculate_reward(api_id)

    print('api_id, probability, done: ', api_id, probability, done)
    pd.DataFrame([[api_id, probability, done]]).to_csv('random_record_' + file_name + '.csv', mode='a', header=False,
                                                       index=None)

    pd.DataFrame([[iteration, s, api_id, probability, done]]).to_csv(
        '../ExperimentData/Analysis/Data_Random/random_8s_road1_' + file_name + '.csv',
        mode='a',
        header=False, index=None)

    step += 1
    if done:
        # break
        requests.post("http://192.168.50.81:5000/LGSVL/LoadScene?scene=SanFrancisco&road_num=" + '1')
        iteration += 1
        if iteration == 31:
            break
