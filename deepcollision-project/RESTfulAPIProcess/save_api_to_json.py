import json

RESTful_API = {
    "command": {
        'num': 22,
        '0': "http://192.168.1.121:5000/LGSVL/LoadNPCVehicleRandomly",
        '1': "http://192.168.1.121:5000/LGSVL/LoadPedestriansRandomly",
        '2': "http://192.168.1.121:5000/LGSVL/Control/Weather/Nice",
        '3': "http://192.168.1.121:5000/LGSVL/Control/Weather/Rain?rain_level=Light",
        '4': "http://192.168.1.121:5000/LGSVL/Control/Weather/Rain?rain_level=Moderate",
        '5': "http://192.168.1.121:5000/LGSVL/Control/Weather/Rain?rain_level=Heavy",
        '6': "http://192.168.1.121:5000/LGSVL/Control/Weather/Fog?fog_level=Light",
        '7': "http://192.168.1.121:5000/LGSVL/Control/Weather/Fog?fog_level=Moderate",
        '8': "http://192.168.1.121:5000/LGSVL/Control/Weather/Fog?fog_level=Heavy",
        '9': "http://192.168.1.121:5000/LGSVL/Control/Weather/Wetness?wetness_level=Light",
        '10': "http://192.168.1.121:5000/LGSVL/Control/Weather/Wetness?wetness_level=Moderate",
        '11': "http://192.168.1.121:5000/LGSVL/Control/Weather/Wetness?wetness_level=Heavy",
        '12': "http://192.168.1.121:5000/LGSVL/Control/TimeOfDay?time_of_day=Morning",
        '13': "http://192.168.1.121:5000/LGSVL/Control/TimeOfDay?time_of_day=Noon",
        '14': "http://192.168.1.121:5000/LGSVL/Control/TimeOfDay?time_of_day=Evening",
        '15': "http://192.168.1.121:5000/LGSVL/Control/Agents/NPCVehicle/AddNPCVehicle?which_lane=Left_Lane",
        '16': "http://192.168.1.121:5000/LGSVL/Control/Agents/NPCVehicle/AddNPCVehicle?which_lane=Right_Lane",
        '17': "http://192.168.1.121:5000/LGSVL/Control/Agents/NPCVehicle/AddNPCVehicle?which_lane=Current_Lane",
        '18': "http://192.168.1.121:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane",
        '19': "http://192.168.1.121:5000/LGSVL/Control/Agents/Pedestrians/WalkRandomly?which_lane=Left_Lane",
        '20': "http://192.168.1.121:5000/LGSVL/Control/Agents/Pedestrians/WalkRandomly?which_lane=Right_Lane",
        '21': "http://192.168.1.121:5000/LGSVL/Control/Agents/Pedestrians/WalkRandomly?which_lane=Current_Lane"
    },
    "status": {
        'num': 4,
        '0': "http://192.168.1.121:5000/LGSVL/Status/CollisionInfo",
        '1': "http://192.168.1.121:5000/LGSVL/Status/EGOVehicle/Speed",
        '2': "http://192.168.1.121:5000/LGSVL/Status/EGOVehicle/Position",
        '3': "http://192.168.1.121:5000/LGSVL/Status/GPSData"

    }
}

# a = [{"type": "CAN-Bus", "name": "CAN Bus",
#             "params": {"Frequency": 10, "Topic": "/apollo/canbus/chassis"},
#             "transform": {"x": 0, "y": 0, "z": 0, "pitch": 0, "yaw": 0, "roll": 0}},{"type": "GPS Device", "name": "GPS",
#             "params": {"Frequency": 12.5, "Topic": "/apollo/sensor/gnss/best_pose", "Frame": "gps"},
#             "transform": {"x": 0, "y": 0, "z": -1.348649, "pitch": 0, "yaw": 0, "roll": 0}},{"type": "GPS Odometry", "name": "GPS Odometry",
#             "params": {"Frequency": 12.5, "Topic": "/apollo/sensor/gnss/odometry", "Frame": "gps"},
#             "transform": {"x": 0, "y": 0, "z": -1.348649, "pitch": 0, "yaw": 0, "roll": 0}},{"type": "GPS-INS Status", "name": "GPS INS Status",
#             "params": {"Frequency": 12.5, "Topic": "/apollo/sensor/gnss/ins_stat", "Frame": "gps"},
#             "transform": {"x": 0, "y": 0, "z": -1.348649, "pitch": 0, "yaw": 0, "roll": 0}},{"type": "IMU", "name": "IMU",
#             "params": {"Topic": "/apollo/sensor/gnss/imu", "Frame": "imu", "CorrectedTopic": "/apollo/sensor/gnss/corrected_imu", "CorrectedFrame": "imu"},
#             "transform": {"x": 0, "y": 0, "z": -1.348649, "pitch": 0, "yaw": 0, "roll": 0}},{"type": "Radar", "name": "Radar",
#                "params": {"Frequency": 13.4, "Topic": "/apollo/sensor/conti_radar"},
#                "transform": {"x": 0, "y": 0.689, "z": 2.272, "pitch": 0, "yaw": 0, "roll": 0}},{"type": "Lidar", "name": "Lidar",
#             "params": {"LaserCount": 32, "MinDistance": 0.5, "MaxDistance": 100, "RotationFrequency": 10, "MeasurementsPerRotation": 360, "FieldOfView": 41.33, "CenterAngle": 10, "Compensated": 'true', "PointColor": "#ff000000", "Topic": "/apollo/sensor/lidar128/compensator/PointCloud2", "Frame": "velodyne"},
#             "transform": {"x": 0, "y": 2.312, "z": -0.11, "pitch": 0, "yaw": 0, "roll": 0}},{"type": "Color Camera", "name": "Main Camera",
#             "params": {"Width": 1920, "Height": 1080, "Frequency": 15, "JpegQuality": 75, "FieldOfView": 50, "MinDistance": 0.1, "MaxDistance": 1000, "Topic": "/apollo/sensor/camera/front_6mm/image/compressed"},
#             "transform": {"x": 0, "y": 1.7, "z": -0.2, "pitch": 0, "yaw": 0, "roll": 0}},{"type": "Color Camera", "name": "Telephoto Camera",
#             "params": {"Width": 1920, "Height": 1080, "Frequency": 15, "JpegQuality": 75, "FieldOfView": 10, "MinDistance": 0.1, "MaxDistance": 1000, "Topic": "/apollo/sensor/camera/front_12mm/image/compressed"},
#             "transform": {"x": 0, "y": 1.7, "z": -0.2, "pitch": -4, "yaw": 0, "roll": 0}},{"type": "Keyboard Control", "name": "Keyboard Car Control"},{"type": "Wheel Control", "name": "Wheel Car Control"},{"type": "Vehicle Control", "name": "Apollo Car Control",
#             "params": {"Topic": "/apollo/control"} }]


b = json.dumps(RESTful_API, indent=4)
file = open('RESTful_API.json', 'w')
file.write(b)
file.close()
