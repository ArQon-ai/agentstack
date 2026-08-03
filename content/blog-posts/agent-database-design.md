# Blog Post: The Agent Engineer's Guide to Database Design for RAG Systems
## Published: October 8, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to Database Design for RAG Systems

*Your vector database choice affects cost, performance, and reliability.*

---

## Option Comparison

| Feature | pgvector | Pinecone | Weaviate | Chroma | Qdrant |
|---------|----------|----------|----------|--------|--------|
| Self-hosted | ✅ | ❌ | ✅ | ✅ | ✅ |
| Managed | ✅ (Neon) | ✅ | ✅ | ✅ | ✅ |
| Cost | Low | High | Medium | Low | Medium |
| Performance | Good | Excellent | Good | Good | Excellent |
| Scalability | Good | Excellent | Good | Limited | Good |
| Features | Basic | Rich | Rich | Basic | Rich |

---

## pgvector (Recommended for Startups)

### Setup

```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding VECTOR(1536),  -- OpenAI ada-002
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index
CREATE INDEX ON documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Query

```python
import asyncpg

class PgvectorStore:
    def __init__(self, dsn):
        self.dsn = dsn
    
    async def search(self, query_embedding, top_k=5, filters=None):
        async with asyncpg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                # Build query
                sql = """
                    SELECT id, content, metadata,
                           1 - (embedding <=> $1) as similarity
                    FROM documents
                    WHERE 1=1
                """
                params = [query_embedding]
                
                # Add filters
                if filters:
                    for key, value in filters.items():
                        sql += f" AND metadata->>'{key}' = ${len(params)+1}"
                        params.append(value)
                
                sql += " ORDER BY embedding <=> $1 LIMIT $2"
                params.append(top_k)
                
                rows = await conn.fetch(sql, *params)
                
                return [
                    {
                        "id": row["id"],
                        "content": row["content"],
                        "metadata": row["metadata"],
                        "similarity": row["similarity"]
                    }
                    for row in rows
                ]
```

### Performance Tuning

```sql
-- Index tuning for 100K documents
CREATE INDEX ON documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);  -- sqrt(100K) ≈ 316, use 100 for balance

-- For 1M documents
CREATE INDEX ON documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 1000);

-- HNSW for better recall (slower inserts)
CREATE INDEX ON documents 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

---

## Hybrid Search (Vector + Full-Text)

```sql
-- Add full-text search
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    search_vector TSVECTOR,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create full-text index
CREATE INDEX idx_fts ON documents USING GIN(search_vector);

-- Update search vector on insert/update
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', NEW.content);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER documents_search_vector
    BEFORE INSERT OR UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_search_vector();
```

```python
class HybridSearch:
    async def search(self, query, query_embedding, top_k=10):
        # Vector search results
        vector_results = await self.vector_search(query_embedding, top_k)
        
        # Full-text search results
        text_results = await self.text_search(query, top_k)
        
        # Reciprocal Rank Fusion
        scores = {}
        
        for rank, result in enumerate(vector_results):
            scores[result["id"]] = scores.get(result["id"], 0) + 1 / (rank + 60)
        
        for rank, result in enumerate(text_results):
            scores[result["id"]] = scores.get(result["id"], 0) + 1 / (rank + 60)
        
        # Sort by fused score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return [r for r in ranked[:top_k]]
```

---

## Chunking Strategies

### Fixed-Size

```python
def fixed_chunk(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks
```

### Semantic

```python
class SemanticChunker:
    def __init__(self, embedder):
        self.embedder = embedder
    
    def chunk(self, text, threshold=0.8):
        sentences = text.split(". ")
        chunks = []
        current_chunk = [sentences[0]]
        
        for sentence in sentences[1:]:
            current_embedding = self.embedder.embed(". ".join(current_chunk))
            sentence_embedding = self.embedder.embed(sentence)
            
            similarity = cosine_similarity(current_embedding, sentence_embedding)
            
            if similarity > threshold:
                current_chunk.append(sentence)
            else:
                chunks.append(". ".join(current_chunk))
                current_chunk = [sentence]
        
        if current_chunk:
            chunks.append(". ".join(current_chunk))
        
        return chunks
```

---

## Cost Optimization

### Embedding Caching

```python
class CachedEmbedder:
    def __init__(self, embedder, cache):
        self.embedder = embedder
        self.cache = cache
    
    async def embed(self, text):
        cache_key = hashlib.md5(text.encode()).hexdigest()
        
        if cached := await self.cache.get(cache_key):
            return cached
        
        embedding = await self.embedder.embed(text)
        await self.cache.set(cache_key, embedding, ttl=86400)
        
        return embedding
```

### Dimension Reduction

```python
from sklearn.decomposition import PCA

class DimensionReducer:
    def __init__(self, target_dims=384):
        self.pca = PCA(n_components=target_dims)
    
    def fit(self, embeddings):
        self.pca.fit(embeddings)
    
    def transform(self, embeddings):
        return self.pca.transform(embeddings)
```

---

## The Database Checklist

- [ ] Choose vector store
- [ ] Design schema
- [ ] Create indexes
- [ ] Implement hybrid search
- [ ] Add chunking strategy
- [ ] Cache embeddings
- [ ] Monitor performance
- [ ] Backup strategy
- [ ] Scaling plan
- [ ] Cost tracking

---

## Conclusion

Database design:
- Affects cost significantly
- Impacts query performance
- Determines scalability
- Enables hybrid search

Design for your scale.
Optimize for your queries.

---

*ArQon Agentics builds production-grade RAG systems. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
