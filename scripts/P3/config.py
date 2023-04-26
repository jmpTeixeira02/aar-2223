from netmiko import ConnectHandler
import datetime
import csv
import re

devices = []

def parseNeighbors(os, output):
    result = []
    if os == "arista_eos":
        columnsRaw = output[:output.find("\n")]
        columns = re.split("\s\s+", columnsRaw)
        result.append(columns)
        devicesRaw = output[output.find("---\n"):].split("\n")[1:]
        for device in devicesRaw:
            result.append(re.split("\s\s+", device))
    elif os == "nokia_srl":
        print(output)       
    #print(result)
    

with open('config.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    columns = next(reader)
    for row in reader:
        device = dict(zip(columns, row))
        devices.append(device)


command_version = {"arista_eos" : "show ver", "nokia_srl": "show version", "mikrotik_routeros": "system;resource;print"}
versionStrStart = {"arista_eos" : "Software image version", "nokia_srl": "Software Version", "mikrotik_routeros": "factory-software"}
versions = []

command_neighbors = {"arista_eos" : "show lldp neighbors", "nokia_srl": "show system lldp neighbor", "mikrotik_routeros": "/ip/neighbor/print detail"}
neighborsStrStart = {"arista_eos" : "Port", "nokia_srl": "+", "mikrotik_routeros": "0"}
neighborsStrEnd = {"arista_eos" : "\n\n", "nokia_srl": "--{", "mikrotik_routeros": "\n\n\n"}
neighbors = []

for device in devices:
    os = device["type"]
    host = device["host"]
    router = ConnectHandler(host = host, username = device['user'], password = device['password'], device_type=os)
    
    
    router.enable()
    router.config_mode()
    
    # SHOW VERSION
    # commands = command_version[os].split(";")
    # output = router.send_config_set(commands)
    # idxStart = output.find(versionStrStart[os])
    # idxEnd = output.find('\n', idxStart)
    # version = output[idxStart:idxEnd].split(":")[1].strip()
    # print(host, os, version)
    # versions.append([host, os, version])

    # SHOW NEIGHBORS
    commands = command_neighbors[os].split(";")
    output = router.send_config_set(commands)
    idxStart = output.find(neighborsStrStart[os])
    idxEnd = output.find(neighborsStrEnd[os], idxStart)
    output = output[idxStart:idxEnd]
    parseNeighbors(os, output)



# writeName = f"version_{datetime.datetime.now()}.csv"
# with open(writeName, "w", newline = '') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow(['host', 'type', 'version'])
#     writer.writerows(versions)
