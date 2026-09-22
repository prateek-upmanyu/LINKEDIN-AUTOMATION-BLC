import os
import requests
import json

token = 'IfwhI__dFlw9aanEGYQq1QpIq147g3pOUz4gqVhjuDq'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
url = 'https://api.buffer.com'

def query(q_str, variables=None):
    payload = {'query': q_str}
    if variables:
        payload['variables'] = variables
    r = requests.post(url, headers=headers, json=payload, timeout=15)
    return r.json()

mutation = '''
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess {
      post {
        id
        status
      }
    }
    ... on InvalidInputError {
      message
    }
    ... on UnexpectedError {
      message
    }
    ... on RestProxyError {
      message
    }
  }
}
'''

variables = {
  "input": {
    "channelId": "6ab2ba02ea19ca0bdeb83136",
    "text": "\"Make a customer, not a sale.\"\n— Katherine Barchetti\n\n#Sales #ColdCalling #LeadGeneration #BulkLeadsCaller #SalesMotivation #BusinessGrowth",
    "mode": "shareNow",
    "schedulingType": "automatic",
    "assets": [
      {
        "image": {
          "url": "https://files.catbox.moe/6qhxep.png"
        }
      }
    ]
  }
}

print("--- Testing Buffer createPost Mutation ---")
res = query(mutation, variables)
print(json.dumps(res, indent=2))
