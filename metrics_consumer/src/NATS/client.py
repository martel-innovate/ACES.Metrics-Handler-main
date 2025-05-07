import asyncio
import nats
from nats.errors import TimeoutError
import json
import re

prefix = "kube_node"
easy_node_metrics = [
    f"{prefix}_spec_unschedulable",
    f"{prefix}_created",
    f"{prefix}_status_allocatable",
]

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


class NatsMetricsConsumer():
    def __init__(self, nats_url="localhost:4222", nats_subject="metrics.*"):
        self.nats_url = nats_url
        self.nats_subject = nats_subject
    async def connect(self):
        self.nc = await nats.connect(self.nats_url)
    async def subscribe(self):
        self.sub = await self.nc.subscribe(self.nats_subject)
    async def consume(self):
        while True:
            try:
                msg = await self.sub.next_msg(timeout=10)
                print("Received:", msg)
                # Convert the NATS message to Kafka format  
                kafka_message = map_nats_to_kafka_format(msg.data.decode())
                print("Converted to Kafka format:", kafka_message)
            except TimeoutError:
                print("No message received in the last 10 seconds, continuing...")
                continue
            except Exception as e:
                print(f"Error processing message: {e}")
                continue
    async def close(self):
        await self.nc.drain()
    def handler(self, msg, mem_obj, aces_metrics):
        json_result = json.loads(msg.value().decode())
        # dict_keys(['labels', 'name', 'timestamp', 'value'])
        result = json_result["labels"]
        metric_name = result["__name__"]
        if metric_name.startswith("container"):
            if "pod" in result.keys():
                query = mem_obj.insert_pod_metric(
                    node_id="node1",
                    pod_id=result["pod"],
                    name=metric_name,
                    timeseries_origin="metrics_values"
                )
                mem_obj.bolt_transaction(query)
                aces_metrics.insert_metrics(
                    table_name="metrics_values",
                    time=json_result['timestamp'],
                    metric=metric_name,
                    pod=result['pod'],
                    value=json_result['value'],
                    node=result["instance"]
                )
        elif metric_name in easy_node_metrics:
            self.logger.info(metric_name)
            self.logger.info(json_result)
            query = mem_obj.make_easy_node_metrics(
                node_id="node1",
                node_metric=metric_name,
                instance=json_result["labels"]["instance"],
                node_details=json_result["labels"]["node"]
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_node_metrics(
                node_table_name="node_metrics",
                time=json_result["timestamp"],
                metric=metric_name,
                value=json_result["value"],
                node=result["node"]
            )
        elif metric_name == "kube_node_info":
            query = mem_obj.set_kube_node_info(
                node_id="node1",
                node_metric=metric_name,
                instance=json_result["labels"]["instance"],
                node_details=json_result["labels"]["node"],
                internal_ip=json_result["labels"]["internal_ip"],
                kernel_version=json_result["labels"]["kernel_version"],
                os_image=json_result["labels"]["os_image"],
                kubelet_version=json_result["labels"]["kubelet_version"],
                kubeproxy_version=json_result["labels"]["kubeproxy_version"]
            )
            mem_obj.bolt_transaction(query)
        elif metric_name == "kube_node_role":
            query = mem_obj.set_kube_node_role(
                node_id="node1",
                node_metric=metric_name,
                instance=json_result["labels"]["instance"],
                node_details=json_result["labels"]["node"],
                node_role=json_result["labels"]["role"]
            )
            mem_obj.bolt_transaction(query)
        elif metric_name == "kube_node_status_capacity":
            query, target_metric_name, value, time_stmp = mem_obj.set_status_capacity(
                json_result
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_node_metrics(
                node_table_name="node_metrics",
                time=time_stmp,
                metric=target_metric_name,
                value=value,
                node=result["node"]
            )
        elif metric_name == "kube_pod_status_phase":
            query = mem_obj.insert_pod_metric(
                node_id='node1',
                pod_id=json_result['labels']['pod'],
                name="kube_pod_status_phase",
                timeseries_origin="pod_phase"
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_pod_phase_details(
                table_name="pod_phase",
                time=json_result['timestamp'],
                pod=json_result['labels']['pod'],
                phase=json_result['labels']['phase'],
                status_flag=json_result['value'],
                node=result["node"]
            )
        elif metric_name == "kube_pod_container_status_restarts_total":
            query = mem_obj.insert_pod_metric(
                node_id='node1',
                pod_id=result['pod'],
                name="kube_pod_container_status_restarts_total",
                timeseries_origin="metrics_values"
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_metrics(
                table_name="metrics_values",
                time=json_result['timestamp'],
                metric=metric_name,
                pod=result['pod'],
                value=json_result['value'],
                node=result["node"]
            )
        elif metric_name == "kube_pod_container_resource_limits":
            query = mem_obj.insert_pod_metric(
                node_id='node1',
                pod_id=result['pod'],
                name="kube_pod_container_resource_limits",
                timeseries_origin="container_resource_limits"
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_resource_limits(
                time=json_result['timestamp'],
                pod=result['pod'],
                value=json_result['value'],
                resource=result['resource'],
                unit=result['unit']
            )
        elif metric_name == "kube_pod_container_resource_requests":
            query = mem_obj.insert_pod_metric(
                node_id='node1',
                pod_id=result['pod'],
                name="kube_pod_container_resource_requests",
                timeseries_origin="container_resource_requests"
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_resource_requests(
                time=json_result['timestamp'],
                pod=result['pod'],
                value=json_result['value'],
                resource=result['resource'],
                unit=result['unit']
            )
        elif metric_name == "aces_pod_cpu_utilization" and 'pod' in result.keys():
            query = mem_obj.insert_pod_metric(
                node_id='node1',
                pod_id=result['pod'],
                name="aces_pod_cpu_utilization",
                timeseries_origin="pod_utilization"
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_utilization(
                time=json_result['timestamp'],
                pod=result['pod'],
                value=json_result['value'],
                type='cpu'
            )
        elif metric_name == "aces_pod_memory_utilization" and 'pod' in result.keys():
            query = mem_obj.insert_pod_metric(
                node_id='node1',
                pod_id=result['pod'],
                name="aces_pod_memory_utilization",
                timeseries_origin="pod_utilization"
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_utilization(
                time=json_result['timestamp'],
                pod=result['pod'],
                value=json_result['value'],
                type='memory'
            )
        elif metric_name == "kubelet_active_pods" or metric_name == "kubelet_restarted_pods_total":
            if "static" in json_result["labels"].keys():
                if json_result["labels"]["static"] == "true":
                    query = mem_obj.insert_kubelet_metric(
                        node_id="node1",
                        metric_name=metric_name,
                        timeseries_origin="kubelet_metrics"
                    )
                    mem_obj.bolt_transaction(query)
                    aces_metrics.insert_kubelet(
                        time=json_result["timestamp"],
                        value=json_result["value"],
                        metric=metric_name
                    )
        elif metric_name in [
            "kubelet_managed_ephemeral_containers",
            "kubelet_running_containers",
            "kubelet_running_pods",
            "kubelet_started_containers_total",
            "kubelet_started_pods_errors_total",
            "kubelet_started_pods_total"
        ]:
            query = mem_obj.insert_kubelet_metric(
                node_id="node1",
                metric_name=metric_name,
                timeseries_origin="kubelet_metrics"
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_kubelet(
                time=json_result["timestamp"],
                value=json_result["value"],
                metric=metric_name
            )
        elif metric_name == "kubelet_working_pods":
            if "static" in json_result["labels"].keys():
                if json_result["labels"]["static"] == "true":
                    formatted_metric_name = f'{metric_name}_{json_result["labels"]["config"]}_{json_result["labels"]["lifecycle"]}'
                    query = mem_obj.insert_kubelet_metric(
                        node_id="node1",
                        metric_name=formatted_metric_name,
                        timeseries_origin="kubelet_metrics"
                    )
                    mem_obj.bolt_transaction(query)
                    aces_metrics.insert_kubelet(
                        time=json_result["timestamp"],
                        value=json_result["value"],
                        metric=formatted_metric_name
                    )
        else:
            pass   

