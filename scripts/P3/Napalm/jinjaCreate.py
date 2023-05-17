from jinja2 import Environment, FileSystemLoader
ENV = Environment(loader=FileSystemLoader('.'))
areaXTemplate = ENV.get_template("ospfInterfaces.j2")

class NetworkInterfaceAreaX(object):
    def __init__(self, name, area, description, uplink=False):
        self.name = name
        self.number = area
        self.description = description

port_type = {"arista_eos": "Et", "nokia_srl": "ethernet-", "mikrotik_routeros": "ether"}    
        
interface_obj = NetworkInterfaceAreaX("Et", 2, "Server Port")

print(areaXTemplate.render(interface=interface_obj))