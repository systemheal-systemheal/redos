#!/usr/bin/env python3

import json
from ldap3 import Server, Connection, ALL
from ansible_vault import Vault

vault_password = open("/etc/ansible/vars/.vault-pass.txt").read().strip()
vault = Vault(vault_password)
secrets = vault.load(open("/etc/ansible/vars/ldap.yml").read())

LDAP_SERVER = secrets['LDAP-SERVER']
LDAP_USER = secrets['LDAP-USER']
LDAP_PASSWORD = secrets['LDAP-PASSWORD']
BASE_DN = secrets['NEW-WORKSTATION']

def get_inventory():
    server = Server(LDAP_SERVER, get_info=ALL)
    conn = Connection(server, user=LDAP_USER, password=LDAP_PASSWORD, auto_bind=True)

    conn.search(BASE_DN, '(objectClass=computer)', attributes=['cn', 'dNSHostName'])

    hosts = []
    hostvars = {}

    for entry in conn.entries:
        hostname = entry.cn.value
        dns_name = entry.dNSHostName.value if hasattr(entry, 'dNSHostName') else None

        if 'rds' in hostname.lower() and dns_name:
            hosts.append(hostname)
            hostvars[hostname] = {"ansible_host": dns_name}

    return {
        "all": {
            "hosts": hosts,
        },
        "_meta": {
            "hostvars": hostvars
        }
    }

if __name__ == '__main__':
    print(json.dumps(get_inventory(), indent=4))
