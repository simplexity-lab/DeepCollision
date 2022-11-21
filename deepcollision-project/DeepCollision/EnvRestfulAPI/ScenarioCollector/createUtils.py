# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/3 15:25
# @Author  : Chengjie
# @File    : createUtils.py


import xml.dom.minidom

# doc = xml.dom.minidom.Document()
# root = doc.createElement('SVLScenario')


def initialization(datatime='2021-7-8', timestamp='1625673600', weatherdataset='./Nanjing_2021-7-8.json'):
    doc = xml.dom.minidom.Document()
    root = doc.createElement('SVLScenario')

    fileheader = doc.createElement('FileHeader')
    fileheader.setAttribute('simulatorVersion', '2021.01')
    fileheader.setAttribute('date', '2021-11-27T10:00:00')
    fileheader.setAttribute('description', 'SVL Scenario Format')
    fileheader.setAttribute('author', 'DeepCollision')

    environment = doc.createElement('Environment')
    hdmap = doc.createElement('HDMap')
    hdmap.setAttribute('city', 'SanFrancisco')
    realworldeffect = doc.createElement('RealWorldEffect')
    realworldeffect.setAttribute('dateTime', datatime)
    realworldeffect.setAttribute('unixTimeStamp', timestamp)
    realworldeffect.setAttribute('fixTime', 'False')
    openweatherdatabase = doc.createElement('OpenWeatherDatabase')
    openweatherdatabase.setAttribute('filepath', weatherdataset)
    environment.appendChild(hdmap)
    environment.appendChild(realworldeffect)
    environment.appendChild(openweatherdatabase)

    root.appendChild(fileheader)
    root.appendChild(environment)

    doc.appendChild(root)
    return doc, root


def create_scenario_object(name, doc, model, object_uid, object_type, color_vector):
    color = 'Default'
    if color_vector == 'Vector(-1, -1, -1)':
        color = 'Default'
    elif color_vector == 'Vector(0, 0, 0)':
        color = 'black'
    elif color_vector == 'Vector(1, 1, 1)':
        color = 'white'
    elif color_vector == 'Vector(1, 1, 0)':
        color = 'yellow'
    elif color_vector == 'Vector(1, 0, 1)':
        color = 'pink'
    elif color_vector == 'Vector(0, 1, 1)':
        color = 'skyblue'
    elif color_vector == 'Vector(0, 1, 1)':
        color = 'red'
    elif color_vector == 'Vector(0, 1, 1)':
        color = 'green'
    elif color_vector == 'Vector(0, 1, 1)':
        color = 'blue'

    scenarioobject = doc.createElement('ScenarioObject')
    scenarioobject.setAttribute('name', name)
    scenarioobject.setAttribute('model', model)
    scenarioobject.setAttribute('uid', object_uid)

    objectparameter = doc.createElement('ObjectParameter')
    objectparameter.setAttribute('ObjectType', object_type)
    objectparameter.setAttribute('ObjectColor', color)
    objectparameter.setAttribute('ObjectColorVector', color_vector)
    scenarioobject.appendChild(objectparameter)
    return scenarioobject


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


def initializeStory(agents, doc, root):
    entities = doc.createElement('Entities')
    storyboard = doc.createElement('StoryBoard')
    init = doc.createElement('Initialization')

    count_ego = 0
    count_npc = 0
    count_pedestrian = 0
    for agent in agents:
        obj_name = "None"
        obj_uid = agent.uid
        # print(obj_uid, type(agent.uid))
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

        entity = create_scenario_object(obj_name, doc, model, obj_uid, get_type(agent.__class__), obj_color_vector)
        entities.appendChild(entity)

        obj_init = doc.createElement('ObjectInitialization')
        obj_init.setAttribute('objectRef', obj_name)

        obj_position = doc.createElement('ObjectInitialPosition')
        obj_position.setAttribute('positionX', str(round(agent.state.position.x, 3)))
        obj_position.setAttribute('positionY', str(round(agent.state.position.y, 3)))
        obj_position.setAttribute('positionZ', str(round(agent.state.position.z, 3)))

        obj_rotation = doc.createElement('ObjectInitialRotation')
        obj_rotation.setAttribute('rotationX', str(round(agent.state.rotation.x, 3)))
        obj_rotation.setAttribute('rotationY', str(round(agent.state.rotation.y, 3)))
        obj_rotation.setAttribute('rotationZ', str(round(agent.state.rotation.z, 3)))

        obj_velocity = doc.createElement('ObjectInitialVelocity')
        obj_velocity.setAttribute('velocityX', str(round(agent.state.velocity.x, 3)))
        obj_velocity.setAttribute('velocityY', str(round(agent.state.velocity.y, 3)))
        obj_velocity.setAttribute('velocityZ', str(round(agent.state.velocity.z, 3)))

        obj_angular_velocity = doc.createElement('ObjectInitialAngularVelocity')
        obj_angular_velocity.setAttribute('angularVelocityX', str(round(agent.state.angular_velocity.x, 3)))
        obj_angular_velocity.setAttribute('angularVelocityY', str(round(agent.state.angular_velocity.y, 3)))
        obj_angular_velocity.setAttribute('angularVelocityZ', str(round(agent.state.angular_velocity.z, 3)))

        obj_init.appendChild(obj_position)
        obj_init.appendChild(obj_rotation)
        obj_init.appendChild(obj_velocity)
        obj_init.appendChild(obj_angular_velocity)
        # v_x = agent.state.velocity.x

        init.appendChild(obj_init)

    root.appendChild(entities)
    storyboard.appendChild(init)
    return entities, storyboard


