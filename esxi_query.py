import ssl
import socket
import datetime
import sys
try:
    from pyVmomi import vim
    from pyVim import connect
except:
    print("You need to install pyVmomi and pyVim via 'pip install pyVim pyVmomi' ")
    sys.exit()




def list_folders(folder, lookfor, indent=0):
    # Print the folder name with indentation
    if lookfor in str(folder.name):
        print("  " * (2*indent) + folder.name)
        list_deployments(folder, indent)
    else:
        pass
    # Check if the folder contains subfolders
    if hasattr(folder, 'childEntity'):
        # Recursively list subfolders
        for child in folder.childEntity:
            if isinstance(child, vim.Folder):
                list_folders(child, lookfor, indent + 1)

def list_deployments(folder, indent):
    fh = open("oldVMs.csv",'a')
    if hasattr(folder, 'childEntity'):
        for child in folder.childEntity:
            if isinstance(child,vim.Folder):
                list_deployments(child,indent+1)
            if isinstance(child,vim.VirtualMachine):
                vmdate = (child.config.createDate).year
                #If the VM is from 2022 or earlier, list it.
                if vmdate < 2023:
                    fh.write(f"{vmdate},{child.parent.name},{child.name},{child.config.createDate}\n")
                    print("  " * (2*indent+1) + f"{child.parent.name}\{child.name} - {child.config.createDate}")
    fh.close()

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
ssl_context.verify_mode = ssl.CERT_NONE

#Only checking PROD and EV2
SERVERS = ["vcenter-ev2.simspace.lan","vcenter-prod.simspace.lan"]

#Checking specifically for Portal and TCDEV deployments
FOLDERS = [".dt_tcdev", ".dt_portal-us"]

#Can be changed to any search term. 
search_root = "deployments"

for server in SERVERS:
    try:
        print(f"CURRENT SERVER: {server}")
        esxi_host = socket.gethostbyname(server)
        ADusername = "YOUR_AD_USERNAME"
        ADpassword = "YOUR_AD_PASSWORD"
        service_instance = connect.SmartConnect(host=esxi_host,user=ADusername,pwd=ADpassword,sslContext=ssl_context)

        content = service_instance.RetrieveContent()
        vm_view = content.viewManager.CreateContainerView(content.rootFolder,[vim.VirtualMachine],True)
        datacenter = content.rootFolder.childEntity[0]
    
        vm_items = {}
        date = 0
    
        list_folders(datacenter.vmFolder, search_root,0)
    except:
        pass
