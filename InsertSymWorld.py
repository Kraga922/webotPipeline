import json
import os
import random

def read_text_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    return content.strip()

def getMissionLocation(json_data):
    #find flags 
    # add flag name as key and flag x and y values and the value
    # return the dict
    json_obj = json.loads(json_data)
    missions_dict = {}

    for mission in json_obj["Missions"]:
        mission_name = mission["Name"]
        x_location = mission["X-location"]
        y_location = mission["Y-location"]
        missions_dict[mission_name] = (x_location, y_location)

    return missions_dict

def insertMissions(json_data):
    json_obj = json.loads(json_data)
    num = 0
    body_design = ""
    for missions in json_obj["Missions"]:
        num += 1
        body_design += f"""
Pose {{
  translation {missions["X-location"]} {missions["Y-location"]} 2.5
  children [
    Shape {{
      appearance PBRAppearance {{
        transparency 0.2
      }}
      geometry Cylinder {{
        height 4
        radius {json_obj["ZoneRadius"]} 
      }}
    }}
  ]
}}
"""
    return body_design

def insertVehicle(modified_world, json_data):
    json_obj = json.loads(json_data)
    modified_world = modified_world.replace(f"*drop*", str(json_obj["Drop"]))
    return modified_world

def replaceMaterial(modified_world, json_data):
    json_obj = json.loads(json_data)
    for material in json_obj["Materials"]:
      Friction = str(material["Friction Coefficient"]) # just a number   
      RollingFriction = str(material["Rolling Resistance Coefficient"])
      modified_world = modified_world.replace(f"*InsertCoulombFriction*", Friction)
      modified_world = modified_world.replace(f"*InsertRollingFriction*", RollingFriction)
    return modified_world

def modifyTerrain(modified_world, json_data):
    json_obj = json.loads(json_data)
    peaks =[] 
    for terrain in json_obj["Peaks"]:
      if terrain["Name"] == "Q1":    
        q1Min = terrain["Min"]
        q1Max = terrain["Max"]
      elif terrain["Name"] == "Q2":  
        q2Min = terrain["Min"]
        q2Max = terrain["Max"]
      elif terrain["Name"] == "Q3":
        q3Min = terrain["Min"]
        q3Max = terrain["Max"]
      else:
        q4Min = terrain["Min"]
        q4Max = terrain["Max"]
    r = 18
    for i in range(r):
      peaks += [round(random.uniform(q1Min, q1Max), 2) for _ in range(r)]
      peaks += [round(random.uniform(q2Min, q2Max), 2) for _ in range(r)]
    ##random_numbers += [round(random.uniform(0, 1), 2) for _ in range(50)]
    #random_numbers += [round(random.uniform(2, 4), 2) for _ in range(50)]
    for j in range(r):
      peaks += [round(random.uniform(q4Min, q4Max), 2) for _ in range(r)]
      peaks += [round(random.uniform(q3Min, q3Max), 2) for _ in range(r)]
    
    modified_world = modified_world.replace(f"*peaks*", str(peaks))
    return modified_world
    
def main(pipeline_dir):
   

    json_world_file_path = os.path.join(pipeline_dir, "jsonWheelShapes/ConvJsonWorld.json")
    json_world_data = read_text_file(json_world_file_path) 

    with open(os.path.join(pipeline_dir, "obstacleTesting1/worlds/obstacleTesting9Temp.wbt"), "r") as file:
        content = file.read()
 
    #num_bodies, num_wheels = num_wheels_bodies(json_data)
    #modified_content = content.replace("**InsertBodiesAndWheels**", create_template(num_bodies-1,num_wheels, json_data))
    modified_world = content.replace("**Missions**", insertMissions(json_world_data))
    #print(modified_world)
    modified_world = insertVehicle(modified_world, json_world_data)
    modified_world = replaceMaterial(modified_world, json_world_data)
    modified_world = modifyTerrain(modified_world, json_world_data)
    #print(modified_world)
    with open(os.path.join(pipeline_dir, "obstacleTesting1/worlds/obstacleTesting9.wbt"), "w") as file:
        file.write(modified_world)
     
 
