import json

def handler(event, context):
    http_method = event['httpMethod']
    
    if http_method == 'GET':
        return handle_get(event)
    elif http_method == 'POST':
        return handle_post(event)
    elif http_method == 'PUT':
        return handle_put(event)
    elif http_method == 'DELETE':
        return handle_delete(event)
    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }

def handle_get(event):
    # Implement GET logic here
    body = {
        "message": "GET request processed successfully",
        "input": event,
    }
    return create_response(200, body)

def handle_post(event):
    # Implement POST logic here
    body = {
        "message": "POST request processed successfully",
        "input": event,
    }
    return create_response(201, body)

def handle_put(event):
    # Implement PUT logic here
    body = {
        "message": "PUT request processed successfully",
        "input": event,
    }
    return create_response(200, body)

def handle_delete(event):
    # Implement DELETE logic here
    body = {
        "message": "DELETE request processed successfully",
        "input": event,
    }
    return create_response(204, body)

def create_response(status_code, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body)
    }