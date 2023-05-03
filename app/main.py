import argparse

from pod.VMware import VMware
import json
import sys, traceback
from pod.logger import logging
from datetime import datetime
import textwrap
from io import StringIO
import warnings

# Ignore warnings from the OpenSSL module
warnings.filterwarnings("ignore", category=DeprecationWarning, module="OpenSSL")


parser = argparse.ArgumentParser(description='Input information about Vcenter.')
parser.add_argument('--username', dest='username' , required=False,
                        help='Please enter username of Vcenter')
parser.add_argument('--password', dest='password' , required=False,
                        help='Please enter password of Vcenter')
parser.add_argument('--url', dest='url' , required=False,
                        help='Please enter URL of Vcenter')
parser.add_argument('--task_identifier', dest='task_identifier' , required=False,
                        help='Please enter flag')
parser.add_argument('--job_id', dest='job_id' , required=False,
                        help='Please enter job_id')
args = parser.parse_args()


def Body():
    """
     Standard Script Response Format
    :return:
    """
    return  {"Data": "","Info": "","Error": ""}

try:
        
    vcenter_username = args.username
    vcenter_password = args.password
    vcenter_url = args.url
    object_identifier = args.task_identifier

    buffer = sys.stdout
    sys.stdout = captured_output = StringIO()
    sys.stderr = captured_errors = StringIO()
    body = Body()
    if vcenter_url is not None:
        vcenter = {"url": vcenter_url, "username": vcenter_username, "password": vcenter_password}
        vmware = VMware(vcenter=vcenter)

    if (object_identifier == "datastore"):
        print ("Before")
        body.update({"Data": vmware.GetDatastore()})

    if (object_identifier == "fetch_template"):
        print ("Before")
        body.update({"Data": vmware.get_templates_softwares_from_contentlibrary()})

    # Restore standard output and get the captured output as a string
    sys.stdout = buffer
    
    console_output = captured_output.getvalue()
    
    # Wrap and jsonify the captured output
    wrapped_output = textwrap.fill(console_output)
    json_output = json.dumps(body)
    print(json_output)

except Exception as e:
    tb=traceback.format_exc()
    logging.error("Traceback [%s]" % (str(tb)), 100, ex=True)
