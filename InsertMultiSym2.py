import json
import os
import random

def read_text_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    return content.strip()

# def read_json_file(file_path):
#     with open(file_path, "r") as file:
#         data = json.load(file)
#     return data

def generate_geometry_code(geom_data, indentation=14):
    if isinstance(geom_data, str):
        return geom_data
    else:
        indent = " " * indentation
        geom_code = ""
        for geom_type, geom_props in geom_data.items():
            geom_code += f" {indent}{geom_type} {geom_props}\n"
        return geom_code

# def battery_energy_to_weight(template, json_data):
#     json_obj = json.loads(json_data)
#     energy = json_obj["battery"]["Energy"]
#     mass = (99.1049 + 0.000001274 * energy) * 1000
#     template = template.replace(f"*INSERT_BATTERY_MASS*", str(mass))
#     return template

def create_proto_from_template(template, json_data):
    json_obj = json.loads(json_data)
    #num_bodies = 0 
    i = 0
    for body in json_obj["bodies"]:
        #num_bodies += 1
        body_name = body["Name"]
        body_shape = body["Shape"]
        body_anchor = body["Anchor"]
        template = template.replace(f"*{body_name}_GEOMETRY*", body_shape)
        template = template.replace(f"*{body_name}_ANCHOR*", body_anchor)
        template = template.replace(f"*{body_name}_SIZE*", generate_geometry_code(body["Dimensions"]))
        if body["Rigid"]:
            template = template.replace(f"*{body_name}_RIGID*", '.001')
        else: 
            template = template.replace(f"*{body_name}_RIGID*", '.5')

    # Replace the wheel geometries and sizes
    for body in json_obj["bodies"]:
        for wheel in body["wheels"]:
            i += 1
            wheel_name = wheel["Name"] # just a number 
            #if wheel["Symmetrical"] == "Yes":    
            wheel_shape = wheel["Shape"]
            wheel_anchor = wheel["Anchor"]
            template = template.replace(f"*{wheel_name}_GEOMETRY*", wheel_shape)
            template = template.replace(f"*{wheel_name}_ANCHOR*", wheel_anchor)
            template = template.replace(f"*{wheel_name}_SIZE*", generate_geometry_code(wheel["Dimensions"]))
            if wheel["Symmetrical"]:
                template = template.replace(f"*{wheel_name}SYM_GEOMETRY*", wheel_shape)

                split_values = wheel_anchor.split()
                split_values[1] = str(-float(split_values[1]))  # Negate the second element
                sym_wheel_anchor = " ".join(split_values)

                template = template.replace(f"*{wheel_name}SYM_ANCHOR*", sym_wheel_anchor)
                template = template.replace(f"*{wheel_name}SYM_SIZE*", generate_geometry_code(wheel["Dimensions"]))
       

    return template

    
#idt this is needed anymore
# def num_wheels_bodies(json_data):
#     json_obj = json.loads(json_data)

#     return len(json_obj["bodies"]), len(json_obj["wheels"])

#see if you can merge with create_proto_from_template method
def insert_wheel(wheel_number):
    wheel_design = f"""
            DEF WHEEL{wheel_number} HingeJoint {{
                jointParameters HingeJointParameters {{
                axis 0 1 0
                anchor *WHEEL{wheel_number}_ANCHOR* 
                }}
                device [
                RotationalMotor {{
                    name "motor{wheel_number}"
                    maxTorque 5000
                    maxVelocity 26
                }}
                ]
                endPoint Solid {{
                translation *WHEEL{wheel_number}_ANCHOR* 
                rotation 1 0 0 1.5708
                children [
                    DEF WHEEL{wheel_number} Shape {{
                    appearance PBRAppearance {{
                        baseColor 0.305882 0.898039 0.25098
                        roughness 1
                        metalness 0
                    }}
                    geometry *WHEEL{wheel_number}_GEOMETRY* {{
                        *WHEEL{wheel_number}_SIZE*
                    }}
                    }}
                ]
                name "wheel_{wheel_number}"
                contactMaterial "wheel"
                boundingObject USE WHEEL{wheel_number}
                physics Physics {{
                    density 100
                }}
                }}
            }}
    """
    return wheel_design 


