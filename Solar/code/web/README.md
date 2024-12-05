# Solar-Web

## Main Components:

#### Frontend: streamlit.py (implemented with Streamlit)

Prerequisites:

- Python 3.8 or later installed
- Install the necessary dependencies:
  - You can create a virtual environment (optional but recommended):
  
    python -m venv venv
    source venv/bin/activate #Linux/macOS
    venv\Scripts\activate #Windows

  - Install the required packages by running:

    - pip install streamlit: To work with streamlit
    - pip install PyPDF2: to work with PDF files
    - pip install pymupdf: Also known as fitz, it is for manipulating PDF files and documents
    - pip install requests: To make HTTP requests

    **The modules io, tempfile, os, time, and json are standard Python modules and do not require additional installation**
      - time: allows working with time-related functions
      - os: provides an interface to interact with the operating system, e.g., working with files and directories, querying environment variables, or executing system commands.
      - json: to work with data in JSON format.
      - io: to work with data streams. It is used to read and write data in memory rather than physical files.
      - tempfile: to create temporary files or directories that are automatically deleted when the program ends or can also be manually removed.
#### STEP 1: Run grobid

1. Navigate to the directory where your grobid folder is located.
2. Run grobid using the following command:

  ./gradlew run

#### STEP 2: Run the backend (FastAPI)

1. Navigate to the directory where the cli.py file is located.
2. Run the backend using the following command:

  uvicorn cli:app --reload

This will start a FastAPI server accessible from http://127.0.0.1:8000

#### STEP 3: Run the frontend (Streamlit)

1. In another terminal, ensure you are in the same environment where the dependencies were installed.
2. Navigate to the directory where the streamlit.py file is located.
3. Run the frontend with:

