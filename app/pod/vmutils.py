# coding=utf-8

from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import time
from pathlib import Path

def _get_obj(content, vimtype, name):
    """
    Get the vsphere object associated with a given text name
    """
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj

def _get_obj_from_cluster(content, vimtype, resource_pool_name,cluster_object):
    """
    Get the vsphere object associated with a given text name in a provided cluster
    """
    obj = None
    container = content.viewManager.CreateContainerView(cluster_object, vimtype, True)
    for c in container.view:
        if c.name ==resource_pool_name:
            obj = c
            break
    return obj

def _get_all_objs(content, vimtype):
    """
    Get all the vsphere objects associated with a given type
    """
    obj = {}
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        obj.update({c: c.name})
    return obj


def login_in_guest(username, password):
    return vim.vm.guest.NamePasswordAuthentication(username=username,password=password)

def start_process(si, vm, auth, program_path, args=None, env=None, cwd=None):
    cmdspec = vim.vm.guest.ProcessManager.ProgramSpec(arguments=args, programPath=program_path, envVariables=env, workingDirectory=cwd)
    cmdpid = si.content.guestOperationsManager.processManager.StartProgramInGuest(vm=vm, auth=auth, spec=cmdspec)
    return cmdpid

def is_ready(vm):

    while True:
        system_ready = vm.guest.guestOperationsReady
        system_state = vm.guest.guestState
        system_uptime = vm.summary.quickStats.uptimeSeconds
        if system_ready and system_state == 'running' and system_uptime > 90:
            break
        time.sleep(10)

def get_vm_by_name(si, name):
    """
    Find a virtual machine by it's name and return it
    """
    return _get_obj(si, [vim.VirtualMachine], name)

def get_host_by_name(si, name):
    """
    Find a virtual machine by it's name and return it
    """
    return _get_obj(si.RetrieveContent(), [vim.HostSystem], name)

def get_resource_pool(si, name):
    """
    Find a virtual machine by it's name and return it
    """
    return _get_obj(si.RetrieveContent(), [vim.ResourcePool], name)

def get_resource_pool_from_cluster(si, resource_pool_name, cluster_object):
    """
    Find a virtual machine by it's name and return it
    """
    return _get_obj_from_cluster(si.RetrieveContent(), [vim.ResourcePool],
        resource_pool_name,cluster_object)

def get_resource_pools(si):
    """
    Returns all resource pools
    """
    return _get_all_objs(si.RetrieveContent(), [vim.ResourcePool])

def get_datastores(si):
    """
    Returns all datastores
    """
    return _get_all_objs(si.RetrieveContent(), [vim.Datastore])

def get_hosts(si):
    """
    Returns all hosts
    """
    return _get_all_objs(si.RetrieveContent(), [vim.HostSystem])

def get_datacenters(si):
    """
    Returns all datacenters
    """
    return _get_all_objs(si.RetrieveContent(), [vim.Datacenter])

def get_registered_vms(si):
    """
    Returns all vms
    """
    return _get_all_objs(si.RetrieveContent(), [vim.VirtualMachine])

def get_os_customization_spec_item (si , name ):
    """
    Rrturn OS Customization object
    :param si:
    :param name:
    :return:
    """
    customizations = si.customizationSpecManager.info
    for cus in customizations:
        if name == cus.name:
            return cus
    return False

def get_event(si, entitities , names ):
    byEntity = vim.event.EventFilterSpec.ByEntity( entity = entitities , recursion="self" )

    filter = vim.event.EventFilterSpec(entity = byEntity , eventTypeId=names)
    return si.eventManager.QueryEvents( filter )

def get_snapshots(vm):
    if not vm.snapshot:
        return list()
    if not vm.snapshot.rootSnapshotList:
            return list()
    return get_snapshot_list(vm.snapshot.rootSnapshotList )

def get_snapshot_list(snapshots):
    snapshot_list = []
    if not snapshots:
        return snapshot_list

    for snapshot in snapshots:
        snapshot_list.append(snapshot.name)
        snapshot_list += get_snapshot_list(snapshot.childSnapshotList)

    return snapshot_list

def get_snapshots_recursively(snapshots, snapshot_location):
    snapshot_paths = []

    if not snapshots:
        return snapshot_paths

    for snapshot in snapshots:
        if snapshot_location:
            current_snapshot_path = snapshot_location + '/' + snapshot.name
        else:
            current_snapshot_path = snapshot.name

        snapshot_paths.append(current_snapshot_path)
        snapshot_paths = snapshot_paths + get_snapshots_recursively( snapshot.childSnapshotList, current_snapshot_path)

    return snapshot_paths


def remove_directory(folder_name, recursive = True ):
    # Remove file from host temp dir
    #return
    path = Path(folder_name)

    for file in path.iterdir():
        if file.is_file():
            file.unlink()

        if recursive:
            if file.is_dir():
                remove_directory (str(file), recursive=True)

def get_file_folder(folder_name , recursive = False, root_folder = None):
    if root_folder is None:
        root_folder = folder_name
    file_list = list()
    path = Path(folder_name)

    for file in path.iterdir():
        if file.is_file():
            file_list.append( str(file.relative_to(root_folder)) )

        if recursive:
            if file.is_dir():
                file_list += get_file_folder( str(file) , recursive = True, root_folder=folder_name )

    return file_list