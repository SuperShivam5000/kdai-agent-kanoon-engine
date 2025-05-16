import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from ikapi import IKApi, FileStorage
import argparse
from cleaners import clean_search_query_response, clean_search_document_response

# Set up simulated argparse args
args = argparse.Namespace(
    token=os.getenv("INDIAN_KANOON_API_KEY"),
    datadir="./data",
    maxcites=0,
    maxcitedby=0,
    orig=False,
    maxpages=1,
    pathbysrc=False,
    numworkers=1,
    addedtoday=False,
    fromdate=None,
    todate=None,
    sortby=None
)

# Initialize storage and IKApi client
storage = FileStorage(args.datadir)
ikapi_client = IKApi(args, storage)

app = FastAPI()

# Enable CORS for all origins and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class SearchQueryRequest(BaseModel):
    query: str
    pageNo: int

class SearchDocumentRequest(BaseModel):
    documentID: str

@app.get("/")
def root():
    return {"message": "Kanoon Engine is awake!"}

@app.post("/searchQuery")
def search_query(req: SearchQueryRequest):
    try:
        result = ikapi_client.search(req.query, req.pageNo, args.maxpages)
        return clean_search_query_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/searchDocument")
def search_document(req: SearchDocumentRequest):
    try:
        result = ikapi_client.fetch_doc(int(req.documentID))
        return clean_search_document_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
