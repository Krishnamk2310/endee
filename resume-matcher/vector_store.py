import requests
import json
import msgpack
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from config import ENDEE_API_URL, ENDEE_INDEX_NAME, ENDEE_AUTH_TOKEN, VECTOR_DIMENSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if ENDEE_AUTH_TOKEN:
        headers["Authorization"] = ENDEE_AUTH_TOKEN
    return headers

def create_index() -> bool:
    """ create endee index """
    url = f"{ENDEE_API_URL}/index/create"
    payload = {
        "index_name": ENDEE_INDEX_NAME,
        "dim": VECTOR_DIMENSION,
        "space_type": "cosine",
        "M": 32,
        "ef_con": 200,
        "precision": "float32" # float32 for all-MiniLM
    }
    try:
        response = requests.post(url, json=payload, headers=get_headers())
        if response.status_code == 200:
            logger.info(f"Index created successfully: {ENDEE_INDEX_NAME}")
            return True
        elif response.status_code == 409 and "already exists" in response.text.lower():
            logger.info(f"Index {ENDEE_INDEX_NAME} already exists.")
            return True
        else:
            logger.error(f"Failed to create index. Status: {response.status_code}, Msg: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error creating index: {e}")
        return False

def insert_resume(resume_id: str, vector: List[float], metadata: Dict[str, Any]) -> bool:
    """ insert doc embedding """
    url = f"{ENDEE_API_URL}/index/{ENDEE_INDEX_NAME}/vector/insert"
    
    
    # format for endee bulk api
    payload = {
        "id": resume_id,
        "vector": vector,
        "meta": json.dumps(metadata) # serialize metadata
    }
    
    try:
        response = requests.post(url, json=[payload], headers=get_headers())
        if response.status_code == 200:
            logger.info(f"Successfully inserted vector for resume {resume_id}")
            return True
        else:
            logger.error(f"Failed to insert vector. Status: {response.status_code}, Msg: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error inserting vector: {e}")
        return False

def search_job_description(query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    """ search with query vector """
    url = f"{ENDEE_API_URL}/index/{ENDEE_INDEX_NAME}/search"
    payload = {
        "vector": query_vector,
        "k": top_k,
        "ef": 64,
        "include_vectors": False
    }
    
    try:
        response = requests.post(url, json=payload, headers=get_headers())
        if response.status_code == 200:
            # decode results
            
            parsed_results = []
            
            # handle msgpack list format
            if isinstance(results, list):
                for item in results:
                    if isinstance(item, list) and len(item) >= 3:
                        distance = item[0]
                        vec_id = item[1]
                        meta_str = item[2]
                        
                        parsed_results.append({
                            "id": vec_id,
                            "similarity_score": 1.0 - float(distance),
                            "metadata": json.loads(meta_str) if meta_str else {}
                        })
                    
                    # dict format fallback
                    elif isinstance(item, dict):
                         parsed_results.append({
                            "id": item.get("id", ""),
                            "similarity_score": 1.0 - float(item.get("distance", 1.0)),
                            "metadata": json.loads(item.get("meta", "{}")) if item.get("meta") else {}
                        })

            # sort by score
            parsed_results.sort(key=lambda x: x["similarity_score"], reverse=True)
            return parsed_results
            
        else:
            logger.error(f"Search failed. Status: {response.status_code}, Msg: {response.text}")
            return []
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return []

