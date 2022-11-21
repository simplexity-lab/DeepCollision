import math
import numpy as np
import random

pedestrian = [
    "Bob",
    "EntrepreneurFemale",
    "Howard",
    "Johny",
    "Pamela",
    "Presley",
    "Robin",
    "Stephen",
    "Zoe"
]

print("Bob" in pedestrian)

# while True:
#     print(random.randint(0, 8))

npc_vehicle = {
    "Sedan",
    "SUV",
    "Jeep",
    "Hatchback",
    "SchoolBus",
    "BoxTruck"
}


#
# for v in pedestrian:
#     print(v, pedestrian[v])
def calculate_angle_tan(k1, k2):
    if k1 == k2:
        k2 = k2 - 0.0001
    tan_theta = abs((k1 - k2) / (1 + k1 * k2))
    theta = np.arctan(tan_theta)
    return theta


def calculate_angle(vector1, vector2):
    cos_theta = (vector1.x * vector2.x + vector1.y * vector2.y + vector1.z * vector2.z) / \
                ((math.sqrt(vector1.x * vector1.x + vector1.y * vector1.y + vector1.z * vector1.z) *
                  math.sqrt(vector2.x * vector2.x + vector2.y * vector2.y + vector2.z * vector2.z)))
    theta = np.arccos(cos_theta)
    # print(cos_theta)
    return theta


def calculate_distance(vector1, vector2):
    distance = math.sqrt(pow(vector1.x - vector2.x, 2) + pow(vector1.y - vector2.y, 2) + pow(vector1.z - vector2.z, 2))
    return distance


# Calculate safe distance
def calculate_safe_distance(speed, u):
    safe_distance = (speed * speed) / (2 * 9.8 * u)
    return safe_distance


# Calculate collision probability
def calculate_collision_probability(safe_distance, current_distance):
    collision_probability = None
    if current_distance >= safe_distance:
        collision_probability = 0
    elif current_distance < safe_distance:
        collision_probability = (safe_distance - current_distance) / safe_distance
    return collision_probability


def get_collision_probability(agents, ego, agents_len, u, z_axis):
    # agents = sim.get_agents()
    # ego = agents[0]
    ego_speed = ego.state.speed
    ego_transform = ego.transform
    # global u
    probability = probability1 = probability2 = probability3 = 0
    break_distance = calculate_safe_distance(ego_speed, u)
    for i in range(1, agents_len):
        transform = agents[i].state.transform
        current_distance = calculate_distance(transform.position, ego_transform.position)
        # print('current distance: ', current_distance)
        if current_distance > 40:
            continue
        if ego_transform.rotation.y - 10 < transform.rotation.y < ego_transform.rotation.y + 10:
            # In this case, we can believe the ego vehicle and obstacle are on the same direction.
            vector = transform.position - ego_transform.position
            if ego_transform.rotation.y - 10 < calculate_angle(vector, z_axis) < ego_transform.rotation.y + 10:
                # In this case, we can believe the ego vehicle and obstacle are driving on the same lane.
                safe_distance = break_distance
                probability1 = calculate_collision_probability(safe_distance, current_distance)
            else:
                # In this case, the ego vehicle and obstacle are not on the same lane. They are on two parallel lanes.
                safe_distance = 1
                probability2 = calculate_collision_probability(safe_distance, current_distance)
        else:
            # In this case, the ego vehicle and obstacle are either on the same direction or the same lane.
            safe_distance = 5
            probability3 = calculate_collision_probability(safe_distance, current_distance)
        new_probability = probability1 + (1 - probability1) * 0.2 * probability2 + \
                          (1 - probability1) * 0.8 * probability3
        if new_probability > probability:
            probability = new_probability
    # print(probability)
    return str(probability)


