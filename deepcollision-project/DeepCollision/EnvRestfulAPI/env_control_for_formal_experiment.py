import socket
import time

import cv2
from flask import Flask, request
import os
from datetime import timedelta
import json
import lgsvl
import numpy as np
import pickle
from ScenarioCollector.createUtils import *
from collision_utils import pedestrian, npc_vehicle, calculate_measures
import math


########################################
observation_time = 6  # OTP [4, 6, 8, 10]

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

sim = lgsvl.Simulator(os.environ.get("SIMUSaveStateLATOR_HOST", "localhost"), 8181)

print('connected')
# state = lgsvl.AgentState()
# print(state.transform)
collision_object = None
probability = 0
time_step_collision_object = None
sensors = None
DATETIME_UNIX = None
WEATHER_DATA = None
TIMESTAMP = None
DESTINATION = None
EGO = None
CONSTRAINS = True
ROAD = '1'
SAVE_SCENARIO = False
REALISTIC = False
collision_tag = False
EFFECT_NAME = 'Default'
EPISODE = 0
collision_speed = 0  # 0 indicates there is no collision occurred.

speed_list = []
u = 0.6
z_axis = lgsvl.Vector(0, 0, 100)

APOLLO_HOST = '192.168.1.236'  # or 'localhost'
PORT = 6000
ADDR = (APOLLO_HOST, PORT)

ACC_ADDR = (APOLLO_HOST, 6002)

ss_route = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss_route.connect(ADDR)

ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.connect(ACC_ADDR)

# apollo_host = "192.168.50.51"

"""
Util Functions
"""


def on_collision(agent1, agent2, contact):
    name1 = agent1.__dict__.get('name')
    name2 = agent2.__dict__.get('name') if agent2 is not None else "OBSTACLE"
    print("{} collided with {} at {}".format(name1, name2, contact))
    global collision_object
    global collision_tag
    global collision_speed
    collision_object = name2
    collision_tag = True
    # raise evaluator.TestException("Ego collided with {}".format(agent2))
    try:
        collision_speed = agent1.state.speed
    except KeyError:
        collision_speed = -1
        print('KeyError')


def get_no_conflict_position(position, car):
    if car == 'BoxTruck' or car == 'SchoolBus':
        sd = 8
    elif car == 'pedestrian':
        sd = 4
    else:
        sd = 6
    generate = True
    if CONSTRAINS:
        agents = sim.get_agents()
        for agent in agents:
            if math.sqrt(pow(position.x - agent.transform.position.x, 2) +
                         pow(position.y - agent.transform.position.y, 2) +
                         pow(position.z - agent.transform.position.z, 2)) < sd:
                generate = False
                break
    # if not CONSTRAINS:
    #     generate = True
    return generate


def get_image(camera_name):
    for sensor in sensors:
        if sensor.name == camera_name:
            camera = sensor
    filename = os.path.dirname(os.path.realpath(__file__)) + '/Image/' + str(camera_name).replace(' ', '_') + '.jpg'
    # print(filename)
    camera.save(filename, quality=75)
    im = cv2.imread(filename, 1)
    # print(im.shape)
    # im = cv2.resize(im, (297, 582))
    im = im[400:800, 500:1020]
    cv2.imwrite("./Image/" + str(camera_name).replace(' ', '_') + "_cropped.jpg", im)
    im = im.astype(np.float32)
    im /= 255.0
    # print(im)
    # main_image_dict = {'index': im.tolist()}
    # main_json = json.dumps(main_image_dict)
    return im


# def save_image(sensor_name):
#     for sensor in sensors:
#         if sensor.name == sensor_name:
#             camera = sensor
#             break
#     tag = str(int(time.time()))
#     filename = os.path.dirname(os.path.realpath(__file__)) + '/Image/' + str(sensor_name).replace(' ',
#                                                                                                   '_') + '/' + tag + '.jpg'
#     print(filename)
#     camera.save(filename, quality=75)
#

def save_image(sensor_name):
    path = './Image/' + str(sensor_name).replace(' ', '_')
    if not os.path.exists(path):
        os.makedirs(path)
    for sensor in sensors:
        if sensor.name == sensor_name:
            camera = sensor
            break
    tag = str(int(time.time()))
    filename = os.path.dirname(os.path.realpath(__file__)) + '/Image/' + str(sensor_name).replace(' ',
                                                                                                  '_') + '/' + tag + '.jpg'
    # print(filename)
    camera.save(filename, quality=75)


def save_lidar():
    path = './Lidar'
    tag = str(int(time.time()))
    if not os.path.exists(path):
        os.mkdir(path)
    for sensor in sensors:
        if sensor.name == "Lidar":
            sensor.save(
                "D:/RTCM COPY/Autonomous Car/LGSVL/LGSVLProject/StrategyForLiveTCM/WithoutRestfulAPI/Lidar/lidar_" + tag + ".pcd")


