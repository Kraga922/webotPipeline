
from controller import Supervisor
import sys
import os
import math
basedir = '../../..'
sys.path.append(basedir)
from InsertMultiSym2 import get_motors, getMissionLocation 
import traceback
import json

def save_results(results_dir, obs_passed, time):
    result_obj = { 'num_obs': obs_passed, 'time': time }
    result_file = os.path.join(results_dir,'result.json')
    with open(result_file,'w') as fp:
        json.dump(result_obj, fp, indent=2, separators=(',', ':'))

def obstaclePassed(time, value, old_obs_passed, old_time):
    obs = []

    if value >= 359.9:
        new_obs_passed = 3
    elif value >= 0.4:
        new_obs_passed = 2
    elif value >= -0.1:
        new_obs_passed = 1
    else:
        new_obs_passed = 0
    
    if new_obs_passed > old_obs_passed:
        new_time = time
    else:
        new_time = old_time

    return [new_obs_passed, new_time]

    # if value >= 0.9:
    #     if (obs_passed[0] == 3):
    #         time = min(time,obs_passed[1]) 
    #     obs = [3, time]
    # elif value >= 0.4: 
    #     if (obs_passed[0] == 2):
    #         time = min(time,obs_passed[1]) 
    #     obs = [2, time]
    # elif value >= -0.1:
    #     if (obs_passed[0] == 1):
    #         time = min(time,obs_passed[1]) 
    #     obs = [1, time]
    # else:
    #     obs = [0, time]

    #num_obs = obs[0]
    #print(f'Passed {num_obs} obstacles in {time} time units')
    # result_obj = { 'num_obs': num_obs, 'time': int(time) }
    # result_file = os.path.join(results_dir,'result.json')
    # with open(result_file,'w') as fp:
    #     json.dump(result_obj, fp, indent=2, separators=(',', ':'))
def read_text_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    return content.strip()


def closest_mission(missions, coordinates):
    mission_keys = list(missions.keys())
    closest_mission = mission_keys[0]
    closest_distance = distanceToMission(coordinates, missions[closest_mission])
    for key in mission_keys:
        distance = distanceToMission(coordinates, missions[key])
        if distance< closest_distance:
            closest_distance = distance
            closest_mission = key
    return closest_mission

def distanceToMission(coordinates, mission):
    return math.sqrt((coordinates[0]-mission[0])**2 + (coordinates[1]-mission[1])**2)
        
def goToMission(current_angle_radians, missions, coordinates):
    closestMission = missions[closest_mission(missions,coordinates)]
    current_angle_radians = round(current_angle_radians, 1)
    # if current_angle_radians<0:
    #     current_angle_radians = 6.28 + current_angle_radians
    #print(f"cur {current_angle_radians}")
    y = coordinates[1] - closestMission[1]
    x = coordinates[0] - closestMission[0]
    #print (f"x: {x}, y: {y}")
    mission_angle_radians = round(math.atan2(-y, -x),1)
    #print(mission_angle_radians)
    #print(f"mis {mission_angle_radians}")
    if coordinates[1] == closestMission[1] and coordinates[0] == closestMission[0]:
        #remove mission
        print("At mission")
    
    if current_angle_radians < mission_angle_radians- .7:
        #print("right")
        leftSpeed = -5.0
        rightSpeed = 10.0
    elif current_angle_radians - .7 > mission_angle_radians: 
        #print("left")
        leftSpeed = -1.0
        rightSpeed = 5.0
    else:
        #print("same")
        leftSpeed = 15.0
        rightSpeed = 15.0

    return leftSpeed, rightSpeed


