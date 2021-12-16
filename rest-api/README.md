# DeepCollision REST APIs

## Ⅰ. DeepCollision REST API Example

> This section is an example demonstrating how to use **DeepCollision REST APIs** for environment parameter configurations.<br/>
> You can refer it to write your own Python programs.<br/>
> Also we provide a [video](https://github.com/DeepCollision/DeepCollisionData/blob/main/REST%20APIs/Demo.mkv) to show an running example.

### Prerequisite
Users can access our server with Apollo and LGSVL deployed through our provided REST APIs. To call the APIs through Python Scripts, one needs to install [requests](https://docs.python-requests.org/en/latest/):

```sh
$ python -m pip install requests
```

### Visualization

We have integrated the REST APIs into LGSVL and Apollo and put the into online server, users can see the effects of the environment configuration following the below instructions.
- Open Apollo Dreamviewer in browser by navigating to this [link (http://101.35.135.164:8888/)](http://101.35.135.164:8888/).
![image](https://user-images.githubusercontent.com/26716009/146319148-5825df37-e8f4-44be-8271-73edd9dff311.png)

- Select the **Lincoln2017MKZ** vehicle and **San Francisco** map in the top right corner.

- Enable **Localization**, **Transform**, **Perception**, **Traffic Light**, **Planning**, **Prediction**, **Routing**, and **Control** modules.


<!-- #### Example -->
### Step 1: Load scene and generate AVUT's initial position

There are two parameters in **LoadScene API**: the first one is Map, and the second one is the road which the AVUT will drive on.

```python
import requests
requests.post("http://101.35.135.164:5000/LGSVL/LoadScene?scene=SanFrancisco&road_num=1")
```
Once the scene is loaded, the loaded vehicle and map will show in Apollo Dreamviewer.
![image](https://user-images.githubusercontent.com/26716009/146320798-a3164a71-2db7-469e-b004-4834acd0a906.png)

### Step 2: Configure the operating environment

Add a Sedan switching lane from left to right.

```python
requests.post("http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Left_Lane&which_car=Sedan")

```
Once the Sedan is added, the effect can be seen below.
![image](https://user-images.githubusercontent.com/26716009/146322330-781d9690-dc2d-4b3f-b0ca-c8f06421e252.png)

### Step 3: Get state returned

```python
r = requests.get("http://101.35.135.164:5000/LGSVL/Status/Environment/State")
a = r.json()
#### State returned after one configuration action executed.
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
```
The returned state will be used as the new state S<sub>t+1</sub>. Users can also use other GET method to obtain state like *GPS Data*, *EGO vehicle status*.

## Ⅱ. REST API List

> This section lists all the REST APIs in DeepCollision for environment parameter configurations.<br/>

## Main Page

http://101.35.135.164:5000/LGSVL

## Command API [POST]
### Load Scene
http://101.35.135.164:5000/LGSVL/LoadScene?scene=<scene_name>&road_num=<road_num>

In our experiment the scene_name is 'SanFrancisco'.

### Set weather effect
**1. Nice weather**  
http://101.35.135.164:5000/LGSVL/Control/Weather/Nice  
**2. Rain**  
2.1. Light Rain  
http://101.35.135.164:5000/LGSVL/Control/Weather/Rain?rain_level=Light  
2.2. Moderate Rain  
http://101.35.135.164:5000/LGSVL/Control/Weather/Rain?rain_level=Moderate  
2.3. Heavy Rain  
http://101.35.135.164:5000/LGSVL/Control/Weather/Rain?rain_level=Heavy  
**3. Fog**  
3.1. Light Fog  
http://101.35.135.164:5000/LGSVL/Control/Weather/Fog?fog_level=Light  
3.2. Moderate Fog  
http://101.35.135.164:5000/LGSVL/Control/Weather/Fog?fog_level=Moderate  
3.3. Heavy Fog  
http://101.35.135.164:5000/LGSVL/Control/Weather/Fog?fog_level=Heavy  
**4. Wetness**  
4.1. Light Wetness  
http://101.35.135.164:5000/LGSVL/Control/Weather/Wetness?wetness_level=Light  
4.2. Moderate Wetness  
http://101.35.135.164:5000/LGSVL/Control/Weather/Wetness?wetness_level=Moderate  
4.3. Heavy Wetness  
http://101.35.135.164:5000/LGSVL/Control/Weather/Wetness?wetness_level=Heavy  

### Set time of day
**5. Time of Day**  
5.1. Morning  
http://101.35.135.164:5000/LGSVL/Control/TimeOfDay?time_of_day=Morning  
5.2. Noon  
http://101.35.135.164:5000/LGSVL/Control/TimeOfDay?time_of_day=Noon  
5.3. Evening  
http://101.35.135.164:5000/LGSVL/Control/TimeOfDay?time_of_day=Evening  
### Agents control
**6. NPC Vehicle**  
6.1. NPC Vehicle Switch Lane  
http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Left_Lane&which_car=Sedan

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Right_Lane&which_car=Sedan

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Current_Lane&which_car=Sedan

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Left_Lane&which_car=SUV

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Right_Lane&which_car=SUV

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Current_Lane&which_car=SUV

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Left_Lane&which_car=Jeep

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Right_Lane&which_car=Jeep

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Current_Lane&which_car=Jeep

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Left_Lane&which_car=Hatchback

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Right_Lane&which_car=Hatchback

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Current_Lane&which_car=Hatchback

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Left_Lane&which_car=Hatchback

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Right_Lane&which_car=SchoolBus

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Current_Lane&which_car=SchoolBus

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Left_Lane&which_car=BoxTruck

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Right_Lane&which_car=BoxTruck

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Current_Lane&which_car=BoxTruck

6.2. NPC Vehicle Maintain Lane

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Left_Lane&which_car=Sedan

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Right_Lane&which_car=Sedan

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Current_Lane&which_car=Sedan

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Left_Lane&which_car=SUV

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Right_Lane&which_car=SUV

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Current_Lane&which_car=SUV

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Left_Lane&which_car=Jeep

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Right_Lane&which_car=Jeep

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Current_Lane&which_car=Jeep

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Left_Lane&which_car=Hatchback

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Right_Lane&which_car=Hatchback

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Current_Lane&which_car=Hatchback

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Left_Lane&which_car=SchoolBus

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Right_Lane&which_car=SchoolBus

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Current_Lane&which_car=SchoolBus

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Left_Lane&which_car=BoxTruck

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Right_Lane&which_car=BoxTruck

http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Current_Lane&which_car=BoxTruck

6.3. NPC Vehicle Parked On Lane
http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleParked?which_lane=Current_Lane&which_car=BoxTruck
  
6.4. NPC Vehicle Overtaking
http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleOvertaking

6.5. NPC Vehicle Road Crossing
http://101.35.135.164:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleRoadCrossing

**7. Pedestrians**  
7.1. Pedestrian walk on left lane  
http://101.35.135.164:5000/LGSVL/Control/Agents/Pedestrians/WalkRandomly?which_lane=Left_Lane  
7.2. Pedestrian walk on right lane  
http://101.35.135.164:5000/LGSVL/Control/Agents/Pedestrians/WalkRandomly?which_lane=Right_Lane  
7.3. Pedestrian walk on current lane  
http://101.35.135.164:5000/LGSVL/Control/Agents/Pedestrians/WalkRandomly?which_lane=Current_Lane  

<!-- ### Objects control
**8. Traffic Light**  
http://101.35.135.164:5000/LGSVL/Control/ControllableObjects/TrafficLight   -->
## Status API [GET]
### EGO Vehicle Data
**1. Get Collision Information**  
http://101.35.135.164:5000/LGSVL/Status/CollisionInfo  
**2. EGO Vehicle Status**  
2.1. Speed  
http://101.35.135.164:5000/LGSVL/Status/EGOVehicle/Speed  
2.2. Position  
http://101.35.135.164:5000/LGSVL/Status/EGOVehicle/Position  
### Sensors Data
**3. GPS Data**  
3.1. Latitude  
http://101.35.135.164:5000/LGSVL/Status/GPS/Latitude  
3.2. Longitude  
http://101.35.135.164:5000/LGSVL/Status/GPS/Longitude  
3.3. Northing  
http://101.35.135.164:5000/LGSVL/Status/GPS/Northing  
3.4. Easting  
http://101.35.135.164:5000/LGSVL/Status/GPS/Easting  
3.5. Altitude  
http://101.35.135.164:5000/LGSVL/Status/GPS/Altitude 