def insert_body(body_number):
    body_design = f"""
      DEF BODY{body_number} HingeJoint {{
        jointParameters HingeJointParameters {{
          axis 0 1 0
          anchor *BODY{body_number}_ANCHOR* 
          minStop -*BODY{body_number}_RIGID*     
          maxStop *BODY{body_number}_RIGID* 
        }}
        endPoint Solid {{
          translation *BODY{body_number}_ANCHOR* 
          rotation 1 0 0 0
          children [
            DEF BODY{body_number} Shape {{
              appearance PBRAppearance {{
                baseColor 0.5 0.3 0.8
                roughness 1
                metalness 0
              }}
              geometry *BODY{body_number}_GEOMETRY* {{
                 *BODY{body_number}_SIZE*
              }}
            }}
            *BODY{body_number}_WHEEL*
          ]
          name "body_{body_number}"
          contactMaterial "body_{body_number}"
          boundingObject USE BODY{body_number}
          physics Physics {{
            density 300
          }}
        }}
      }}
    """
    return body_design 

def get_motors(json_file_path):
    #json_file_path = "jsonWheelShapes/ConvJsonMultiSym.json"
    json_data = read_text_file(json_file_path)
    return create_template(json_data)[1]

def create_template(json_data):
    json_obj = json.loads(json_data)
    max_body_num = len(json_obj["bodies"])
    #max_body_num = max(max([int(num) for wheel in json_obj["wheels"] for num in wheel["BodyNum"]]), 0)
    motors = []
    bodies_wheels_code = ""
    #wheel_codes = {str(num): "" for num in range(max_body_num + 1)}

    for i in range(1, max_body_num):
        bodies_wheels_code += insert_body(i)

    j = 0
    for body in json_obj["bodies"]:
        j += 1
        #i = 0
        wheel_code = ""
        for wheel in body["wheels"]:
            motors.append(f"motor{wheel['WheelNum']}")
            if body["Name"] == "BODY":
                bodies_wheels_code += insert_wheel(wheel["WheelNum"])
                if wheel["Symmetrical"]:
                    motors.append(f'motor{wheel["WheelNum"]}SYM')
                    bodies_wheels_code += insert_wheel(f'{wheel["WheelNum"]}SYM') # naming needs to be matched in the controller, maybe import an array with all the names
            else:
                #wheel_codes[num] += insert_wheel(j)
                #print(wheel)
                #print("hi")
                wheel_code += insert_wheel(wheel["WheelNum"])
                if wheel["Symmetrical"]:
                    motors.append(f'motor{wheel["WheelNum"]}SYM')
                    wheel_code += insert_wheel(f'{wheel["WheelNum"]}SYM')
                    #wheel_codes[num] += insert_wheel(f'{j}SYM')
                #print (bodies_wheels_code)
        bodies_wheels_code = bodies_wheels_code.replace(f"*BODY{j-1}_WHEEL*", wheel_code)


    # for num, code in wheel_codes.items():
    #     bodies_wheels_code = bodies_wheels_code.replace(f"*BODY{num}_WHEEL*", code)

    #print(bodies_wheels_code)
    return bodies_wheels_code, motors


def main(pipeline_dir):
   
    json_file_path = os.path.join(pipeline_dir, "jsonWheelShapes/ConvJsonMultiSym2.json")
    json_data = read_text_file(json_file_path)
   
    get_motors(json_file_path)
   
    #print(missions[list(missions.keys())[0]])
    #Modifies the template
    with open(os.path.join(pipeline_dir, "Car4wMultiTemp.proto"), "r") as file:
        content = file.read()
 
    #num_bodies, num_wheels = num_wheels_bodies(json_data)
    #modified_content = content.replace("**InsertBodiesAndWheels**", create_template(num_bodies-1,num_wheels, json_data))
    modified_content = content.replace("**InsertBodiesAndWheels**", create_template(json_data)[0])
    with open(os.path.join(pipeline_dir, "Car4wMultiTemp2.proto"), "w") as file:
        file.write(modified_content)
    
    template_path = os.path.join(pipeline_dir, "Car4wMultiTemp2.proto")
    template_proto = read_text_file(template_path)
 
    # Convert JSON to Proto
    proto_output = create_proto_from_template(template_proto, json_data)
    #proto_output = battery_energy_to_weight(proto_output, json_data)
 
    # Write the output into a new Proto file
    output_proto_file = os.path.join(pipeline_dir, "obstacleTesting1/protos/Car4wMulti2.proto")
    with open(output_proto_file, "w") as file:
        file.write(proto_output)
 
    #print(f"Proto data has been written to '{output_proto_file}'.")
    # with open(os.path.join(pipeline_dir, "obstacleTesting4.wbt"), "r") as file:
    #   world_data = file.read()

    
 
 
 
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