def save_all():
    save_image('Main Camera')
    save_image('Left Camera')
    save_image('Right Camera')
    save_image('Left Segmentation Camera')
    save_image('Right Segmentation Camera')
    save_image('Segmentation Camera')
    save_lidar()


def get_type(class_name):
    # print(class_name)
    object_type = None
    if str(class_name) == '<class \'lgsvl.agent.EgoVehicle\'>':
        object_type = 'Ego'
    elif str(class_name) == '<class \'lgsvl.agent.Pedestrian\'>':
        object_type = 'Pedestrian'
    elif str(class_name) == '<class \'lgsvl.agent.NpcVehicle\'>':
        object_type = 'NPC'
    return object_type


def calculate_metrics(agents, ego):
    global probability
    global DATETIME_UNIX
    global collision_tag

    global SAVE_SCENARIO
    # probability = 0

    # global uncomfortable_angularAcceleration
    global collision_object
    global collision_speed
    global TIMESTAMP

    # uncomfortable_angularAcceleration = [20, JERK_THRESHOLD, 2800]
    collision_object = None
    collision_speed = 0  # 0 indicates there is no collision occurred.
    collision_speed_ = 0
    collision_type = "None"

    TTC_list = []
    JERK_list = []
    distance_list = []
    probability_list = []
    i = 0
    time_step = 0.5
    speed = 0

    if SAVE_SCENARIO:
        # print(sim.current_time)
        doc, root = initialization('2022-11-11', get_time_stamp(), './{}.json'.format(EFFECT_NAME))
        entities, storyboard = initializeStory(agents, doc, root)
        story = doc.createElement('Story')
        story.setAttribute('name', 'Default')

    while i < observation_time / time_step:
        # """
        # Updating date time.
        # """
        # dt = sim.current_datetime
        # DATETIME_UNIX = time.mktime(dt.timetuple())
        #
        ss.send('acc_start'.encode('utf-8'))

        acc_old = float(ss.recv(1024).decode('utf-8'))
        # print(acc_old)

        if SAVE_SCENARIO:
            create_story_by_timestamp(i + 1, doc, story, entities, agents, sim)  # create scenarios each at time step
        sim.run(time_limit=time_step)  # , time_scale=2
        ss.send('acc_start'.encode('utf-8'))
        acc_new = float(ss.recv(1024).decode('utf-8'))
        # print('acc_new:', acc_new)
        # speed_new = EGO.state.speed
        JERK_list.append(abs(acc_new - acc_old) / 0.5)

        TTC, distance, probability2 = 100000, 100000, 0
        if SAVE_SCENARIO:
            TTC, distance, probability2 = calculate_measures(agents, ego, SAVE_SCENARIO)
            # probability2 = get_collision_probability2(agents)
        TTC_list.append(round(TTC, 6))
        distance_list.append(round(distance, 6))
        if collision_tag:
            speed = EGO.state.speed
            probability2 = 1
            print('speed at collision')
            collision_tag = False

        probability_list.append(round(probability2, 6))
        i += 1

    # if SAVE_SCENARIO:
    collision_type, collision_speed_ = get_collision_info()
    if collision_speed_ == -1:
        collision_speed_ = speed

    if SAVE_SCENARIO:
        storyboard.appendChild(story)
        root.appendChild(storyboard)
        root.setAttribute('timestep', '0.5')

        path = '../../DeepQTestExperiment/Road{}'.format(ROAD)
        try:
            os.makedirs(path)
        except Exception as e:
            print(e)

        time_t = str(int(time.time()))

        fp = open(path + "/{}_Scenario_{}.deepscenario".format(EPISODE, time_t), "w")
        # fp = open('./Scenario_{}.deepscenario'.formconnect-dreamviewat(TIMESTAMP), 'w')
        doc.writexml(fp, addindent='\t', newl='\n', encoding="utf-8")

    # print({'TTC': TTC_list, 'distance': distance_list, 'collision_type': collision_type,
    #        'collision_speed': collision_speed_, 'JERK': JERK_list, 'probability': probability_list})
    probability = max(probability_list)
    return {'TTC': TTC_list, 'distance': distance_list, 'collision_type': collision_type,
            'collision_speed': collision_speed_, 'JERK': JERK_list,
            'probability': probability_list}  # 'uncomfortable': uncomfortable,


@app.route('/LGSVL')
def index():
    return "RESTful APIs for LGSVL simulator control."


@app.route('/LGSVL/get-datetime', methods=['GET'])
def get_time_stamp():
    # timeofday = round(sim.time_of_day)
    # if timeofday == 24:
    #     timeofday = 0
    # dt = sim.current_time
    # # print(dt)
    # dt = dt.replace(hour=timeofday, minute=0, second=0)
    # # print(int(time.mktime(dt.timetuple())))
    # return json.dumps(int(time.mktime(dt.timetuple())))
    return json.dumps(int(time.time()))


