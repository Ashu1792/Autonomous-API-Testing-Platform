import requests

def validate_contract():

    url = "https://jsonplaceholder.typicode.com/posts/1"

    expected = ["userId","id","title","body"]

    try:

        response = requests.get(url)
        data = response.json()

        for field in expected:
            if field not in data:
                return False

        return True

    except:
        return False