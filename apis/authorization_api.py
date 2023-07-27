import os
from dotenv import load_dotenv
from urllib.parse import urlencode
import streamlit as st
import base64
import requests
import time

def load_environment_variables():
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    redirect_uri = os.getenv("REDIRECT_URI")
    scope = os.getenv("SCOPE")
    auth_url = os.getenv("AUTH_URL")
    token_url = os.getenv("TOKEN_URL")
    return client_id, client_secret, redirect_uri, scope, auth_url, token_url

class AuthorizationAPI(object):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        client_id, client_secret, redirect_uri, scope, auth_url, token_url = load_environment_variables()
        self.code = None
        self.access_token = None
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.auth_url = auth_url
        self.token_url = token_url
    
    def get_authorization_url(self):
        auth_headers = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope
        }
        authorization_url = self.auth_url + urlencode(auth_headers)
        return authorization_url
    
    def _get_authorization_code(self):
        query_params = st.experimental_get_query_params()
        while len(query_params) == 0:
            time.sleep(1)
            query_params = st.experimental_get_query_params()
        self.code = query_params['code'][0]
    
    def _get_access_token(self):
        if not self.code:
            raise Exception("No access code")
        encoded_credentials = base64.b64encode(self.client_id.encode() + b':' + self.client_secret.encode()).decode("utf-8")
        token_headers = {
            "Authorization": "Basic " + encoded_credentials,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        token_data = {
            "grant_type": "authorization_code",
            "code": self.code,
            "redirect_uri": self.redirect_uri
        }
        r = requests.post(self.token_url, data=token_data, headers=token_headers)
        access_token = r.json()['access_token']
        self.access_token = access_token
    
    def authorize(self):
        try:
            self._get_authorization_code()
            self._get_access_token()
            return self.access_token
        except:
            print("Error occured during authorization")






    
