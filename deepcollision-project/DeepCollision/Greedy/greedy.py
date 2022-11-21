import socket
import time

import pandas as pd

from DeepCollision.DQNEnvironment.utils import *

requests.post("http://192.168.50.81:5000/LGSVL/LoadScene?scene=SanFrancisco&road_num=1")

HOST = '192.168.50.51'  # or 'localhost'
PORT = 6001
ADDR = (HOST, PORT)

ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.connect(ADDR)


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


action_space = get_action_space()['command']
scenario_space = get_action_space()['scenario_description']
N_ACTIONS = action_space['num']
N_STATES = get_environment_state().shape[0]
ENV_A_SHAPE = 0


# Execute action
def execute_action(action_id):
    api = action_space[str(action_id)]
    probability_list = requests.post(api).json()
    return probability_list


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


# title = ["Episode", "State", "Action", "Reward", "Probability", "Done"]
# df_title = pd.DataFrame([title])
# file_name = str(int(time.time()))
# df_title.to_csv('./greedy.csv', mode='w', header=False,
#                 index=None)

def greedy(opt, road_num):
    i_episode = 0
    step = 0
    previous_cp = 0
    api_id = random.randint(0, N_ACTIONS - 1)
    path = '../ExperimentData/Greedy/greedy_{}_road{}_timestamp{}.csv'.format(opt, road_num, str(time.time())) + '.csv'
    df_title.to_csv(path, mode='w', header=False, index=None)
    while True:
        s = get_environment_state()
        requests.post("http://192.168.50.81:5000/LGSVL/SaveState?ID={}".format(step))
        # api_id = init_action
        ss.send(json.dumps(['start']).encode('utf-8'))
        _, probability, done, _, probability_list_in_one_action = calculate_reward(api_id)
        ss.send(json.dumps(['stop']).encode('utf-8'))

        if probability < previous_cp and step > 0:
            requests.post("http://192.168.50.81:5000/LGSVL/RollBack?ID={}".format(step))
            while True:
                temp_id = random.randint(0, N_ACTIONS - 1)
                if temp_id != api_id:
                    api_id = temp_id
                    break
            _, reward, probability, done, _ = calculate_reward(api_id)
        else:
            previous_cp = probability
            print('iteration, api_id, probability, done: ', i_episode, api_id, probability, done)

            cmd_res_size = ss.recv(1024)
            received_size = 0
            received_data = b''
            while received_size < int(cmd_res_size.decode()):
                cmd_res = ss.recv(1024)
                received_size += len(cmd_res)
                received_data += cmd_res
            received_data = json.loads(received_data.decode('utf-8'))
            state_arr = received_data['state_arr']
            pose_arr = received_data['pose_arr']
            obstacle_arr = received_data['obstacle_arr']
            traffic_light = received_data['traffic_light']
            pd.DataFrame([[i_episode, step, s, api_id, probability, scenario_space[str(api_id)], state_arr, pose_arr, obstacle_arr, traffic_light, probability_list_in_one_action, done]]).to_csv(
                path, mode='a', header=False, index=None)

            # pd.DataFrame([[i_episode, s, api_id, reward, probability, done]]).to_csv(
            #     './greedy.csv', mode='a', header=False,
            #     index=None)

        step += 1

        if done:
            # break
            requests.post("http://192.168.50.81:5000/LGSVL/LoadScene?scene=SanFrancisco&road_num=" + road_num)
            i_episode += 1
            step = 0
            previous_cp = 0
            api_id = random.randint(0, N_ACTIONS - 1)
            if i_episode == 31:
                break


if __name__ == '__main__':
    title = ["Episode", "Step", "State", "Action", "Reward", "Collision_Probability", "Action_Description",
             "Ego_Vehicle_Ops_Value", "Ego_Vehicle_Pose", "Obstacle_Info", "Traffic_Light",
             "Collision_Probability_Per_Time_Step",
             "Done"]
    df_title = pd.DataFrame([title])

    time_list = [4, 6, 8, 10]
    road_num_list = ["1", "2", "3", "4"]

    for t in time_list:
        OPT = str(t)
        requests.post("http://192.168.50.81:5000/LGSVL/SetObTime?observation_time=" + OPT)
        for rn in road_num_list:
            greedy(OPT, rn)
