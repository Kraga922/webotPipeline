# Installing

`curl -L -O https://github.com/cyberbotics/webots/releases/download/R2023b/webots-R2023b.dmg open webots-R2023b.dmg`
Drag and Drop to the applications folder

# Create an environment for webots
e.g. using conda,
```
conda create -n webots python=3.10
conda activate webots
pip install pillow pandas
```
Find out the path to python for this environment:
```
which python
```
In the Webots Preferences, change the "Python command" to the python path from the previous step.

# Running
Start Webots
Press command+shift+O
In the webotsPipeline repo, find `obstacleTesting1/worlds/obstacleTesting2.wbt` file and run it
Press play button to start
At the end of the simulation, in webots console, time and box output will be printed

# How to use the pipeline
The pipeline is now integrated in the CarSup controller. By starting the simulation on you local machine, it will update wheel shape, run simulation, export data, and check at what time the car passed its furthest box.

# Additional Information
Use Car4wA proto for the simulations. Other Protos are cars with different hard coded wheel shapes.
On line 12 of the Car4wA proto code file there is a 'controller' attribute. Change the name to 'CarCam' if image export is desired. The simulation takes longer if so. Use 'CarSup' if the full integration is desired (files not adjusted for servers). Use CarCon for a basic run.
json2overcome3 and json2proto3 are independent classes and can be used to run the individual parts of the pipeline.
CarSup controller implement an end to end pipeline.

# Running via Docker
Log onto server  
Update file paths in files  
Use sftp to upload files to server  
run in server: `docker run -it cyberbotics/webots:latest`  
Transfer files to docker container `docker cp FOLDER_FILE_PATH DOCKER_CONTAINER_ID:/usr/local/webots/COPIED_FOLDER`  
Run the simulation headlessly using 
`xvfb-run webots --stdout --stderr --batch --mode=fast obstacleTesting2.wbt`  
(Make sure you are in the worlds folder)
