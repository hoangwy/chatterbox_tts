import requests

rootUrl = "https://localhost/v1"

def updateEpisodeStatus(state):
    """
    Update the status of an episode.
    
    Args:
        state (str): Episode status
            "0": processing
            "1": finish
            "2": error
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
    """
    Add an uploaded episode.
    
    Args:
        data: Episode data to upload
    """
    url = f"{rootUrl}/addUploadedEpisole"
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error adding uploaded episode: {e}")
        return None