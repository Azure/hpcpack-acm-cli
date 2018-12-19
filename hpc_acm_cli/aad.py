import adal

def get_access_token(issuer_url, client_id, client_secret):
    context = adal.AuthenticationContext(issuer_url)
    token = context.acquire_token_with_client_credentials(client_id, client_id, client_secret)
    return token['accessToken']
