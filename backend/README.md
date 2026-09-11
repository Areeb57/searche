# Multi-Stage Research Agent Backend

A production-grade, asynchronous Python backend for an autonomous **Multi-Stage Research Agent**. It executes deep multi-source research, crawls relevant pages, extracts structured evidence and claims, deduplicates knowledge while preserving source provenance, detects cross-source contradictions, compiles interactive knowledge graphs for React Flow, synthesizes concise answers, and powers follow-up Q&A directly from stored vector memory without re-running searches.

---

## Architecture & Workflow

```text
                                User Query
                                    ↓
                         Generate Additional Queries
                                    ↓
                            Search All Queries
                                    ↓
                          Collect Search Results
                                    ↓
                               Rank Results
                                    ↓
                          Select Initial Sources
                                    ↓
                              Normalize URLs
                                    ↓
                           Remove Duplicate URLs
                                    ↓
                             Create Crawl Queue
                                    ↓
                              Fetch Webpages
                                    ↓
                       Extract Main Article Content
                                    ↓
                              Clean Content
                                    ↓
                             Discover Useful Links
                                    ↓
                           Evaluate Link Relevance
                                    ↓
                     Add Relevant Links to Crawl Queue
                                    ↓
                          Analyze Article with LLM
                                    ↓
                       Extract Structured Information
                                    ↓
                  Store Raw + Clean + Structured Information
                                    ↓
                     Create Source-Level Knowledge Graph
                                    ↓
                       Merge Knowledge from All Sources
                                    ↓
                            Detect Similar Meaning
                                    ↓
                             Merge Similar Claims
                                    ↓
                             Detect Contradictions
                                    ↓
                           Preserve Source Provenance
                                    ↓
                          Create Unified Knowledge Graph
                                    ↓
                             Generate Concise Answer
                                    ↓
                             Store Research Session
                                    ↓
                 Answer Follow-up Questions From Stored Knowledge
```

---

## Key Features

- **Multi-Stage Orchestration**: Modular pipeline separating Query Generation, Multi-Engine Search, Source Selection, Crawling, Cleaning, Knowledge Extraction, Deduplication, Contradiction Detection, Graph Building, and Synthesis.
- **Provider Abstractions**:
  - **LLM**: Pluggable adapters for `OpenAI`, `Google Gemini`, `Anthropic Claude`, and a deterministic offline `MockLLMProvider` for zero-cost testing.
  - **Search Engine**: Pluggable adapters for `Tavily`, `Brave Search`, `Serper.dev`, free keyless `DuckDuckGo`, and deterministic `MockSearch`.
- **Intelligent Crawling & Extraction**: Breadth-first asynchronous crawl queue with `asyncio.Semaphore`, domain visit caps, depth control, SSRF defense, Trafilatura article extraction with BeautifulSoup fallback, and HTML noise elimination.
- **Strict Source Provenance**: Every claim and fact traces directly back to its source document ID, parent source ID, and original URL via a relational provenance junction (`claim_sources`).
- **Semantic Deduplication & Contradiction Detection**: Merges equivalent claims across disparate sources using vector cosine similarity and LLM semantic synthesis, while highlighting contradictory guidelines or context qualifications.
- **React Flow Ready Knowledge Graphs**: Generates generic, typed nodes (`topic`, `source`, `claim`, `entity`, `contradiction`) and edges with pre-computed 2D layout coordinates for direct rendering in frontend graph libraries.
- **Real-Time WebSocket Streaming**: Full granular event stream (`research_started`, `queries_generated`, `search_started`, `crawl_started`, `page_fetched`, `article_analyzed`, `knowledge_merged`, `contradiction_detected`, `answer_generated`, `completed`).
- **Follow-Up Memory RAG**: Answers follow-up questions from stored session knowledge and vector embeddings (`pgvector` / SQLite fallback) without re-crawling the web.

---

## Project Structure

