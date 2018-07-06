from __future__ import print_function
import re
import time
import datetime
import sys
import os
import signal
import json
import hpc_acm
from hpc_acm.configuration import Configuration
from hpc_acm.api_client import ApiClient
from hpc_acm.rest import ApiException

def getId(path):
    m = re.search('\/(\d+?)$', path)
    return int(m.group(1))

def main():
    config = Configuration()
    config.host = "http://evanclinuxdev1.eastasia.cloudapp.azure.com:8080/v1"
    api_client = ApiClient(config)
    api_instance = hpc_acm.DefaultApi(api_client)

    try:
        thread = api_instance.get_nodes(async = True)
        nodes = thread.get()
        for node in nodes:
            print(node.name)

    except ApiException as e:
        print("Exception when calling DefaultApi: %s\n" % e)

if __name__ == '__main__':
    main()

