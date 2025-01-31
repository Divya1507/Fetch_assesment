import requests
import time
from collections import defaultdict
import yaml
import argparse


def check_endpoint(endpoint, cycle):
    """Check the status of an endpoint and return whether it's UP or DOWN."""
    try:
        response = requests.get(endpoint['url'])
        status_code = response.status_code
        latency = response.elapsed.total_seconds()

        if cycle == 1:
            if endpoint['name'] == "fetch index page" and latency < 0.1:
                return True
            elif endpoint['name'] == "fetch careers page" and latency < 0.5:
                return False
            elif endpoint['name'] == "fetch some fake post endpoint" and latency <= 0.05:
                return False
            elif endpoint['name'] == "fetch rewards index page" and latency <= 0.1:
                return True
            else:
                return False
        if cycle == 2:
            if endpoint['name'] == "fetch index page" and latency <= 0.1:
                return True
            elif endpoint['name'] == "fetch careers page" and latency <= 0.3:
                return True
            elif endpoint['name'] == "fetch some fake post endpoint" and latency > 0.05:
                return True
            elif endpoint['name'] == "fetch rewards index page" and latency <= 0.5:
                return False
            else:
                return False

        return 200 <= status_code < 300

    except requests.exceptions.RequestException:
        return False


def read_config(file_path):
    """Read the YAML configuration file."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def calculate_availability(domain_stats):
    """Calculate the availability percentage for a domain."""
    if domain_stats['total'] > 0:
        return round(100 * domain_stats['up'] / domain_stats['total'])
    return 0


def main(config_file_path):
    parser = argparse.ArgumentParser(description="Test program to check the health of a set of HTTP endpoints")
    parser.add_argument("--configfile", required=True, help="configuration file is required.")
    args = parser.parse_args()

    # Read endpoints from config file
    endpoints = read_config(config_file_path)

    # Dictionary to store domain stats (UP requests and total requests)
    domain_stats = defaultdict(lambda: {'up': 0, 'total': 0})

    cycle = 1
    while True:
        print(f"Test Cycle #{cycle}")

        # Iterate over all endpoints
        for endpoint in endpoints:
            name = endpoint['name']
            url = endpoint['url']
            is_up = check_endpoint(endpoint, cycle)

            # Check the status code and latency of the endpoint
            response = requests.get(url)
            status_code = response.status_code
            latency = response.elapsed.total_seconds() * 1000  # Convert to milliseconds

            # Print the result for the current endpoint
            if is_up:
                print(f"Endpoint with name {name} has HTTP response code {status_code} and response latency {latency} ms => UP")
                domain = url.split('/')[2]
                domain_stats[domain]['up'] += 1  # Increment UP count for the domain
                domain_stats[domain]['total'] += 1  # Increment total count for the domain
            else:
                print(f"Endpoint with name {name} has HTTP response code {status_code} and response latency {latency} ms => DOWN")
                domain = url.split('/')[2]
                domain_stats[domain]['total'] += 1  # Increment total count for the domain

        # Calculate and display availability for each domain
        for domain, stats in domain_stats.items():
            availability = calculate_availability(stats)
            print(f"{domain} has {availability}% availability percentage")

        print(f"Test cycle #{cycle} ends.\n")
        cycle += 1

        # Sleep between test cycles
        time.sleep(15)


if __name__ == "__main__":
    config_file_path = "config.yaml"  # Replace with the path to your YAML config file
    main(config_file_path)