```text
searche/backend/
├── app/
│   ├── main.py                     # FastAPI entrypoint, lifespan, CORS, and routers
│   ├── config.py                   # Pydantic Settings & environment variable configuration
│   │
│   ├── api/
│   │   ├── routes.py               # Root API router & health check
│   │   ├── research_routes.py      # REST endpoints (/research, /sources, /graph, /questions)
│   │   └── websocket.py            # WebSocket streaming (/ws/research/{session_id})
│   │
│   ├── schemas/
│   │   ├── research.py             # ResearchConfig, ResearchRequest, SessionStatusEnum
│   │   ├── search.py               # SearchResult, GeneratedQueries
│   │   ├── source.py               # Source, Document, CrawlQueueItem
│   │   ├── knowledge.py            # Claim, Entity, UnifiedClaim, Contradiction, KnowledgeNode
│   │   ├── answer.py               # ResearchAnswer, FollowUpRequest, FollowUpResponse
│   │   └── websocket.py            # WebSocketEvent, WebSocketEventType
│   │
│   ├── database/
│   │   ├── connection.py           # Async SQLAlchemy engine & session factory
│   │   ├── models.py               # SQLAlchemy 2.0 declarative models & VectorType
│   │   └── repositories.py         # Repositories for sessions, claims, graph, and vector search
│   │
│   ├── llm/
│   │   ├── base.py                 # Abstract LLMProvider interface
│   │   ├── factory.py              # LLM provider factory
│   │   ├── openai.py               # OpenAI / OpenRouter client
│   │   ├── gemini.py               # Google Gemini client
│   │   ├── claude.py               # Anthropic Claude client
│   │   └── mock.py                 # Offline/testing Mock LLM provider
│   │
│   ├── search/
│   │   ├── base.py                 # Abstract SearchEngine interface
│   │   ├── factory.py              # Search engine factory
│   │   ├── tavily.py               # Tavily API adapter
│   │   ├── brave.py                # Brave search adapter
│   │   ├── serper.py               # Serper.dev Google search adapter
│   │   ├── duckduckgo.py           # Free keyless web search adapter
│   │   └── mock.py                 # Mock search for testing
│   │
│   ├── crawler/
│   │   ├── url_normalizer.py       # Canonical URL cleaning & tracking param stripping
│   │   ├── deduplication.py        # Content hash & URL deduplication manager
│   │   ├── fetcher.py              # Async HTTP client with SSRF guard and exponential backoff
│   │   ├── browser.py              # Optional Playwright dynamic renderer
│   │   ├── extractor.py            # Trafilatura + BeautifulSoup article extractor
│   │   ├── cleaner.py              # Content cleaner preserving headings, lists, tables
│   │   └── link_discovery.py       # Outgoing link relevance scoring and discovery
│   │
│   ├── knowledge/
│   │   ├── schemas.py              # Re-exported knowledge schemas
│   │   ├── extraction.py           # LLM prompts & structured extraction parser
│   │   ├── graph.py                # React Flow graph layout & generator
│   │   ├── deduplication.py        # Semantic claim deduplication & clustering
│   │   ├── contradiction.py        # Contradiction detection engine
│   │   └── provenance.py           # Source provenance lineage tracker
│   │
│   ├── services/
│   │   ├── embedding_service.py    # Vector embedding & cosine similarity service
│   │   └── websocket_manager.py    # Active connections & session broadcast
│   │
│   └── agent/
│       ├── research_state.py       # Central ResearchState data object
│       ├── query_generator.py      # Generates complementary research queries
│       ├── search_manager.py       # Runs concurrent searches and stores results
│       ├── source_selector.py      # Multi-criteria source selection and ranking
│       ├── crawl_manager.py        # Asynchronous crawl queue with concurrency semaphore
│       ├── article_analyzer.py     # Analyzes articles and extracts structured claims
│       ├── knowledge_builder.py    # Builds independent source-level knowledge
│       ├── knowledge_merger.py     # Merges unified claims, detects contradictions, builds graph
│       ├── answer_generator.py     # Synthesizes concise, source-aware final answer
│       ├── follow_up_service.py    # Answers follow-up questions from stored memory
│       └── research_agent.py       # Main pipeline coordinator
│
├── tests/
│   ├── conftest.py                 # Fixtures, test database, and Mock providers
│   ├── test_url_normalizer.py      # URL canonicalization tests
│   ├── test_query_generator.py     # Query generation tests
│   ├── test_search_normalization.py# Search adapter tests
│   ├── test_extractor.py           # Article extraction and link discovery tests
│   ├── test_deduplication.py       # Semantic claim deduplication tests
│   ├── test_contradiction.py       # Contradiction detection tests
│   ├── test_knowledge_graph.py     # React Flow graph formatting tests
│   └── test_api.py                 # REST and validation integration tests
│
├── .env.example                    # Configuration template
├── requirements.txt                # Python package dependencies
├── Dockerfile                      # Production container image definition
├── docker-compose.yml              # Multi-container setup (PostgreSQL 16 + pgvector)
└── README.md                       # Documentation
```

