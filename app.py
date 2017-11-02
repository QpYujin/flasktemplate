
from flask import Flask
from flask_api import FlaskAPI
import requests
import json


app = FlaskAPI(__name__)
headers = {
    'Authorization': 'Bearer **********',
}

res = requests.get('************',verify=False, headers=headers)
health_res = requests.get('************',verify=False, headers=headers)

hel_d = str(health_res.text)



n = json.loads(res.text)


headers = {
    'Content-type': 'application/json',
}


data = {}


@app.route("/status", methods=['GET'])
def status():
    for key, value in n.items():
      if key == 'items':
          na = value
          for key, value in na[0].items():
              if key == 'status':
                 nastatus = value
                 for key, value in nastatus.items():
                     if key == 'phase':
                      data['text']=unicode(value)


    dt = json.dumps(data)

    req = requests.post('https://***********************', headers=headers, data=dt)
    return ('', 204)    


# Health Check
@app.route("/healthz", methods=['GET'])
def health():

    data['text']=hel_d

    dt = json.dumps(data)

    req = requests.post('*************************', headers=headers, data=dt)
    return ('', 204)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
