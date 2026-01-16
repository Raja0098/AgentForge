AgentForge is a **full-stack AI workflow platform** consisting of:

### 🧠 Frontend (No-Code Visual Builder)
- Visual **workflow canvas** with auto-connected nodes
- Drag-and-add **agents and tools**
- Clear **input → processing → output** flow
- Real-time execution results and logs
- Workflow saving and loading

### ⚙️ Backend (Agent Execution Engine)
- DAG-based workflow execution engine
- Pluggable **agent + tool architecture**
- Safe execution with **guardrails**
- Modular design to add new agents/tools easily

---

## 🧩 Core Concepts

### Nodes
Each workflow is composed of nodes:

- **Input Node** – text, URL, or file (PDF/Image)
- **Agents**
  - LLM Agent
  - LLM with Tools (ReAct)
  - Summarizer
  - Guardrail (Safety)
- **Tools**
  - Web Search
  - Document Extractor
- **Output Node** – final result display

### Connections
- Nodes are connected **sequentially**
- Execution follows a **topological (DAG) order**
- Cycles are automatically rejected

---

## 🛠 Tools & Models Used

### 🔤 Language Model
- **Google Gemini** (via API)
  - Text generation
  - Reasoning
  - Tool-augmented responses

### 🔍 Tools
- **Web Search**  
  - Powered by DuckDuckGo
- **Document Extraction**  
  - PDFs & Images using Docling

### 🖥 Frontend
- Vue 3 (Composition API)
- Vuex for state management
- SVG-based workflow connections
- Pure CSS (no UI framework)

### 🔧 Backend
- FastAPI
- Pydantic
- Async execution engine
- Modular agent registry



## 🏗️ Architecture Overview

```mermaid

%%{init: {
  'themeVariables': {
    'fontSize': '16px',
    'edgeLabelBackground':'#fff',
    'fontFamily': 'Segoe UI, Arial',
    'clusterBorder': '#bbb',
    'primaryColor': '#F5F7FA'
  },
  'flowchart': { 
    'htmlLabels': true,
    'curve': 'monotoneX'
  }
}}%%
flowchart LR

%% =========== FRONTEND =============
subgraph FE["🖥️ **Frontend (Vue.js No-Code Builder)**"]
  direction TB
  NP["Node Panel\n*Drag/Drop Agents, Tools, Inputs*"]
  CANVAS["Workflow Canvas\n*Main visual editing area*"]
  EXEC["Execution Panel\n*Run, View Results & Logs*"]
  WM["Workflow Manager\n*Save, Load, Share*"]
end
classDef front fill:#DFE8FB,stroke:#2563eb,stroke-width:2px;
class NP,CANVAS,EXEC,WM front;

%% =========== BACKEND =============
subgraph BE["🛡️ **Backend (FastAPI)**"]
  direction TB
  API["FastAPI Application\n*REST interface, Auth, Validation*"]
  REG["Node Registry\n*Central Node Definitions*"]
  ENG["Workflow Engine\n*Execution logic, DAG processing*"]
end
classDef back fill:#FDE68A,stroke:#B45309,stroke-width:2px;
class API,REG,ENG back;

%% =========== CORE =============
subgraph CORE["⚙️ **Execution Core**"]
  direction TB
    INPUT["Input Node\n*Receives user/input data*"]
    AGENTS["AI Agents\n*LLM/ Summarizer/ Guardrail*"]
    TOOLS["Tools\n*Web Search/ Doc Extractor*"]
    OUTPUT["Output Node\n*Final output/ results*"]
end
classDef core fill:#DEF7EC,stroke:#10B981,stroke-width:2px;
class INPUT,AGENTS,TOOLS,OUTPUT core;

%% =========== EXTERNAL SERVICES =============
subgraph EXT["🌐 **External Services**"]
  direction TB
  LLM["Gemini, OpenAI, etc.\n*LLM API*"]
  WEB["DuckDuckGo\n*Web search*"]
  DOC["Docling\n*PDF/Image/Text Extraction*"]
end
classDef ext fill:#FECACA,stroke:#DC2626,stroke-width:2px;
class LLM,WEB,DOC ext;

%% =========== DATA FLOW =============

%% User flow
NP -- "Drag node" --> CANVAS
CANVAS -- "Edit, arrange" --> EXEC
WM -- "Save/Load" --> CANVAS

%% API flow
EXEC -- "POST /api/execute\n(run workflow)" --> API
CANVAS -- "GET /api/nodes\n(fetch nodes)" --> API
WM -- "POST /api/workflow\n(save/load workflow)" --> API

%% Backend logic
API -- "Node type/schema request" --> REG
API -- "Execute workflow" --> ENG

%% Internal workflow processing
ENG --> INPUT
INPUT -- "User/Input data" --> AGENTS
AGENTS -- "LLM call, summarization/guardrail" --> TOOLS
TOOLS -- "Tool result\n(Web search, doc extract)" --> AGENTS
AGENTS -- "Processed output" --> OUTPUT

%% External calls
AGENTS -- "Prompt & API call" --> LLM
TOOLS -- "Web query" --> WEB
TOOLS -- "Document ingest" --> DOC

%% Result returns
OUTPUT -- "Results & logs" --> EXEC

%% Borders for clarity
FE -.->|UI/API Integration| BE
BE -.->|Job Execution| CORE
CORE -.->|External API/Service Calls| EXT

%% =========== LEGEND ==============
%% Optional: A legend can be provided for managers

%% Use comment blocks to keep them visually out of main graph
%% You may uncomment the below legend and adjust style if you want it in-diagram

%% subgraph LEGEND["Legend"]
%%   LUI((UI Node)):::front
%%   LSU((Server Node)):::back
%%   LCORE((Core Logic)):::core
%%   LEXT((External API)):::ext
%%   LAPI("API Route")--->LUI
%% end

%% Notes:
%% - Hover for tooltips (if supported by your viewer)
%% - Color = domain; shape = function (card = UI, rectangle = service, circle = external API, parallelogram = I/O)



## 🚦 Current Status

-  Core workflow engine implemented - done
-  Visual canvas UI - done
-  Agents and tools integrated - done
-  File uploads supported - done
-  More tools and more agents 
-  Database persistence (SQLite + SQLAlchemy)
-  User authentication
-  Workflow export/import
-  Cloud deployment support
