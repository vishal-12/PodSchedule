import argparse

from pyVim.connect import SmartConnect, Disconnect
from pod.VMware import VMware
import json
import sys, traceback
from pod.logger import logging
from datetime import datetime
import textwrap
from io import StringIO
import warnings

# Ignore warnings from the OpenSSL module
warnings.filterwarnings("ignore")


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
    return  {"Data": "","Info": "","ExitError": "","ExitCode":""}

try:
    logging.set_log_file( args.job_id)        
    vcenter_username = args.username
    vcenter_password = args.password
    vcenter_url = args.url
    object_identifier = args.task_identifier

    body = Body()
    if vcenter_url is not None:
        vcenter = {"url": vcenter_url, "username": vcenter_username, "password": vcenter_password}
        vmware = VMware(vcenter=vcenter)

    if (object_identifier == "datastore"):
        logging.data({"Data": vmware.GetDatastore(object_identifier)})

    if (object_identifier == "fetch_template"):
        logging.data({"Data": vmware.get_templates_softwares_from_contentlibrary(object_identifier)})

    if (object_identifier == "switch"):
        logging.data({"Data": vmware.get_public_switch_list(change_job_keys=True)})

    #Disconnect from VC
    vmware.disconnected_from_all_vc()
except Exception as e:
    logging.error("Error occured {}".format(e),100)
logging.exit_log()
