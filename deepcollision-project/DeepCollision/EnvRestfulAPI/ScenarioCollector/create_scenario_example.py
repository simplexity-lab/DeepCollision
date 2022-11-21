# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/3 15:28
# @Author  : Chengjie
# @File    : npc_follow_waypoints.py

# !/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import copy
import json
import socket
import sys
from environs import Env
import lgsvl
from ScenarioCollector.createUtils import *

print("Python API Quickstart #13: NPC following waypoints")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host),
                      env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))
if sim.current_scene == lgsvl.wise.DefaultAssets.map_sanfrancisco:
    sim.reset()
else:
    sim.load(lgsvl.wise.DefaultAssets.map_sanfrancisco)

spawns = sim.get_spawn()
forward = lgsvl.utils.transform_to_forward(spawns[0])
right = lgsvl.utils.transform_to_right(spawns[0])

# Creating state object to define state for Ego and NPC
state = lgsvl.AgentState()
state.transform = spawns[0]

# Ego
ego_state = copy.deepcopy(state)
ego_state.transform.position += 50 * forward
ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5),
                    lgsvl.AgentType.EGO, state)
ego.connect_bridge(env.str("LGSVL__AUTOPILOT_0_HOST", lgsvl.wise.SimulatorSettings.remote_bridge_host), env.int("LGSVL__AUTOPILOT_0_PORT", lgsvl.wise.SimulatorSettings.bridge_port))

# NPC
npc_state = copy.deepcopy(state)
npc_state.transform.position += 10 * forward
npc = sim.add_agent("Sedan", lgsvl.AgentType.NPC, npc_state, lgsvl.Vector(1, 1, 1))

state = lgsvl.AgentState()
# Spawn the pedestrian in front of car
state.transform.position = spawns[0].position - 4 * right + 20 * forward
state.transform.rotation = spawns[0].rotation
p = sim.add_agent("Bob", lgsvl.AgentType.PEDESTRIAN, state)
p.walk_randomly(True)

vehicles = {
    ego: "EGO",
    npc: "Sedan",
}

# Executed upon receiving collision callback -- NPC is expected to drive through colliding objects
collision = False


def on_collision(agent1, agent2, contact):
    global collision
    name1 = agent1.__dict__.get('name')
    name2 = agent2.__dict__.get('name') if agent2 is not None else "OBSTACLE"
    print("{} collided with {} at {}".format(name1, name2, contact))
    collision = True


ego.on_collision(on_collision)
npc.on_collision(on_collision)

# This block creates the list of waypoints that the NPC will follow
# Each waypoint is an position vector paired with the speed that the NPC will drive to it
waypoints = []
x_max = 2
z_delta = 12

layer_mask = 0
layer_mask |= 1 << 0  # 0 is the layer for the road (default)

for i in range(20):
    speed = 12  # if i % 2 == 0 else 12
    px = 0
    pz = (i + 1) * z_delta
    # Waypoint angles are input as Euler angles (roll, pitch, yaw)
    angle = spawns[0].rotation
    # Raycast the points onto the ground because BorregasAve is not flat
    hit = sim.raycast(
        spawns[0].position + pz * forward, lgsvl.Vector(0, -1, 0), layer_mask
    )

    # NPC will wait for 1 second at each waypoint
    wp = lgsvl.DriveWaypoint(hit.point, speed, angle)
    waypoints.append(wp)


# When the NPC is within 0.5m of the waypoint, this will be called
def on_waypoint(agent, index):
    print("waypoint {} reached".format(index))


# The above function needs to be added to the list of callbacks for the NPC
npc.on_waypoint_reached(on_waypoint)

# The NPC needs to be given the list of waypoints.
# A bool can be passed as the 2nd argument that controls whether or not the NPC loops over the waypoints (default false)
npc.follow(waypoints)

agents = sim.get_agents()

print(sim.map_to_gps(agents[0].transform))

initialization()
entities, storyboard = initializeStory(agents)
story = doc.createElement('Story')
story.setAttribute('name', 'Default')

##########

HOST = '192.168.50.51'  # or 'localhost'
PORT = 6001
ADDR = (HOST, PORT)
ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.connect(ADDR)

# sim.run(30)
f = open('target_speed3.txt', 'w', encoding='utf-8')
target_speed = 0
for i in range(200):
    ego_speed = create_story_by_timestamp(i + 1, story, entities, agents, sim)
    # print(ego_speed, target_speed)
    # f.writelines(str(ego_speed) + " " + str(target_speed) + '\n')
    f.writelines(str(target_speed) + '\n')
    ss.send(json.dumps(['start']).encode('utf-8'))
    sim.run(0.1)
    ss.send(json.dumps(['stop']).encode('utf-8'))
    state_arr = ss.recv(1024)
    state_arr = json.loads(state_arr.decode('utf-8'))
    # print(state_arr[0])
    target_speed = state_arr[len(state_arr) - 1]['target_speed']
    # print(state_arr)

    if collision:
        break

f.close()
storyboard.appendChild(story)
root.appendChild(storyboard)
root.setAttribute('timestep', '0.1')

fp = open('./target3.deepscenario', 'w')
doc.writexml(fp, addindent='\t', newl='\n', encoding="utf-8")
