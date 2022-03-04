import json
import requests

def create_header():
    with open('./.twitter_cred.json') as f:
        data = json.load(f)

        bearer = data["bearer_token"]
        headers = {
            'Authorization': 'Bearer '+bearer,
            'User-Agent': 'v2RecentSearchPython'
        }
        
        return headers


def get_tweet(category):
    query_params = {
        "query": category + " -is:retweet -has:images lang:en",
    }

    response = requests.get("https://api.twitter.com/2/tweets/search/recent", params=query_params, headers=create_header())

    if (response.status_code != 200):
        print("Error: status code not 200")
        print(response)
        print()
        print(query_params)
        print()
        raise

    print(response.text)

    # ...

    return response.json()

res = get_tweet("love")
print('\n', res['data'][0])
