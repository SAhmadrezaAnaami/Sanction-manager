import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import subprocess
import sys
import shutil
import json
from manager import DNSManager  # Assuming the DNSManager is in manager.py

# A scrollable frame to be used in multiple places
class ScrollableFrame(tk.Frame):
    def __init__(self, container, height=150, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, height=height)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

# A main scrollable container for the entire window or tab
class MainScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

# DNS Manager Tab
class DNSApp:
    def __init__(self, parent):
        self.dns_manager = DNSManager()

        self.main_container = MainScrollableFrame(parent)
        self.main_container.pack(fill="both", expand=True)

        # DNS Listbox section
        list_frame = tk.Frame(self.main_container.scrollable_frame)
        list_frame.pack(padx=10, pady=10)
        self.dns_listbox = tk.Listbox(list_frame, width=50, height=10)
        self.dns_listbox.pack(side=tk.LEFT)
        list_scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.dns_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.dns_listbox.config(yscrollcommand=list_scrollbar.set)

        refresh_button = tk.Button(self.main_container.scrollable_frame, text="Refresh List", command=self.refresh_dns_list)
        refresh_button.pack(pady=5)

        self.dns_entry = tk.Entry(self.main_container.scrollable_frame, width=50)
        self.dns_entry.pack(pady=5)

        add_button = tk.Button(self.main_container.scrollable_frame, text="Add DNS Server", command=self.add_dns_server)
        add_button.pack(pady=5)
        remove_button = tk.Button(self.main_container.scrollable_frame, text="Remove DNS Server", command=self.remove_dns_server)
        remove_button.pack(pady=5)
        close_button = tk.Button(self.main_container.scrollable_frame, text="Close", command=parent.quit)
        close_button.pack(pady=5)

        # Predefined DNS Providers section
        predefined_label = tk.Label(self.main_container.scrollable_frame, text="Predefined DNS Providers", font=("Arial", 14, "bold"))
        predefined_label.pack(pady=5)

        predefined_container = tk.Frame(self.main_container.scrollable_frame)
        predefined_container.pack(padx=10, pady=10, fill="both", expand=True)
        self.predefined_frame = ScrollableFrame(predefined_container, height=150)
        self.predefined_frame.pack(fill="both", expand=True)

        self.predefined_dns = {
            "Shaken": ["178.22.122.100", "185.51.200.2"],
            "403": ["10.202.10.202", "10.202.10.102"],
            "electro": ["78.157.42.101", "78.157.42.100"],
            "google": ["8.8.8.8"]
        }
        self.checkbuttons = {}

        for provider, servers in self.predefined_dns.items():
            provider_label = tk.Label(self.predefined_frame.scrollable_frame, text=provider,
                                      font=("Arial", 12, "bold"), cursor="hand2")
            provider_label.pack(anchor=tk.W)
            provider_label.bind("<Button-1>", lambda e, prov=provider: self.check_provider(prov))
            for server in servers:
                var = tk.BooleanVar(value=False)
                checkbox = tk.Checkbutton(self.predefined_frame.scrollable_frame, text=server, variable=var)
                checkbox.pack(anchor=tk.W)
                self.checkbuttons[server] = var

        activate_button = tk.Button(self.main_container.scrollable_frame, text="Activate Selected DNS", command=self.activate_predefined_dns)
        activate_button.pack(pady=5)
        deactivate_button = tk.Button(self.main_container.scrollable_frame, text="Deactivate All DNS", command=self.deactivate_all_dns)
        deactivate_button.pack(pady=5)
        flush_button = tk.Button(self.main_container.scrollable_frame, text="Flush DNS Cache", command=self.flush_dns_cache)
        flush_button.pack(pady=5)

        self.refresh_dns_list()

    def refresh_dns_list(self):
        self.dns_listbox.delete(0, tk.END)
        try:
            dns_servers = self.dns_manager.list_dns_servers()
            for server in dns_servers:
                self.dns_listbox.insert(tk.END, server)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_dns_server(self):
        dns_server = self.dns_entry.get().strip()
        if not dns_server:
            messagebox.showwarning("Input Error", "Please enter a DNS server.")
            return
        try:
            self.dns_manager.add_dns_server(dns_server)
            self.refresh_dns_list()
            self.dns_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_dns_server(self):
        try:
            selected_index = self.dns_listbox.curselection()
            if not selected_index:
                messagebox.showwarning("Selection Error", "Please select a DNS server to remove.")
                return
            dns_server = self.dns_listbox.get(selected_index)
            self.dns_manager.remove_dns_server(dns_server)
            self.refresh_dns_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def check_provider(self, provider):
        for server in self.predefined_dns[provider]:
            self.checkbuttons[server].set(True)

    def activate_predefined_dns(self):
        for server, var in self.checkbuttons.items():
            if var.get():
                try:
                    self.dns_manager.add_dns_server(server)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add {server}: {str(e)}")
        self.refresh_dns_list()

    def deactivate_all_dns(self):
        for server in self.checkbuttons.keys():
            try:
                self.dns_manager.remove_dns_server(server)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove {server}: {str(e)}")
        self.refresh_dns_list()

    def flush_dns_cache(self):
        try:
            if sys.platform.startswith("win"):
                subprocess.check_call("ipconfig /flushdns", shell=True)
            elif sys.platform.startswith("darwin"):
                subprocess.check_call("sudo killall -HUP mDNSResponder", shell=True)
            elif sys.platform.startswith("linux"):
                if shutil.which("systemd-resolve"):
                    subprocess.check_call("sudo systemd-resolve --flush-caches", shell=True)
                elif shutil.which("resolvectl"):
                    subprocess.check_call("sudo resolvectl flush-caches", shell=True)
                else:
                    raise Exception("No command found to flush DNS caches on Linux.")
            messagebox.showinfo("Success", "DNS cache flushed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to flush DNS cache: {e}")

