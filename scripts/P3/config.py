from netmiko import ConnectHandler
import datetime
import csv
import re

devices = []

def parseNeighbors(os, output):
    result = []
    if os == "arista_eos":
        devicesRaw = output[output.find("---\n"):].split("\n")[1:]
        for device in devicesRaw:
            result.append(re.split("\s\s+", device))
    elif os == "nokia_srl":
        output = output.split("\n")[3:-2]
        for i in range(len(output)):
            #print(output[i])
            output[i] = output[i].replace(" ", "").split("|")[1:-1]
            result.append(output[i])
    elif os == "mikrotik_routeros":
        output = output.split("\n\n")
        for i in range(len(output)):
            output[i] = output[i].split("=")[1:]
            for k in range(len(output[i])):
                output[i][k] = output[i][k].replace("\"", "").split(" ")[0]
            result.append(output[i])
    return result    

def parseInterfaces(os, output):
    result = []
    if os == "arista_eos":
        raw = output.split("\n")[2:-1]
        print(raw)
    elif os == "nokia_srl":
        print("A")
    elif os == "mikrotik_routeros":
        print("A")
    return result    



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

command_ips = {"arista_eos": "show ip int brief", "nokia_srl": "show interface"}
ipsStrStart = {"arista_eos": "Interface", "nokia_srl": "==="}
ipsStrEnd = {"arista_eos": "\n\n", "nokia_srl": "Summary"}

neighbors = {}
hostsOs = {}
for device in devices:
    os = device["type"]
    host = device["host"]
    hostsOs[host] = os
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
    # commands = command_neighbors[os].split(";")
    # output = router.send_config_set(commands)
    # idxStart = output.find(neighborsStrStart[os])
    # idxEnd = output.find(neighborsStrEnd[os], idxStart)
    # output = output[idxStart:idxEnd]
    # neighbor = parseNeighbors(os, output)
    # neighbors[host] = neighbor

    # SHOW IPS
    commands = command_ips[os].split(";")
    output = router.send_config_set(commands)
    idxStart = output.find(ipsStrStart[os])
    idxEnd = output.find(ipsStrEnd[os], idxStart)
    output = output[idxStart:idxEnd]
    print(output)


# writeName = f"version_{datetime.datetime.now()}.csv"
# with open(writeName, "w", newline = '') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow(['host', 'type', 'version'])
#     writer.writerows(versions)

def writeNeighbors(os, writer, input):
    arr = []
    if os == "arista_eos":
        for x in range(len(input)):
            arr.append(input[x][:-1])
    elif os == "nokia_srl":
        for x in range(len(input)):
            innerArr = []
            innerArr.append(input[x][0])
            innerArr.append(input[x][2])
            innerArr.append(input[x][-1])
            arr.append(innerArr)
    elif os == "mikrotik_routeros":
        for x in range(len(input)):
            innerArr = []
            innerArr.append(input[x][0])
            innerArr.append(input[x][4])
            innerArr.append(input[x][13])
            arr.append(innerArr)
    writer.writerows(arr)

        
# for host, value in neighbors.items():
#     writeName = f"neighbors_{host}_{datetime.datetime.now()}.csv"
#     with open(writeName, "w", newline="") as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(["interface", "neighbour_host", "neighbour_interface"])
#         #ARISTA
#         writeNeighbors(hostsOs[host],writer, value)