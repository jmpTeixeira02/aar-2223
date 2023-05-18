import sys
import time
from telnetlib import Telnet


def writeCommand(tn, command, timer = 1):
    command = command + "\r\n"
    #print(bytes(command, 'utf-8'))
    tn.write(command.encode())
    time.sleep(timer)
    i = tn.read_some()
    output = i
    while i != b'':
        print(i.decode(), end="")
        i = tn.read_until(b"Router#", 1)
        output += i
    return output

def init(group_number, password):
    ROUTER_INT_IP = f"192.168.10{group_number}.254"
    ROUTER_INT_OUT_IP = f"192.168.3.10{group_number}"
    ROUTER_INT_MASK = "255.255.255.0"
    ROUTER_OUT_INT = "fa0/1"
    ROUTER_LO_IP = f"{group_number}.{group_number}.{group_number}.{group_number}"
    ROUTER_LO_MASK = "255.255.255.255"
    OSPF_WILDCARD = "0.0.0.255"
    OSPF_INNER_AREA_NUMBER = f"10{group_number}"
    OSPF_OUTTER_AREA_NUMBER = "0"
    OSPF_INNER_IP = f"192.168.10{group_number}.0"
    OSPF_OUTTER_IP = "192.168.3.0"
    with Telnet(ROUTER_INT_IP, 23, 5) as tn:
        writeCommand(tn, password)
        writeCommand(tn, "en")
        writeCommand(tn, password)
        writeCommand(tn, "conf t")
        writeCommand(tn, "int loop 0")
        writeCommand(tn, f"ip address {ROUTER_LO_IP} {ROUTER_LO_MASK}")
        writeCommand(tn, 'no sh')
        writeCommand(tn, "exit")
        writeCommand(tn, f"int {ROUTER_OUT_INT}")
        writeCommand(tn, f"ip address {ROUTER_INT_OUT_IP} {ROUTER_INT_MASK}")
        writeCommand(tn, f"router ospf {group_number}")
        writeCommand(tn, f"router-id {ROUTER_LO_IP}")
        writeCommand(tn, f"network {OSPF_INNER_IP} {OSPF_WILDCARD} area {OSPF_INNER_AREA_NUMBER}")
        writeCommand(tn, f"network {OSPF_OUTTER_IP} {OSPF_WILDCARD} area {OSPF_OUTTER_AREA_NUMBER}")
        writeCommand(tn, "no passive-interface default")
        writeCommand(tn, "exit")

        # tn.write(b"end\n")
        # tn.write(b"exit\n")