if __name__ == "__main__":
    main('.')


# {
#     "bodies":[
#     {
#       "Name": "BODY",
#       "Rigid": true,
#       "Anchor": "0",
#       "Shape": "Box",
#       "Dimensions": {
#         "size": "0.2 0.1 0.05"
#       },
#       "wheels": [
#         {
#           "Name": "WHEEL1",
#           "Symmetrical": true,
#           "WheelNum": "1",
#           "Anchor": "0.05 0.06 0",
#           "Shape": "Box",
#           "Dimensions": {
#               "size": "0.08 0.08 0.02"
#           }
#         },
#         {
#           "Name": "WHEEL2",
#           "Symmetrical": true,
#           "WheelNum": "2",
#           "Anchor": "-0.05 0.06 0",
#           "Shape": "Box",
#           "Dimensions": {
#               "size": "0.08 0.08 0.02"
#           }
#         }
#       ]
#     },
#     {
#         "Name": "BODY1",
#         "Rigid": true,
#         "Anchor": "0.2 0 0",
#         "Shape": "Cylinder",
#         "Dimensions": {
#             "height": "0.05",
#             "radius": "0.1"
#         },
#         "wheels": [
#           {
#             "Name": "WHEEL3",
#             "Symmetrical": true,
#             "WheelNum": "3",
#             "Anchor": "-0.05 0.06 0",
#             "Shape": "Box",
#             "Dimensions": {
#                 "size": "0.08 0.08 0.02"
#             }
#           }
#         ]
#       },
#       {
#         "Name": "BODY2",
#         "Rigid": true,
#         "Anchor": "0.35 0 0",
#         "Shape": "Box",
#         "Dimensions": {
#           "size": "0.1 0.1 0.05"
#         },
#         "wheels": [
#           {
#             "Name": "WHEEL4",
#             "Symmetrical": true,
#             "WheelNum": "4",
#             "Anchor": "0.05 0.06 0",
#             "Shape": "Box",
#             "Dimensions": {
#                 "size": "0.08 0.08 0.02"
#             }
#           }   
#         ]
#       }
#     ]
#   }
 


 


"""

# Replace Car4wMultiTemp.proto with the following code to have the weight battery trade off senario

{
  "bodies":[
    {
      "Name":"BODY",
      "Rigid":false,
      "Anchor":"0.0 0.0 0.0",
      "wheels":[
        {
          "Name":"WHEEL1",
          "WheelNum":"1",
          "Symmetrical":true,
          "Anchor":"-0.010459649587189535 0.14060051888227462 -0.02961112663149834",
          "Shape":"Box",
          "Dimensions":{
            "size":"0.03566353142261505 0.03334794282913208 0.06309681117534638"
          }
        },
        {
          "Name":"WHEEL2",
          "WheelNum":"2",
          "Symmetrical":true,
          "Anchor":"0.003272926515345992 0.10361949801445007 -0.04646447807550431",
          "Shape":"Box",
          "Dimensions":{
            "size":"0.04595842629671097 0.0942377781867981 0.08698218286037446"
          }
        },
        {
          "Name":"WHEEL3",
          "WheelNum":"3",
          "Symmetrical":true,
          "Anchor":"-0.006278231024799061 0.11376732885837555 -0.04673374146223069",
          "Shape":"Sphere",
          "Dimensions":{
            "radius":"0.07958815336227418",
            "subdivision":"1"
          }
        },
        {
          "Name":"WHEEL4",
          "WheelNum":"4",
          "Symmetrical":true,
          "Anchor":"-0.014243564470717028 0.10708364993333816 -0.05350601702928544",
          "Shape":"Sphere",
          "Dimensions":{
            "radius":"0.09642051696777344",
            "subdivision":"1"
          }
        }
      ],
      "Shape":"Box",
      "Dimensions":{
        "size":"0.051422166731208564 0.18649818003177643 0.07502251565456391"
      }
    },
    {
      "Name":"BODY1",
      "Rigid":true,
      "Anchor":"0.16579751665703957 0.0 0.0",
      "wheels":[
        {
          "Name":"WHEEL5",
          "WheelNum":"5",
          "Symmetrical":true,
          "Anchor":"0.09489910791494512 0.17529031932353978 -0.08635855525732042",
          "Shape":"Sphere",
          "Dimensions":{
            "radius":"0.022253832817077636",
            "subdivision":"1"
          }
        },
        {
          "Name":"WHEEL6",
          "WheelNum":"6",
          "Symmetrical":true,
          "Anchor":"0.016801187880652796 0.14472229294478897 -0.0643162938952446",
          "Shape":"Cylinder",
          "Dimensions":{
            "height":"0.09458864331245423",
            "radius":"0.09485652089118958"
          }
        },
        {
          "Name":"WHEEL7",
          "WheelNum":"7",
          "Symmetrical":true,
          "Anchor":"-0.08202028966684945 0.1610744029283524 -0.057474016249179846",
          "Shape":"Box",
          "Dimensions":{
            "size":"0.029702944159507756 0.07000573098659515 0.06728777348995209"
          }
        }
      ],
      "Shape":"Cylinder",
      "Dimensions":{
        "height":0.08036726415157319,
        "radius":0.14008643329143528
      }
    }
  ]
}



"""

