import requests

rootUrl = "http://143.198.100.198:3003/api"
API_TOKEN = "EhrPbyW4xyFA"

def get_headers():
    """Get headers with Bearer token"""
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

def updateEpisodeStatus(state):
    """    
    Args:
        state (str): Episode status
            "queue", "processing", "finished", "error"
    """
    url = f"{rootUrl}/updateStatus"
    data = {"status": state}
    
    try:
        response = requests.post(url, json=data, headers=get_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error updating episode status: {e}")
        return None


def addUploadedEpisole(data):
    url = f"{rootUrl}/addUploadedEpisole"
    
    try:
        response = requests.post(url, json=data, headers=get_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error adding uploaded episode: {e}")
        return None


def getQueuedArticle():
    url = f"{rootUrl}/getQueuedArticle"
    
    try:
        response = requests.post(url, json={}, headers=get_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting queued article: {e}")
        return None