def run():
    try:
        headless = bool(os.getenv('WEBOTS_HEADLESS'))
        results_dir = os.getenv('WEBOTS_RESULTS_DIR')
        if results_dir is None:
            results_dir = f"{basedir}/obstacleTesting1/controllers/CarSupMulti/"
        timeout = os.getenv('WEBOTS_TIMEOUT')
        if timeout is None:
            timeout = 120000  # in ms
        else:
            timeout = int(timeout) 
        
        #print(f'Headless: {headless}')
        #print(f'Results dir: {results_dir}')
        #print(f'Timeout: {timeout}')

        TIME_STEP = 64
        supervisor = Supervisor()

        gps = supervisor.getDevice("gps")
        #gyro = supervisor.getDevice("gyro")
        imu = supervisor.getDevice("inertial unit")
        #print(f"gps {gps}")
        gps.enable(10)
        #gyro.enable(10)
        imu.enable(10)

        ds = []
        dsNames = ['ds_right', 'ds_left']
        timestep = int(supervisor.getBasicTimeStep())

        supervisor.step(timestep) 
        html_save_path = os.path.join(results_dir,'WebotSim2.html') 
        supervisor.animationStartRecording(html_save_path)

        for i in range(2):
            ds.append(supervisor.getDevice(dsNames[i]))
            ds[i].enable(TIME_STEP)
        wheelsNames = get_motors("../../../jsonWheelShapes/ConvJsonMultiSym2.json")
        wheels = []
        for i in range(len(wheelsNames)): 
            wheels.append(supervisor.getDevice(wheelsNames[i]))
            wheels[i].setPosition(float('inf'))
            wheels[i].setVelocity(0.0)
        
        missions = getMissionLocation(read_text_file("../../../jsonWheelShapes/ConvJsonWorld.json"))
        
        num_missions = len(missions)
        #avoidObstacleCounter = 0
        time = 0
        #Main loop
        #obs_passed = [0,0]
        best_obs_passed = 0
        best_time = 0
        maxDistance = 1.0  # where to stop the run, past all the obstacles
        
        while supervisor.step(TIME_STEP) != -1: 
            #pos = supervisor.getFromId(43).getOrientation()
            #print(pos[3])
            coordinates = gps.getValues()
            #gyro_val = gyro.getValues()
            rpy = imu.getRollPitchYaw()
            #quat = imu.getQuaternion()
            #print(quat)
            leftSpeed, rightSpeed = goToMission(rpy[2], missions, coordinates)

            closestMission = closest_mission(missions, coordinates)
            mission_keys = list(missions.keys())
            #print (mission_keys)
            if (abs(coordinates[0] - missions[closestMission][0]) <= 3 and abs(coordinates[1] - missions[closestMission][1]) <=3 ):
                missions.pop(closestMission)
                #print("YOU MADE IT")
            #print(gps.getSpeed())
            #print([round(number,3) for number in numbers])
            speedVector = gps.getSpeedVector()
            #print(speedVector)
            #print(rpy)
            mission_keys = list(missions.keys())


            time = int(supervisor.getTime() *1000)
            #print(time)
            #body_position = body_node.getPosition()
            #print("BODY position:", body_position)
            #print(robot_body.getPosition())
            [best_obs_passed, best_time] = obstaclePassed(time, coordinates[0], best_obs_passed, best_time)

            if time > timeout or len(mission_keys) == 0:
                leftSpeed = 0
                rightSpeed = 0
                
                #obs_passed = obstaclePassed(time, coordinates[0], obs_passed)
                print(f'obs passed: {num_missions-len(mission_keys)}, time: {time}')
                #print(f'obs passed: {best_obs_passed}, time: {best_time}')

                supervisor.animationStopRecording()
                supervisor.simulationSetMode(supervisor.SIMULATION_MODE_PAUSE)

                save_results(results_dir, best_obs_passed, best_time)
                
                supervisor.simulationReset()
                if headless:
                    print('Headless mode, quitting simulation...')
                    supervisor.simulationQuit(0)

            for i in range (len(wheels)):
                if (wheels[i].getName()).endswith("SYM"):
                    wheels[i].setVelocity(leftSpeed)
                else:
                    wheels[i].setVelocity(rightSpeed)     

        #supervisor.worldRestart()
    except:
        traceback.print_exc()
        if headless:
            supervisor.simulationQuit(0)
        else:
            supervisor.simulationReset()

if __name__ == "__main__":

    run()
    