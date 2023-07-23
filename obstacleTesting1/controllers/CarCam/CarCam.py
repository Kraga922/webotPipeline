from controller import Supervisor
from PIL import Image
import os

TIME_STEP = 64
supervisor = Supervisor()
ds = []
dsNames = ['ds_right', 'ds_left']
timestep = int(supervisor.getBasicTimeStep())

# Export scene after 5 seconds
camera = supervisor.getDevice("camera")
camera.enable(timestep)

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



# Function to save camera image
def save_camera_image(time):
    #folder_path = 'obstacleTesting1/controllers/CarCam/SimImages'
    image_data = camera.getImage()
    width = camera.getWidth()
    height = camera.getHeight()
    image = Image.frombytes('RGBA', (width, height), image_data)
    #os.makedirs(folder_path, exist_ok=True)
    #filename = os.path.join(folder_path, f'camera_image_{time}.png')
    filename = f'camera_image_{time}.png'
    image.save(filename, 'png')

#car_node = supervisor.getFromDef("Car4wA")
#body_node = car_node.getFromDef("BODY")
#print(supervisor.getUniqueId(91))
# car_node = supervisor.getRoot()
# print(body_node)
# print(car_node)


# Main loop
time = 0
while supervisor.step(TIME_STEP) != -1:
    leftSpeed = 4.0
    rightSpeed = 4.0
    if time > 222:  # or reaches a certain time
        # avoidObstacleCounter -= 1
        leftSpeed = 0
        rightSpeed = 0
        supervisor.animationStopRecording()
        supervisor.simulationSetMode(supervisor.SIMULATION_MODE_PAUSE)
        supervisor.simulationReset()
        # supervisor.step(TIME_STEP) = -1
    else:
        # Save camera image at each time step
        save_camera_image(time)
        time += 1

        # read sensors
        # for i in range(2):
        #     if ds[i].getValue() < 950.0:
        #         avoidObstacleCounter = 100

    wheels[0].setVelocity(leftSpeed)
    wheels[1].setVelocity(rightSpeed)
    wheels[2].setVelocity(leftSpeed)
    wheels[3].setVelocity(rightSpeed)

    # if supervisor.step(TIME_STEP) == 10:
    #     supervisor.animationStopRecording()
    #     supervisor.simulationResetPhysics()
    #     supervisor.step(TIME_STEP) == -1