@app.route('/LGSVL/Episode', methods=['POST'])
def get_effect_info():
    global EPISODE
    EPISODE = int(request.args.get('episode'))

    # print('episode: ', EPISODE)

    return 'set effect-episode'


@app.route('/LGSVL/ego/collision_info', methods=['GET'])
def get_collision_info():
    """
    three types of collision: obstacle, NPC vehicle, pedestrian, None(no collision)
    :return:
    """
    global collision_object
    global collision_speed
    # global uncomfortable_angularAcceleration
    global JERK

    collision_info = str(collision_object)
    collision_speed_ = collision_speed
    # uncomfortable = uncomfortable_angularAcceleration

    collision_object = None
    collision_speed = 0
    # uncomfortable_angularAcceleration = [20, JERK_THRESHOLD, 2800]
    JERK = 0
    # convert collision information to one of three types
    collision_type = 'None'
    if collision_info == 'OBSTACLE':
        collision_type = "obstacle"
    if collision_info in npc_vehicle:
        collision_type = "npc_vehicle"
    if collision_info in pedestrian:
        collision_type = "pedestrian"
    return collision_type, collision_speed_


@app.route('/LGSVL/SetObTime', methods=['POST'])
def set_time():
    global observation_time
    observation_time = int(request.args.get('observation_time'))
    print(observation_time)
    return 'get time'


"""
Command APIs
"""


@app.route('/LGSVL/LoadScene', methods=['POST'])
def load_scene():
    global sensors
    global EGO
    global ROAD
    print('obTime: ', observation_time)
    scene = str(request.args.get('scene'))
    road_num = str(request.args.get('road_num'))
    ROAD = str(road_num)
    print('load scene', scene)
    if sim.current_scene == scene:
        sim.reset()
    else:
        sim.load(scene)

    # controllables = sim.get_controllables("signal")
    # for c in controllables:
    #     c.control("green=3;loop")

    EGO = None
    # spawns = sim.get_spawn()
    state = lgsvl.AgentState()
    # state.transform = spawns[0]
    roadTransform_start = open('Transform/transform-road' + road_num + '-start', 'rb')
    state.transform = pickle.load(roadTransform_start)

    EGO = sim.add_agent("Lincoln2017MKZ (Apollo 5.0)", lgsvl.AgentType.EGO, state)
    EGO.connect_bridge(os.environ.get("BRIDGE_HOST", APOLLO_HOST), 9090)

    # speed = ego.state.speed
    # velocity = ego.state.velocity

    sensors = EGO.get_sensors()
    sim.get_agents()[0].on_collision(on_collision)

    # ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = {'road_num': road_num}
    print(road_num)

    ss_route.send(json.dumps(data).encode('utf-8'))
    # ss.close()
    roadTransform_start.close()
    sim.run(2)
    return 'load success'


@app.route('/LGSVL/SaveTransform', methods=['POST'])
def save_transform():
    transform = sim.get_agents()[0].state.transform
    f = open('Transform/transform2', 'wb')
    pickle.dump(transform, f)
    return 'saved'


"""
Sim run
"""


@app.route('/LGSVL/Run', methods=['POST'])
def run():
    sim.run(8)
    return 'sim run'


"""
Randomly Load Agents
"""


@app.route('/LGSVL/LoadNPCVehicleRandomly', methods=['POST'])
def load_npc_vehicle_randomly():
    sim.add_random_agents(lgsvl.AgentType.NPC)
    return 'NPC Loaded'


@app.route('/LGSVL/LoadPedestriansRandomly', methods=['POST'])
def load_pedestrians_randomly():
    sim.add_random_agents(lgsvl.AgentType.PEDESTRIAN)
    sim.run(6)
    # sim.run(5)
    return "Pedestrians Loaded"


@app.route('/LGSVL/Reset', methods=['POST'])
def reset_env():
    state = lgsvl.AgentState()
    state.transform = sim.get_agents()[0].state.transform
    sim.reset()
    ego = sim.add_agent("Lincoln2017MKZ (Apollo 5.0)", lgsvl.AgentType.EGO, state)
    # ego.transform.position
    ego.connect_bridge(os.environ.get("BRIDGE_HOST", APOLLO_HOST), 9090)
    global sensors
    sensors = ego.get_sensors()
    sim.get_agents()[0].on_collision(on_collision)
    # sim.run(5)
    sim.run(6)
    return "reset"


"""
Reset Agent
"""


