import os
import yaml
import re
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from typing import Dict, Any

def generate_handlers(serverless_yaml_path: str, openapi_yaml_path: str, example_handler_path: str, output_dir: str):
    # Load environment variables and set up API key
    load_dotenv()
    os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

    # Initialize ChatAnthropic
    llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

    def load_yaml(file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    def load_example_handler(file_path: str) -> str:
        with open(file_path, 'r') as file:
            return file.read()

    # Load the example handler
    example_handler = load_example_handler(example_handler_path)

    # Load the YAML files
    serverless_config = load_yaml(serverless_yaml_path)
    openapi_spec = load_yaml(openapi_yaml_path)

    def extract_code(text: str) -> str:
        # Try to find code between triple backticks
        code_match = re.search(r'```python\n(.*?)```', text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()

        # If no triple backticks, try to find the first Python-like code block
        lines = text.split('\n')
        code_lines = []
        in_code_block = False
        for line in lines:
            if line.strip().startswith('def ') or line.strip().startswith('import '):
                in_code_block = True
            if in_code_block:
                code_lines.append(line)

        return '\n'.join(code_lines).strip()

    def generate_handler(function_name: str, http_event: Dict[str, Any], openapi_spec: Dict[str, Any]) -> str:
        path = http_event.get('path', '')
        method = http_event.get('method', '').lower()

        # Find the corresponding OpenAPI spec for this path and method
        path_spec = openapi_spec.get('paths', {}).get(path, {})
        operation_spec = path_spec.get(method, {})

        prompt = f"""
        Modify the following example AWS Lambda handler to create a new handler for the function '{function_name}' with these specifications:

        1. HTTP Method: {method.upper()}
        2. Path: {path}
        3. Summary: {operation_spec.get('summary', 'No summary provided')}
        4. Operation ID: {operation_spec.get('operationId', 'No operationId provided')}

        Example handler:
        ```python
        {example_handler}
        ```
        Handler requirements:
        - The handler should be a function that takes an event and context as arguments, always called handler(event, context)
        - The handler should return a response object with the following properties: statusCode, body, and headers
        - The handler should write proper error handling and appropriate HTTP responses
        - When neeeded use the logging library to log the request and response


        To mock the api responses, use the following openapi spec which contains api responses examples:
        ```yaml
        {openapi_spec}
        ```

        Requirements:
        - The purpose of the handlers is to serve api endpoints that will be used to mock the api responses
        - Make the api responses as realistic as possible
        - Each handler will manage the function of a single endpoint
        - Maintain the basic structure of the example handler
        - Modify the logic to handle the specific HTTP method and path
        - Parse any path parameters, query string parameters, and request body as needed
        - Include error handling and appropriate HTTP responses
        - Use boto3 for any AWS service interactions (if needed)
        - Include comments explaining the main parts of the code

        Please provide only the modified Python code for this Lambda handler, enclosed in triple backticks.
        """
        print("✨", end="", flush=True)
        response = llm.invoke(prompt, temperature=0)
        return extract_code(response.content)

    # Generate handlers for each function
    for function_name, function_config in serverless_config.get('functions', {}).items():
        events = function_config.get('events', [])
        for event in events:
            if 'http' in event:
                handler_code = generate_handler(function_name, event['http'], openapi_spec)

                # Create a directory for the handlers if it doesn't exist
                os.makedirs(output_dir, exist_ok=True)

                # Write the handler to a file
                with open(f'{output_dir}/{function_name}.py', 'w') as file:
                    file.write(handler_code)

    print("✨")
if __name__ == "__main__":
    # This block will only run if the script is executed directly
    generate_handlers(
        serverless_yaml_path='deploy/api.yml',
        openapi_yaml_path='input/openapi.yml',
        example_handler_path='input/handler.py',
        output_dir='deploy/handlers'
    )
