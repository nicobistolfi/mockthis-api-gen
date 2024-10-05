# python filter.py input_openapi.yaml output_openapi.yaml repos
import yaml
import copy
import sys

def filter_endpoints_by_tag(openapi_data, tag):
    filtered_paths = {}
    used_schemas = set()

    for path, methods in openapi_data['paths'].items():
        filtered_methods = {}
        for method, details in methods.items():
            if 'tags' in details and tag in details['tags']:
                filtered_methods[method] = details
                
                # Collect schemas used in this endpoint
                collect_used_schemas(details, used_schemas)
        
        if filtered_methods:
            filtered_paths[path] = filtered_methods
    
    return filtered_paths, used_schemas

def collect_used_schemas(endpoint_details, used_schemas):
    if 'requestBody' in endpoint_details:
        collect_schemas_from_content(endpoint_details['requestBody'], used_schemas)
    if 'responses' in endpoint_details:
        for response in endpoint_details['responses'].values():
            collect_schemas_from_content(response, used_schemas)
    if 'parameters' in endpoint_details:
        for parameter in endpoint_details['parameters']:
            if 'schema' in parameter:
                used_schemas.add(parameter['schema'].get('$ref', '').split('/')[-1])

def collect_schemas_from_content(content, used_schemas):
    if 'content' in content:
        for media_type in content['content'].values():
            if 'schema' in media_type:
                ref = media_type['schema'].get('$ref', '')
                if ref:
                    used_schemas.add(ref.split('/')[-1])
                elif 'properties' in media_type['schema']:
                    for prop in media_type['schema']['properties'].values():
                        ref = prop.get('$ref', '')
                        if ref:
                            used_schemas.add(ref.split('/')[-1])

def filter_schemas(openapi_data, used_schemas):
    filtered_schemas = {}
    for schema_name, schema_details in openapi_data['components']['schemas'].items():
        if schema_name in used_schemas:
            filtered_schemas[schema_name] = schema_details
    return filtered_schemas

def main(input_file, output_file, tag):
    with open(input_file, 'r') as file:
        openapi_data = yaml.safe_load(file)

    # Filter endpoints by the given tag
    filtered_paths, used_schemas = filter_endpoints_by_tag(openapi_data, tag)

    # Filter schemas
    filtered_schemas = filter_schemas(openapi_data, used_schemas)

    # Create new OpenAPI structure
    filtered_openapi = copy.deepcopy(openapi_data)
    filtered_openapi['paths'] = filtered_paths
    filtered_openapi['components']['schemas'] = filtered_schemas

    # Save to output file
    with open(output_file, 'w') as file:
        yaml.safe_dump(filtered_openapi, file)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python filter_openapi.py <input_file> <output_file> <tag>")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
