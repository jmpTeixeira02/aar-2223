from napalm import get_network_driver
import json
from jinja2 import Environment, FileSystemLoader


ENV = Environment(loader=FileSystemLoader('.'))

class NetworkInterfaceAreaX(object):
    def __init__(self, name, number, description, uplink=False):
        self.name = name
        self.number = number
        self.description = description

routers = []

# routers.append({"template": "arista", "hostname": "clab-aar-lab-r1", "os": "eos", "user": "admin","pw": "admin", "ethName": "Ethernet"})
# routers.append({"template": "arista", "hostname": "clab-aar-lab-r2", "os": "eos", "user": "admin","pw": "admin", "ethName": "Ethernet"})
routers.append({"template": "srlinux", "hostname": "clab-aar-lab-r3", "os": "srl", "user": "admin","pw": "NokiaSrl1!", "ethName": "ethernet-1/"})
# routers.append({"template": "arista", "hostname": "clab-aar-lab-r4", "os": "ros", "user": "admin","pw": "admin", "ethName": "ether"})

for router in routers:
    print(router)
    templateName = router["template"]
    template = ENV.get_template(f"{templateName}.j2")
    driver = get_network_driver(router['os'])
    number = router['hostname'].split("-")[-1]
    optional_args = {
        "gnmi_port": 57400,
        "jsonrpc_port": 80,
        "target_name": f"{router['hostname']}",
        "tls_ca": f"/home/server/vrnetlab/clab-aar-lab/{number}/config/tls/clab-profile.pem",
        "skip_verify": True,
        "encoding": "JSON_IETF",
        "transport": "http"
    }

    device = driver(router['hostname'], router['user'], router['pw'], 120, optional_args)

    device.open()

    interface = NetworkInterfaceAreaX(router['ethName'], int(number[-1]), "Server Port")
    output = template.render(interface = interface)
    print(output)
    # device.discard_config()

    device.load_merge_candidate(config=output)
    # device.load_replace_candidate(config=output)
    
    print(device.get_config())


# driver = get_network_driver("srl")

# optional_args = {
#     "gnmi_port": 57400,
#     "jsonrpc_port": 80,
#     "target_name": f"clab-aar-lab-r3",
#     "tls_ca": f"/home/server/vrnetlab/clab-aar-lab/r3/config/tls/clab-profile.pem",
#     "skip_verify": True,
#     "encoding": "JSON_IETF"
#     }

# device = driver("clab-aar-lab-r3", "admin", "admin", 60, optional_args)

# device.open()

# print(device.get_config())

