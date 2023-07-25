FROM cyberbotics/webots:latest
RUN apt-get update -y
RUN apt-get install pip -y
RUN pip3 install pillow pandas
