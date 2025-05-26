import os

# KAFKA SETTINGS
KAFKA_HOST = os.environ.get("KAFKA_HOST", "localhost")
KAFKA_PORT = os.environ.get("KAFKA_PORT", 29092)
GROUP_ID = os.environ.get("GROUP_ID", "PAUSE")
#TARGET_TOPICS = ["metrics"]
TARGET_TOPICS = "metrics.*"

# NATS SETTINGS
NATS_HOST = os.environ.get("NATS_HOST", "localhost")
NATS_PORT = os.environ.get("NATS_PORT", 4222)

# TSCALE SETTINGS
TSCALE_HOST = os.environ.get("TSCALE_HOST", "localhost")
TSCALE_USER = os.environ.get("TSCALE_NAME", "aces")
TSCALE_DB = os.environ.get("TSCALE_DB", "aces")
TSCALE_PASS = os.environ.get("TSCALE_PASS", "aces")

# NEO4J SETTINGS
NEO4J_HOST = os.environ.get("NEO4J_HOST", "127.0.0.1")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASS", "neo4j290292")
