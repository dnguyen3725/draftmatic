import requests
from oauth_hook import OAuthHook
from requests import request
from urlparse import parse_qs
import webbrowser
import csv
import pdb

GET_TOKEN_URL = 'https://api.login.yahoo.com/oauth2/get_token'
AUTHORIZATION_URL = 'https://api.login.yahoo.com/oauth2/request_auth'
REQUEST_TOKEN_URL = 'https://api.login.yahoo.com/oauth2/get_request_token'
CALLBACK_URL = 'oob'
RESPONSE_TYPE = 'code'
GRANT_TYPE = 'authorization_code'
LANGUAGE = 'en-us'

class YHandler(object):

    def __init__(self, authf):
        self.authf = authf
        self.authd = self.get_authvals_csv(self.authf)
		
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
        
        # Send user to Yahoo login to approve app
        auth_url = AUTHORIZATION_URL + '?'
        auth_url = auth_url + 'client_id={}'.format(self.authd['client_id'])
        auth_url = auth_url + '&redirect_uri={}'.format(CALLBACK_URL)
        auth_url = auth_url + '&response_type={}'.format(RESPONSE_TYPE)
        auth_url = auth_url + '&language={}'.format(LANGUAGE)        
        webbrowser.open(auth_url)
        
        # Poll user for PIN
        print "You will now be directed to a website for authorization.\n\
Please authorize the app, and then copy and paste the provide PIN below."
        self.authd['oauth_verifier'] = raw_input('Please enter your PIN:')
        
        #get final auth token
        self.get_login_token()
        
    def get_login_token(self):
        
        pdb.set_trace()
        
        token_url = GET_TOKEN_URL + '?'
        token_url = token_url + 'client_id={}'.format(self.authd['client_id'])
        token_url = token_url + '&client_secret={}'.format(self.authd['client_secret'])
        token_url = token_url + '&redirect_uri={}'.format(CALLBACK_URL)
        token_url = token_url + '&code={}'.format(self.authd['oauth_verifier'])
        token_url = token_url + '&grant_type={}'.format(GRANT_TYPE)
        
        response = requests.post(token_url)
        qs = parse_qs(response.content)
        self.authd.update(map(lambda d: (d[0], (d[1][0])), qs.items()))
        self.write_authvals_csv(self.authd, self.authf)
        return response