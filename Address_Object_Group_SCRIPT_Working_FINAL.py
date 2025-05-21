#### pyinstaller --onefile your_script.py ### 
import csv
import re

##############Customization Variables###############
address_object_host_name = "Host"
address_object_network_name = "Network"
address_object_fqdn_name = "FQDN"
csv_file_path = "c:\\scripts\\Address_Object\\Address_Object_Group.csv"
output_file_path = "c:\\scripts\\Address_Object\\Address_Object_Group_CLI.txt"
####################################################

# regex patterns
ip_regex = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
network_regex = r"^((\d{1,3}\.){3}\d{1,3})/(3[0-2]|[12]?\d)$"
fqdn_regex = r"(?=^.{4,253}$)(^(\*\.)?((?!-)[a-zA-Z0-9-]{0,62}[a-zA-Z0-9]\.)+[a-zA-Z]{2,63}$)"
ip_with_subnet_regex = r"^((\d{1,3}\.){3}\d{1,3})/((\d{1,3}\.){3}\d{1,3})$"

# Keep Track of Network Addresses in the List
network_address_count = 0

# Keep Track of Host Addresses in the List
ip_address_count = 0

# Keep Track of FQDN Addresses in the List
fqdn_count = 0

# Read SRNumber and GroupName from the CSV file
with open(csv_file_path, newline='') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    first_row = next(csv_reader)
    sr_number = first_row['SRNumber']
    group_name = first_row['GroupName']
    
# Define allowed zones
allowed_zones = {"WAN", "LAN", "MDT", "CLIENT LAN", "SYSINT", "SYSEXT", "SYSCLIENT", "DMZ"}
    
