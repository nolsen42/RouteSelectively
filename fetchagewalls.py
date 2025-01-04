# This script is designed to fetch the URL and subdomains of adult websites, and catch any URLs that may be using age checking/geoip.
# This script is experimental and a W.I.P

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import urllib3
import validators

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set to store unique domains
unique_domains = set()

def get_base_domain(url):
    parsed_url = urlparse(url)
    netloc_parts = parsed_url.netloc.split('.')
    if len(netloc_parts) > 2:
        # Handles subdomains like sub.example.com -> example.com
        return '.'.join(netloc_parts[-2:])
    return parsed_url.netloc  # Returns the original if no subdomain exists


def log_unique_url(url, file_name):
    # Extract the domain of the URL
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    # Check if the domain is already in the set
    if len(domain) > 2:
        if domain not in unique_domains:
            unique_domains.add(domain)  # Add domain to the set
            with open(file_name, "a") as file:
                if file.tell() == 0:  # Check if file is empty
                    file.write(domain)  # Write without newline if file is empty
                else:
                    file.write("\n" + domain)  # Append with newline
            print(f"Added new domain: {domain}")


def fetch_resources(url, keyword, grab_all, go_nuclear):
    base_domain = get_base_domain(url)
    # Dictionary to store resources in memory
    resource_cache = {}

    print(f"Fetching URL: {url}")
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        print(f"Error fetching the main page: {url} - {e}")
        return

    print("Parsing HTML...")
    soup = BeautifulSoup(html_content, 'html.parser')

    # Collect resource URLs
    resources = []
    nuclear_count = 0
    for tag, attr in [('script', 'src'), ('link', 'href'), ('img', 'src')]:
        for resource in soup.find_all(tag):
            resource_url = resource.get(attr)
            if resource_url:
                resources.append(urljoin(url, resource_url))

    # Fetch and store resources with progress bar
    print("Fetching resources...")
    for resource_url in tqdm(resources, desc="Fetching", unit="file"):
        try:
            res = requests.get(resource_url, verify=False)
            res.raise_for_status()
            # Store content in memory
            resource_cache[resource_url] = res.text
        except Exception as e:
            print(f"Error fetching resource: {resource_url} - {e}")

    print("Scanning resources...")
    for name, content in tqdm(resource_cache.items(), desc="Scanning", unit="file"):
        if keyword.lower() in content.lower():
            log_unique_url(name, f"{base_domain}.txt")

        elif grab_all or go_nuclear:
            parsed_url = urlparse(name)
            full_domain = parsed_url.netloc 
            if full_domain.endswith(base_domain):
                log_unique_url(resource_url, f"{base_domain}.txt")
            elif go_nuclear:
                if full_domain not in unique_domains:
                    nuclear_count += 1
                    log_unique_url(resource_url, f"{base_domain}.nuclear.txt")
    print(f"{len(unique_domains)} domain(s) has been added to {base_domain}.txt")
    if go_nuclear and nuclear_count != 0:
        print(f"\nSince you chose to go nuclear on querying, it is separated at {base_domain}.nuclear.txt\n{nuclear_count} Unrelated domain(s) has been added to the list.")
    elif go_nuclear and nuclear_count == 0:
        print("You chose to go nuclear on querying, but no unrelated domains was found.")


if __name__ == "__main__":
    try:
        website_url = None
        while not website_url:
            website_url = input("Enter website URL (must include the http(s)://): ")
            if not validators.url(website_url):
                print("Error: Invalid URL format.")
                exit("\n")

        search_keyword = input("Enter keyword to search for (optional, by default it would search for \"age\"): ")
        grab_all = None
        while not grab_all:
            grab_all_choice = input(f"(Recommended) Grab all domains and subdomains related to {website_url}, regardless of the search keyword? (Y/N): ")
            if "y" in grab_all_choice.lower():
                grab_all = True
                break
            if "n" in grab_all_choice.lower():
                grab_all = False
                break
            else:
                print("Invalid option, please type (Y)es or (N)o")
        go_nuclear = None
        while not go_nuclear:
            go_nuclear_choice = input(f"(Not Recommended, Nuclear/Aggressive option) Grab ALL domains found upon query, regardless of relation or keyword (THIS WILL CATCH **EVERYTHING** IT FINDS) (Y/N): ")
            if "y" in go_nuclear_choice.lower():
                go_nuclear = True
                break
            if "n" in go_nuclear_choice.lower():
                go_nuclear = False
                break
            else:
                print("Invalid option, please type (Y)es or (N)o")
        if not search_keyword:
            search_keyword = "age"
        fetch_resources(website_url, search_keyword, grab_all, go_nuclear)
    except KeyboardInterrupt:
        exit("\n")
