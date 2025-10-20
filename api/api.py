import requests

rootUrl = "http://143.198.100.198:3003/api"
API_TOKEN = "EhrPbyW4xyFA"

def get_headers():
    """Get headers with Bearer token"""
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

def updateEpisodeStatus(state, id, fileName=None, acastUploaded=None, errorCode=None, errorMsg=None):
    """    
    Args:
        state (str): Episode status
            "queue", "processing", "finished", "error"
        id (str): Episode ID (required)
        fileName (str, optional): Name of the generated audio file
        acastUploaded (bool, optional): Whether the file was successfully uploaded to Acast
        errorCode (str, optional): Error code if status is "error"
        errorMsg (str, optional): Error message if status is "error"
    """
    url = f"{rootUrl}/updateArticleQueueStatus"
    data = {
        "status": state,
        "id": id
    }
    
    if fileName is not None:
        data["fileName"] = fileName
    if acastUploaded is not None:
        data["acastUploaded"] = acastUploaded
    if errorCode is not None:
        data["errorCode"] = errorCode
    if errorMsg is not None:
        data["errorMsg"] = errorMsg
    
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