import os

class DNSManager:
    def __init__(self, resolv_conf_path='/etc/resolv.conf'):
        self.resolv_conf_path = resolv_conf_path
    
    def read_dns_config(self):
        if not os.path.exists(self.resolv_conf_path):
            raise FileNotFoundError(f"{self.resolv_conf_path} not found.")
        
        with open(self.resolv_conf_path, 'r') as file:
            return file.readlines()

    def write_dns_config(self, config_lines):
        with open(self.resolv_conf_path, 'w') as file:
            file.writelines(config_lines)
    
    def add_dns_server(self, dns_server):
        config_lines = self.read_dns_config()
        
        for line in config_lines:
            if line.startswith('nameserver') and dns_server in line:
                print(f"DNS server {dns_server} already exists.")
                return
        
        config_lines.append(f"nameserver {dns_server}\n")
        self.write_dns_config(config_lines)
        print(f"DNS server {dns_server} added successfully.")
    
    def remove_dns_server(self, dns_server):
        config_lines = self.read_dns_config()
        
        config_lines = [line for line in config_lines if not (line.startswith('nameserver') and dns_server in line)]
        
        self.write_dns_config(config_lines)
        print(f"DNS server {dns_server} removed successfully.")
    
    def list_dns_servers(self):
        config_lines = self.read_dns_config()
        
        dns_servers = [line.split()[1] for line in config_lines if line.startswith('nameserver')]
        return dns_servers