# Docker Repo Manager Tab
class DockerRepoApp:
    def __init__(self, parent):
        self.main_container = MainScrollableFrame(parent)
        self.main_container.pack(fill="both", expand=True)

        title_label = tk.Label(self.main_container.scrollable_frame, text="Docker Registry Management", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        info_label = tk.Label(self.main_container.scrollable_frame, text="Select a Docker registry from the list below:")
        info_label.pack(pady=5)

        # Predefined docker registries
        self.predefined_registries = {
            "Docker Hub": "https://registry.hub.docker.com",
            "Arvan Cloud": "https://docker.arvancloud.ir"
            # Additional registries can be added here
        }
        self.registry_var = tk.StringVar()
        self.registry_var.set(next(iter(self.predefined_registries.values())))  # Default registry

        for name, url in self.predefined_registries.items():
            rb = tk.Radiobutton(self.main_container.scrollable_frame, text=name, variable=self.registry_var, value=url)
            rb.pack(anchor=tk.W, padx=20, pady=2)

        set_button = tk.Button(self.main_container.scrollable_frame, text="Set Docker Registry", command=self.set_docker_registry)
        set_button.pack(pady=10)

        show_button = tk.Button(self.main_container.scrollable_frame, text="Show Current Registry", command=self.show_current_registry)
        show_button.pack(pady=5)

    def set_docker_registry(self):
        registry = self.registry_var.get()
        json_str = f'''{{
  "insecure-registries" : ["{registry}"],
  "registry-mirrors": ["{registry}"]
}}'''
        command = f"sudo bash -c 'cat > /etc/docker/daemon.json <<EOF\n{json_str}\nEOF'"
        try:
            subprocess.check_call(command, shell=True)
            subprocess.check_call("docker logout", shell=True)
            subprocess.check_call("sudo systemctl restart docker", shell=True)
            messagebox.showinfo("Success", "Docker registry updated and Docker restarted!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update Docker registry: {e}")

    def show_current_registry(self):
        try:
            # Use sudo to read the file if necessary
            output = subprocess.check_output("sudo cat /etc/docker/daemon.json", shell=True, universal_newlines=True)
            config = json.loads(output)
            insecure = config.get("insecure-registries", [])
            mirrors = config.get("registry-mirrors", [])
            msg = f"Insecure Registries:\n{insecure}\n\nRegistry Mirrors:\n{mirrors}"
            messagebox.showinfo("Current Docker Registry", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read current registry: {e}")

class InfoTab:
    def __init__(self, parent):
        self.main_container = MainScrollableFrame(parent)
        self.main_container.pack(fill="both", expand=True)
        
        # Creator Information
        info_frame = self.main_container.scrollable_frame
        
        title = tk.Label(info_frame, text="Application Information", font=("Arial", 16, "bold"))
        title.pack(pady=10, padx=10, anchor=tk.W)
        
        creator = tk.Label(info_frame, text="Created by: Ahmadreza Anaami", font=("Arial", 12))
        creator.pack(pady=5, padx=10, anchor=tk.W)
        
        contact = tk.Label(info_frame, text="Contact: sky.lighthouse.me@gmail.com", font=("Arial", 12))
        contact.pack(pady=5, padx=10, anchor=tk.W)
        
        version = tk.Label(info_frame, text="Version: 1.0.0", font=("Arial", 12))
        version.pack(pady=5, padx=10, anchor=tk.W)
        
        description = tk.Label(info_frame, text="This application provides DNS management and Docker registry configuration tools.\n"
                                               "Features include DNS server management, predefined DNS providers, and Docker registry switching.\nIn order to bypass cruel US Sanctions.",
                             justify=tk.LEFT, wraplength=450)
        description.pack(pady=10, padx=10, anchor=tk.W)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("System Configuration Tool")
    root.geometry("450x550")
    
    # Create Notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)
    
    # Add Tabs
    dns_tab = DNSApp(notebook)
    docker_tab = DockerRepoApp(notebook)
    info_tab = InfoTab(notebook)  # New Info Tab
    
    notebook.add(dns_tab.main_container, text="DNS Manager")
    notebook.add(docker_tab.main_container, text="Docker Registry")
    notebook.add(info_tab.main_container, text="Info")  # Add Info tab to notebook
    
    root.mainloop()