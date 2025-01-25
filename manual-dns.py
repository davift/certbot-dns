#!/usr/bin/env python3
import sys
import os

def main():
    # Get the Certbot environment variables
    domain = os.getenv("CERTBOT_DOMAIN")
    validation = os.getenv("CERTBOT_VALIDATION")

    if len(sys.argv) == 2:
        hook_type = sys.argv[1] 

        if hook_type == "auth":
            # Create a TXT record in DNS
            print(f"Add the following TXT record to your DNS:")
            print(f"_acme-challenge.{domain} IN TXT \"{validation}\"")
            input("Enter to continue...")
            sys.exit()
        elif hook_type == "cleanup":
            # Optionally, instruct the user to remove the TXT record
            print(f"Remove the TXT record for _acme-challenge.{domain} from your DNS.")
            sys.exit()

    print("Usage: script.py <auth|cleanup>")
    sys.exit(1)

if __name__ == "__main__":
    main()
