import os
from flask import Flask, render_template, request, jsonify
import requests
import urllib.parse
import warnings

app = Flask(__name__)
warnings.filterwarnings('ignore')

CLIENT_ID = "100067"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"

def inspect_token_logic(token):
    url = f"https://100067.connect.garena.com/oauth/token/inspect?token={token}"
    try:
        res = requests.get(url, headers={'ReleaseVersion': 'OB52'}, verify=False, timeout=10)
        if res.status_code == 200:
            data = res.json()
            return {
                "status": "success",
                "uid": data.get('uid') or data.get('open_id'),
                "nickname": data.get('nickname', 'N/A'),
                "platform": data.get('platform', 'Garena'),
                "token": token
            }
    except:
        pass
    return {"status": "error", "message": "Invalid or Expired Token"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    mode = request.json.get('mode')
    
    if mode == 'id_pass':
        uid = request.json.get('uid')
        pw = request.json.get('password')
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        payload = {'uid': uid, 'password': pw, 'response_type': "token", 'client_type': "2", 'client_secret': CLIENT_SECRET, 'client_id': CLIENT_ID}
        res = requests.post(url, data=payload, verify=False).json()
        if 'access_token' in res:
            return jsonify(inspect_token_logic(res['access_token']))
        return jsonify({"status": "error", "message": res.get('error_description', 'Login Failed')})

    elif mode == 'eat_url':
        input_data = request.json.get('data')
        eat_token = input_data
        if 'http' in input_data:
            parsed = urllib.parse.urlparse(input_data)
            params = urllib.parse.parse_qs(parsed.query)
            eat_token = params.get('eat', [None])[0] or params.get('access_token', [None])[0]
        
        if not eat_token: return jsonify({"status": "error", "message": "Invalid EAT/URL"})
        
        try:
            res = requests.get(f"https://api-otrss.garena.com/support/callback/?access_token={eat_token}", allow_redirects=True, verify=False, timeout=15)
            parsed_res = urllib.parse.urlparse(res.url)
            at = urllib.parse.parse_qs(parsed_res.query).get('access_token', [None])[0]
            if at: return jsonify(inspect_token_logic(at))
        except: pass
        return jsonify({"status": "error", "message": "Conversion Failed"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
