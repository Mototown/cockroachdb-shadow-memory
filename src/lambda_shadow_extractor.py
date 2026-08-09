"""
AWS Lambda-style shadow extractor.

Pipeline:
1. Receive image (from S3 event in production)
2. Extract shadow features
3. Generate embedding via Amazon Bedrock Titan
4. Persist to CockroachDB (vector + transactional memory)
5. Store artifacts in S3
"""

import json
import os
from typing import Any, Dict, List

import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    import boto3
except ImportError:
    boto3 = None


def extract_shadow_features(image_bytes: bytes) -> Dict[str, Any]:
    """Feature extraction stub.

    Replace with real vision pipeline (OpenCV / model) for production.
    The important part for this hackathon is that the *memory* of the
    extracted signal lives in CockroachDB.
    """
    return {
        "sun_azimuth": 135.0,
        "sun_elevation": 35.0,
        "shadow_length_px": 120.5,
        "risk_level": "PRE_APPEARANCE",
        "aisle_id": "aisle_3",
        "camera_id": "cam_1",
    }


def get_embedding_bedrock(text: str) -> List[float]:
    """Amazon Bedrock Titan embedding (AWS service requirement)."""
    if boto3 is None or os.getenv("MOCK_AWS") == "1":
        return [0.1] * 1024

    bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-west-2"))
    body = json.dumps({"inputText": text})
    resp = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(resp["body"].read())
    return result["embedding"]


def store_to_cockroachdb(features: Dict[str, Any], embedding: List[float]) -> str:
    """Write semantic + transactional memory into CockroachDB."""
    conn = psycopg2.connect(os.environ["COCKROACHDB_URL"])
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO shadow_embeddings
                    (embedding, sun_azimuth, sun_elevation, shadow_length_px,
                     risk_level, aisle_id, camera_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    embedding,
                    features["sun_azimuth"],
                    features["sun_elevation"],
                    features["shadow_length_px"],
                    features["risk_level"],
                    features["aisle_id"],
                    features["camera_id"],
                ),
            )
            shadow_id = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO near_miss_events (forklift_id, shadow_id, location, action_taken)
                VALUES (%s, %s, %s, %s)
                """,
                ("forklift_1", shadow_id, features["aisle_id"], "STOP"),
            )
            conn.commit()
            return str(shadow_id)
    finally:
        conn.close()


def lambda_handler(event, context):
    """AWS Lambda entry point."""
    # Production path reads from S3 event; local path accepts a mock.
    if "Records" in event and boto3 is not None and os.getenv("MOCK_AWS") != "1":
        s3 = boto3.client("s3")
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]
        image_bytes = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    else:
        image_bytes = b"demo"

    features = extract_shadow_features(image_bytes)
    embedding_text = (
        f"shadow azimuth {features['sun_azimuth']} elevation {features['sun_elevation']} "
        f"length {features['shadow_length_px']} aisle {features['aisle_id']}"
    )
    embedding = get_embedding_bedrock(embedding_text)
    shadow_id = store_to_cockroachdb(features, embedding)

    return {
        "statusCode": 200,
        "body": json.dumps({"shadow_id": shadow_id, "risk": features["risk_level"]}),
    }


if __name__ == "__main__":
    print("Local extractor demo")
    print(lambda_handler({"Records": []}, None))
