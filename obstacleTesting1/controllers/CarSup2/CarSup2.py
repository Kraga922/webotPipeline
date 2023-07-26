
from controller import Supervisor
import sys
import os
basedir = '../../..'
sys.path.append(basedir)
from json2overcome2 import json2overcome2 
from json2proto2 import json2proto2 

def save_results(results_dir):
    json2overcome = json2overcome2()
    json_file_path = os.path.join(results_dir,'WebotSim2.json') 
    #json2overcome.add_brackets_to_json_file(json_file_path)
    file = json2overcome.openData(json_file_path)
    dfTranslation= json2overcome.getTranslationDF(file)
    dfTranslation['translation'] = json2overcome.formatTranslationDF(dfTranslation)
    #print(dfTranslation['translation'])
    print(json2overcome.obstaclePassed(dfTranslation, 'translation'))

 
def run():
    headless = bool(os.getenv('WEBOTS_HEADLESS'))
    results_dir = bool(os.getenv('WEBOTS_RESULTS_DIR'))

    TIME_STEP = 64
    supervisor = Supervisor()
    
    ds = []
    dsNames = ['ds_right', 'ds_left']
    timestep = int(supervisor.getBasicTimeStep())

    # Export scene after 5 seconds
    #camera = supervisor.getDevice("camera")
    #camera.enable(timestep)

    supervisor.step(timestep) 

    supervisor.animationStartRecording("WebotSim2.html")
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
        if time > 172:
            leftSpeed = 0
            rightSpeed = 0
            
            #supervisor.movieStopRecording()
            supervisor.animationStopRecording()
            supervisor.simulationSetMode(supervisor.SIMULATION_MODE_PAUSE)
            #supervisor.SIMULATION_MODE_PAUSE
            #json2overcome
            save_results(results_dir)
            
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
