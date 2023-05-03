#!bin/bash/env python3
# encoding=utf8


import warnings
warnings.filterwarnings("ignore")

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
import atexit
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import sys, traceback
import requests
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import requests
from pod.logger import logging
from com.vmware import content_client
from com.vmware.content import library_client
session = requests.session()
session.verify = False
import logging
from samples.vsphere.contentlibrary.lib.cls_api_client import ClsApiClient
from samples.vsphere.contentlibrary.lib.cls_api_helper import ClsApiHelper
from vmware.vapi.vsphere.client import create_vsphere_client
from samples.vsphere.common.service_manager import ServiceManager
import atexit
#importlib.reload(sys)
# sys.setdefaultencoding('utf8')

from pod.logger import logging

class VMware:
    """
    Class for accessing Vmware objects
    Asumptions:
    1. if datacenter name not provided then it will pic first datacenter by default
    2. if cluster name not provided then it will pic first cluster in datacenter

    Args:
        :vcenter - Provide vcenter Credentails like {"url":"","username":"","password":""}
            -type Dict
        :connection
            -type VMware Object
        :datacenter - Datacenter Name
            - type String
        :cluster
            - type String
        :skip_verification - Skip verification
            -type Bool
        return
    """

    _vcenter_version = ""

    def __init__(self, vcenter, datacenter=None, cluster=None, extra_vars=None):

        """Constructor

        Args:
            conf (dict): config variables
        """
        # initlization
        self.vcenter = vcenter
        self.connection = None
        self.datacenter = datacenter
        self.cluster = cluster
        self.content = None
        self.cfg = extra_vars
        self.skip_verification = False

        # TODO: Have to remove
        self.Connect_Vcenter()
        #self.Connect_vSphere()

    def Connect_Vcenter(self):
        """
            Connect to vCenter instances with the help of pyVomi
        """
        try:
            import ssl
            if hasattr(ssl, '_create_unverified_context'):
                sslContext = ssl._create_unverified_context()
                self.connection = SmartConnect(host=self.vcenter['url'], user=self.vcenter['username'],
                                               pwd=self.vcenter['password'], sslContext=sslContext)
                self.service_manager = ServiceManager(server=self.vcenter['url'], username=self.vcenter['username'],
                                                      password=self.vcenter['password'], skip_verification="false")
                self.service_manager.connect()
                atexit.register(self.service_manager.disconnect)
                self.client = ClsApiClient(self.service_manager)
                self.helper = ClsApiHelper(self.client, self.skip_verification)

                self.vsphere_client = create_vsphere_client(server=self.vcenter['url'],
                                                            username=self.vcenter['username'],
                                                            password=self.vcenter['password'], session=session)
            else:
                self.connection = None
                logging.error("Unable to connect to vsphere server. Error message: _create_unverified_context", 100)
        except Exception as e:
            self.connection = None
            tb = traceback.format_exc()
            logging.error("Unable to connect to vsphere server - Traceback {} - Error message: {}".format(str(tb), str(e)),100)

        atexit.register(Disconnect, self.connection)
        self.content = self.connection.RetrieveContent()

        # Search for datacenter
        datacenter_found = False

        if self.datacenter == None:
            if self.content.rootFolder.childEntity:
                self.datacenter = self.content.rootFolder.childEntity[0]
                datacenter_found = True
        else:
            for datacenter in self.content.rootFolder.childEntity:
                if datacenter.name == self.datacenter:
                    self.datacenter = datacenter
                    datacenter_found = True
                    break

        # Send error if datacenter not found
        if datacenter_found == False:
            error_msg = "Datacenter [%s] not found in Vcenter" % self.datacenter
            logging.error(error_msg, 100)

        # Search for datacenter
        cluster_found = False
        if self.cluster == None:
            if self.datacenter.hostFolder.childEntity:
                self.cluster = self.datacenter.hostFolder.childEntity[0]
                cluster_found = True
        else:
            for cluster in self.datacenter.hostFolder.childEntity:
                if cluster.name == self.cluster:
                    self.cluster = cluster
                    cluster_found = True
                    break

        # Send error if cluster not found
        if cluster_found == False:
            error_msg = "Cluster [%s] not found in Vcenter" % self.cluster
            logging.error(error_msg, 100)


    def get_templates_softwares_from_contentlibrary(self):
        """
           Get template and software from the Content Library

           ARGS : None
           return Dict
        """
        template_list = list()
        find_spec = content_client.Library.FindSpec()
        find_spec.type = content_client.LibraryModel.LibraryType.LOCAL
        library_stub = content_client.Library(self.service_manager.stub_config)
        library_ids = library_stub.list()
        item_stub = library_client.Item(self.service_manager.stub_config)
        template_list_local = []
        template_list_global = []
        software_list_local = []
        software_list_global = []
        for library_id in library_ids:
            library = library_stub.get(library_id)
            dp = self.client.library_item_service.list(library_id)
            for item_id in dp:

                item = item_stub.get(item_id)
                if item.type == "ovf" or item.type == "vm-template":
                    if library.type == content_client.LibraryModel.LibraryType.LOCAL:
                        template_list_local.append(item.name)
                    else:
                        if library.type == content_client.LibraryModel.LibraryType.SUBSCRIBED:
                            template_list_global.append(item.name)
                else:
                    if library.type == content_client.LibraryModel.LibraryType.LOCAL:
                        software_list_local.append(item.name)
                    else:
                        software_list_global.append(item.name)
        datastore_templates = [ds.name for ds in self.datacenter.datastore]
        templates_and_othertypes = {"localLibraryTemplates": template_list_local,
                                    "globalLibraryTemplates": template_list_global,
                                    "localLibraryOtherTypeSoftwares": software_list_local,
                                    "globalLibraryOtherTypeSoftwares": software_list_global,
                                    "datastore_templates": datastore_templates}
        template_list.append(templates_and_othertypes)
        return template_list

    def get_obj_using_pyvmomi(self, vimtype, name=None):
        """
         Get the vsphere object associated with a given text name
        """
        obj = None
        if name is None:
            obj = list()
        container = self.content.viewManager.CreateContainerView(self.content.rootFolder, vimtype, True)
        for c in container.view:
            if name is None:
                obj.append(c)
            else:
                if c.name == name:
                    obj = c
                    break

        if not obj:
            if vimtype == [vim.VirtualMachine]:
                logging.error("Virtual Machine or Virtual Machine image with Name [%s] not found" % name, 100)
            elif vimtype == [vim.DistributedVirtualSwitch]:
                logging.info("skipped switched in case of vmc")
            else:
                logging.error("[%s] with Name [%s] not found" % (vimtype, name), 100)
        return obj

    def get_public_switch_list(self,change_job_keys = False):
        """
        Get all public switch list base on PUBNET string present in name of switch
        :return:
        """
        dv_switch_name = list()
        for dv_switch in self.get_obj_using_pyvmomi([vim.DistributedVirtualSwitch]):
            public_port_group = list()
            for port_group in dv_switch.portgroup:
                if isinstance(port_group.config.defaultPortConfig.vlan.vlanId, int):
                    if change_job_keys is True:
                        public_port_group.append({
                            "network_name": port_group.name,
                            "vlan_id": int(port_group.config.defaultPortConfig.vlan.vlanId),
                            "dv_port_group_id": port_group.key
                        })
                    else:
                        public_port_group.append({
                            "name": port_group.name,
                            "vlan": int(port_group.config.defaultPortConfig.vlan.vlanId)
                             })
            if change_job_keys is True:
                dv_switch_name.append({
                    "switch": dv_switch.name,
                    "network": public_port_group
                })
            else:
                dv_switch_name.append({
                    "name": dv_switch.name,
                    "port": public_port_group
                })
        return dv_switch_name

    def get_cluster_obj(self, cluster_name):
        """
            Get the cluster object with the cluster name

            params: cluster_name
            return object
        """
        logging.info("Cluster name on which resource pool is going to create : [%s]" % cluster_name)
        for cluster in self.datacenter.hostFolder.childEntity:
            if cluster.name == cluster_name:
                return cluster

    def GetDatastore(self,object_identifier, summary=False):
        """
        Get Datastore arrange by freeSpace
        :return:
        """
        try:
            datastores = sorted(self.datacenter.datastore, key=lambda k: k.info.freeSpace, reverse=True)
            datastore_list = list()
            for ds in datastores:
                # datastore_list.append(ds.name)
                datastore_list.append({
                    "name": ds.summary.name,
                    "url": ds.summary.url,
                    "capacity": ds.summary.capacity,
                    "type": ds.summary.type,
                    "accessible": ds.summary.accessible,
                    "freeSpace": ds.summary.freeSpace
                })
            return { object_identifier :  datastore_list}

        except Exception as e:
            logging.error("GetDataStore list error - {}".format(e),100)
    
    def get_dc(self, connection, name):
        """
             Get the Datacenter instance
             :param - Connection
                      -type Object
             :param - name - Name of the Datacenter
                       -type String
             return None
        """
        for dc in connection.content.rootFolder.childEntity:
            if dc.name == name:
                return dc
        logging.error('Failed to find datacenter named %s' % name,100)
