import requests

def upload(file_instance):
    response = requests.post('http://localhost:8000/', files={'attachment': file_instance})
    return response.content
