import asyncio
from timescaledb.client import AcesMetrics
from graph_base.demand import DemandGraph
from NATS.client import NatsMetricsConsumer
from settings import NATS_HOST, NATS_PORT, TSCALE_HOST, TSCALE_USER, TSCALE_DB, \
    TSCALE_PASS, TARGET_TOPICS, NEO4J_HOST, NEO4J_USER, NEO4J_PASS, GROUP_ID

async def main():
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
    nats_obj = NatsMetricsConsumer(
        nats_host=NATS_HOST,
        nats_port=NATS_PORT
    )
    await nats_obj.consume(
        TARGET_TOPICS,
        mem_obj=this_obj,
        aces_metrics=aces_metrics
    )

if __name__ == "__main__":
    asyncio.run(main())