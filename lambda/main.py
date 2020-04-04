from datetime import datetime, timedelta

import jwt

key = "#KEY_TO_BE_REPLACED#"

def handler(event, context):
    if event.get('Records') is not None:
        return process_cf_request(event)

    return generate_token(event)

def generate_token(event):
    uri = event['uri']

    if uri[0] is not '/':
        uri = '/' + uri

    payload = {
        'uri': uri,
        'iat': datetime.now(),
        'exp': datetime.now() + timedelta(minutes=event.get("minutes", 30))
    }

    return jwt.encode(payload, key, algorithm='HS256')

def process_cf_request(event):
    request = event["Records"][0]["cf"]["request"]

    try:
        # The uri will start with a "/" that is not part of the token that
        # we are trying to decode
        decoded = jwt.decode(request["uri"][1:], key, algorithms=["HS256"])
        request["uri"] = decoded["uri"]
        return request
    except jwt.PyJWTError:
        return {
            'status': "401",
            'statusDescription': "Unauthorized",
            'body': "Unauthorized",
            'bodyEncoding': "text"
        }