# Create Output File
with open(output_file_path, 'w') as output_file:
    # Enter Configuration Mode
    #output_file.write("configure\n")
    

    # Re-open the CSV file to read the rest of the rows
    with open(csv_file_path, newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        for row in csv_reader:
            ip_address = row['IPAddress']
            zone = row['Zone'].strip().upper()  # Convert zone to uppercase
            name = row.get('Name', '').strip()  # Get the Name value, allow null
            #sr_number = row.get('SRNumber', '').strip()  # Get the SRNumber value, allow null
            
                       
            # Check if the zone is allowed
            if zone not in allowed_zones:
                #skipped_rows.append(f"IP {ip_address} with zone {zone} is not allowed")
                continue  # Skip this row if the zone is not allowed
             # Remove trailing space if name is empty
            #sr_number = f"{sr_number} " if sr_number else ""
            
            name = f" {name}" if name and sr_number else name
            # Check if entry is a Network Address
            match = re.match(network_regex, ip_address)
            if match:
                ip_add, mask = ip_address.split('/')
                if mask == '32':
                    # Treat as a host IP address
                    ip_address_count += 1
                    if name:
                        output_file.write(f'address-object ipv4 "{sr_number}{name}" host {ip_add} zone {zone}\n')
                    else:
                        output_file.write(f'address-object ipv4 "{sr_number} {address_object_host_name}{ip_address_count}" host {ip_add} zone {zone}\n')
                else:
                    network_address_count += 1
                    if name:
                        output_file.write(f'address-object ipv4 "{sr_number}{name}" network {ip_add}/{mask} zone {zone}\n')
                    else:
                        output_file.write(f'address-object ipv4 "{sr_number} {address_object_network_name}{network_address_count}" network {ip_add}/{mask} zone {zone}\n')
            elif re.match(ip_with_subnet_regex, ip_address):
                ip_add, subnet_mask = ip_address.split('/')
                if subnet_mask == '255.255.255.255':
                    # Treat as a host IP address
                    ip_address_count += 1
                    if name:
                        output_file.write(f'address-object ipv4 "{sr_number}{name}" host {ip_add} zone {zone}\n')
                    else:
                        output_file.write(f'address-object ipv4 "{sr_number} {address_object_host_name}{ip_address_count}" host {ip_add} zone {zone}\n')
                else:
                    network_address_count += 1
                    if name:
                        output_file.write(f'address-object ipv4 "{sr_number}{name}" network {ip_add} \\{subnet_mask} zone {zone}\n')
                    else:
                        output_file.write(f'address-object ipv4 "{sr_number} {address_object_network_name}{network_address_count}" network {ip_add} \\{subnet_mask} zone {zone}\n')
            elif re.match(ip_regex, ip_address):
                ip_address_count += 1
                if name:
                    output_file.write(f'address-object ipv4 "{sr_number}{name}" host {ip_add} zone {zone}\n')
                else:
                    output_file.write(f'address-object ipv4 "{sr_number} {address_object_host_name}{ip_address_count}" host {ip_add} zone {zone}\n')
            elif re.match(fqdn_regex, ip_address):
                fqdn_count += 1
                if name:
                    output_file.write(f'address-object fqdn "{sr_number}{name}" domain {ip_address} zone {zone}\n')
                    output_file.write(f'domain "{ip_address}"\n')
                    output_file.write("exit\n")
                else:
                    output_file.write(f'address-object fqdn "{sr_number}{name} {address_object_fqdn_name}{fqdn_count}" domain {ip_address} zone {zone}\n')
                    output_file.write(f'domain "{ip_address}"\n')
                    output_file.write("exit\n")
    # Commit Changes
    output_file.write("commit\n")

# Add Address Objects to Address Group
    #sr_number = f" {sr_number}" if sr_number else ""           
        # Create or Modify the Address Group.
    group_name = f"{group_name} " if group_name and sr_number else group_name
    #sr_number = f" {sr_number}" if sr_number else ""
    output_file.write(f'address-group ipv4 "{group_name}{sr_number}"\n')
        # Reset the Address Counts
    fqdn_count = 0
    network_address_count = 0
    ip_address_count = 0
    
    # List to store skipped rows
    skipped_rows = []    

    # Go through the CSV entries again and generate the respective commands to add the Address Objects to the Address Group
    # Re-open the CSV file to read the rest of the rows
    with open(csv_file_path, newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        csv_file.seek(0)
        for row in csv_reader:
            ip_address = row['IPAddress']
            zone = row['Zone'].strip().upper()
            name = row.get('Name', '').strip()
            #sr_number = row.get('SRNumber', '').strip()
            
            # Check if the IPAddress has a value and the zone is not in the allowed zones or is empty
            if ip_address and (not zone or zone not in allowed_zones):
                skipped_rows.append(f"IP/Domain {ip_address} with zone {zone} is not allowed")
                continue
            
            # Remove trailing space if name is empty
            #name = f" {name}" if name else ""
            name = f" {name}" if name and sr_number else name
            
             # Check if entry is a Network Address
            match = re.match(network_regex, ip_address)
            if match:
                ip_add, mask = ip_address.split('/')
                if mask == '32':
                    # Treat as a host IP address
                    ip_address_count += 1
                    if name:
                        output_file.write(f'address-object ipv4 "{sr_number}{name}"\n')
                    else:
                        output_file.write(f'address-object ipv4 "{sr_number} {address_object_host_name}{ip_address_count}"\n')
                else:
                    network_address_count += 1
                    if name:
                        output_file.write(f'address-object ipv4 "{sr_number}{name}"\n')
                    else:
                        output_file.write(f'address-object ipv4 "{sr_number} {address_object_network_name}{network_address_count}"\n')
            elif re.match(ip_with_subnet_regex, ip_address):
                ip_add, subnet_mask = ip_address.split('/')
                if subnet_mask == '255.255.255.255':
                    # Treat as a host IP address
                    ip_address_count += 1
                    if name:
                        output_file.write(f'address-object ipv4 "{sr_number}{name}"\n')
                    else:
                        output_file.write(f'address-object ipv4 "{sr_number} {address_object_host_name}{ip_address_count}"\n')
                else:
                    network_address_count += 1
                    if name:
                        output_file.write(f'address-object ipv4 "{sr_number}{name}"\n')
                    else:
                        output_file.write(f'address-object ipv4 "{sr_number} {address_object_network_name}{network_address_count}"\n')
            elif re.match(ip_regex, ip_address):
                ip_address_count += 1
                if name:
                    output_file.write(f'address-object ipv4 "{sr_number}{name}"\n')
                else:
                    output_file.write(f'address-object ipv4 "{sr_number} {address_object_host_name}{ip_address_count}"\n')
            elif re.match(fqdn_regex, ip_address):
                fqdn_count += 1
                if name:
                    output_file.write(f'address-object fqdn "{sr_number}{name}"\n')
                else:
                    output_file.write(f'address-object fqdn "{sr_number}{name} {address_object_fqdn_name}{fqdn_count}"\n')
        
    # Exit the Address Group configuration
    output_file.write("exit\n")
    # Commit Changes
    output_file.write("commit\n")
        
    # Write skipped rows at the end of the output file
    if skipped_rows:
        output_file.write("\n# Skipped rows:\n")
        for skipped_row in skipped_rows:
            output_file.write(f"# {skipped_row}\n")