@app.route('/LGSVL/EGOVehicle/Reset', methods=['POST'])
def clear_env():
    # FIXME, UNUSED
    # spawns = sim.get_spawn()
    # # sim.get_agents().
    # state = lgsvl.AgentState()
    # state.transform = spawns[0]
    # ego = sim.add_agent("Lincoln2017MKZ (Apollo 5.0)", lgsvl.AgentType.EGO, state)
    # sim.run()
    agents = sim.get_agents()
    # for agent in agents:
    for i in range(1, len(agents)):
        sim.remove_agent(agents[i])
    # sim.remove_agent(agents[1])
    # sim.reset()
    sim.run(6)
    return 'reset'


@app.route('/LGSVL/SaveState', methods=['POST'])
def save_state():
    state_id = str(request.args.get('ID'))

    agents = sim.get_agents()
    count_ego = 0
    count_npc = 0
    count_pedestrian = 0

    states_dict = {}

    weather_dict = {}

    weather_dict.update(
        {'rain': sim.weather.rain, 'fog': sim.weather.fog, 'wetness': sim.weather.wetness, 'time': sim.time_of_day})

    for agent in agents:
        obj_name = "None"
        obj_uid = agent.uid
        print(obj_uid, type(agent.uid))
        obj_color_vector = "None"
        obj_type = get_type(agent.__class__)
        if obj_type == 'Ego':
            obj_name = 'Ego' + str(count_ego)
            obj_color_vector = str(agent.color)
            count_ego += 1
        elif obj_type == 'NPC':
            obj_name = 'NPC' + str(count_npc)
            count_npc += 1
            obj_color_vector = str(agent.color)
        elif obj_type == 'Pedestrian':
            obj_name = 'Pedestrian' + str(count_pedestrian)
            obj_color_vector = str(agent.color)
        model = agent.name

        agent_dict = {}
        agent_dict.update({'model': model, 'name:': obj_name, 'obj_color': obj_color_vector})
        agent_dict.update({'positionX': agent.state.position.x, 'positionY': agent.state.position.y,
                           'positionZ': agent.state.position.z})
        agent_dict.update({'rotationX': agent.state.rotation.x, 'rotationY': agent.state.rotation.y,
                           'rotationZ': agent.state.rotation.z})
        agent_dict.update({'velocityX': agent.state.velocity.x, 'velocityY': agent.state.velocity.y,
                           'velocityZ': agent.state.velocity.z})
        agent_dict.update(
            {'angularVelocityX': agent.state.angular_velocity.x, 'angularVelocityY': agent.state.angular_velocity.y,
             'angularVelocityZ': agent.state.angular_velocity.z})

        states_dict.update({obj_uid: agent_dict})

    states_dict.update({'worldEffect': weather_dict})

    b = json.dumps(states_dict, indent=4)
    file = open('state/current_state_{}.json'.format(state_id), 'w')
    file.write(b)
    file.close()
    return 'save successfully'


@app.route('/LGSVL/RollBack', methods=['POST'])
def roll_back():
    state_ID = str(request.args.get('ID'))
    state = open('state/current_state_{}.json'.format(state_ID), 'r')
    content = state.read()
    state_ = json.loads(content)
    sim.weather = lgsvl.WeatherState(rain=state_['worldEffect']['rain'], fog=state_['worldEffect']['fog'],
                                     wetness=state_['worldEffect']['wetness'])
    sim.set_time_of_day(state_['worldEffect']['time'])

    for agent in sim.get_agents():
        if agent.uid not in state_.keys():
            sim.remove_agent(agent)
            continue
        agent_state = state_[agent.uid]
        position = lgsvl.Vector(float(agent_state['positionX']), float(agent_state['positionY']),
                                float(agent_state['positionZ']))
        rotation = lgsvl.Vector(float(agent_state['rotationX']), float(agent_state['rotationY']),
                                float(agent_state['rotationZ']))
        velocity = lgsvl.Vector(float(agent_state['velocityX']), float(agent_state['velocityY']),
                                float(agent_state['velocityZ']))
        angular_velocity = lgsvl.Vector(float(agent_state['angularVelocityX']), float(agent_state['angularVelocityY']),
                                        float(agent_state['angularVelocityZ']))
        state = lgsvl.AgentState()
        state.transform.position = position
        state.transform.rotation = rotation
        state.velocity = velocity
        state.angular_velocity = angular_velocity
        agent.state = state

    return 'rollback'


"""
Set weather effect
"""


@app.route('/LGSVL/Control/Weather/Nice', methods=['POST'])
def nice():
    global REALISTIC
    sim.weather = lgsvl.WeatherState(rain=0, fog=0, wetness=0)
    REALISTIC = False
    print('realistic constraints: ', REALISTIC)

    agents = sim.get_agents()
    ego = agents[0]

    return calculate_metrics(agents, ego)


