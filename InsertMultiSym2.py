import json
import os

def read_text_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    return content.strip()

def read_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

def generate_geometry_code(geom_data, indentation=14):
    if isinstance(geom_data, str):
        return geom_data
    else:
        indent = " " * indentation
        geom_code = ""
        for geom_type, geom_props in geom_data.items():
            geom_code += f" {indent}{geom_type} {geom_props}\n"
        return geom_code


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
                contactMaterial "wheel_{wheel_number}"
                boundingObject USE WHEEL{wheel_number}
                physics Physics {{
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
    #Modifies the template
    with open(os.path.join(pipeline_dir, "Car4wMultiTemp.proto"), "r") as file:
        content = file.read()
 
    #num_bodies, num_wheels = num_wheels_bodies(json_data)
    #modified_content = content.replace("**InsertBodiesAndWheels**", create_template(num_bodies-1,num_wheels, json_data))
    modified_content = content.replace("**InsertBodiesAndWheels**", create_template(json_data)[0])
 
    with open(os.path.join(pipeline_dir, "Car4wMultiTemp2.proto"), "w") as file:
        file.write(modified_content)
 
 
        # Read JSON data from file
 
 
    template_path = os.path.join(pipeline_dir, "Car4wMultiTemp2.proto")
    template_proto = read_text_file(template_path)
 
    # Convert JSON to Proto
    proto_output = create_proto_from_template(template_proto, json_data)
 
    # Write the output into a new Proto file
    output_proto_file = os.path.join(pipeline_dir, "obstacleTesting1/protos/Car4wMulti2.proto")
    with open(output_proto_file, "w") as file:
        file.write(proto_output)
 
    #print(f"Proto data has been written to '{output_proto_file}'.")
 
 
 
if __name__ == "__main__":
    main('.')