def get_line(agent):
    agent_position_x = agent.transform.position.x
    agent_position_z = agent.transform.position.z

    agent_velocity_x = agent.state.velocity.x if agent.state.velocity.x != 0 else 0.0001
    agent_velocity_z = agent.state.velocity.z

    # print('x, z, vx, vz: ', agent_position_x, agent_position_z, agent_velocity_x, agent_velocity_z)
    # if agent_velocity_x == 0:
    #     agent_velocity_x = 0.0001
    # print('k, b: ', agent_velocity_z / agent_velocity_x, -(agent_velocity_z / agent_velocity_x) * agent_position_x + agent_position_z)

    return agent_velocity_z / agent_velocity_x, -(
                agent_velocity_z / agent_velocity_x) * agent_position_x + agent_position_z


def get_distance(agent, x, z):
    return math.sqrt(pow(agent.transform.position.x - x, 2) + pow(agent.transform.position.z - z, 2))


def judge_same_line(agent1, agent2, k1, k2):
    judge = False
    ego_ahead = False
    direction_vector = (agent1.transform.position.x - agent2.transform.position.x, agent1.transform.position.z - agent2.transform.position.z)
    distance = get_distance(agent1, agent2.transform.position.x, agent2.transform.position.z)

    if abs(k1 - k2) < 0.6:
        if abs((agent1.transform.position.z - agent2.transform.position.z) /
               ((agent1.transform.position.x - agent2.transform.position.x) if (agent1.transform.position.x - agent2.transform.position.x) != 0 else 0.01) - (k1 + k2) / 2) < 0.6:
            judge = True

    if not judge:
        return judge, ego_ahead, -1

    if direction_vector[0] * agent1.state.velocity.x >= 0 and direction_vector[1] * agent1.state.velocity.z >= 0:
        ego_ahead = True  # Ego ahead of NPC.
        TTC = distance / (agent1.state.speed - agent2.state.speed)
    else:
        TTC = distance / (agent2.state.speed - agent1.state.speed)
    if TTC < 0:
        TTC = 100000

    return judge, ego_ahead, TTC


def calculate_TTC(agents, ego, dis_tag):
    trajectory_ego_k, trajectory_ego_b = get_line(ego)
    ego_speed = ego.state.speed if ego.state.speed > 0 else 0.0001

    # time_ego_list = []
    # time_agent_list = []
    TTC = 100000
    distance = 100000
    loProC_list, laProC_list = [0], [0]

    for i in range(1, len(agents)):
        if dis_tag:
            dis = get_distance(ego, agents[i].transform.position.x, agents[i].transform.position.z)
            distance = dis if dis <= distance else distance
        # print('distance:', get_distance(ego, agents[i].transform.position.x, agents[i].transform.position.z))
        trajectory_agent_k, trajectory_agent_b = get_line(agents[i])
        agent_speed = agents[i].state.speed if agents[i].state.speed > 0 else 0.0001

        same_lane, _, ttc = judge_same_line(ego, agents[i], trajectory_ego_k, trajectory_agent_k)
        # print('same_lane, TTC: ', same_lane, ttc)
        if same_lane:
            # print('Driving on Same Lane, TTC: {}'.format(ttc))
            time_ego = ttc
            time_agent = ttc
        else:
            trajectory_agent_k = trajectory_agent_k if trajectory_ego_k - trajectory_agent_k != 0 else trajectory_agent_k + 0.0001

            collision_point_x, collision_point_z = (trajectory_agent_b - trajectory_ego_b) / (trajectory_ego_k - trajectory_agent_k), \
                                                   (trajectory_ego_k * trajectory_agent_b - trajectory_agent_k * trajectory_ego_b) / (trajectory_ego_k - trajectory_agent_k)

            ego_distance = get_distance(ego, collision_point_x, collision_point_z)
            agent_distance = get_distance(agents[i], collision_point_x, collision_point_z)
            time_ego = ego_distance / ego_speed
            time_agent = agent_distance / agent_speed
            # print('Driving on Different Lane, TTC: {}'.format(time_ego))

        if abs(time_ego - time_agent) < 1:
            TTC = min(TTC, (time_ego + time_agent) / 2)

    return TTC, distance


