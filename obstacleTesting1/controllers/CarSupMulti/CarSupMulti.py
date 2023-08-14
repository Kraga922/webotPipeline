
from controller import Supervisor
import sys
import os
basedir = '../../..'
sys.path.append(basedir)
from InsertMultiSym2 import get_motors 
import traceback
import json

# def process_results(results_dir):
#     json2overcome = json2overcome2()
#     json_file_path = os.path.join(results_dir,'WebotSim2.json') 
#     #json2overcome.add_brackets_to_json_file(json_file_path)
#     file = json2overcome.openData(json_file_path)
#     #print(file)
#     dfTranslation= json2overcome.getTranslationDF(file)
#     #print(dfTranslation)
#     dfTranslation['translation'] = json2overcome.formatTranslationDF(dfTranslation)
#     #print(dfTranslation['translation'])
#     (num_obs, time) = json2overcome.obstaclePassed(dfTranslation, 'translation')
#     print(f'Passed {num_obs} obstacles in {time} time units')
#     result_obj = { 'num_obs': num_obs, 'time': int(time) }
#     result_file = os.path.join(results_dir,'result.json')
#     with open(result_file,'w') as fp:
#         json.dump(result_obj, fp, indent=2, separators=(',', ':'))

def obstaclePassed(time, value, obs_passed):
    obs = []
    if value >= 0.9:
        if (obs_passed[0] == 3):
            time = min(time,obs_passed[1]) 
        obs = [3, time]
    elif value >= 0.4: 
        if (obs_passed[0] == 2):
            time = min(time,obs_passed[1]) 
        obs = [2, time]
    elif value >= -0.1:
        if (obs_passed[0] == 1):
            time = min(time,obs_passed[1]) 
        obs = [1, time]
    else:
        obs = [0, time]


    #num_obs = obs[0]
    #print(f'Passed {num_obs} obstacles in {time} time units')
    # result_obj = { 'num_obs': num_obs, 'time': int(time) }
    # result_file = os.path.join(results_dir,'result.json')
    # with open(result_file,'w') as fp:
    #     json.dump(result_obj, fp, indent=2, separators=(',', ':'))
    return obs
def run():
    try:
        headless = bool(os.getenv('WEBOTS_HEADLESS'))
        results_dir = os.getenv('WEBOTS_RESULTS_DIR')
        if results_dir is None:
            results_dir = f"{basedir}/obstacleTesting1/controllers/CarSup2/"
        timeout = os.getenv('WEBOTS_TIMEOUT')
        if timeout is None:
            timeout = 12000  # in ms
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
        obs_passed = [0,0]
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
            obs_passed = obstaclePassed(time, coordinates[0], obs_passed)
            #print(obs_passed)
            #print(obs_passed)
            if time > timeout or coordinates[0] > 1.1:
                leftSpeed = 0
                rightSpeed = 0
                
                print(obstaclePassed(time, coordinates[0], obs_passed))

                supervisor.animationStopRecording()
                supervisor.simulationSetMode(supervisor.SIMULATION_MODE_PAUSE)


                #process_results(results_dir)
                
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
    
