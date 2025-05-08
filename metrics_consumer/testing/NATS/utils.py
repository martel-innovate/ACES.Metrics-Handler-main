import json
import re

def normalize_json_input(input_str: str) -> str:
    """
    Normalize JSON input by removing extra quotes if present and handling escaping.
    """
    # If the string starts and ends with quotes, remove them and unescape
    #if input_str.startswith('"') and input_str.endswith('"'):
        # Remove the outer quotes and unescape the inner content
    #    return json.loads(input_str[1:-1])
    input_str=input_str.strip()
    input_str= re.sub(r'\s+', '', input_str)
    if input_str.startswith('"') and input_str.endswith('"'):
        input_str=input_str[1:-1]
    cleaned_string = re.sub(r'\\n|\\r|\\t', '', input_str)  # remove \n, \r, \t
    cleaned_string = cleaned_string.replace('\\"', '"')        # replace \" with "
    cleaned_string = cleaned_string.replace('\\\\', '\\')      # replace \\ with \
    return cleaned_string

def map_nats_to_kafka_format(nats_message: str) -> dict:
    # Load the raw message
    #json_str = extract_json_from_nats_message(nats_message)
    #parsed_message = json.loads(nats_message)
    
    
    normalized_input = normalize_json_input(nats_message)
    #print("Normalized input: ",normalized_input)
    # Load the raw message
    parsed_message = json.loads(normalized_input)
    #print("Parsed message: ",parsed_message)
    # Transform labels from list of dicts to a single dict
    #print(type(parsed_message))
    labels_dict = {label['name']: label['value'] for label in parsed_message['labels']}
    
    # Assume only one sample per message
    sample = parsed_message['samples'][0]
    value = str(sample.get('value', 'N/A'))  # Cast value to string if needed
    timestamp = sample['timestamp']

    # Build the kafka-style message
    kafka_message = {
        "labels": labels_dict,
        "name": labels_dict.get("__name__", "unknown_metric"),
        "timestamp": timestamp,
        "value": value
    }
    #print("Kafka message: ",kafka_message)
    return kafka_message
