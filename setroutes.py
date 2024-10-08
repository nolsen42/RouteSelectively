import subprocess

# ZeroTier info
exit_node_ip = "enter.your.zerotier.endpoint.ip"
interface = "ztly5x7b3u" # Edit this if needed.

def read_domains_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def resolve_ip(domain):
    result = subprocess.run(['dig', '+short', domain], capture_output=True, text=True)
    ips = result.stdout.splitlines()
    
    # Try to resolve CNAMEs if any
    resolved_ips = []
    for ip in ips:
        if is_valid_ip(ip):
            resolved_ips.append(ip)
        else:
            # If it's a domain (CNAME), resolve it recursively
            resolved_ips.extend(resolve_ip(ip))
    
    return resolved_ips

def is_valid_ip(ip):
    # Check for both IPv4 and IPv6 addresses
    try:
        parts = ip.split('.')
        if len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts):
            return True  # Valid IPv4
        return False
    except ValueError:
        return False

def add_routes_and_rules(ip):
    # Add route to zerotier table
    route_cmd = f"sudo ip route add {ip} via {exit_node_ip} dev {interface} table zerotier"
    subprocess.run(route_cmd, shell=True)
    
    # Add rule to lookup zerotier table
    rule_cmd = f"sudo ip rule add to {ip} lookup zerotier"
    subprocess.run(rule_cmd, shell=True)

def main():
    filename = "domains.txt" # Change this if you like.
    
    file_domains = read_domains_from_file(filename)
    
    domain_count = 0
    
    for domain in file_domains:
        print(f"Resolving IPs for {domain}:")
        ips = resolve_ip(domain)
        for ip in ips:
            print(f"Adding route and rule for IP: {ip}")
            add_routes_and_rules(ip)
            domain_count += 1

    print(f"All routes and rules added for {domain_count} domains.")

# Run the main function
if __name__ == "__main__":
    main()
