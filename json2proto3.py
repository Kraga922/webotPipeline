import json

class json2proto3:
    def convert_json_to_proto(json_file_path, proto_file_path):
        # Read and parse the JSON file
        with open(json_file_path, 'r') as json_file:
            json_data = json.load(json_file)
        
        # Generate the Webots proto code
        proto_code = ""

        # Define the WheelP proto message
        proto_code += '#VRML_SIM R2023b utf8 \n'
        proto_code += 'PROTO WheelP2 [\n'
        proto_code += '  field SFVec3f    translation 0 0 0\n'
        proto_code += '  field SFRotation rotation    0 1 0 0\n'
        proto_code += '  field SFFloat    mass        2\n'
        proto_code += '  field  SFString  name        "WheelP2"\n'
        proto_code += ']\n'
        proto_code += '{\n'
        proto_code += '  Solid {\n'
        proto_code += '    translation IS translation\n'
        proto_code += '    rotation IS rotation\n'
        proto_code += '    name IS name\n'
        proto_code += '    mass IS mass\n'
        proto_code += '    children [\n'
        proto_code += '      DEF WHEEL Shape {\n'
        proto_code += '        appearance PBRAppearance {\n'
        proto_code += '          baseColor 0.305882 0.898039 0.25098\n'
        proto_code += '          roughness 1\n'
        proto_code += '          metalness 0\n'
        proto_code += '        }\n'
        for key, value in json_data.items(): 
            # Generate the message
            proto_code += f"        geometry {key} {{\n"
            for prop_key, prop_value in value.items():
                proto_code += f"          {prop_key}   {prop_value}\n"
            proto_code += "        }\n\n"
        proto_code += '      }\n'
        proto_code += '    ]\n'
        proto_code += '    boundingObject USE WHEEL\n'
        proto_code += '    physics Physics {\n'
        proto_code += '      mass IS mass\n'
        proto_code += '    }\n'
        proto_code += '  }\n'
        proto_code += '}'

        # Write the generated proto code to a file
        with open(proto_file_path, 'w') as proto_file:
            proto_file.write(proto_code)
        
        print(f"Conversion successful. Webots proto code saved to {proto_file_path}.")

    # Usage example
    if __name__ == "__main__":
        json_file_path = 'jsonWheelShapes/ConvJsonCy.json'
        proto_file_path = 'obstacleTesting1/protos/WheelP2.proto'
        convert_json_to_proto(json_file_path, proto_file_path)