@app.route('/LGSVL/Control/Weather/Rain', methods=['POST'])
def rain():
    """
    three parameters: Light, Moderate and Heavy,
    apparently, wetness will be influenced.
    :return:
    """
    global REALISTIC
    rain_level = request.args.get('rain_level')
    # print(rain_level, 'rain')
    r_level = 0
    w_level = 0
    if rain_level == 'Light':
        r_level = 0.2
        w_level = 0.2

    elif rain_level == 'Moderate':
        r_level = 0.5
        w_level = 0.5
    elif rain_level == 'Heavy':
        r_level = 1
        w_level = 1
    sim.weather = lgsvl.WeatherState(rain=r_level, fog=0, wetness=w_level)
    # sim.get_agents()[0].on_collision(on_collision)
    REALISTIC = False
    print('realistic constraints: ', REALISTIC)

    agents = sim.get_agents()
    ego = agents[0]

    return calculate_metrics(agents, ego)


@app.route('/LGSVL/Control/Weather/Fog', methods=['POST'])
def fog():
    """
    three parameters: Light, Moderate and Heavy
    :return:
    """
    global REALISTIC
    fog_level = request.args.get('fog_level')
    # print(fog_level, 'fog')
    f_level = 0
    if fog_level == 'Light':
        f_level = 0.2
    elif fog_level == 'Moderate':
        f_level = 0.5
    elif fog_level == 'Heavy':
        f_level = 1
    sim.weather = lgsvl.WeatherState(rain=0, fog=f_level, wetness=0)
    # sim.get_agents()[0].on_collision(on_collision)
    REALISTIC = False
    print('realistic constraints: ', REALISTIC)

    agents = sim.get_agents()
    ego = agents[0]
    return calculate_metrics(agents, ego)


@app.route('/LGSVL/Control/Weather/Wetness', methods=['POST'])
def wetness():
    """
    three parameters: Light, Moderate and Heavy
    :return:
    """
    global REALISTIC
    wetness_level = request.args.get('wetness_level')
    # print(wetness_level, 'wetness')
    w_level = 0
    if wetness_level == 'Light':
        w_level = 0.2
    elif wetness_level == 'Moderate':
        w_level = 0.5
    elif wetness_level == 'Heavy':
        w_level = 1
    sim.weather = lgsvl.WeatherState(rain=0, fog=0, wetness=w_level)
    # sim.get_agents()[0].on_collision(on_collision)
    REALISTIC = False
    print('realistic constraints: ', REALISTIC)
    agents = sim.get_agents()
    ego = agents[0]

    return calculate_metrics(agents, ego)


"""
Set time of day
"""


@app.route('/LGSVL/Control/TimeOfDay', methods=['POST'])
def time_of_day():
    """
    three parameters: Morning(10), Noon(14), Evening(20)
    :return:
    """
    global REALISTIC
    time = request.args.get('time_of_day')
    # print(time)
    day_time = 10  # initial time: 10
    if time == 'Morning':
        day_time = 10
    elif time == 'Noon':
        day_time = 14
    elif time == 'Evening':
        day_time = 20
    sim.set_time_of_day(day_time, fixed=True)
    # sim.get_agents()[0].on_collision(on_collision)
    REALISTIC = False
    print('realistic constraints: ', REALISTIC)

    agents = sim.get_agents()
    ego = agents[0]
    return calculate_metrics(agents, ego)


"""
Control Agents
"""


@app.route('/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane', methods=['POST'])
def add_npc_vehicle():
    """
    three parameters: Left_Lane, Right_Lane, Current_Lane,
    on each lane, the npc vehicle will drive forward without switching lane.
    :return:
    """
    global REALISTIC
    which_lane = request.args.get('which_lane')
    which_car = request.args.get('which_car')
    # print('NPC vehicle drive on', which_lane)
    ego_transform = sim.get_agents()[0].state.transform
    forward = lgsvl.utils.transform_to_forward(ego_transform)
    right = lgsvl.utils.transform_to_right(ego_transform)
    npc_state = lgsvl.AgentState()
    # convert to lane position
    if which_lane == 'Left_Lane':
        # 10 meters ahead, on left lane
        npc_state.transform.position = ego_transform.position - 4.0 * right + 20.0 * forward
    elif which_lane == 'Right_Lane':
        # 10 meters ahead, on right lane
        npc_state.transform.position = ego_transform.position + 4.0 * right + 20.0 * forward
    elif which_lane == 'Current_Lane':
        # 10 meters ahead, on current lane
        npc_state.transform.position = ego_transform.position + 20.0 * forward

    npc_state.transform.rotation = ego_transform.rotation

    car = str(which_car)
    REALISTIC = get_no_conflict_position(npc_state.position, which_car)
    print('realistic constraints: ', REALISTIC)

    npc = sim.add_agent(car, lgsvl.AgentType.NPC, npc_state, lgsvl.Vector(1, 1, 0))
    npc.follow_closest_lane(True, 5.6)
    if which_lane == "Current_Lane":
        npc.change_lane(True)
    else:
        npc.change_lane(False)
    # sim.get_agents()[0].on_collision(on_collision)
    # sim.run(5)

    agents = sim.get_agents()
    ego = agents[0]
    return calculate_metrics(agents, ego)


