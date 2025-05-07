from Kafka.client import KafkaObject
from timescaledb.client import AcesMetrics
from graph_base.demand import DemandGraph

from settings import NATS_HOST, NATS_PORT, TSCALE_HOST, TSCALE_USER, TSCALE_DB, \
    TSCALE_PASS, TARGET_TOPICS, NEO4J_HOST, NEO4J_USER, NEO4J_PASS, GROUP_ID

if __name__ == "__main__":
    this_obj = DemandGraph(
        neo4j_host=NEO4J_HOST,
        neo4j_user=NEO4J_USER,
        neo4j_pass=NEO4J_PASS
    )
    aces_metrics = AcesMetrics(
        host=TSCALE_HOST,
        username=TSCALE_USER,
        database=TSCALE_DB,
        password=TSCALE_PASS
    )
    kafka_obj = KafkaObject(
        bootstrap_servers=f'{NATS_HOST}:{NATS_PORT}'
    )
    kafka_obj.consumer(
        TARGET_TOPICS,
        group_id=GROUP_ID,
        mem_obj=this_obj,
        aces_metrics=aces_metrics
    )
