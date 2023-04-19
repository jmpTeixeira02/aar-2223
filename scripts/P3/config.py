from netmiko import ConnectHandler
import csv

with open('config.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    columns = next(reader)
    devices = []
    for row in reader:
        device = dict(zip(columns, row))
        devices.append(device)

    for device in devices:
        print(device)
        router = ConnectHandler(host = device['host'], username = device['user'], password = device['password'], device_type=device['type'])
        router.enable()
