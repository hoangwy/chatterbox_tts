import requests
import os
from typing import Optional, Dict, Any
from pathlib import Path
from . import api

rootUrl = "https://open.acast.com/rest"
apiKey = None

def getHeaders() -> dict:
    """Get headers with global API key"""
    return {
        "X-API-Key": apiKey,
        "User-Agent": "DNN-Publishing/1.0"
    }

def uploadToAcast(
    audioPath: str,
    showId: str = None,
    title: str = None,
    subtitle: str = None,
    summary: str = None
) -> Dict[str, Any]:

    if not showId:
        showId = os.getenv('ACAST_SHOW_ID')
        if not showId:
            raise ValueError("showId must be provided or set in ACAST_SHOW_ID environment variable")
    
    # Prepare episode data
    episode_data = {
        'title': title,
        'status': 'draft'  # Start as draft
    }
    
    if subtitle:
        episode_data['subtitle'] = subtitle
    if summary:
        episode_data['summary'] = summary
    
    # Set API key if not already set
    global apiKey
    if not apiKey:
        apiKey = os.getenv('ACAST_API_KEY')
        if not apiKey:
            raise ValueError("ACAST_API_KEY environment variable must be set")
    
    print(f"[ACAST] Uploading audio to Acast: {audioPath}")
    
    try:
        episode = createEpisode(showId, episode_data, audioPath)
        print(f"[ACAST] Successfully uploaded to Acast: {episode.get('id', 'Unknown ID')}")
        return episode
    except Exception as e:
        print(f"[ACAST] Failed to upload to Acast: {e}")
        raise


def createEpisode(
    showId: str,
    data: dict,
    audioPath: str
) -> Dict[str, Any]:
 
    url = f"{rootUrl}/shows/{showId}/episodes"
    
    # Prepare form data
    form_data = {}
    
    # Add episode data to form_data
    if data.get('title'):
        form_data['title'] = data['title']
    if data.get('subtitle'):
        form_data['subtitle'] = data['subtitle']
    if data.get('summary'):
        form_data['summary'] = data['summary']
    if data.get('alias'):
        form_data['alias'] = data['alias']
    if data.get('link'):
        form_data['link'] = data['link']
    if data.get('publishDate'):
        form_data['publishDate'] = data['publishDate']
    if data.get('season') is not None:
        form_data['season'] = str(data['season'])
    if data.get('episodeNumber') is not None:
        form_data['episodeNumber'] = str(data['episodeNumber'])
    if data.get('type'):
        form_data['type'] = data['type']
    if data.get('explicit') is not None:
        form_data['explicit'] = str(data['explicit'])
    if data.get('duration') is not None:
        form_data['duration'] = str(data['duration'])
    if data.get('status'):
        form_data['status'] = data['status']
    if data.get('markers'):
        form_data['markers'] = str(data['markers']) 
        
    if audioPath and os.path.exists(audioPath):
        with open(audioPath, 'rb') as f:
            form_data['audio'] = f.read()
    
    hardcoded_files = {
        'cover': 'cover.jpg',
        'privateIntro': 'private-intro.mp3',
        'privateOutro': 'private-outro.mp3',
        'publicIntro': 'public-intro.mp3',
        'publicOutro': 'public-outro.mp3'
    }
    
    for key, file_path in hardcoded_files.items():
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                form_data[key] = f.read()
    
    try:
        for key, value in form_data.items():
            print(f"  {key}: {value}")
        
        response = requests.post(
            url,
            data=form_data,
            headers=getHeaders(apiKey)
        )
        
        if not response.ok:
            print(f"Acast API Response Status: {response.status_code}")
            print(f"Acast API Response Headers: {dict(response.headers)}")
            print(f"Acast API Response Body: {response.text}")
            
            error_message = f"Failed to create episode: {response.status_code} {response.reason}"
            
            try:
                error_data = response.json()
                if error_data.get('message'):
                    error_message = error_data['message']
            except:
                if response.text:
                    error_message = response.text
            
            raise Exception(error_message)
        
        episode = response.json()
        
        api.updateEpisodeStatus("1")
        api.addUploadedEpisole({})
        
        # Delete audio file if response is successful
        if audioPath and os.path.exists(audioPath):
            try:
                os.remove(audioPath)
                print(f"Deleted audio file: {audioPath}")
            except Exception as e:
                print(f"Failed to delete audio file {audioPath}: {e}")
        
        return episode
        
    except requests.exceptions.RequestException as e:
        api.updateEpisodeStatus("2")
        raise Exception(f"Network error creating episode: {str(e)}")
