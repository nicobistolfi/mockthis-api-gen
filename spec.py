import os
import sys
import argparse
from dotenv import load_dotenv
import yaml
import json
from typing import Dict, Any
from collections import OrderedDict
from langchain_anthropic import ChatAnthropic
from utils import to_snake_case

def generate_serverless_config(input_file: str) -> str:
    # Load environment variables and set up API key
    load_dotenv()
    os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

    # Initialize ChatAnthropic
    llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

    # Read the YAML file for serverless structure
    serverless_yaml_path = "input/serverless.yml"
    with open(serverless_yaml_path, 'r') as file:
        serverless_yaml_content = yaml.safe_load(file)

    # Read the OpenAPI definition from the input argument
    with open(input_file, 'r') as file:
        openapi_yaml_content = yaml.safe_load(file)
        openapi_content = json.loads(json.dumps(openapi_yaml_content))

    def create_schema_from_yaml(yaml_dict: Dict[str, Any], title: str = "ServerlessConfig") -> Dict[str, Any]:
        properties = OrderedDict([
            ("frameworkVersion", {"type": "string"}),
            ("service", {"type": "string"}),
            ("provider", {"type": "object"}),
            # ("resources", {"type": "object"}),
            ("functions", {"type": "object"}),
            ("plugins", {"type": "array"})
        ])
        
        for key, value in yaml_dict.items():
            if key not in properties:
                if isinstance(value, dict):
                    properties[key] = create_schema_from_yaml(value, key)
                else:
                    properties[key] = {"type": "string"}
        
        return {
            "title": title,
            "type": "object",
            "properties": properties
        }

    # Create schema from YAML content
    schema = create_schema_from_yaml(serverless_yaml_content)
    schema["description"] = "Serverless configuration structure"

    # Use the created schema as the output definition
    structured_llm = llm.with_structured_output(schema)

    # Extract API paths and methods from OpenAPI definition
    api_functions = []
    for path, methods in openapi_content.get("paths", {}).items():
        for method, details in methods.items():
            function_name = details.get("operationId", f"{method}_{to_snake_case(path.replace('/', '_'))}")
            api_functions.append({
                "name": to_snake_case(function_name),
                "method": method.upper(),
                "path": path,
                "summary": details.get("summary", "No summary provided")
            })

    # Create a base prompt
    base_prompt = f"""
    Generate a serverless configuration for an API with the following specifications:

    1. Service name: '{openapi_content.get("info", {}).get("title", "api-service")}'
    1.1 Framework version: '3'
    1.2 Service: '{openapi_content.get("info", {}).get("title", "api-service")}' but in lower case with dashes instead of spaces
    2. Provider: AWS
    3. Runtime: Python 3.8
    4. Region: us-west-1
    5. Include basic IAM role permissions for CloudWatch Logs
    6. The handler functions will be under the handlers/ directory, the filename will be in the format: {{function_name}}.py and the function name will be handler

    Please structure the configuration according to the provided schema, ensuring all necessary sections are included and properly formatted. Make sure to follow this order for the top-level keys: service, provider, functions, and then any other keys.
    """

    # Initialize an empty response
    response = {}

    # Process each function separately
    for func in api_functions:
        function_prompt = base_prompt + f"""
        Add the following function to the configuration:
        Function name: '{func['name']}'
        - HTTP {func['method']} endpoint at '{func['path']}'
        - {func['summary']}
        """
        
        # Invoke the model with the function-specific prompt
        function_response = structured_llm.invoke(function_prompt, temperature=0)
        
        # Merge the function response into the main response
        if 'functions' not in response:
            response['functions'] = {}
        response['functions'].update(function_response.get('functions', {}))
        
        # Merge other top-level keys
        for key in ['frameworkVersion', 'service', 'provider', 'plugins']:
            if key in function_response and key not in response:
                response[key] = function_response[key]

    # Custom YAML dumper to maintain order
    class OrderedDumper(yaml.Dumper):
        def represent_ordereddict(self, data):
            return self.represent_mapping('tag:yaml.org,2002:map', data.items())

    OrderedDumper.add_representer(OrderedDict, OrderedDumper.represent_ordereddict)

    # Convert response to OrderedDict to maintain order
    ordered_response = OrderedDict([
        ("frameworkVersion", response.get("frameworkVersion")),
        ("service", response.get("service")),
        ("provider", response.get("provider")),
        # ("resources", response.get("resources")),
        ("functions", response.get("functions")),
        ("plugins", response.get("plugins"))
    ])

    # If the org key exists, remove it
    if "org" in ordered_response:
        ordered_response.pop("org")

    # Add any remaining keys
    for key, value in response.items():
        if key not in ordered_response:
            ordered_response[key] = value

    # Check if deploy directory exists
    if not os.path.exists("deploy"):
        os.makedirs("deploy")

    # Output the response to a new YAML file
    output_path = "deploy/api.yml"
    with open(output_path, 'w') as file:
        yaml.dump(ordered_response, file, Dumper=OrderedDumper, default_flow_style=False)

    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate serverless configuration from OpenAPI spec")
    parser.add_argument('--input', required=True, help="Path to the OpenAPI YAML file")
    args = parser.parse_args()

    output_file = generate_serverless_config(args.input)
    print(f"Generated serverless configuration has been written to {output_file}")