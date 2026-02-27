##  Project Overview & Problem Statement

### The Problem
Traditional resume screening relies on **keyword matching** (e.g., searching for "Python"). However, this often fails because:
- Candidates use synonyms or different phrasing (e.g., "Scripting Expert" vs "Python Developer").
- Recruiters have to manually read hundreds of PDFs to find "closeness" to a role.
- Standard databases aren't designed to measure "semantic meaning."

### The Solution
The **AI Resume Matcher** uses **Vector Embeddings** to translate human language into coordinates in a high-dimensional space. By using **Endee** as our high-performance vector database, we can instantly calculate the mathematical similarity between a job's requirements and a candidate's skills, ensuring the most qualified people are found instantly—even if they used different words.

---

## System Design & Technical Approach

This project follows a modern **Vector Search Architecture**. We use a specialized AI model to process text and the Endee engine to handle the heavy mathematical lifting.

```mermaid
graph TD
    subgraph "1. Data Ingestion"
        A[Resume PDF] -->|pypdf| B(Raw Text)
        B -->|all-MiniLM-L6-v2| C[384D Vector Embedding]
    end

    subgraph "2. Storage (Endee)"
        C -->|POST /vector/insert| D[(Endee Vector DB)]
    end

    subgraph "3. Retrieval"
        E[Job Description] -->|all-MiniLM-L6-v2| F[Query Vector]
        F -->|POST /search| D
        D -->|Cosine Similarity| G[Ranked Matches]
    end

    G -->|JSON| H[Dashboard UI]
```

### 🗺️ How it Works (Architecture Flow)

```text
[Resume PDF] -> (pypdf) -> [Text] \
                                   -> (sentence-transformers) -> [Vector 384D] -> [Endee Vector DB]
                                                                                            |
[Job Description] -> (sentence-transformers) -> [Query Vector 384D] ----------------> (Match/Similarity Search)
                                                                                            |
                                                                                    [Ranked Resumes]
```

### Technical Stack:
- **Database:** Endee (High-performance C++ Vector DB)
- **Backend:** FastAPI (Python)
- **AI Model:** Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Frontend:** Vanilla JS, CSS (Glassmorphism Dark Theme)

---

## 🏗️ How Endee is Used

Think of **Endee** as the high-speed "Brain" of this project. While a normal database looks for exact words, Endee understands the **meaning** of the text.

### 1. The Setup (Indexing)
When the app starts, it tells Endee to set up a specialized "Comparison Room" (Index). This room is configured to understand 384 different types of skills for every resume we upload.

### 2. Saving Candidates (Insertion)
When you upload a PDF, the AI turns the text into a long list of numbers called a **Vector**. We send this list to Endee, which stores it in its high-speed memory so it can be searched in milliseconds.

**API Endpoint:** `POST /api/v1/index/{index_name}/vector/insert`  
*Payload:* `[{"id": "resume_1", "vector": [...], "meta": "{...}"}]`

### 3. Finding the Best Match (Search)
When you type a Job Description, Endee calculates the "mathematical angle" between your requirement and every resume it has stored. 

Even if a resume doesn't use the exact same words, if the **meaning** matches, Endee finds it! It returns the best candidates ranked by a **Similarity Score**.

**API Endpoint:** `POST /api/v1/index/{index_name}/search`  
*Payload:* `{"vector": [...], "k": 5}`

## 🚀 Quick Step-by-Step Guide to Run

Follow these simple steps from your terminal to run the software on your own computer:

### Step 1: Start the Database (Endee)
Open your terminal in the main `endee` repository folder and run:
```bash
docker compose up -d
```
*(This starts the Endee database silently in the background.)*

### Step 2: Start the Python App
Open a terminal inside the `resume-matcher` folder and run these commands to install dependencies and start the web server:
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --port 8000
```

### Step 3: Open the Dashboard!
Open your web browser and click this link:  
👉 **[http://localhost:8000/](http://localhost:8000/)**

You will see the shiny new user interface. You can drag and drop your PDFs inside, type a job requirement, and click search!

---

## 📸 Sample Output and Demo Video

Here is a video demonstration of the project in action:


[![Watch Demo](assets/thumbnail.png)](https://drive.google.com/file/d/1j9ESxL590447c3mFbRnzFXVTeebn84Vi/view?usp=sharing)

---

### Sample API Output (`/match` endpoint internally):
When the frontend searches for a candidate, the backend returns this clean JSON structure directly to the UI containing the matched Resumes ranked entirely by Semantic AI!

```json
{
  "job_description_snippet": "Looking for an experienced Python developer familiar with FastAPI...",
  "matches": [
    {
      "id": "c7de902d-c141-4762-8b6a-317f3faf0fc9",
      "similarity_score": 0.9818479623645544,
      "metadata": {
        "filename": "sample_resume.pdf",
        "text_snippet": "Markandey Krishna Mishra. Senior Python Engineer. Experience with FastAPI and Vector Databases like Endee...."
      }
    }
  ]
}
```
