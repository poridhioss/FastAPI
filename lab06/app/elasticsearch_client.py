from elasticsearch import AsyncElasticsearch, Elasticsearch
from typing import List, Dict, Any
import os
import asyncio
import logging
from datetime import datetime
from . import schemas, models

logger = logging.getLogger(__name__)

class ElasticsearchClient:
    def __init__(self):
        self.es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
        self.index_name = os.getenv("ELASTICSEARCH_INDEX", "notes")
        
        # Async client for async operations
        self.async_client = AsyncElasticsearch(
            [self.es_url],
            request_timeout=30,
            max_retries=3,
            retry_on_timeout=True
        )
        
        # Sync client for sync operations
        self.sync_client = Elasticsearch(
            [self.es_url],
            request_timeout=30,
            max_retries=3,
            retry_on_timeout=True
        )

    async def create_index(self):
        """Create the notes index with proper mapping"""
        mapping = {
            "mappings": {
                "properties": {
                    "title": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "created_at": {
                        "type": "date",
                        "format": "strict_date_optional_time||epoch_millis"
                    }
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
        
        try:
            # Check if index exists
            exists = await self.async_client.indices.exists(index=self.index_name)
            if not exists:
                await self.async_client.indices.create(index=self.index_name, body=mapping)
                logger.info(f"Created Elasticsearch index: {self.index_name}")
            else:
                logger.info(f"Elasticsearch index already exists: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            raise

    async def index_note(self, note: models.Note):
        """Index a note in Elasticsearch (async)"""
        doc = {
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at.isoformat() if note.created_at else datetime.now().isoformat()
        }
        
        try:
            response = await self.async_client.index(
                index=self.index_name,
                id=note.id,
                body=doc
            )
            logger.debug(f"Indexed note {note.id}: {response}")
            return response
        except Exception as e:
            logger.error(f"Failed to index note {note.id}: {e}")
            raise

    def index_note_sync(self, note: models.Note):
        """Index a note in Elasticsearch (sync)"""
        doc = {
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at.isoformat() if note.created_at else datetime.now().isoformat()
        }
        
        try:
            response = self.sync_client.index(
                index=self.index_name,
                id=note.id,
                body=doc
            )
            logger.debug(f"Indexed note {note.id}: {response}")
            return response
        except Exception as e:
            logger.error(f"Failed to index note {note.id}: {e}")
            raise

    async def search_notes(self, query: str, limit: int = 10) -> List[schemas.NoteSearchResult]:
        """Search notes using Elasticsearch"""
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^2", "content"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            },
            "size": limit,
            "sort": [
                "_score",
                {"created_at": {"order": "desc"}}
            ],
            "highlight": {
                "fields": {
                    "title": {},
                    "content": {
                        "fragment_size": 150,
                        "number_of_fragments": 3
                    }
                }
            }
        }
        
        try:
            response = await self.async_client.search(
                index=self.index_name,
                body=search_body
            )
            
            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                result = schemas.NoteSearchResult(
                    id=int(hit["_id"]),
                    title=source["title"],
                    content=source["content"],
                    created_at=datetime.fromisoformat(source["created_at"].replace('Z', '+00:00')),
                    score=hit["_score"]
                )
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    async def delete_note(self, note_id: int):
        """Delete a note from Elasticsearch (async)"""
        try:
            response = await self.async_client.delete(
                index=self.index_name,
                id=note_id
            )
            logger.debug(f"Deleted note {note_id}: {response}")
            return response
        except Exception as e:
            if "not_found" not in str(e).lower():
                logger.error(f"Failed to delete note {note_id}: {e}")
            raise

    def delete_note_sync(self, note_id: int):
        """Delete a note from Elasticsearch (sync)"""
        try:
            response = self.sync_client.delete(
                index=self.index_name,
                id=note_id
            )
            logger.debug(f"Deleted note {note_id}: {response}")
            return response
        except Exception as e:
            if "not_found" not in str(e).lower():
                logger.error(f"Failed to delete note {note_id}: {e}")
            raise

    async def health_check(self):
        """Check Elasticsearch cluster health"""
        try:
            health = await self.async_client.cluster.health()
            return health["status"]
        except Exception as e:
            logger.error(f"Elasticsearch health check failed: {e}")
            raise

    async def close(self):
        """Close the Elasticsearch clients"""
        try:
            await self.async_client.close()
            self.sync_client.close()
            logger.info("Closed Elasticsearch clients")
        except Exception as e:
            logger.error(f"Failed to close Elasticsearch clients: {e}")