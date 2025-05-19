# 🔧 Code Comparison – Technical Specification

## 🌍 Live Deployment

The application is publicly accessible at:

👉 https://cs.taltech.ee/services/codecomparison/

This version is deployed to a TalTech server. It provides access to the web interface that in turn provides access to the backend service for comparing Python code solutions.

## 🚀 Local Development

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Git

### Backend Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables.

5. Start the backend server:

```bash
python backend/app.py
```

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
# or
yarn install
```

3. Start the development server:

```bash
npm start
# or
yarn start
```

The application will be available at `http://localhost:3000`

## 🔌 API Documentation

### Endpoints

#### `POST /api/diff`

Compares student and teacher Python code by analyzing their Abstract Syntax Trees (AST).

**Request body:**

```json
{
  "student_id": "string",  // Student identifier
  "exercise": "string",    // Exercise code (e.g., "EX02")
  "year": "string",        // Academic year (e.g., "2024")
  "use_llm": boolean      // Whether to include AI analysis
}
```

**Response:**

```json
{
  "message": "ok",
  "differences": {
    "module_specific_diffs": {
      "function_mismatch": string[]
    },
    "function_specific_diffs": {
      "filename": {
        "function_name": {
          "strict_comparison": string[],
          "unifiedDSL": string,
          "structural_error": string,
          "unified_diff": string
        }
      }
    }
  },
  "conclusion": string,    // AI analysis conclusion
  "llm_model": string,     // Model used for analysis
  "diff_error": string,    // Error in code comparison
  "llm_error": string      // Error in AI analysis
}
```

## 🏗️ Project Architecture

### Frontend

- React with TypeScript
- Taltech Styleguide for UI components
- Key components:
  - `CompareCode`: Main comparison interface
  - `DiffView`: Code difference visualization
  - `FlowchartComparison`: Structural comparison view
  - `AnalysisConclusion`: AI analysis display

### Backend

- Python Flask server
- Key modules:
  - `strict_comparison.py`: AST-based code comparison
  - `structural_comparison.py`: Flowchart-based comparison
  - `openai_client.py`: AI analysis integration
  - `gitlab_client.py`: Code retrieval from GitLab
