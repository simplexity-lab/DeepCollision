import requests
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import pandas as pd
import time
import socket
import math

from DeepCollision.DQNEnvironment.utils import *

road_num = '1'  # the Road Number
second = '6'  # the experiment second
requests.post("http://192.168.50.81:5000/LGSVL/LoadScene?scene=SanFrancisco&road_num=" + road_num)


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


# # Hyper Parameters
# BATCH_SIZE = 32
# LR = 0.01  # learning rate
# EPSILON = 0.8  # greedy policy
# GAMMA = 0.9  # reward discount
# TARGET_REPLACE_ITER = 100  # target update frequency
# MEMORY_CAPACITY = 2000

action_space = get_action_space()['command']
scenario_space = get_action_space()['scenario_description']
N_ACTIONS = action_space['num']
N_STATES = get_environment_state().shape[0]
ENV_A_SHAPE = 0

HyperParameter = dict(BATCH_SIZE=32, GAMMA=0.9, EPS_START=1, EPS_END=0.1, EPS_DECAY=6000, TARGET_UPDATE=100,
                      lr=1e-2, INITIAL_MEMORY=2000, MEMORY_SIZE=2000)


class Net(nn.Module):
    def __init__(self, ):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(N_STATES, 200)
        self.fc1.weight.data.normal_(0, 0.1)  # initialization
        self.fc2 = nn.Linear(200, 200)
        self.fc2.weight.data.normal_(0, 0.1)  # initialization
        self.out = nn.Linear(200, N_ACTIONS)
        self.out.weight.data.normal_(0, 0.1)  # initialization

    def forward(self, x):
        # x = self.fc1(x)
        # print('x1', x)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        # print('x', x)
        actions_value = self.out(x)
        return actions_value


class DQN(object):
    def __init__(self):
        self.eval_net, self.target_net = Net(), Net()

        self.learn_step_counter = 0  # for target updating
        self.memory_counter = 0  # for storing memory
        self.memory = np.zeros((HyperParameter['MEMORY_SIZE'], N_STATES * 2 + 2))  # initialize memory
        self.optimizer = torch.optim.Adam(self.eval_net.parameters(), lr=HyperParameter['lr'])
        self.loss_func = nn.MSELoss()
        self.steps_done = 0

    def choose_action(self, x):
        x = torch.unsqueeze(torch.FloatTensor(x), 0)
        # input only one sample
        eps_threshold = HyperParameter['EPS_END'] + (
                HyperParameter['EPS_START'] - HyperParameter['EPS_END']) * math.exp(
            -1. * self.steps_done / HyperParameter['EPS_DECAY'])
        self.steps_done += 1
        if np.random.uniform() < eps_threshold:  # greedy
            actions_value = self.eval_net.forward(x)
            # print('action value: ', actions_value, actions_value.shape)
            action = torch.max(actions_value, 1)[1].data.numpy()
            # print(actions_value.data)
            action = action[0] if ENV_A_SHAPE == 0 else action.reshape(ENV_A_SHAPE)  # return the argmax index
            # print(action)
        else:  # random
            action = np.random.randint(0, N_ACTIONS)
            action = action if ENV_A_SHAPE == 0 else action.reshape(ENV_A_SHAPE)
        return action

    def store_transition(self, s, a, r, s_):
        transition = np.hstack((s, [a, r], s_))
        # replace the old memory with new memory
        index = self.memory_counter % HyperParameter['MEMORY_SIZE']
        self.memory[index, :] = transition
        self.memory_counter += 1

    def learn(self):
        # target parameter update
        if self.learn_step_counter % HyperParameter['TARGET_UPDATE'] == 0:
            self.target_net.load_state_dict(self.eval_net.state_dict())
        self.learn_step_counter += 1

        # sample batch transitions
        sample_index = np.random.choice(HyperParameter['MEMORY_SIZE'], HyperParameter['BATCH_SIZE'])
        b_memory = self.memory[sample_index, :]
        b_s = torch.FloatTensor(b_memory[:, :N_STATES])
        b_a = torch.LongTensor(b_memory[:, N_STATES:N_STATES + 1].astype(int))
        b_r = torch.FloatTensor(b_memory[:, N_STATES + 1:N_STATES + 2])
        b_s_ = torch.FloatTensor(b_memory[:, -N_STATES:])

        # q_eval w.r.t the action in experience
        q_eval = self.eval_net(b_s).gather(1, b_a)  # shape (batch, 1)
        q_next = self.target_net(b_s_).detach()  # detach from graph, don't backpropagate
        q_target = b_r + HyperParameter['GAMMA'] * q_next.max(1)[0].view(HyperParameter['BATCH_SIZE'], 1)  # shape (batch, 1)
        loss = self.loss_func(q_eval, q_target)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()


