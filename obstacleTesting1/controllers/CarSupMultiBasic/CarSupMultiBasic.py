
from controller import Supervisor
import sys
import os
basedir = '../../..'
sys.path.append(basedir)
from InsertMultiSym2 import get_motors 
import traceback
import json

def save_results(results_dir, obs_passed, time):
    result_obj = { 'num_obs': obs_passed, 'time': time }
    result_file = os.path.join(results_dir,'result.json')
    with open(result_file,'w') as fp:
        json.dump(result_obj, fp, indent=2, separators=(',', ':'))

def obstaclePassed(time, value, old_obs_passed, old_time):
    obs = []

    if value >= 9:
        new_obs_passed = 3
    elif value >= 1:
        new_obs_passed = 2
    elif value >= -7:
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

def run():
    try:
        headless = bool(os.getenv('WEBOTS_HEADLESS'))
        results_dir = os.getenv('WEBOTS_RESULTS_DIR')
        if results_dir is None:
            results_dir = f"{basedir}/obstacleTesting1/controllers/CarSupMulti/"
        timeout = os.getenv('WEBOTS_TIMEOUT')
        if timeout is None:
            timeout = 20000  # in ms
        else:
            timeout = int(timeout) 
        
        #print(f'Headless: {headless}')
        #print(f'Results dir: {results_dir}')
        #print(f'Timeout: {timeout}')

        TIME_STEP = 64
        supervisor = Supervisor()

        gps = supervisor.getDevice("gps")
        #print(f"gps {gps}")
        gps.enable(10)

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
        
        #avoidObstacleCounter = 0
        time = 0
        #Main loop
        #obs_passed = [0,0]
        best_obs_passed = 0
        best_time = 0
        maxDistance = 1.0  # where to stop the run, past all the obstacles
        while supervisor.step(TIME_STEP) != -1: 

            coordinates = gps.getValues()

            #print(gps.getSpeed())
            #print([round(number,3) for number in numbers])

            leftSpeed = 4.0
            rightSpeed = 4.0

            time = int(supervisor.getTime() *1000)
            #print(time)
            #body_position = body_node.getPosition()
            #print("BODY position:", body_position)
            #print(robot_body.getPosition())
            [best_obs_passed, best_time] = obstaclePassed(time, coordinates[0], best_obs_passed, best_time)
            #print(obs_passed)
            #print(obs_passed)
            #if time > timeout or coordinates[0] > maxDistance:
            if time > timeout or best_obs_passed == 3:
                leftSpeed = 0
                rightSpeed = 0
                
                #obs_passed = obstaclePassed(time, coordinates[0], obs_passed)
                print(f'obs passed: {best_obs_passed}, time: {best_time}')

                supervisor.animationStopRecording()
                supervisor.simulationSetMode(supervisor.SIMULATION_MODE_PAUSE)

                save_results(results_dir, best_obs_passed, best_time)
                
                supervisor.simulationReset()
                if headless:
                    print('Headless mode, quitting simulation...')
                    supervisor.simulationQuit(0)

            for i in range (len(wheels)):
                wheels[i].setVelocity(leftSpeed)     
            # wheels[0].setVelocity(leftSpeed)
            # wheels[1].setVelocity(rightSpeed)
            # wheels[2].setVelocity(leftSpeed)
            # wheels[3].setVelocity(rightSpeed)
            # wheels[4].setVelocity(leftSpeed)
            # wheels[5].setVelocity(rightSpeed)

        #supervisor.worldRestart()
    except:
        traceback.print_exc()
        if headless:
            supervisor.simulationQuit(0)
        else:
            supervisor.simulationReset()

if __name__ == "__main__":

    run()
    
