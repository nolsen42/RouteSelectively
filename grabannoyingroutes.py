# The purpose of this script is to grab the million or so CDNs that a website may have, which is usually a pattern but have a different digit in the URL.
# You will need to customize this script to fit with the domain you need to fetch.
# Once it has outputted all the domains it found, just manually add them to domains.txt

import subprocess

# Base domain pattern
base_domain = "w{}.example.com"

# Range of numbers to replace {}
start = 0
end = 99  # Adjust this as needed

def check_subdomains(start, end):
    for i in range(start, end + 1):
        domain = base_domain.format(i)
        result = subprocess.run(['dig', '+short', domain], capture_output=True, text=True)
        ips = result.stdout.strip().splitlines()
        
        if ips:
            print(f"{domain}")

check_subdomains(start, end)
