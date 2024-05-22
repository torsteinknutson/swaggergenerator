import re
import os
import json

service_name = None
controller_name = None
router_name = None

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def extract_properties(controller_content, controller_name):
    # Use regex to extract properties
    properties = re.findall(r'\"(\w+)\": element.\w+.trim\(\)', controller_content)
    required_properties_params = re.findall(r'let (\w+) = req.params.\w+', controller_content)
    required_properties_query = re.findall(r'let (\w+) = req.query.\w+', controller_content)
    required_properties_body = re.findall(fr'{controller_name}.*?req.body.(\w+)', controller_content, re.DOTALL)
    return properties, required_properties_params, required_properties_query, required_properties_body

def generate_property(name):
    # Generate a single property
    return f'"{name}": {{"type": "string", "example": "{name}"}}'

def generate_schema(properties, required_properties):
    # Generate the schema and insert properties
    properties_str = ',\n    '.join([generate_property(p) for p in properties])
    required_str = ', '.join([f'"{p}"' for p in required_properties])
    schema_template = f'''
    {{
      "type": "object",
      "properties": {{
        {properties_str}
      }},
      "required": [{required_str}]
    }}
    '''
    return schema_template

def extract_controller_names(controller_content):
    # Use regex to extract controller function names
    controller_names = re.findall(r'async function (\w+)', controller_content)
    return controller_names

def generate_swagger_schema(controller_file, router_file):
    controller_content = read_file(controller_file)
    router_content = read_file(router_file)

    # Split the controller content into blocks
    controller_blocks = re.split(r"(async function \w+)", controller_content)

    # The first block is likely to be code before the first async function, so we ignore it
    controller_blocks = controller_blocks[1:]

    schemas = {}

    for i in range(0, len(controller_blocks), 2):
        name = controller_blocks[i].replace("async function ", "").strip()
        content = controller_blocks[i+1]

        properties, required_properties_params, required_properties_query, required_properties_body = extract_properties(content, name)
        schema = generate_schema(properties, required_properties_params + required_properties_query + required_properties_body)
        schemas[name] = json.loads(schema)

    # Combine everything to generate the complete Swagger Schema Definition
    swagger_schema = {
        "components": {
            "schemas": schemas
        }
    }
    return swagger_schema

def json_to_jsdoc(json_obj):
    # Convert the JSON object to a string with indentation
    json_str = json.dumps(json_obj, indent=2)

    # Add an asterisk at the start of each line
    jsdoc_str = '\n'.join('* ' + line for line in json_str.split('\n'))

    # Add @swagger at the start of each schema and remove the {
    jsdoc_str = re.sub(r'\*\s*\{\s*\n\*\s*"(\w+)', r'* @swagger\n*   "\1', jsdoc_str)

    # Wrap the JSDoc string in comment delimiters
    jsdoc_str = '/**\n' + jsdoc_str + '\n */'

    # Remove the extra space before the last */
    jsdoc_str = re.sub(r'\n \*/', '\n*/', jsdoc_str)

    return jsdoc_str

def generateswagger(service_name, controller_name, router_name):
    # Example usage:
    controller_navn = controller_name
    router_navn = router_name

    swagger_schema = generate_swagger_schema(controller_navn, router_navn)

    # Convert each schema in the Swagger Schema Definition to JSDoc and write it to a file
    with open(f'{service_name}SwaggerSchema_generated.js', 'w') as file:
        for schema_name, schema in swagger_schema['components']['schemas'].items():
            # Create a new JSON object for each schema
            schema_obj = {
                "components": {
                    "schemas": {
                        schema_name: schema
                    }
                }
            }

            # Convert the schema JSON object to JSDoc
            schema_jsdoc = json_to_jsdoc(schema_obj)

            # Write the JSDoc schema to the file
            file.write(schema_jsdoc + '\n\n')

    # Write the Swagger Schema Definition to a JSON file    
        with open(f'{service_name}SwaggerSchema_generated.json', 'w') as file:
            json.dump(swagger_schema, file, indent=2)