---

## Installation & Setup

### Prerequisites

- Python 3.11+
- (Optional) Docker & Docker Compose for PostgreSQL with `pgvector`

### 1. Clone or Navigate to Directory

```bash
cd searche/backend
```

### 2. Create and Activate a Virtual Environment

On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

On Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

*(Optional) Install Playwright browsers if JavaScript dynamic rendering is required:*
```bash
playwright install chromium
```

### 4. Configure Environment Variables

Copy the configuration template:
```bash
cp .env.example .env
```

Edit `.env` as needed:
```ini
# Database: defaults to SQLite for local development out of the box
DATABASE_URL=sqlite+aiosqlite:///./research.db

# Or use PostgreSQL + pgvector:
# DATABASE_URL=postgresql+asyncpg://postgres:postgrespassword@localhost:5432/research_db

# LLM Provider: 'openai', 'gemini', 'claude', or 'mock'
LLM_PROVIDER=mock

# Search Provider: 'tavily', 'brave', 'serper', 'duckduckgo', or 'mock'
SEARCH_PROVIDER=duckduckgo

# API Keys (when using external providers)
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
GEMINI_API_KEY=your_gemini_key
CLAUDE_API_KEY=your_claude_key
```

---

## Running the Application

### Local Development Server

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The server will initialize tables automatically on startup:
- **Interactive OpenAPI Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Documentation (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### Running with Docker Compose (PostgreSQL + pgvector)

To spin up the PostgreSQL 16 container with `pgvector` alongside the backend:

```bash
docker-compose up --build
```

---

## Running the Automated Test Suite

Run the full pytest suite:

```bash
pytest tests/ -v
```

All 20 unit and integration tests run isolated in-memory without making real external API calls:
```text
tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_start_research_endpoint PASSED
tests/test_api.py::test_validation_limits PASSED
tests/test_api.py::test_sources_and_graph_endpoints PASSED
tests/test_contradiction.py::test_contradiction_detection PASSED
tests/test_deduplication.py::test_claim_deduplication PASSED
tests/test_extractor.py::test_content_extraction PASSED
tests/test_extractor.py::test_content_cleaner PASSED
tests/test_extractor.py::test_link_discovery PASSED
tests/test_knowledge_graph.py::test_knowledge_graph_builder PASSED
tests/test_query_generator.py::test_query_generator_execution PASSED
tests/test_query_generator.py::test_generated_queries_schema PASSED
tests/test_search_normalization.py::test_search_results_normalization PASSED
tests/test_search_normalization.py::test_search_result_validation PASSED
tests/test_url_normalizer.py::test_url_normalization_tracking_params PASSED
tests/test_url_normalizer.py::test_url_normalization_trailing_slash_and_fragment PASSED
tests/test_url_normalizer.py::test_url_normalization_case_and_port PASSED
tests/test_url_normalizer.py::test_url_normalization_relative PASSED
tests/test_url_normalizer.py::test_domain_extraction PASSED
tests/test_url_normalizer.py::test_deduplication_manager PASSED
============================= 20 passed in 0.35s ==============================
```

---

## REST API Documentation

### 1. Initiate Research Session
- **`POST /api/research`**
- **Request Body**:
```json
{
  "query": "best foods for healthy weight gain",
  "config": {
    "number_of_queries": 4,
    "initial_sources": 8,
    "max_pages": 20,
    "max_depth": 1,
    "max_pages_per_domain": 3
  }
}
```
- **Response** (`201 Created`):
```json
{
  "session_id": "rs_a4f9b8c21e",
  "status": "created"
}
```

### 2. Get Session Status & Final Answer
- **`GET /api/research/{session_id}`**
- **Response**:
```json
{
  "session_id": "rs_a4f9b8c21e",
  "original_query": "best foods for healthy weight gain",
  "status": "completed",
  "configuration": {
    "number_of_queries": 4,
    "initial_sources": 8,
    "max_pages": 20,
    "max_depth": 1,
    "max_pages_per_domain": 3
  },
  "created_at": "2026-09-11T12:00:00Z",
  "updated_at": "2026-09-11T12:00:45Z",
  "final_answer": "Healthy weight gain requires a sustained caloric surplus...",
  "error_message": null,
  "stats": {
    "queries_generated": 4,
    "search_results_found": 32,
    "sources_selected": 8,
    "pages_crawled": 8,
    "claims_extracted": 24,
    "unified_claims": 6,
    "contradictions_found": 1
  }
}
```

### 3. Get Sources & Documents
- **`GET /api/research/{session_id}/sources`**
- Returns all selected sources and extracted documents with URLs and metadata.

### 4. Get Unified Knowledge & Contradictions
- **`GET /api/research/{session_id}/knowledge`**
- Returns consolidated claims with provenance link arrays (`source_id`, `document_id`, `support`) and contradiction records.

### 5. Get Knowledge Graph (React Flow Format)
- **`GET /api/research/{session_id}/graph`**
- Returns nodes and edges formatted for React Flow with pre-computed `(x, y)` coordinates:
```json
{
  "nodes": [
    {
      "id": "node_topic_root",
      "type": "topic",
      "label": "best foods for healthy weight gain",
      "data": { "title": "best foods for healthy weight gain" },
      "position": { "x": 500.0, "y": 50.0 }
    },
    {
      "id": "node_uclm_1",
      "type": "claim",
      "label": "Protein consumption of 1.6-2.2 g/kg maximizes muscle growth",
      "data": { "confidence": 0.95, "sources_count": 3 },
      "position": { "x": 500.0, "y": 180.0 }
    }
  ],
  "edges": [
    {
      "id": "edge_src_1_uclm_1",
      "source": "node_src_1",
      "target": "node_uclm_1",
      "relationship": "cites",
      "label": "cites",
      "data": { "support": "direct" }
    }
  ]
}
```

### 6. Answer Follow-Up Questions (Vector RAG)
- **`POST /api/research/{session_id}/questions`**
- **Request Body**:
```json
{
  "question": "Which source disagreed with the others regarding surplus size?"
}
```
- **Response**:
```json
{
  "session_id": "rs_a4f9b8c21e",
  "question": "Which source disagreed with the others regarding surplus size?",
  "answer": "According to the research findings, medical guidelines recommend a controlled surplus of 300-500 kcal/day, whereas sports nutrition sources advocate larger surpluses exceeding 1000 kcal/day.",
  "cited_sources": [
    {
      "source_id": "src_1",
      "domain": "healthline.com",
      "url": "https://www.healthline.com/nutrition/18-foods-to-gain-weight"
    }
  ],
  "relevant_claims": [
    "A caloric surplus of 300 to 500 calories daily promotes lean tissue accumulation."
  ],
  "disagreements_or_nuances": "Disagreement between conservative clinical guidelines and aggressive athletic mass protocols."
}
```

---

## WebSocket Event Streaming

Clients connect to:
```text
ws://localhost:8000/ws/research/{session_id}
```

### Event Packet Schema

```json
{
  "type": "crawling",
  "session_id": "rs_a4f9b8c21e",
  "stage": "crawling",
  "message": "Crawling: https://www.healthline.com/nutrition/18-foods-to-gain-weight",
  "payload": {
    "completed": 3,
    "total": 8
  },
  "timestamp": 1726058000.123
}
```

### Supported Event Types

| Event Type | Stage | Description |
|---|---|---|
| `research_started` | `created` | Pipeline initialized and config confirmed |
| `queries_generated` | `generating_queries` | Sub-queries formulated by LLM |
| `search_started` | `searching` | Multi-engine concurrent searches underway |
| `sources_selected` | `selecting_sources` | Initial high-scoring sources filtered and chosen |
| `crawl_started` | `crawling` | Asynchronous queue crawling begins |
| `page_fetched` | `crawling` | Webpage fetched and text extracted |
| `article_analyzed` | `analyzing` | Structured claims, entities, and facts extracted by LLM |
| `knowledge_created`| `building_knowledge`| Source-level independent knowledge models created |
| `knowledge_merged` | `merging_knowledge` | Claims deduplicated and contradictions detected |
| `answer_generated` | `generating_answer` | Concise, source-aware research answer written |
| `completed` | `completed` | Pipeline complete with final answer and metrics |
| `error` | `failed` | Error information broadcast upon unrecoverable issue |

---

## Frontend Integration Examples

### 1. React / JavaScript WebSocket Usage

```javascript
import { useEffect, useState } from "react";

export function useResearchStream(sessionId) {
  const [events, setEvents] = useState([]);
  const [currentStage, setCurrentStage] = useState("created");
  const [finalAnswer, setFinalAnswer] = useState(null);

  useEffect(() => {
    if (!sessionId) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/research/${sessionId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents((prev) => [...prev, data]);
      setCurrentStage(data.stage);

      if (data.type === "completed") {
        setFinalAnswer(data.payload.final_answer);
      }
    };

    ws.onerror = (err) => console.error("WebSocket Error:", err);

    return () => ws.close();
  }, [sessionId]);

  return { events, currentStage, finalAnswer };
}
```

### 2. React Flow Knowledge Graph Rendering

```jsx
import React, { useEffect, useState } from 'react';
import ReactFlow, { Background, Controls } from 'reactflow';
import 'reactflow/dist/style.css';

export function ResearchGraph({ sessionId }) {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  useEffect(() => {
    fetch(`http://localhost:8000/api/research/${sessionId}/graph`)
      .then((res) => res.json())
      .then((data) => {
        setNodes(data.nodes);
        setEdges(data.edges);
      });
  }, [sessionId]);

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
```

---

## How to Add New Providers

### Adding an LLM Provider

1. Create a new file in `app/llm/my_provider.py` implementing `LLMProvider`:
```python
from app.llm.base import LLMProvider

class MyLLMProvider(LLMProvider):
    async def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        # Call provider API
        ...

    async def generate_structured(self, prompt: str, schema, system_prompt: str | None = None):
        # Call provider API with JSON schema enforcement
        ...

    async def generate_embedding(self, text: str) -> list[float]:
        # Return vector embedding (1536 float elements)
        ...
```
2. Register the provider in `app/llm/factory.py`.
3. Add configuration keys in `app/config.py`.

### Adding a Search Provider

1. Create a new file in `app/search/my_search.py` implementing `SearchEngine`:
```python
from app.search.base import SearchEngine
from app.schemas.search import SearchResult

class MySearch(SearchEngine):
    async def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        # Query provider API and return list of normalized SearchResult instances
        ...
```
2. Register the provider in `app/search/factory.py`.
3. Add configuration keys in `app/config.py`.

---

## License

MIT License. Designed for deep AI research and synthesis applications.
