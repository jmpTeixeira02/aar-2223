import serial
import time

def writeCommand(console, command, timer = 3):
    command = command + "\r\n"
    #print(bytes(command, 'utf-8'))
    console.write(command.encode())
    time.sleep(timer)
    line = console.read_all().decode()
    return line

def init(group_number):
    with serial.Serial(port='/dev/ttyUSB0', baudrate=9600, parity='N',stopbits=1, bytesize=8, timeout=8) as console:
        if console.isOpen():
            print('Serial is Opened')
            DHCP_NETWORK = f"192.168.10{group_number}.0"
            ROUTER_INT_IP = f"192.168.10{group_number}.254"
            ROUTER_INT_MASK = "255.255.255.0"
            setup = False

            while(1):
                line = writeCommand(console, '')
                if setup:
                    break
                elif "Router>" in line or "Router#" in line:
                    print(writeCommand(console, 'en'), end="")
                    interfaces_out = writeCommand(console, 'sh ip int brief')
                    print(interfaces_out)
                    interfaces = interfaces_out.split("\n")[2:-1]
                    interface = interfaces[0].split(" ")[0]
                    if interface != "":
                        print(writeCommand(console, 'conf t'))
                        print(writeCommand(console, f'int {interface}'))
                        print(writeCommand(console, f'ip address {ROUTER_INT_IP} {ROUTER_INT_MASK}'))
                        print(writeCommand(console, 'no sh'))
                elif "Would you like to enter the initial configuration" in line:
                    print(writeCommand(console, 'no', 15))
                elif "Router(config)#" in line:
                    print(writeCommand(console, f'ip dhcp excluded-address {ROUTER_INT_IP}'))
                    print(writeCommand(console, 'ip dhcp pool rede-interna'), end="")
                    print(writeCommand(console, f'network {DHCP_NETWORK} {ROUTER_INT_MASK}'))
                    #print(writeCommand(console, f'default-router {ROUTER_INT_IP}'))
                    setup = True
                    print(writeCommand(console, 'exit'))
                elif "Router(config-if)" in line:
                    print(writeCommand(console, 'exit'))
                    print(writeCommand(console, 'enable secret server'))
                    print(writeCommand(console, 'line vty 0 4'))
                    print(writeCommand(console, 'login'))
                    print(writeCommand(console, 'password server'))
                    print(writeCommand(console, 'exit'))
                elif "Router(config-line)" in line:
                    print(writeCommand(console, 'exit'))
                elif "Router(dhcp-config)" in line:
                    print(writeCommand(console, 'exit'))
                else:
                    print(line, end ="")
