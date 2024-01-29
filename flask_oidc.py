# -*- coding: UTF-8 -*-
from flask import Flask, render_template, redirect, url_for, request
from googleapiclient.discovery import build
from google.oauth2 import id_token
from google.auth.transport.requests import Request
import flask
import google.oauth2.credentials
import google_auth_oauthlib.flow
import json

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

app = Flask(__name__)
app.config['PREFERRED_URL_SCHEME'] = 'https'
flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/drive.readonly', 'openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'])
flow.redirect_uri = 'https://free5gmanowebui.nutc-imac.com/callback'
authorization_url, state = flow.authorization_url(
    access_type='offline',
    include_granted_scopes='true')

@app.route('/')
def index():
    url = url_for("index", _external=True, _scheme='https')
    return render_template('index.html', url=url)
    

@app.route('/login', methods=['POST'])
def login():
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    print("--------request------------")
    print(request.url)
    print(request.args)
    auth_code = request.args.get('code')
    state = request.args.get('state')
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/drive.readonly', 'openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
        state=state)
    flow.redirect_uri = flask.url_for('callback', _external=True, _scheme='https')

    print(flow.redirect_uri)
    
    authorization_response = flask.request.url.replace("http://", "https://")
    print(authorization_response)
    flow.fetch_token(authorization_response=authorization_response)


    credentials = flow.credentials
    print("--------access_token---------")
    access_token = credentials.token
    print(access_token)
    print("----credentials--------")
    print(credentials.to_json)
    id_info = id_token.verify_oauth2_token(credentials.id_token, Request(), credentials.client_id)

    print(id_info)
    print(id_info['email'])

    print("--------drive------------")
    credentials = flow.credentials
    drive_service = build('drive', 'v3', credentials=credentials)
    results = drive_service.files().list(
        pageSize=10,
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()
    items = results.get('files', [])
    print(json.dumps(id_info, indent=4))
    if not items:
        return 'No files found.'
    else:
        # 顯示 Google Drive 檔案列表
        return render_template('files.html', files=items, userinfo=json.dumps(id_info, indent=4, ensure_ascii=False), access_token=access_token)

    return render_template('callback.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
