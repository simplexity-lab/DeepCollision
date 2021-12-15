# DeepCollision REST APIs

## Ⅰ. DeepCollision REST API Example

> This section is an example demonstrating how to use **DeepCollision REST APIs** for environment parameter configurations.<br/>
> You can refer it to write your own Python programs.<br/>
> Also we provide a [video](https://github.com/DeepCollision/DeepCollisionData/blob/main/REST%20APIs/Demo.mkv) to show an running example.

### Step 1: Load scene and generate AVUT's position

There are two parameters in **LoadScene API**: the first one is Map, and the second one is the road which the AVUT will drive on.

```python
import request
requests.post("http://119.45.188.204:5000/LGSVL/LoadScene?scene=SanFrancisco&road_num=1")
```
Once the scene is loaded, the simulator will show the loaded SanFrancisco Map. See [here](https://github.com/DeepCollision/DeepCollisionData/blob/main/REST%20APIs/example%20figures/loadScene.png).
### Step 2: Configure the operating environment

Set rain level to light rain.

```python
requests.post("http://119.45.188.204:5000/LGSVL/Control/Weather/Rain?rain_level=Light")
```
Once the weather of rain is configured, it will rain in the simulator. See [here](https://github.com/DeepCollision/DeepCollisionData/blob/main/REST%20APIs/example%20figures/HeavyRain.png).
### Step 3: Get state returned

```python
    r = requests.get("http://192.168.50.81:5000/LGSVL/Status/Environment/State")
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

http://119.45.188.204:5000/LGSVL

## Command API [POST]
### Load Scene
http://119.45.188.204:5000/LGSVL/LoadScene?scene=<scene_name>&road_num=<road_num>

In our experiment the scene_name is 'SanFrancisco'.

### Set weather effect
**1. Nice weather**  
http://119.45.188.204:5000/LGSVL/Control/Weather/Nice  
**2. Rain**  
2.1. Light Rain  
http://119.45.188.204:5000/LGSVL/Control/Weather/Rain?rain_level=Light  
2.2. Moderate Rain  
http://119.45.188.204:5000/LGSVL/Control/Weather/Rain?rain_level=Moderate  
2.3. Heavy Rain  
http://119.45.188.204:5000/LGSVL/Control/Weather/Rain?rain_level=Heavy  
**3. Fog**  
3.1. Light Fog  
http://119.45.188.204:5000/LGSVL/Control/Weather/Fog?fog_level=Light  
3.2. Moderate Fog  
http://119.45.188.204:5000/LGSVL/Control/Weather/Fog?fog_level=Moderate  
3.3. Heavy Fog  
http://119.45.188.204:5000/LGSVL/Control/Weather/Fog?fog_level=Heavy  
**4. Wetness**  
4.1. Light Wetness  
http://119.45.188.204:5000/LGSVL/Control/Weather/Wetness?wetness_level=Light  
4.2. Moderate Wetness  
http://119.45.188.204:5000/LGSVL/Control/Weather/Wetness?wetness_level=Moderate  
4.3. Heavy Wetness  
http://119.45.188.204:5000/LGSVL/Control/Weather/Wetness?wetness_level=Heavy  

### Set time of day
**5. Time of Day**  
5.1. Morning  
http://119.45.188.204:5000/LGSVL/Control/TimeOfDay?time_of_day=Morning  
5.2. Noon  
http://119.45.188.204:5000/LGSVL/Control/TimeOfDay?time_of_day=Noon  
5.3. Evening  
http://119.45.188.204:5000/LGSVL/Control/TimeOfDay?time_of_day=Evening  
### Agents control
**6. NPC Vehicle**  
6.1. NPC Vehicle Switch Lane  
http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Left_Lane&which_car=Sedan

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Right_Lane&which_car=Sedan

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Current_Lane&which_car=Sedan

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Left_Lane&which_car=SUV

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Right_Lane&which_car=SUV

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Current_Lane&which_car=SUV

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Left_Lane&which_car=Jeep

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Right_Lane&which_car=Jeep

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Current_Lane&which_car=Jeep

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Left_Lane&which_car=Hatchback

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Right_Lane&which_car=Hatchback

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Current_Lane&which_car=Hatchback

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Left_Lane&which_car=Hatchback

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Right_Lane&which_car=SchoolBus

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Current_Lane&which_car=SchoolBus

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Left_Lane&which_car=BoxTruck

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Right_Lane&which_car=BoxTruck

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleSwitchLane?which_lane=Current_Lane&which_car=BoxTruck

6.2. NPC Vehicle Maintain Lane

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Left_Lane&which_car=Sedan

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Right_Lane&which_car=Sedan

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Current_Lane&which_car=Sedan

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Left_Lane&which_car=SUV

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Right_Lane&which_car=SUV

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Current_Lane&which_car=SUV

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Left_Lane&which_car=Jeep

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Right_Lane&which_car=Jeep

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Current_Lane&which_car=Jeep

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Left_Lane&which_car=Hatchback

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Right_Lane&which_car=Hatchback

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Current_Lane&which_car=Hatchback

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Left_Lane&which_car=SchoolBus

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Right_Lane&which_car=SchoolBus

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Current_Lane&which_car=SchoolBus

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Left_Lane&which_car=BoxTruck

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Right_Lane&which_car=BoxTruck

http://119.45.188.204:5000/LGSVL/Control/Agents/NPCVehicle/NPCVehicleMaintainLane?which_lane=Current_Lane&which_car=BoxTruck

6.2. NPC Vehicle Stop On Lane

**7. Pedestrians**  
7.1. Pedestrian walk on left lane  
http://119.45.188.204:5000/LGSVL/Control/Agents/Pedestrians/WalkRandomly?which_lane=Left_Lane  
7.2. Pedestrian walk on right lane  
http://119.45.188.204:5000/LGSVL/Control/Agents/Pedestrians/WalkRandomly?which_lane=Right_Lane  
7.3. Pedestrian walk on current lane  
http://119.45.188.204:5000/LGSVL/Control/Agents/Pedestrians/WalkRandomly?which_lane=Current_Lane  

### Objects control
**8. Traffic Light**  
http://119.45.188.204:5000/LGSVL/Control/ControllableObjects/TrafficLight  
## Status API [GET]
### EGO Vehicle Data
**1. Get Collision Information**  
http://119.45.188.204:5000/LGSVL/Status/CollisionInfo  
**2. EGO Vehicle Status**  
2.1. Speed  
http://119.45.188.204:5000/LGSVL/Status/EGOVehicle/Speed  
2.2. Position  
http://119.45.188.204:5000/LGSVL/Status/EGOVehicle/Position  
### Sensors Data
**3. GPS Data**  
3.1. Latitude  
http://119.45.188.204:5000/LGSVL/Status/GPS/Latitude  
3.2. Longitude  
http://119.45.188.204:5000/LGSVL/Status/GPS/Longitude  
3.3. Northing  
http://119.45.188.204:5000/LGSVL/Status/GPS/Northing  
3.4. Easting  
http://119.45.188.204:5000/LGSVL/Status/GPS/Easting  
3.5. Altitude  
http://119.45.188.204:5000/LGSVL/Status/GPS/Altitude 
