# certbot-dns

This project provides custom manual hooks for Certbot, enabling the issuance of SSL/TLS certificates with DNS challenges, including support for wildcard certificates.

## Usage

For manual creation of the DNS record.

```bash
certbot certonly \
    --manual \
    --dry-run \
    --preferred-challenges dns \
    --manual-auth-hook "/PATH/manual-dns.py auth" \
    --manual-cleanup-hook "/PATH/manual-dns.py cleanup" \
    -d 'example.com' \
    -d '*.example.com'
```

For integrating with cPanel API.

```bash
export CPANEL_API_HOST=''
export CPANEL_API_USER=''
export CPANEL_API_TOKEN=''

certbot certonly \
    --manual \
    --dry-run \
    --preferred-challenges dns \
    --manual-auth-hook "/PATH/cpanel-dns.py auth" \
    --manual-cleanup-hook "/PATH/cpanel-dns.py cleanup" \
    -d 'example.com' \
    -d '*.example.com'
```

Be sure to remove the --dry-run flag after testing to proceed with the actual certificate issuance.
