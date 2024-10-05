import os
import sys
import spec
import implement
import document
import argparse
from dotenv import load_dotenv

def main(input_arg):
    # Check that the input file exists
    if not os.path.exists(input_arg):
        print(f"Input file {input_arg} does not exist")
        sys.exit(1)
    else:
        print(f"Processing file {input_arg} 👷")

    # Generate serverless.yml
    spec.generate_serverless_config(input_arg)

    print("Platform deployment file generated. 🏗️")

    #implement the platform
    print("Implementing platform functions and logic... 🔨")
    implement.generate_handlers(serverless_yaml_path='deploy/api.yml',
        openapi_yaml_path=input_arg,
        example_handler_path='input/handler.py',
        output_dir='deploy/handlers')

    print("Platform functions and logic implemented. 🧠")

    #deploy the platform, run command line
    print("Deploying platform... 🚀")
    os.system("touch deploy/deploy.log")

    # Load environment variables from .env file
    load_dotenv()

    # Get AWS credentials from environment variables
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    if aws_access_key_id is None or aws_secret_access_key is None:
        print("AWS credentials not found in .env file.")
        print("Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
        sys.exit(1)

    # Construct the serverless deploy command with environment variables
    deploy_command = f"cd deploy && AWS_ACCESS_KEY_ID={aws_access_key_id} AWS_SECRET_ACCESS_KEY={aws_secret_access_key} serverless deploy --config api.yml --stage dev >> deploy.log"

    # Execute the deploy command
    os.system(deploy_command)

    # log os.system output
    print("Platform deployed. ✅ 🛰️")
    print("-----------------------------------")
    os.system("cd deploy && npm init --yes && npm install serverless-python-requirements --save")
    os.system("cd deploy && serverless deploy --config api.yml --stage dev")
    os.system("cd deploy && serverless info --config api.yml --stage dev")
    print("-----------------------------------")

    #generate documentation
    print("Generating API documentation... 📝")
    documentation = document.generate_api_documentation(serverless_yaml_path='deploy/api.yml',
        openapi_yaml_path=input_arg,
        deploy_log_path='deploy/deploy.log')
    document.save_documentation(documentation, 'deploy/API_DOCUMENTATION.md')
    print("API documentation generated. 📚")


def generate_serverless_yml(data):
    # Logic to generate serverless.yml file
    with open('serverless.yml', 'w') as f:
        # Write the generated content to the file
        f.write(data)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide an input argument")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Generate serverless configuration from OpenAPI spec")
    parser.add_argument('--input', required=True, help="Path to the OpenAPI YAML file")
    args = parser.parse_args()

    output_file = main(args.input)
