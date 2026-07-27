"""
lambda_shadow_extractor.py - AWS Lambda that extracts shadow and stores to CockroachDB
Uses Bedrock Titan Embeddings + S3 + CockroachDB Vector Index
"""
import json
import os
import boto3
import psycopg2
from datetime import datetime
import numpy as np

# From our Helios work - same sun extraction, new for CockroachDB
def extract_shadow_features(image_bytes):
    """Mock shadow extraction - replace with sun_extract_jetson.py logic"""
    # In real Lambda, use OpenCV layer
    # For starter, return mock features
    return {
        "sun_azimuth": 135.0,
        "sun_elevation": 35.0,
        "shadow_length_px": 120.5,
        "risk_level": "PRE_APPEARANCE",
        "aisle_id": "aisle_3",
        "camera_id": "cam_1"
    }

def get_embedding_bedrock(text):
    """Get embedding from Bedrock Titan - AWS Service used"""
    bedrock = boto3.client("bedrock-runtime", region_name="us-west-2")
    body = json.dumps({"inputText": text})
    resp = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        body=body,
        contentType="application/json",
        accept="application/json"
    )
    result = json.loads(resp["body"].read())
    return result["embedding"]  # 1024 dim

def store_to_cockroachdb(features, embedding):
    """Store to CockroachDB with vector index - Distributed Vector Indexing tool"""
    conn_str = os.getenv("COCKROACHDB_URL")
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    
    # Insert with vector
    cur.execute("""
        INSERT INTO shadow_embeddings 
        (embedding, sun_azimuth, sun_elevation, shadow_length_px, risk_level, aisle_id, camera_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
    """, (
        embedding,
        features["sun_azimuth"],
        features["sun_elevation"],
        features["shadow_length_px"],
        features["risk_level"],
        features["aisle_id"],
        features["camera_id"]
    ))
    shadow_id = cur.fetchone()[0]
    
    # Transactional insert to near_miss_events with SERIALIZABLE
    cur.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
    cur.execute("""
        INSERT INTO near_miss_events (forklift_id, shadow_id, location, action_taken)
        VALUES (%s, %s, %s, %s)
    """, ("forklift_1", shadow_id, features["aisle_id"], "STOP"))
    
    conn.commit()
    cur.close()
    conn.close()
    return shadow_id

def lambda_handler(event, context):
    """AWS Lambda entry point - serverless agent execution"""
    # Get image from S3
    s3 = boto3.client("s3")
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    
    # Download image
    image_bytes = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    
    # Extract shadow features (from Helios)
    features = extract_shadow_features(image_bytes)
    
    # Get embedding via Bedrock - AWS service
    embedding_text = f"shadow azimuth {features['sun_azimuth']} elevation {features['sun_elevation']} length {features['shadow_length_px']} aisle {features['aisle_id']}"
    embedding = get_embedding_bedrock(embedding_text)
    
    # Store to CockroachDB with vector index
    shadow_id = store_to_cockroachdb(features, embedding)
    
    # Store raw to S3 for artifact storage
    s3.put_object(
        Bucket=bucket,
        Key=f"processed/{shadow_id}.json",
        Body=json.dumps(features)
    )
    
    return {
        "statusCode": 200,
        "body": json.dumps({"shadow_id": str(shadow_id), "risk": features["risk_level"]})
    }

# Local test
if __name__ == "__main__":
    mock_event = {
        "Records": [{"s3": {"bucket": {"name": "shadow-memory-bucket"}, "object": {"key": "test.jpg"}}}]
    }
    # Mock without AWS
    print("Local test - would store shadow embedding to CockroachDB")
    print("Features:", extract_shadow_features(b"dummy"))
