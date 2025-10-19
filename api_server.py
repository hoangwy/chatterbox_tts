#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException
import requests
import os

# Create FastAPI app
app = FastAPI(title="Chatterbox API Service", version="1.0")

# API Configuration
rootUrl = "http://209.38.74.62:3001/api"
API_TOKEN = "EhrPbyW4xyFA"

def get_headers():
    """Get headers with Bearer token"""
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

@app.get("/")
def root():
    return {
        "status": "ok", 
        "message": "Chatterbox API Service running",
        "version": "1.0"
    }

@app.post("/updateStatus")
async def update_episode_status(request: dict):
    """Update episode status"""
    state = request.get("status")
    if not state:
        raise HTTPException(status_code=400, detail="status field is required")
    
    url = f"{rootUrl}/updateStatus"
    data = {"status": state}
    
    try:
        response = requests.post(url, json=data, headers=get_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error updating episode status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update episode status: {str(e)}")

@app.post("/addUploadedEpisole")
async def add_uploaded_episode(request: dict):
    """Add uploaded episode"""
    url = f"{rootUrl}/addUploadedEpisole"
    
    try:
        response = requests.post(url, json=request, headers=get_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error adding uploaded episode: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add uploaded episode: {str(e)}")

@app.post("/getQueuedArticle")
async def get_queued_article():
    """Get a queued article from the external API"""
    url = f"{rootUrl}/getQueuedArticle"
    
    try:
        response = requests.post(url, json={}, headers=get_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting queued article: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get queued article: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3003)
