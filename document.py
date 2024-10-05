import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

def generate_api_documentation(serverless_yaml_path: str, openapi_yaml_path: str, deploy_log_path: str) -> str:
    # Load environment variables and set up API key
    load_dotenv()
    os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

    # Initialize ChatAnthropic
    llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

    # Read the serverless.yml, openapi.yml, and deploy.log files
    with open(serverless_yaml_path, 'r') as file:
        serverless_content = file.read()
    
    with open(openapi_yaml_path, 'r') as file:
        openapi_content = file.read()
    
    with open(deploy_log_path, 'r') as file:
        deploy_log_content = file.read()

    prompt = f"""
    Generate markdown format documentation on how to consume the mock API that was implemented. Use the following information:

    1. Serverless configuration:
    ```yaml
    {serverless_content}
    ```

    2. OpenAPI specification:
    ```yaml
    {openapi_content}
    ```

    3. Deployment log (contains information about the endpoints):
    ```
    {deploy_log_content}
    ```

    The documentation should include:
    1. An introduction to the API
    2. Base URL for the API (extract this from the deployment log)
    3. Available endpoints with their HTTP methods, descriptions, and example requests/responses
    3.1 Expand on the description of each endpoint
    3.2 Add the example request and response for each endpoint, expanding on the example response
    4. Any authentication requirements
    5. Error handling and common status codes

    Please provide the documentation in markdown format.
    """

    response = llm.invoke(prompt, temperature=0)
    return response.content

def save_documentation(documentation: str, output_path: str):
    """
    Save the generated documentation to a file.

    Args:
    documentation (str): The generated API documentation in markdown format.
    output_path (str): The path where the documentation file should be saved.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as file:
        file.write(documentation)
    print(f"API documentation has been generated and saved to {output_path}")

if __name__ == "__main__":
    # Generate API documentation
    print("Generating API documentation... 📝")
    documentation = generate_api_documentation(
        serverless_yaml_path='deploy/api.yml',
        openapi_yaml_path='input/openapi.yml',
        deploy_log_path='deploy/deploy.log'
    )
    
    # Use the new function to save the documentation
    save_documentation(documentation, 'deploy/API_DOCUMENTATION.md')
    print("API documentation generated. 📚")