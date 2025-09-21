import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass
import logging
import sqlite3
import pickle
from datetime import datetime

try:
    import tensorflow as tf
    import tensorflow_hub as hub
    USE_TENSORFLOW = True
except ImportError:
    USE_TENSORFLOW = False
    
try:
    from sentence_transformers import SentenceTransformer
    USE_SENTENCE_TRANSFORMERS = True
except ImportError:
    USE_SENTENCE_TRANSFORMERS = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Represents a single memory entry"""
    content: str
    embedding: np.ndarray
    metadata: Dict[str, Any]
    timestamp: float
    importance: float
    category: str
    related_entries: List[str]

class VectorStore:
    """Manages vector embeddings and similarity search"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.embedding_dim = 384  # Default for MiniLM
        
        # Initialize embedding model
        if USE_SENTENCE_TRANSFORMERS:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Initialized SentenceTransformer with model: {model_name}")
        elif USE_TENSORFLOW:
            self.model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
            logger.info("Initialized Universal Sentence Encoder")
        else:
            logger.warning("No embedding model available. Using random embeddings.")
            self.model = None
            
    def encode(self, texts: List[str]) -> np.ndarray:
        """Generates embeddings for a list of texts."""
        if not texts:
            return np.array([])
            
        try:
            if self.model is not None:
                if USE_SENTENCE_TRANSFORMERS:
                    return self.model.encode(texts)
                else:  # TensorFlow
                    return self.model(texts).numpy()
            else:
                # Fallback to random embeddings
                return np.random.randn(len(texts), self.embedding_dim)
                
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return np.random.randn(len(texts), self.embedding_dim)
            
    def similarity_search(
        self, 
        query_embedding: np.ndarray,
        stored_embeddings: np.ndarray,
        k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Performs similarity search between a query embedding and stored embeddings.
        Returns indices and scores of top k matches.
        """
        if len(stored_embeddings) == 0:
            return []
            
        # Compute cosine similarity
        similarity = np.dot(stored_embeddings, query_embedding) / (
            np.linalg.norm(stored_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top k matches
        top_indices = np.argsort(similarity)[-k:][::-1]
        return [(idx, similarity[idx]) for idx in top_indices]

class SqliteStorage:
    """Handles persistent storage using SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initializes the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    metadata TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    importance REAL NOT NULL,
                    category TEXT NOT NULL,
                    related_entries TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
    def store_memory(self, entry: MemoryEntry) -> int:
        """Stores a memory entry in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO memories 
                (content, embedding, metadata, timestamp, importance, category, related_entries)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.content,
                    pickle.dumps(entry.embedding),
                    json.dumps(entry.metadata),
                    entry.timestamp,
                    entry.importance,
                    entry.category,
                    json.dumps(entry.related_entries)
                )
            )
            return cursor.lastrowid
            
    def get_all_memories(self) -> List[Tuple[int, MemoryEntry]]:
        """Retrieves all memories from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM memories")
            
            results = []
            for row in cursor.fetchall():
                entry = MemoryEntry(
                    content=row[1],
                    embedding=pickle.loads(row[2]),
                    metadata=json.loads(row[3]),
                    timestamp=row[4],
                    importance=row[5],
                    category=row[6],
                    related_entries=json.loads(row[7])
                )
                results.append((row[0], entry))
                
            return results
            
    def update_preference(self, key: str, value: Any):
        """Updates a preference value."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)",
                (key, json.dumps(value))
            )
            
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Retrieves a preference value."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
            row = cursor.fetchone()
            
            if row is None:
                return default
                
            return json.loads(row[0])

class MemoryManager:
    """
    Enhanced memory manager with vector embeddings and learning capabilities.
    """
    
    def __init__(self, memory_path: str = "memory"):
        os.makedirs(memory_path, exist_ok=True)
        
        self.vector_store = VectorStore()
        self.storage = SqliteStorage(os.path.join(memory_path, "memory.db"))
        
        # Cache for frequently accessed data
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        
    async def store_memory(
        self,
        content: str,
        category: str = "general",
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
        related_entries: Optional[List[str]] = None
    ) -> int:
        """
        Stores a new memory with vector embedding.
        
        Args:
            content: The text content to store
            category: Category for organizing memories
            importance: Importance score (0-1)
            metadata: Additional metadata
            related_entries: IDs of related memories
            
        Returns:
            ID of the stored memory
        """
        # Generate embedding
        embedding = self.vector_store.encode([content])[0]
        
        # Create memory entry
        entry = MemoryEntry(
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            timestamp=time.time(),
            importance=importance,
            category=category,
            related_entries=related_entries or []
        )
        
        # Store in database
        memory_id = self.storage.store_memory(entry)
        
        # Invalidate cache
        self._cache.clear()
        
        return memory_id
        
    async def search_memories(
        self,
        query: str,
        category: Optional[str] = None,
        min_importance: float = 0.0,
        k: int = 5
    ) -> List[Tuple[MemoryEntry, float]]:
        """
        Searches memories using vector similarity.
        
        Args:
            query: Search query
            category: Optional category filter
            min_importance: Minimum importance score
            k: Number of results to return
            
        Returns:
            List of (memory, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = self.vector_store.encode([query])[0]
        
        # Get all memories
        cache_key = f"all_memories_{category}_{min_importance}"
        if cache_key in self._cache:
            cached_time, memories = self._cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                all_memories = memories
            else:
                del self._cache[cache_key]
                all_memories = self.storage.get_all_memories()
                self._cache[cache_key] = (time.time(), all_memories)
        else:
            all_memories = self.storage.get_all_memories()
            self._cache[cache_key] = (time.time(), all_memories)
        
        # Filter memories
        filtered_memories = [
            (mid, mem) for mid, mem in all_memories
            if (category is None or mem.category == category)
            and mem.importance >= min_importance
        ]
        
        if not filtered_memories:
            return []
            
        # Prepare embeddings for similarity search
        memory_ids, memories = zip(*filtered_memories)
        embeddings = np.stack([mem.embedding for mem in memories])
        
        # Perform similarity search
        similar_indices = self.vector_store.similarity_search(
            query_embedding, embeddings, k=k
        )
        
        # Return results
        return [(memories[idx], score) for idx, score in similar_indices]
        
    def get_preferences(self) -> Dict[str, Any]:
        """Gets all user preferences."""
        return {
            key: self.storage.get_preference(key)
            for key in [
                "language",
                "timezone",
                "theme",
                "notifications",
                "auto_learn",
                "memory_limit"
            ]
        }
        
    def update_preferences(self, new_prefs: Dict[str, Any]):
        """Updates user preferences."""
        for key, value in new_prefs.items():
            self.storage.update_preference(key, value)
            
    async def learn_from_interaction(
        self,
        interaction: Dict[str, Any],
        outcome: Optional[Dict[str, Any]] = None
    ):
        """
        Learns from an interaction by storing it and updating related memories.
        
        Args:
            interaction: Dictionary containing interaction details
            outcome: Optional outcome information
        """
        # Store the interaction
        metadata = {
            "type": "interaction",
            "timestamp": datetime.now().isoformat(),
            "outcome": outcome
        }
        
        await self.store_memory(
            content=json.dumps(interaction),
            category="interaction",
            importance=0.7 if outcome and outcome.get("success") else 0.3,
            metadata=metadata
        )
        
        # Update success metrics if outcome provided
        if outcome:
            success_rate_key = f"success_rate_{interaction['type']}"
            current_rate = self.storage.get_preference(success_rate_key, 0.0)
            total_interactions = self.storage.get_preference(f"total_{interaction['type']}", 0)
            
            new_rate = (current_rate * total_interactions + (1 if outcome["success"] else 0)) / (total_interactions + 1)
            
            self.storage.update_preference(success_rate_key, new_rate)
            self.storage.update_preference(f"total_{interaction['type']}", total_interactions + 1)
            
    async def consolidate_memories(self):
        """
        Periodically consolidates memories by merging similar ones and removing duplicates.
        This helps maintain memory efficiency and improve retrieval quality.
        """
        # Get all memories
        all_memories = self.storage.get_all_memories()
        if not all_memories:
            return
            
        # Group memories by category
        memories_by_category = {}
        for mid, memory in all_memories:
            if memory.category not in memories_by_category:
                memories_by_category[memory.category] = []
            memories_by_category[memory.category].append((mid, memory))
            
        # Process each category
        for category, memories in memories_by_category.items():
            memory_ids, memory_entries = zip(*memories)
            embeddings = np.stack([mem.embedding for mem in memory_entries])
            
            # Find similar pairs
            for i, (mid1, mem1) in enumerate(memories):
                similars = self.vector_store.similarity_search(
                    mem1.embedding,
                    embeddings,
                    k=3  # Look for 2 similar memories (excluding self)
                )[1:]  # Exclude self
                
                for idx, score in similars:
                    if score > 0.95:  # Very similar memories
                        mid2 = memory_ids[idx]
                        mem2 = memory_entries[idx]
                        
                        # Merge memories
                        merged_content = f"{mem1.content}\n---\n{mem2.content}"
                        merged_metadata = {**mem1.metadata, **mem2.metadata}
                        merged_importance = max(mem1.importance, mem2.importance)
                        
                        # Store merged memory
                        await self.store_memory(
                            content=merged_content,
                            category=category,
                            importance=merged_importance,
                            metadata=merged_metadata,
                            related_entries=list(set(mem1.related_entries + mem2.related_entries))
                        )
                        
                        # TODO: Implement proper memory deletion
                        # For now, we're just letting the new merged memory exist alongside the originals
                        
    async def generate_insights(self) -> List[Dict[str, Any]]:
        """
        Analyzes stored memories to generate insights about patterns and trends.
        
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        # Analyze success rates across different interaction types
        interaction_types = set()
        for _, memory in self.storage.get_all_memories():
            if memory.category == "interaction":
                interaction_data = json.loads(memory.content)
                interaction_types.add(interaction_data.get("type"))
                
        for itype in interaction_types:
            success_rate = self.storage.get_preference(f"success_rate_{itype}", 0.0)
            total = self.storage.get_preference(f"total_{itype}", 0)
            
            if total > 0:
                insights.append({
                    "type": "success_rate",
                    "interaction_type": itype,
                    "rate": success_rate,
                    "total_interactions": total,
                    "confidence": min(1.0, total / 100)  # Higher confidence with more data
                })
                
        # TODO: Add more types of insights (common patterns, time-based trends, etc.)
        
        return insights
