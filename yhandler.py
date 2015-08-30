import requests
from requests_oauthlib import OAuth1
from requests import request
from urlparse import parse_qs
import webbrowser
import csv
import pdb

GET_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_token'
AUTHORIZATION_URL = 'https://api.login.yahoo.com/oauth/v2/request_auth'
REQUEST_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
QUERY_URL = 'http://fantasysports.yahooapis.com/fantasy/v2/'
CALLBACK_URL = 'oob'

class YHandler(object):

    def __init__(self, authf):
        self.authf = authf
        self.authd = self.get_authvals_csv(self.authf)
        self.authd['callback_uri'] = CALLBACK_URL
		
	#  return a dict copy containing only the keys passed in via args
    def subdict(self, *args):
        return dict((k, self.authd[k]) for k in args if k in self.authd)
        
    def get_authvals_csv(self, authf):
		vals = {}	#dict of vals to be returned
		with open(authf, 'rb') as f:
			f_iter = csv.DictReader(f)
			vals = f_iter.next()
		return vals
		
    def write_authvals_csv(self, authd, authf):
        f = open(authf, 'wb')
        fieldnames = tuple(authd.iterkeys())
        headers = dict((n,n) for n in fieldnames)
        f_iter = csv.DictWriter(f, fieldnames=fieldnames)
        f_iter.writerow(headers)
        f_iter.writerow(authd)
        f.close
        
    def reg_user(self):
        
        # Set up Oauth session to generate request token
        oauth = OAuth1(**self.subdict('client_key', 'client_secret', 'callback_uri'))
        
        # Get request token
        response = requests.post(url=REQUEST_TOKEN_URL, auth=oauth)
        qs = parse_qs(response.text)
        self.authd['resource_owner_key']= (qs['oauth_token'][0])
        self.authd['resource_owner_secret'] = (qs['oauth_token_secret'][0])
        
        # Send user to approve app
        print ''
        print 'You will now be directed to a website for authorization.'
        print 'Please authorize the app, and then copy and paste the provide PIN below.'
        print ''
        webbrowser.open("%s?oauth_token=%s" % (AUTHORIZATION_URL, self.authd['resource_owner_key']))
        self.authd['verifier'] = raw_input('Please enter your PIN:')

        # Get authorization token
        self.get_final_token()
        
    def get_final_token(self, refresh=False):
        
        # Set up an Oauth session to get authorization token
        oa_kwargs = self.subdict('client_key', 'client_secret', 'resource_owner_key', 'resource_owner_secret')
        if not refresh:
            oa_kwargs['verifier'] = self.authd['verifier']
        oauth = OAuth1(**oa_kwargs)
        
        # Get authorization token
        response = requests.post(url=GET_TOKEN_URL, auth=oauth)
        cred = parse_qs(response.content)
        
        # Save credentials from authorization token
        self.save_credentials(cred)
        
        # Return authorization request response
        return response
        
    def save_credentials(self, cred):
    
        # Extract credentials from token
        self.authd['resource_owner_key'] = cred['oauth_token'][0]
        self.authd['resource_owner_secret'] = cred['oauth_token_secret'][0]
        for k in ['xoauth_yahoo_guid','oauth_expires_in','oauth_session_handle','oauth_authorization_expires_in']:
            self.authd[k] = cred[k][0]
        
        # Write credentials to authorization file    
        self.write_authvals_csv(self.authd, self.authf)
        
    def call_api(self, url, req_meth='GET', data=None, headers=None):
        oauth = OAuth1(**self.subdict('client_key', 'client_secret', 'resource_owner_key', 'resource_owner_secret'))
        return requests.request(method=req_meth, url=url, auth=oauth, data=data, headers=headers)

    def api_req(self, querystring, req_meth='GET', data=None, headers=None):
        url = QUERY_URL+querystring
        if ('resource_owner_key' not in self.authd) or ('resource_owner_secret' not in self.authd) or (not (self.authd['resource_owner_key'] and self.authd['resource_owner_secret'])):
            self.reg_user()
        query = self.call_api(url, req_meth, data=data, headers=headers)
        
        #  possible token expiration
        if query.status_code != 200: 
            self.get_final_token(refresh=True)
            query = self.call_api(url, req_meth, data=data, headers=headers)
        
        return query