@app.route('/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane', methods=['POST'])
def switch_lane():
    global REALISTIC
    # print('NPC vehicle switch lane')
    which_lane = request.args.get('which_lane')
    which_car = request.args.get('which_car')
    ego_transform = sim.get_agents()[0].state.transform
    forward = lgsvl.utils.transform_to_forward(ego_transform)
    right = lgsvl.utils.transform_to_right(ego_transform)
    npc_state = lgsvl.AgentState()

    if which_lane == "Left_Lane":
        # npc_state.transform.position = ego_transform.position + 20.0 * forward - 4.0 * right
        npc_state.transform.position = ego_transform.position - 4.0 * right
    elif which_lane == "Right_Lane":
        # npc_state.transform.position = ego_transform.position + 20.0 * forward - 4.0 * right
        npc_state.transform.position = ego_transform.position + 4.0 * right
    elif which_lane == "Current_Lane":
        npc_state.transform.position = ego_transform.position + 10.0 * forward

    npc_state.transform.rotation = ego_transform.rotation

    car = str(which_car)
    REALISTIC = get_no_conflict_position(npc_state.position, which_car)
    print('realistic constraints: ', REALISTIC)

    npc = sim.add_agent(car, lgsvl.AgentType.NPC, npc_state, lgsvl.Vector(1, 1, 0))
    npc.follow_closest_lane(True, 5.6)
    if which_lane == "Current_Lane":
        npc.change_lane(False)
    else:
        npc.change_lane(True)

    # sim.get_agents()[0].on_collision(on_collision)

    agents = sim.get_agents()
    ego = agents[0]
    return calculate_metrics(agents, ego)


@app.route('/LGSVL/Control/Agents/Pedestrians/WalkRandomly', methods=['POST'])
def add_pedestrians():
    global REALISTIC
    which_lane = request.args.get('which_lane')
    # print('Pedestrian walk on', which_lane)
    ego_transform = sim.get_agents()[0].state.transform
    forward = lgsvl.utils.transform_to_forward(ego_transform)
    right = lgsvl.utils.transform_to_right(ego_transform)
    npc_state = lgsvl.AgentState()

    wp = []
    # convert to lane position
    if which_lane == 'Left_Lane':
        # 10 meters ahead, on left lane
        npc_state.transform.position = ego_transform.position - 4.0 * right + 20.0 * forward
        wp.append(lgsvl.WalkWaypoint(ego_transform.position + 4.0 * right, 1))
    elif which_lane == 'Right_Lane':
        # 10 meters ahead, on right lane
        npc_state.transform.position = ego_transform.position + 4.0 * right + 20.0 * forward
        wp.append(lgsvl.WalkWaypoint(ego_transform.position - 4.0 * right, 1))
    elif which_lane == 'Current_Lane':
        # 10 meters ahead, on current lane
        npc_state.transform.position = ego_transform.position + 50.0 * forward
        wp.append(lgsvl.WalkWaypoint(ego_transform.position + 50.0 * forward, 1))

    # npc_state.transform.position = ego_transform.position + 20 * forward - 4.0 * right
    npc_state.transform.rotation = ego_transform.rotation

    REALISTIC = get_no_conflict_position(npc_state.position, 'pedestrian')
    print('realistic constraints: ', REALISTIC)

    p = sim.add_agent("Bob", lgsvl.AgentType.PEDESTRIAN, npc_state)
    # Pedestrian will walk to a random point on sidewalk
    # p.walk_randomly(True)
    p.follow(wp, loop=True)
    # sim.get_agents()[0].on_collision(on_collision)
    # # sim.run(5)

    agents = sim.get_agents()
    ego = agents[0]
    return calculate_metrics(agents, ego)


@app.route('/LGSVL/Control/ControllableObjects/TrafficLight', methods=['POST'])
def control_traffic_light():
    # FIXME
    ego_transform = sim.get_agents()[0].state.transform
    forward = lgsvl.utils.transform_to_forward(ego_transform)
    position = ego_transform.position + 50.0 * forward
    signal = sim.get_controllable(position, "signal")

    # Create a new control policy
    control_policy = "trigger=100;red=5"
    signal.control(control_policy)
    # print(signal.current_state)
    # sim.get_agents()[0].on_collision(on_collision)
    # sim.run(5)

    agents = sim.get_agents()
    ego = agents[0]
    return calculate_metrics(agents, ego)


"""
Status APIs
"""


def interpreter_signal(signal_state):
    code = 0
    if signal_state == 'red':
        code = -1
    elif signal_state == 'yellow':
        code = 0
    elif signal_state == 'green':
        code = 1
    return code


