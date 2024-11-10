# database.py
from pymongo import MongoClient
from neo4j import GraphDatabase

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017"
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["tour_planner_db"]
users_collection = mongo_db["users"]
chats_collection = mongo_db["chats"]

# Neo4j connection
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_password"
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


# Helper functions for Neo4j
def store_user_preference(user_id: str, preference_type: str, preference_value: str):
    with neo4j_driver.session() as session:
        session.run(
            """
            MERGE (u:User {id: $user_id})
            MERGE (p:Preference {type: $preference_type, value: $preference_value})
            MERGE (u)-[:PREFERS]->(p)
        """,
            user_id=user_id,
            preference_type=preference_type,
            preference_value=preference_value,
        )


def get_user_preferences(user_id: str):
    with neo4j_driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id})-[:PREFERS]->(p:Preference)
            RETURN p.type AS type, p.value AS value
        """,
            user_id=user_id,
        )
        return [{"type": record["type"], "value": record["value"]} for record in result]


# Close connections on shutdown
def close_db():
    mongo_client.close()
    neo4j_driver.close()