# Execute action
def execute_action(action_id):
    api = action_space[str(action_id)]
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
def calculate_reward(action_id):
    """
    Function for reward calculating.
    First, interpret action id to real RESTful API and call function -execute_action- to execute current RESTful API;
    then after the execution of RESTful API, the collision information are collected and based on it, we can calculate the reward.
    :param action_id:
    :return:
    """
    # global latitude_position
    # global position_space_size
    # global position_space
    # global collision_probability
    execute_action(action_id)
    observation = get_environment_state()
    action_reward = 0
    collision_probability = 0
    # episode_done = False
    # Reward is calculated based on collision probability.
    collision_info = (requests.get("http://192.168.50.81:5000/LGSVL/Status/CollisionInfo")).content.decode(
        encoding='utf-8')

    episode_done = judge_done()

    '''
    calculate latitude_space
    '''
    # latitude = (requests.get("http://192.168.50.81:5000/LGSVL/Status/EGOVehicle/Position/X")).content.decode(
    #     encoding='utf-8')
    # if len(latitude_space) < check_num:
    #     latitude_space.append(None)
    # latitude_space[latitude_position] = latitude
    # latitude_position = (latitude_position + 1) % check_num
    # if len(latitude_space) == check_num:
    #     for i in range(0, len(latitude_space) - 1):
    #         # print(latitude_space[i], )
    #         if latitude_space[i] != latitude_space[i + 1]:
    #             episode_done = False
    #             break
    #         if i == len(latitude_space) - 2:
    #             episode_done = True

    if collision_info != 'None':
        action_reward = 1
        collision_probability = 1
        # episode_done = True
    elif collision_info == "None":
        collision_probability = round(float(
            (requests.get("http://192.168.50.81:5000/LGSVL/Status/CollisionProbability")).content.decode(
                encoding='utf-8')), 3)
        if collision_probability < 0.2:
            action_reward = -1
        else:
            action_reward = collision_probability
    return observation, action_reward, collision_probability, episode_done, collision_info


title = ["Episode", "Step", "State", "Action", "Reward", "Collision_Probability", "Action_Description", "Done"]
df_title = pd.DataFrame([title])
file_name = str(int(time.time()))
df_title.to_csv('../ExperimentData/DQN_experiment_' + second + 's_' + file_name + '_road' + road_num + '.csv', mode='w',
                header=False,
                index=None)

if __name__ == '__main__':
    '''
    Establish client to connect to Apollo
    '''
    # comm_apollo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # address = ('192.168.1.197', 6000)
    # comm_apollo.connect(address)
    # print('connected')

    dqn = DQN()
    # print(dqn.eval_net.state_dict())
    # print(dqn.target_net.state_dict())
    if int(road_num) >= 2:
        dqn.eval_net.load_state_dict(torch.load('./model/DQN_experiment_'+second+'s/eval_net_600_road'+str(int(road_num)-1)+'.pt'))
    # dqn.target_net.load_state_dict(torch.load('./model/target_net_2.pt'))
    # print(dqn.eval_net.state_dict())
    # print(dqn.target_net.state_dict())
    # requests.post("http://192.168.50.81:5000/LGSVL/LoadScene?scene=SanFrancisco")

    # comm_apollo.send(str(1).encode())

    print('\nCollecting experience...')
    road_num_int = int(road_num)

    while road_num_int <= 4:
        road_num = str(road_num_int)

        df_title = pd.DataFrame([title])
        file_name = str(int(time.time()))
        # df_title.to_csv('../ExperimentData/DQN_experiment_' + second + 's_' + file_name + '_road' + road_num + '.csv',
        #                 mode='w', header=False,
        #                 index=None)

        requests.post("http://192.168.50.81:5000/LGSVL/SetObTime?observation_time=" + '6')
        for i_episode in range(0, 600):
            print('------------------------------------------------------')
            print('+                 Road, Episode: ', road_num_int, i_episode, '                +')
            print('------------------------------------------------------')
            # if i_episode == 1:
            #    requests.post("http://192.168.50.81:5000/LGSVL/SaveTransform")
            requests.post("http://192.168.50.81:5000/LGSVL/LoadScene?scene=SanFrancisco&road_num=" + road_num)
            # comm_apollo.send(str(1).encode())
            # if i_episode % 9 == 0:
            #     requests.post("http://192.168.50.81:5000/LGSVL/LoadScene?scene=SanFrancisco")
            # else:
            #     requests.post("http://192.168.50.81:5000/LGSVL/EGOVehicle/Reset")
            #     requests.post("http://192.168.50.81:5000/LGSVL/Reset")
            s = get_environment_state()
            # s = format_state(get_environment_state())
            ep_r = 0
            step = 0
            while True:
                # env.render()
                action = dqn.choose_action(s)
                action_description = scenario_space[str(action)]
                # take action
                s_, reward, collision_probability, done, info = calculate_reward(action)
                dqn.store_transition(s, action, reward, s_)
                print('>>>>>step, action, reward, collision_probability, action_description, done: ', step, action,
                      reward, collision_probability,
                      "<" + action_description + ">",
                      done)
                pd.DataFrame(
                    [[i_episode, step, s, action, reward, collision_probability, action_description, done]]).to_csv(
                    '../ExperimentData/DQN_experiment_' + second + 's_' + file_name + '_road' + road_num + '.csv',
                    mode='a',
                    header=False, index=None)

                ep_r += reward
                if dqn.memory_counter > HyperParameter['MEMORY_SIZE']:
                    dqn.learn()
                    if done:
                        print('Ep: ', i_episode,
                              '| Ep_r: ', round(ep_r, 2))

                if (i_episode + 1) % 50 == 0:
                    # print('save')
                    # print(dqn.eval_net.state_dict())
                    # print(dqn.target_net.state_dict())
                    torch.save(dqn.eval_net.state_dict(),
                               './model/DQN_experiment_' + second + 's/eval_net_' + str(
                                   i_episode + 1) + '_road' + road_num + '.pt')
                    torch.save(dqn.target_net.state_dict(),
                               './model/DQN_experiment_' + second + 's/target_net_' + str(
                                   i_episode + 1) + '_road' + road_num + '.pt')
                if done:
                    # comm_apollo.send(repr('1').encode())
                    break
                step += 1
                s = s_
        road_num_int = road_num_int + 1
