from controller import Supervisor
from PIL import Image

TIME_STEP = 64
supervisor = Supervisor()
ds = []
dsNames = ['ds_right', 'ds_left']
timestep = int(supervisor.getBasicTimeStep())

# Export scene after 5 seconds


supervisor.step(timestep) 
# supervisor.animationStartRecording('sampleRun2.html')
supervisor.animationStartRecording("video3.html")

for i in range(2):
    ds.append(supervisor.getDevice(dsNames[i]))
    ds[i].enable(TIME_STEP)
wheels = []
wheelsNames = ['motor1', 'motor2', 'motor3', 'motor4']
for i in range(4):
    wheels.append(supervisor.getDevice(wheelsNames[i]))
    wheels[i].setPosition(float(57))
    wheels[i].setVelocity(0.0)
avoidObstacleCounter = 0


# Main loop
time = 0
while supervisor.step(TIME_STEP) != -1:
    leftSpeed = 4.0
    rightSpeed = 4.0
    if time > 222:  # reaches a certain time
        # avoidObstacleCounter -= 1
        leftSpeed = 0
        rightSpeed = 0
        supervisor.animationStopRecording()
        supervisor.simulationSetMode(supervisor.SIMULATION_MODE_PAUSE)

        # read sensors
        # for i in range(2):
        #     if ds[i].getValue() < 950.0:
        #         avoidObstacleCounter = 100
    time +=1
    wheels[0].setVelocity(leftSpeed)
    wheels[1].setVelocity(rightSpeed)
    wheels[2].setVelocity(leftSpeed)
    wheels[3].setVelocity(rightSpeed)