def calculate_measures(agents, ego, dis_tag):
    trajectory_ego_k, trajectory_ego_b = get_line(ego)
    ego_speed = ego.state.speed if ego.state.speed > 0 else 0.0001

    # time_ego_list = []
    # time_agent_list = []
    TTC = 100000
    distance = 100000
    loProC_list, laProC_list = [0], [0]  # probability

    for i in range(1, len(agents)):
        if dis_tag:
            dis = get_distance(ego, agents[i].transform.position.x, agents[i].transform.position.z)
            distance = dis if dis <= distance else distance
        # print('distance:', get_distance(ego, agents[i].transform.position.x, agents[i].transform.position.z))
        trajectory_agent_k, trajectory_agent_b = get_line(agents[i])
        agent_speed = agents[i].state.speed if agents[i].state.speed > 0 else 0.0001

        same_lane, ego_ahead, ttc = judge_same_line(ego, agents[i], trajectory_ego_k, trajectory_agent_k)
        ego_deceleration = 6  # probability
        if same_lane:
            # print('Driving on Same Lane, TTC: {}'.format(ttc))
            time_ego = ttc
            time_agent = ttc

            loSD = 100000
            if agents[i].type == 2:  # type value, 1-EGO, 2-NPC, 3-Pedestrian
                agent_deceleration = 6
                loSD = 1 / 2 * (
                    abs(pow(ego_speed, 2) / ego_deceleration - pow(agent_speed, 2) / agent_deceleration)) + 5
            else:
                agent_deceleration = 1.5
                if not ego_ahead:
                    loSD = 1 / 2 * (pow(ego_speed, 2) / ego_deceleration - pow(agent_speed, 2) / agent_deceleration) + 5
            loProC = calculate_collision_probability(loSD, distance)
            loProC_list.append(loProC)
        else:
            trajectory_agent_k = trajectory_agent_k if trajectory_ego_k - trajectory_agent_k != 0 else trajectory_agent_k + 0.0001

            collision_point_x, collision_point_z = (trajectory_agent_b - trajectory_ego_b) / (
                        trajectory_ego_k - trajectory_agent_k), \
                                                   (
                                                               trajectory_ego_k * trajectory_agent_b - trajectory_agent_k * trajectory_ego_b) / (
                                                               trajectory_ego_k - trajectory_agent_k)

            ego_distance = get_distance(ego, collision_point_x, collision_point_z)
            agent_distance = get_distance(agents[i], collision_point_x, collision_point_z)
            time_ego = ego_distance / ego_speed
            time_agent = agent_distance / agent_speed
            # print('Driving on Different Lane, TTC: {}'.format(time_ego))

            theta = calculate_angle_tan(trajectory_ego_k, trajectory_agent_k)
            # print(trajectory_ego_k, trajectory_agent_k, theta)
            laSD = pow(ego_speed * math.sin(theta), 2) / (ego_deceleration * math.sin(theta)) + 5
            laProC = calculate_collision_probability(laSD, distance)
            laProC_list.append(laProC)

        if abs(time_ego - time_agent) < 1:
            TTC = min(TTC, (time_ego + time_agent) / 2)

    loProC_dt, laProC_dt = max(loProC_list), max(laProC_list)
    proC_dt = max(loProC_dt, laProC_dt) + (1 - max(loProC_dt, laProC_dt)) * min(loProC_dt, laProC_dt)

    return TTC, distance, proC_dt


if __name__ == "__main__":
    # v1 = lgsvl.Vector(0, 0, 1)
    # v2 = lgsvl.Vector(0, 1, 1)
    #
    # print(calculate_angle(v1, v2))
    # print(calculate_distance(v1, v2))
    print(calculate_collision_probability(10, 2))

    a = (1, 99, 3)
    print(a[2])
# print(npc_vehicle)
