from dataclasses import dataclass
import re
import os
import json
from swaggerSchemaGen import generateswagger # you need the swaggerSchemaGen.py file in the same directory as this file

# Set these parameters to match the files you want to use to generate Swagger comments for
service_name = "service_name_here"
controller_path = 'users_controller_example.js'
router_path = 'users_router_example.js'
service_description = f"{service_name} service description here"
response_codes = {200: "OK", 400: "Bad request", 401: "Unauthorized", 404: "Not found",}

@dataclass
class Route:
    path: str
    method: str
    description: str
    responses: dict

def get_service_name_directory(service_name):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    project_root = os.path.dirname(current_dir)
    service_name_directory = os.path.join(current_dir, service_name)
    service_name_directory = service_name_directory.replace(project_root, '')
    service_name_directory = service_name_directory.lstrip('/\\')
    service_name_directory = service_name_directory.replace('\\', '/')
    return service_name_directory.rstrip('/')

def get_route_info(text):
    matches = re.findall(r'router\.(get|post|put|delete|patch)\(.*?\'(.*?)\'', text, re.DOTALL)
    swagger_doc = []
    for match in matches:
        method, route_path = match
        parameters = re.findall(r'check\(\'(.*?)\'', text)
        swagger_parameters = [generate_swagger_parameter(name) for name in parameters]
        route_obj = Route(route_path, method, service_description, response_codes)
        swagger_comment = generate_swagger_comment(route_obj, swagger_parameters)
        route_path = f"/{service_name_directory}{route_obj.path}"
        method = route_obj.method
        swagger_doc.append({route_path: {method: swagger_comment[method]}})
    return swagger_doc

def write_to_file(swagger_doc, file_name):
    swagger_doc_dict = {}
    for doc in swagger_doc:
        for key, value in doc.items():
            if key in swagger_doc_dict:
                swagger_doc_dict[key].update(value)
            else:
                swagger_doc_dict[key] = value
    with open(file_name, 'w') as file:
        json.dump(swagger_doc_dict, file, indent=2)

def generate_swagger_parameter(name):
    # Check if the parameter is one of the predefined parameters
    if name in ['clientid', 'userid', 'messageid']:
        # Return a reference to the predefined parameter in Swagger components
        return {
            "$ref": f"\'#/components/parameters/{name}\'"
        }
    else:
        # Return a reference to the parameter in Swagger components
        return {
            "name": name,
            "in": "query",
            "required": True,
            "description": f"Description for {name}",  # Update this to the correct description
            "schema": {
                "type": "string"
            },
            "example": "Update this for a real example"
        }

def generate_swagger_comment(route: Route, parameters) -> dict:
    comment = {
        route.method: {
            "tags": [service_name],
            "summary": route.description,
            "parameters": parameters,
            "responses": {}
        }
    }
    for code, desc in route.responses.items():
        if code == 200:
            response = {
                "description": desc,
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": f"\'#/components/schemas/{service_name}\'"
                        }
                    }
                }
            }
        else:
            response = {
                "description": desc
            }
        comment[route.method]["responses"][str(code)] = response
    return comment

def adjust_formatting(swagger_doc_str):
    swagger_doc_str = swagger_doc_str[1:]
    swagger_doc_str = '\n'.join('* ' + line for line in swagger_doc_str.split('\n'))
    swagger_doc_parts = swagger_doc_str.split(f'"/{service_name_directory}')
    swagger_doc_str = f'*/\n\n/**\n* @swagger\n* "/{service_name_directory}/'.join(swagger_doc_parts[1:])
    swagger_doc_str = '/**\n* @swagger\n* "/' + service_name_directory + '/' + swagger_doc_parts[0] + swagger_doc_str
    swagger_doc_str = swagger_doc_str.rstrip(',* ')
    swagger_doc_str += '\n */'
    return swagger_doc_str

def adjust_swagger_comments(swagger_comments):
    swagger_comments = re.sub(r'\n \* ', '\n* ', swagger_comments)
    swagger_comments = re.sub(r'\* \n\*   /', '\n  /', swagger_comments)
    swagger_comments = re.sub(r'\n  /":', '\n":', swagger_comments)
    swagger_comments = re.sub(r'\/\n \*   \{', '/ {', swagger_comments)
    swagger_comments = re.sub(r'\*   \*/', '*/', swagger_comments)
    swagger_comments = re.sub(r'^": \{$', '* ": {', swagger_comments, flags=re.MULTILINE)
    swagger_comments = re.sub(r'^ \*', '*', swagger_comments, flags=re.MULTILINE)
    swagger_comments = re.sub('//', '/', swagger_comments)
    swagger_comments = re.sub(r',\n\*   {\n\*     \*/\n\n', '*/\n', swagger_comments)
    swagger_comments = re.sub(r'\*   }\*/', '*   }\n*/', swagger_comments)
    pattern = r'(@swagger\n\* "/)(.*?)(/\* \n\*   {\n\*     /")'
    replacement = r'\1\2"'
    swagger_comments = re.sub(pattern, replacement, swagger_comments)
    swagger_comments = re.sub(r'\]\s*$', '}', swagger_comments, flags=re.MULTILINE)
    return swagger_comments

# Get the service name directory
service_name_directory = get_service_name_directory(service_name)

# Clear the output file at the start
open(f'{service_name}Swagger_generated.json', 'w').close()

# Read the file
with open(router_path, 'r') as file:
    lines = file.readlines()

# Combine the lines into a single string
text = ''.join(lines)

swagger_doc = get_route_info(text)
write_to_file(swagger_doc, f'{service_name}Swagger_generated.json')

# Read the JSON Swagger document
with open(f'{service_name}Swagger_generated.json', 'r') as file:
    swagger_doc = json.load(file)

# Convert the JSON Swagger document to a string with indentation
swagger_doc_str = json.dumps(swagger_doc, indent=2)

swagger_doc_str = adjust_formatting(swagger_doc_str)

# Write the JSDoc Swagger document to a file
with open(f'{service_name}Swagger_generated.js', 'w') as file:
    file.write(swagger_doc_str)

# Read the Swagger comments into a string
with open(f'{service_name}Swagger_generated.js', 'r') as file:
    swagger_comments = file.read()

swagger_comments = adjust_swagger_comments(swagger_comments)

# Write the adjusted Swagger comments back to the file
with open(f'{service_name}Swagger_generated.js', 'w') as file:
    file.write(swagger_comments)

# Generate the schema as well
generateswagger(service_name, controller_path, router_path)