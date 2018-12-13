import adal

def get_access_token(tenant, appid, appsecret):
    authority_url = "https://login.microsoftonline.com/" + tenant
    context = adal.AuthenticationContext(authority_url)
    token = context.acquire_token_with_client_credentials(appid, appid, appsecret)
    return token['accessToken']
