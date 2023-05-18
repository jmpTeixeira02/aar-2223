from netmiko import ConnectHandler
import datetime
import csv
import re

devices = []

distFolder = "./dist"

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
        raw = output.split("-\n")[1]
        interfacesRaw = raw.split("\n")
        for interface in interfacesRaw:
            temp = re.split("\s\s+", interface)
            network = temp[1].split("/")
            result.append([temp[0], temp[2], network[0], network[1]])
    elif os == "nokia_srl":
        output = output.replace("-", "").replace("=", "")
        interfaces = output.split("\n\n")[:-1]
        for interface in interfaces:
            if (interface.count("\n") > 3):
                temp = interface.split(" ")
                network = re.findall("(?:(?:\d|[01]?\d\d|2[0-4]\d|25[0-5]).){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d|\d)(?:/[1-2][0-9]|/30)", output)
                networks = network[0].split("/")
                result.append([temp[0].replace("\n", ""), temp[2][:-1], networks[0], networks[1]])
            else:
                temp = interface.split(" ")
                result.append([temp[0].replace("\n", ""), temp[2], "", ""])
    elif os == "mikrotik_routeros":
        interfaces = output.split("\n")
        for interface in interfaces:
            temp = interface.split("=")
            network = temp[1].split(" ")[0].split("/")
            result.append([temp[-1], "up", network[0], network[1]])
    return result    



with open('config.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    columns = next(reader)
    for row in reader:
        device = dict(zip(columns, row))
        devices.append(device)




command_version = {"arista_eos" : "show ver", "nokia_srl": "show version", "mikrotik_routeros": "system/resource/print"}
versionStrStart = {"arista_eos" : "Software image version", "nokia_srl": "Software Version", "mikrotik_routeros": "factory-software"}
versions = []

command_neighbors = {"arista_eos" : "show lldp neighbors", "nokia_srl": "show system lldp neighbor", "mikrotik_routeros": "/ip/neighbor/print detail"}
neighborsStrStart = {"arista_eos" : "Port", "nokia_srl": "+", "mikrotik_routeros": "0"}
neighborsStrEnd = {"arista_eos" : "\n\n", "nokia_srl": "--{", "mikrotik_routeros": "\n\n\n"}

command_ips = {"arista_eos": "show ip int brief", "nokia_srl": "show interface", "mikrotik_routeros": "ip/address/print detail"}
ipsStrStart = {"arista_eos": "Interface", "nokia_srl": "===", "mikrotik_routeros": "0"}
ipsStrEnd = {"arista_eos": "\n\n", "nokia_srl": "Summary", "mikrotik_routeros": "\n\n"}

commands_conf = {"arista_eos": "sh run | json", "mikrotik_routeros": "export compact", "nokia_srl": "info system"}

neighbors = {}
hostsOs = {}
ips = {}
confs = {}
for device in devices:
    os = device["type"]
    host = device["host"]
    hostsOs[host] = os
    router = ConnectHandler(host = host, username = device['user'], password = device['password'], device_type=os)
    
    
    router.enable()
    
    # SHOW VERSION
    command = command_version[os]
    output = router.send_command(command)
    idxStart = output.find(versionStrStart[os])
    idxEnd = output.find('\n', idxStart)
    version = output[idxStart:idxEnd].split(":")[1].strip()
    print(host, os, version)
    versions.append([host, os, version])

    # SHOW NEIGHBORS
    command = command_neighbors[os]
    output = router.send_command(command)
    idxStart = output.find(neighborsStrStart[os])
    idxEnd = output.find(neighborsStrEnd[os], idxStart)
    output = output[idxStart:idxEnd]
    neighbor = parseNeighbors(os, output)
    neighbors[host] = neighbor

    # SHOW IPS
    command = command_ips[os]
    output = router.send_command(command)
    idxStart = output.find(ipsStrStart[os])
    idxEnd = output.find(ipsStrEnd[os], idxStart)
    output = parseInterfaces(os, output[idxStart:idxEnd])
    ips[host] = output

    # SHOW CONF
    print(f"SHOWING COMMAND OF OS{host}")
    command = commands_conf[os]
    output = router.send_command(command, read_timeout=15)
    confs[host] = output

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

distFolder = "./dist"

# WRITE VERSION  
writeName = f"{distFolder}/version_{datetime.datetime.now()}.csv"
with open(writeName, "w", newline = '') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['host', 'type', 'version'])
    writer.writerows(versions)


# WRITE NEIGHBORS
for host, value in neighbors.items():
    writeName = f"{distFolder}/neighbors_{host}_{datetime.datetime.now()}.csv"
    with open(writeName, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["interface", "neighbour_host", "neighbour_interface"])
        writeNeighbors(hostsOs[host],writer, value)

# WRITE IP
for host, value in ips.items():
    writeName = f"{distFolder}/interfaces_{host}_{datetime.datetime.now()}.csv"
    with open(writeName, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["interface", "status", "ip", "mask"])
        writer.writerows(value)

# WRITE CONF
for host, value in confs.items():
    writeName = f"{distFolder}/conf_{host}_{datetime.datetime.now()}.txt"
    with open(writeName, "w") as file:
        file.write(value)