def create_story_by_timestamp(timeStamp, doc, story, entities, agents, sim):
    """
    Create story by timestamp.
    :param doc:
    :param agents:
    :param sim:
    :param entities:
    :param timeStamp:
    :param story:
    :return:
    """
    ego_speed = round(agents[0].state.speed, 3)
    for agent in agents:

        for entity in entities.getElementsByTagName('ScenarioObject'):
            wp_agent = doc.createElement('WayPoint')
            wp_agent.setAttribute('timeStamp', str(timeStamp))

            if entity.getAttribute('uid') == agent.uid:
                new = True
                action = None
                for oa in story.getElementsByTagName('ObjectAction'):
                    if oa.getAttribute('name') == 'Act_{}'.format(entity.getAttribute('name')):
                        new = False
                        action = oa
                        break
                if new:
                    action = doc.createElement('ObjectAction')
                    action.setAttribute('name', 'Act_{}'.format(entity.getAttribute('name')))
                    object_ref = doc.createElement('objectRef')
                    object_ref.setAttribute('objectRef', entity.getAttribute('name'))
                    action.appendChild(object_ref)

                dynamic_parameters = doc.createElement('DynamicParameters')
                speed = doc.createElement('Speed')
                velocity = doc.createElement('Velocity')
                angular_velocity = doc.createElement('AngularVelocity')

                speed.setAttribute('speed', str(round(agent.state.speed, 3)))
                velocity.setAttribute('velocityX', str(round(agent.state.velocity.x, 3)))
                velocity.setAttribute('velocityY', str(round(agent.state.velocity.y, 3)))
                velocity.setAttribute('velocityZ', str(round(agent.state.velocity.z, 3)))

                angular_velocity.setAttribute('angularVelocityX', str(round(agent.state.angular_velocity.x, 3)))
                angular_velocity.setAttribute('angularVelocityY', str(round(agent.state.angular_velocity.y, 3)))
                angular_velocity.setAttribute('angularVelocityZ', str(round(agent.state.angular_velocity.z, 3)))

                dynamic_parameters.appendChild(speed)
                dynamic_parameters.appendChild(velocity)
                dynamic_parameters.appendChild(angular_velocity)

                wp_agent.appendChild(dynamic_parameters)

                geographic_parameters = doc.createElement('GeographicParameters')
                position = doc.createElement('ObjectPosition')
                position.setAttribute('positionX', str(round(agent.state.position.x, 3)))
                position.setAttribute('positionY', str(round(agent.state.position.y, 3)))
                position.setAttribute('positionZ', str(round(agent.state.position.z, 3)))

                rotation = doc.createElement('ObjectRotation')
                rotation.setAttribute('rotationX', str(round(agent.state.rotation.x, 3)))
                rotation.setAttribute('rotationY', str(round(agent.state.rotation.y, 3)))
                rotation.setAttribute('rotationZ', str(round(agent.state.rotation.z, 3)))

                gps_node = doc.createElement('ObjectGPS')
                gps = sim.map_to_gps(agent.transform)
                gps_node.setAttribute('latitude', str(round(gps.latitude, 3)))
                gps_node.setAttribute('longitude', str(round(gps.longitude, 3)))
                gps_node.setAttribute('northing', str(round(gps.northing, 3)))
                gps_node.setAttribute('easting', str(round(gps.easting, 3)))
                gps_node.setAttribute('altitude', str(round(gps.altitude, 3)))
                gps_node.setAttribute('orientation', str(round(gps.orientation, 3)))

                geographic_parameters.appendChild(position)
                geographic_parameters.appendChild(rotation)
                geographic_parameters.appendChild(gps_node)

                wp_agent.appendChild(geographic_parameters)

                action.appendChild(wp_agent)
                if new:
                    story.appendChild(action)
                break
    return ego_speed


def create_story(doc, entities, agents):
    story = doc.createElement('Story')
    story.setAttribute('name', 'Default')
    create_story_by_timestamp(0.5, story, entities, agents)
    create_story_by_timestamp(1, story, entities, agents)
    create_story_by_timestamp(1.5, story, entities, agents)
    create_story_by_timestamp(2, story, entities, agents)
    create_story_by_timestamp(2.5, story, entities, agents)
    return story
