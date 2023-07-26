
from controller import Supervisor
import sys
import os
basedir = '../../..'
sys.path.append(basedir)
from json2overcome2 import json2overcome2 
from json2proto2 import json2proto2 
import traceback
import json

def process_results(results_dir):
    json2overcome = json2overcome2()
    json_file_path = os.path.join(results_dir,'WebotSim2.json') 
    #json2overcome.add_brackets_to_json_file(json_file_path)
    file = json2overcome.openData(json_file_path)
    dfTranslation= json2overcome.getTranslationDF(file)
    dfTranslation['translation'] = json2overcome.formatTranslationDF(dfTranslation)
    #print(dfTranslation['translation'])
    (num_obs, time) = json2overcome.obstaclePassed(dfTranslation, 'translation')
    print(f'Passed {num_obs} obstacles in {time} time units')
    result_obj = { 'num_obs': num_obs, 'time': int(time) }
    result_file = os.path.join(results_dir,'result.json')
    with open(result_file,'w') as fp:
        json.dump(result_obj, fp, indent=2, separators=(',', ':'))
 
def run():
    try:
        headless = bool(os.getenv('WEBOTS_HEADLESS'))
        results_dir = os.getenv('WEBOTS_RESULTS_DIR')
        if results_dir is None:
            results_dir = f"{basedir}/obstacleTesting1/controllers/CarSup2/"
        timeout = os.getenv('WEBOTS_TIMEOUT')
        if timeout is None:
            timeout = 172  # magic number (?) from original version
        else:
            timeout = int(timeout)
        
        print(f'Headless: {headless}')
        print(f'Results dir: {results_dir}')
        print(f'Timeout: {timeout}')

        TIME_STEP = 64
        supervisor = Supervisor()
        
        ds = []
        dsNames = ['ds_right', 'ds_left']
        timestep = int(supervisor.getBasicTimeStep())

        # Export scene after 5 seconds
        #camera = supervisor.getDevice("camera")
        #camera.enable(timestep)

        supervisor.step(timestep) 
        html_save_path = os.path.join(results_dir,'WebotSim2.html') 
        supervisor.animationStartRecording(html_save_path)
        #supervisor.movieStartRecording('WebotVid.mp4', 1280, 720, 0, 100, 1, False)

        for i in range(2):
            ds.append(supervisor.getDevice(dsNames[i]))
            ds[i].enable(TIME_STEP)
        wheels = []
        wheelsNames = ['motor1', 'motor2', 'motor3', 'motor4']
        for i in range(4):
            wheels.append(supervisor.getDevice(wheelsNames[i]))
            wheels[i].setPosition(float('inf'))
            wheels[i].setVelocity(0.0)
        #avoidObstacleCounter = 0
        time = 0
        #Main loop
        while supervisor.step(TIME_STEP) != -1:
            leftSpeed = 4.0
            rightSpeed = 4.0
            if time > timeout:
                leftSpeed = 0
                rightSpeed = 0
                
                #supervisor.movieStopRecording()
                supervisor.animationStopRecording()
                supervisor.simulationSetMode(supervisor.SIMULATION_MODE_PAUSE)
                #supervisor.SIMULATION_MODE_PAUSE
                #json2overcome
                process_results(results_dir)
                
                supervisor.simulationReset()
                if headless:
                    print('Headless mode, quitting simulation...')
                    supervisor.simulationQuit(0)

            time += 1
            wheels[0].setVelocity(leftSpeed)
            wheels[1].setVelocity(rightSpeed)
            wheels[2].setVelocity(leftSpeed)
            wheels[3].setVelocity(rightSpeed)
            # if supervisor.step(TIME_STEP) == 10:
            #     supervisor.animationStopRecording()
            #     supervisor.simulationResetPhysics()
            #     supervisor.step(TIME_STEP) == -1
        #supervisor.worldRestart()
    except:
        traceback.print_exc()
        if headless:
            supervisor.simulationQuit(0)
        else:
            supervisor.simulationReset()

if __name__ == "__main__":
    #supervisor = Supervisor()
    #pipeline2()
    run()