@app.route('/LGSVL/Status/Environment/State', methods=['GET'])
def get_environment_state():
    # save_image('Main Camera')
    # save_image('Segmentation Camera')
    # Add four new state: rotation <x, y, z>, speed

    # state[0] = position.x
    # state[1] = position.y
    # state[2] = position.z
    # state[3] = rotation.x
    # state[4] = rotation.y
    # state[5] = rotation.z
    # state[6] = weather.rain
    # state[7] = weather.fog
    # state[8] = weather.wetness
    # state[9] = sim.time_of_day
    # state[10] = interpreter_signal(signal.current_state)
    # state[11] = speed
    weather = sim.weather
    position = sim.get_agents()[0].state.position
    rotation = sim.get_agents()[0].state.rotation
    signal = sim.get_controllable(position, "signal")
    speed = sim.get_agents()[0].state.speed

    state_dict = {'x': position.x, 'y': position.y, 'z': position.z,
                  'rx': rotation.x, 'ry': rotation.y, 'rz': rotation.z,
                  'rain': weather.rain, 'fog': weather.fog, 'wetness': weather.wetness,
                  'timeofday': sim.time_of_day, 'signal': interpreter_signal(signal.current_state),
                  'speed': speed}
    # state_dict = {'x': position.x, 'y': position.y, 'z': position.z,
    #               'rain': weather.rain, 'fog': weather.fog, 'wetness': weather.wetness,
    #               'timeofday': sim.time_of_day, 'signal': interpreter_signal(signal.current_state)}
    return json.dumps(state_dict)


@app.route('/LGSVL/Status/Realistic', methods=['GET'])
def get_realistic():

    return json.dumps(REALISTIC)


@app.route('/LGSVL/Status/Environment/Weather', methods=['GET'])
def get_weather():
    weather = sim.weather
    weather_dict = {'rain': weather.rain, 'fog': weather.fog, 'wetness': weather.wetness}

    return json.dumps(weather_dict)


@app.route('/LGSVL/Status/Environment/Weather/Rain', methods=['GET'])
def get_rain():
    return str(sim.weather.rain)


@app.route('/LGSVL/Status/Environment/TimeOfDay', methods=['GET'])
def get_timeofday():
    return str(sim.time_of_day)


@app.route('/LGSVL/Status/CollisionInfo', methods=['GET'])
def get_loc():
    """
    three types of collision: obstacle, NPC vehicle, pedestrian, None(no collision)
    :return:
    """
    global collision_object
    # print(collision_object)
    collision_info = str(collision_object)
    collision_object = None

    # convert collision information to one of three types
    collision_type = str(None)
    if collision_info == 'OBSTACLE':
        collision_type = "obstacle"
    if collision_info in npc_vehicle:
        collision_type = "npc_vehicle"
    if collision_info in pedestrian:
        collision_type = "pedestrian"
    return collision_type


@app.route('/LGSVL/Status/EGOVehicle/Speed', methods=['GET'])
def get_speed():
    speed = "{:.2f}".format(sim.get_agents()[0].state.speed)
    # print(speed)
    return speed


@app.route('/LGSVL/Status/EGOVehicle/Position', methods=['GET'])
def get_position():
    # Vector(-9.02999973297119, -1.03600001335144, 50.3400001525879)
    position = sim.get_agents()[0].state.position
    # x_value = ":.2f".format(position.x)
    # y_value = ":.2f".format(position.y)
    # z_value = ":.2f".format(position.z)
    # format_position = "{:.2f}".format(position.x) + " {:.2f}".format(position.y) + " {:.2f}".format(position.z)
    # print(format_position)
    # return format_position

    pos_dict = {'x': position.x, 'y': position.y, 'z': position.z}
    return json.dumps(pos_dict)


@app.route('/LGSVL/Status/EGOVehicle/Position/X', methods=['GET'])
def get_position_x():
    position = sim.get_agents()[0].state.position
    return "{:.2f}".format(position.x)


@app.route('/LGSVL/Status/EGOVehicle/Position/Y', methods=['GET'])
def get_position_y():
    position = sim.get_agents()[0].state.position
    return "{:.2f}".format(position.y)


@app.route('/LGSVL/Status/EGOVehicle/Position/Z', methods=['GET'])
def get_position_z():
    position = sim.get_agents()[0].state.position
    return "{:.2f}".format(position.z)


"""
RESTful APIs for getting GPS data
"""


