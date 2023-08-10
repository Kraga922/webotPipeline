import json

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
    #num_wheels = 0
    for body in json_obj["bodies"]:
        #num_bodies += 1
        body_name = body["Name"]
        body_shape = body["Shape"]
        body_anchor = body["Anchor"]
        template = template.replace(f"*{body_name}_GEOMETRY*", body_shape)
        template = template.replace(f"*{body_name}_ANCHOR*", body_anchor)
        template = template.replace(f"*{body_name}_SIZE*", generate_geometry_code(body["Dimensions"]))

    # Replace the wheel geometries and sizes
    for wheel in json_obj["wheels"]:
        #num_bodies += 1
        wheel_name = wheel["Name"] # just a number 
        #if wheel["Symmetrical"] == "Yes":
            
        wheel_shape = wheel["Shape"]
        wheel_anchor = wheel["Anchor"]
        template = template.replace(f"*{wheel_name}_GEOMETRY*", wheel_shape)
        template = template.replace(f"*{wheel_name}_ANCHOR*", wheel_anchor)
        template = template.replace(f"*{wheel_name}_SIZE*", generate_geometry_code(wheel["Dimensions"]))

    return template #, num_bodies, num_wheels

def num_wheels_bodies(json_data):
    json_obj = json.loads(json_data)

    return len(json_obj["bodies"]), len(json_obj["wheels"])


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

def create_template(num_bodies, num_wheels):
    bodies_wheels_code = ""

    for i in range(1, num_bodies + 1):
        bodies_wheels_code += insert_body(i)

    for i in range(1, num_wheels + 1):
        bodies_wheels_code += insert_wheel(i)  # Pass only the wheel number

    return bodies_wheels_code

def main():
    
    json_file_path = "jsonWheelShapes/ConvJsonMulti.json"
    json_data = read_text_file(json_file_path)
    
    #Modifies the template 
    with open("Car4wMultiTemp.proto", "r") as file:
        content = file.read()

    num_bodies, num_wheels = num_wheels_bodies(json_data)
    modified_content = content.replace("**InsertBodiesAndWheels**", create_template(num_bodies-1,num_wheels))

    with open("Car4wMultiTemp2.proto", "w") as file:
        file.write(modified_content)


        # Read JSON data from file


    template_path = "Car4wMultiTemp2.proto"
    template_proto = read_text_file(template_path)

    # Convert JSON to Proto
    proto_output = create_proto_from_template(template_proto, json_data)

    # Write the output into a new Proto file
    output_proto_file = "obstacleTesting1/protos/Car4wMulti2.proto"
    with open(output_proto_file, "w") as file:
        file.write(proto_output)

    print(f"Proto data has been written to '{output_proto_file}'.")



if __name__ == "__main__":
    main()
