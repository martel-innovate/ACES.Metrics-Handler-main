# Metrics Collection Overview

## Metrics Actually Processed

The system currently processes the following metrics (some with label-based filtering):
### Container Metrics

- `container_cpu_usage_seconds_total`
- `container_memory_usage_bytes`
- `container_fs_usage_bytes`
- `container_network_receive_bytes_total`
- `container_network_transmit_bytes_total`
- *(and other container-related metrics)*

### Kubernetes Node Metrics

- `kube_node_spec_unschedulable`
- `kube_node_created`
- `kube_node_status_allocatable`
- `kube_node_info`
- `kube_node_role`
- `kube_node_status_capacity`

### Kubernetes Pod Metrics

- `kube_pod_status_phase`
- `kube_pod_container_status_restarts_total`
- `kube_pod_container_resource_limits`
- `kube_pod_container_resource_requests`

### ACES Custom Pod Metrics

- `aces_pod_cpu_utilization`
- `aces_pod_memory_utilization`

###  Kubelet Metrics

- `kubelet_active_pods` 
- `kubelet_restarted_pods_total`
- `kubelet_managed_ephemeral_containers`
- `kubelet_running_containers`
- `kubelet_running_pods`
- `kubelet_started_containers_total`
- `kubelet_started_pods_errors_total`
- `kubelet_started_pods_total`
- `kubelet_working_pods_{config}_{lifecycle}` 


## NATS Subscription Subject
All metrics are received via the following NATS subject: `metrics.*`


## TimescaleDB Tables 

The following tables exist in the TimescaleDB instance and store the processed metrics:

- `container_resource_limits`
- `container_resource_requests`
- `kubelet_metrics`
- `metrics_values`
- `node_metrics`
- `pod_phase`
- `pod_utilization`