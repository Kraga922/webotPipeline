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

    # Replace BODY_GEOMETRY with the robot body geometry type and size
    body_geometry_name = json_obj["robot_body"]["Shape"]
    template = template.replace("*BODY_GEOMETRY*", body_geometry_name)
    template = template.replace("*BODY_SIZE*", generate_geometry_code(json_obj["robot_body"]["Dimensions"]))

    # Replace the wheel geometries and sizes
    for wheel in json_obj["wheels"]:
        wheel_name = wheel["Name"]
        wheel_shape = wheel["Shape"]
        wheel_anchor = wheel["Anchor"]
        template = template.replace(f"*{wheel_name}_GEOMETRY*", wheel_shape)
        template = template.replace(f"*{wheel_name}_ANCHOR*", wheel_anchor)
        template = template.replace(f"*{wheel_name}_SIZE*", generate_geometry_code(wheel["Dimensions"]))

    return template

# Read JSON data from file
json_file_path = "jsonWheelShapes/ConvJsonFullBody.json"
json_data = read_text_file(json_file_path)

template_path = "Car4wTemp.proto"
template_proto = read_text_file(template_path)

# Convert JSON to Proto
proto_output = create_proto_from_template(template_proto, json_data)

# Write the output into a new Proto file
output_proto_file = "obstacleTesting1/protos/CarConvOutput.proto"
with open(output_proto_file, "w") as file:
    file.write(proto_output)

print(f"Proto data has been written to '{output_proto_file}'.")


        # endPoint BODY2 Solid {
        #   translation 0.2 0 0
        #   children [
        #     DEF BODY2 Shape {
        #       appearance PBRAppearance {
        #         baseColor 0.305882 0.898039 0.25098
        #         roughness 1
        #         metalness 0
        #       }
        #       geometry Box {
        #         size 0.2 0.1 0.05
        #       }
        #     }
        #   ]
        #   boundingObject USE BODY2
        #   physics Physics {
        #   }
        # }