"""
#VRML_SIM R2023b utf8


PROTO Car4wMulti2 [
  field SFVec3f    translation  0 0 0.04
  field SFRotation rotation     0 0 1 0
  field MFFloat    battery      [289800000 289800000 0]
  field SFString   controller   "CarSupMulti"
  field  SFString  name         "Car4wMulti2" 
]
{
  Robot {
    translation IS translation
    rotation IS rotation
    controller IS controller
    supervisor TRUE
    children [
      DEF BODY Shape {
        appearance PBRAppearance {
          baseColor 0.917647 0.145098 0.145098
          roughness 1
          metalness 0
        }
        geometry *BODY_GEOMETRY* {
          *BODY_SIZE*
        }
      }
      
      **InsertBodiesAndWheels**

      DEF BATTERY_MASS HingeJoint {
          jointParameters HingeJointParameters {
          axis 0 1 0
          anchor .01 .01 .01
          }
          endPoint Solid {
          translation .01 .01 .01 
          rotation 1 0 0 1.5708
          children [
              DEF WHEEL4SYM Shape {
              appearance PBRAppearance {
                  baseColor 0.1305882 0.098039 0.85098
                  roughness 1
                  metalness 0
              }
              geometry Box {
                  size .1 .1 .1 
              }
              }
          ]
          name "BATTERY_MASS"
          contactMaterial "wheel"
          boundingObject USE WHEEL1
          physics Physics {
              density *INSERT_BATTERY_MASS*
          }
          }
      }
      DEF DS_RIGHT DistanceSensor {
        translation 0.1 -0.03 0
        rotation 0 0 1 -0.3
        children [
          Shape {
            appearance PBRAppearance {
              baseColor 0.184314 0.596078 0.847059
              roughness 1
              metalness 0
            }
            geometry Box {
              size 0.01 0.01 0.01
            }
          }
        ]
        name "ds_right"
      }
      DEF DS_LEFT DistanceSensor {
        translation 0.1 0.03 0
        rotation 0 0 1 0.3
        children [
          Shape {
            appearance PBRAppearance {
              baseColor 0.184314 0.596078 0.847059
              roughness 1
              metalness 0
            }
            geometry Box {
              size 0.01 0.01 0.01
            }
          }
        ]
        name "ds_left"
      }
      DEF COMPASS Compass {
      }
      DEF GPS GPS {
      }
      DEF GYRO Gyro {
      }
      DEF INERTIAL_UNIT InertialUnit {
      }
    ]
    name IS name
    boundingObject USE BODY
    physics Physics {
      density 300
    }
    controller "CarSupMulti"
    battery IS battery
  }
}

Update the MultiSym json file by adding this at the end 

,
  "battery":{
    "Energy" : 289800
  }

Uncomment the battery to weight method
"""