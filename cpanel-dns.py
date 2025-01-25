#!/usr/bin/env python3
import sys
import os
import time
import requests

# cPanel parameters
api_host = os.getenv("CPANEL_API_HOST")
api_user = os.getenv("CPANEL_API_USER")
api_token = os.getenv("CPANEL_API_TOKEN")
domain = os.getenv("CERTBOT_DOMAIN")
validation = os.getenv("CERTBOT_VALIDATION")

def call_cpanel_api(endpoint, params):
    common_params = {
        'cpanel_jsonapi_user': api_user,
        'cpanel_jsonapi_apiversion': '2',
    }
    params.update(common_params)
    headers = { 'Authorization': f'cPanel {api_user}:{api_token}' }
    url = f"{api_host}/json-api/{endpoint}"
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to call cPanel API: {e}")
        sys.exit(1)
    if response.status_code != 200:
        print(f"Error: API call failed with status code {response.status_code} - {response.text}")
        sys.exit(1)
    return response.json()

def add_dns_record(domain, validation):
    fetch_params = {
        'cpanel_jsonapi_module': 'ZoneEdit',
        'cpanel_jsonapi_func': 'fetchzone_records',
        'domain': domain
    }
    response = call_cpanel_api('cpanel', fetch_params)
    records = response.get('cpanelresult', {}).get('data', [])
    
    existing_record_id = None
    for record in records:
        if record['name'] == f"_acme-challenge.{domain}." and record['type'] == 'TXT':
            existing_record_id = record['line']
            break

    if existing_record_id:
        # Update if existing
        params = {
            'cpanel_jsonapi_module': 'ZoneEdit',
            'cpanel_jsonapi_func': 'edit_zone_record',
            'domain': domain,
            'line': existing_record_id,
            'name': f"_acme-challenge.{domain}",
            'type': 'TXT',
            'txtdata': validation,
            'ttl': 120
        }
    else:
        # Add if none exists
        params = {
            'cpanel_jsonapi_module': 'ZoneEdit',
            'cpanel_jsonapi_func': 'add_zone_record',
            'domain': domain,
            'name': f"_acme-challenge.{domain}",
            'type': 'TXT',
            'txtdata': validation,
            'ttl': 120
        }
    call_cpanel_api('cpanel', params)

def remove_dns_record(domain):
    params = {
        'cpanel_jsonapi_module': 'ZoneEdit',
        'cpanel_jsonapi_func': 'fetchzone_records',
        'domain': domain
    }
    response = call_cpanel_api('cpanel', params)
    # Find the record ID to delete
    records = response.get('cpanelresult', {}).get('data', [])
    record_id = None
    for record in records:
        if record['name'] == f"_acme-challenge.{domain}." and record['type'] == 'TXT':
            record_id = record['line']
            break
    if not record_id:
        print("No matching DNS record found to remove.")
        return
    delete_params = {
        'cpanel_jsonapi_module': 'ZoneEdit',
        'cpanel_jsonapi_func': 'remove_zone_record',
        'domain': domain,
        'line': record_id
    }
    call_cpanel_api('cpanel', delete_params)

def main():
    if len(sys.argv) == 2:
        hook_type = sys.argv[1]
        if hook_type == "auth":
            add_dns_record(domain, validation)
            time.sleep(60) 
            sys.exit()
        elif hook_type == "cleanup":
            remove_dns_record(domain)
            sys.exit()
    print("Usage: script.py <auth|cleanup>")
    sys.exit(1)

if __name__ == "__main__":
    main()
