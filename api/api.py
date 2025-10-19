import requests

rootUrl = "http://localhost:3001/api"

def updateEpisodeStatus(state):
    """    
    Args:
        state (str): Episode status
            "queue", "processing", "finished", "error"
    """
    url = f"{rootUrl}/updateStatus"
    data = {"status": state}
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error updating episode status: {e}")
        return None


def addUploadedEpisole(data):
    url = f"{rootUrl}/addUploadedEpisole"
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error adding uploaded episode: {e}")
        return None


def getQueuedArticle():
    url = f"{rootUrl}/getQueuedArticle"
    
    try:
        response = requests.post(url, data={})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting queued article: {e}")
        return None