@app.route('/LGSVL/Status/GPSData', methods=['GET'])
def get_gps_data():
    gps_json = {}  # dict file, also can be defined by gps_json = dict()
    gps_data = sensors[1].data

    # String format: "{:.2f}".format(gps_data.latitude), "{:.2f}".format(gps_data.longitude)
    gps_json.update({'Altitude': round(gps_data.altitude, 2), 'Latitude': round(gps_data.latitude, 2),
                     'Longitude': round(gps_data.longitude, 2), 'Northing': round(gps_data.northing, 2),
                     'Easting': round(gps_data.easting, 2)})
    return json.dumps(gps_json)


@app.route('/LGSVL/Status/GPS/Latitude', methods=['GET'])
def get_latitude():
    gps_data = sensors[1].data
    latitude = "{:.2f}".format(gps_data.latitude)
    # print("Latitude:", latitude)
    return latitude


@app.route('/LGSVL/Status/GPS/Longitude', methods=['GET'])
def get_longitude():
    gps_data = sensors[1].data
    longitude = "{:.2f}".format(gps_data.longitude)
    # print("Latitude:", longitude)
    return longitude


@app.route('/LGSVL/Status/GPS/Altitude', methods=['GET'])
def get_altitude():
    gps_data = sensors[1].data
    altitude = "{:.2f}".format(gps_data.altitude)
    return altitude


@app.route('/LGSVL/Status/GPS/Northing', methods=['GET'])
def get_northing():
    gps_data = sensors[1].data
    northing = "{:.2f}".format(gps_data.northing)
    return northing


@app.route('/LGSVL/Status/GPS/Easting', methods=['GET'])
def get_easting():
    gps_data = sensors[1].data
    easting = "{:.2f}".format(gps_data.easting)
    return easting


"""
RESTful APIs for getting camera data 
"""


@app.route('/LGSVL/Status/CenterCamera', methods=['GET'])
def get_main_camera_data():
    main = get_image('Main Camera')
    main_image_dict = {'index': main.tolist()}
    main_json = json.dumps(main_image_dict)
    return main_json


@app.route('/LGSVL/Status/LeftCamera', methods=['GET'])
def get_left_camera_data():
    left = get_image('Left Camera')
    left_image_dict = {'index': left.tolist()}
    left_json = json.dumps(left_image_dict)
    return left_json


@app.route('/LGSVL/Status/RightCamera', methods=['GET'])
def get_right_camera_data():
    right = get_image('Right Camera')
    right_image_dict = {'index': right.tolist()}
    right_json = json.dumps(right_image_dict)
    return right_json


@app.route('/LGSVL/Status/AllCamera', methods=['GET'])
def get_all_camera_data():
    main = get_image('Main Camera')
    # left = get_image('Left Camera')
    # right = get_image('Right Camera')
    # all_camera = np.hstack((main, left, right))
    # print(all_camera)
    all_camera_dict = {'index': main.tolist()}
    all_camera_json = json.dumps(all_camera_dict)
    return all_camera_json


@app.route('/LGSVL/Status/CollisionProbability', methods=['GET'])
def get_c_probability():
    global probability
    c_probability = probability
    probability = 0
    return str(c_probability)


@app.route('/LGSVL/Status/HardBrake', methods=['GET'])
def get_hard_brake():
    global speed_list
    acceleration_threshold = 8
    hard_brake = False
    speed = speed_list[0]
    for i in range(1, len(speed_list), 2):
        temp = speed_list[i]
        acceleration = abs(temp - speed) / 1
        speed = temp
        if acceleration >= acceleration_threshold:
            hard_brake = True
            break
    return json.dumps(hard_brake)


# @app.route('/LGSVL/Status/CollisionProbability', methods=['GET'])
# def get_collision_probability():
#     agents = sim.get_agents()
#     ego = agents[0]
#     ego_speed = ego.state.speed
#     ego_transform = ego.transform
#     global u
#     probability = 0
#     break_distance = calculate_safe_distance(ego_speed, u)
#     for i in range(1, len(agents)):
#         transform = agents[i].state.transform
#         current_distance = calculate_distance(transform.position, ego_transform.position)
#         print('current distance: ', current_distance)
#         if ego_transform.rotation.y - 10 < transform.rotation.y < ego_transform.rotation.y + 10:
#             # In this case, we can believe the ego vehicle and obstacle are on the same direction.
#             vector = transform.position - ego_transform.position
#             if ego_transform.rotation.y - 10 < calculate_angle(vector, z_axis) < ego_transform.rotation.y + 10:
#                 # In this case, we can believe the ego vehicle and obstacle are driving on the same lane.
#                 safe_distance = break_distance
#             else:
#                 # In this case, the ego vehicle and obstacle are not on the same lane. They are on two parallel lanes.
#                 safe_distance = 1
#         else:
#             # In this case, the ego vehicle and obstacle are either on the same direction or the same lane.
#             safe_distance = 5
#         new_probability = calculate_collision_probability(safe_distance, current_distance)
#         if new_probability > probability:
#             probability = new_probability
#     # print(probability)
#     return str(probability)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
