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
        # (Optional) STEP 0:
        # For a list of available nodes:
        nodes = api_instance.get_nodes()
        for node in nodes:
            print(node.name)

        # STEP 1:
        # Create a diagnostic test
        print("Creating test...")
        job = {
            "name": "Mpi Pingpong@%s" % datetime.datetime.now().isoformat(),
            "targetNodes": ["evancvmss000001", "evancvmss000002", "evancvmss000004"],
            "diagnosticTest": {
                "name": "pingpong",
                "category": "mpi",
                "arguments": "[{\"name\":\"Aim\",\"value\":\"Default\"},{\"name\":\"Packet size\",\"value\":0},{\"name\":\"Mode\",\"value\":\"Tournament\"}]"
            },
        }
        # Should be:
        # job = api_instance.create_diagnostic_job(job = job)
        # job_id = job.id
        data, status, headers = api_instance.create_diagnostic_job_with_http_info(job = job)
        job_id = getId(headers['Location'])
        print("Job %s is created." % job_id)

        # (Optional) STEP 2:
        # Cancel the test when ctrl-C is pressed
        def prompt_for_cancel(signum, frame):
            answer = raw_input("Do you want to cancel the test? (Y/N)").lower()
            if answer == "y":
                api_instance.cancel_diagnostic_job(job_id, job = { "request": "cancel" })
                print("Job %s is canceled." % job_id)
            else:
                print("Exit and leave the job running.")
            sys.exit()

        signal.signal(signal.SIGINT, prompt_for_cancel)

        # STEP 3:
        # Query the test result
        print("Querying test result...")
        agg_result = None
        while not agg_result:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
            result = api_instance.get_diagnostic_job(job_id)
            agg_result = result.aggregation_result
        agg_result = json.loads(agg_result)
        print("\nGood nodes:")
        for node in agg_result["GoodNodes"]:
            print(node)

    except ApiException as e:
        print("Exception when calling DefaultApi: %s\n" % e)

if __name__ == '__main__':
    main()

