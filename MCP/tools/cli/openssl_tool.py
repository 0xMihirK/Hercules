"""
OpenSSL MCP Tool — TLS/SSL certificate and connection tools.
"""
from __future__ import annotations
from typing import Annotated, Literal
from tools._base import require_tool, run_command, sanitize_arg, sanitize_target

def register_openssl_tools(mcp):

    @mcp.tool(tags={'cli', 'tls', 'openssl', 'certificate'}, annotations={'title': 'OpenSSL Certificate Info', 'readOnlyHint': True, 'openWorldHint': False})
    async def cli_openssl_cert_info(cert_file: Annotated[str, 'Path to certificate file (PEM or DER)'], der_format: Annotated[bool, 'Certificate is in DER format (default: PEM)']=False, show_text: Annotated[bool, 'Show human-readable text representation']=True, show_subject: Annotated[bool, 'Show subject only']=False, show_issuer: Annotated[bool, 'Show issuer only']=False, show_dates: Annotated[bool, 'Show validity dates only']=False, show_serial: Annotated[bool, 'Show serial number only']=False, show_fingerprint: Annotated[bool, 'Show fingerprint']=False, show_extensions: Annotated[bool, 'Show X509v3 extensions']=False, cmd_timeout: Annotated[int, 'Command timeout in seconds']=30, wait_for_previous: bool=False) -> dict:
        """Inspect an X.509 certificate file."""
        require_tool('openssl')
        args = ['openssl', 'x509', '-in', sanitize_arg(cert_file, 'cert_file'), '-noout']
        if der_format:
            args.extend(['-inform', 'DER'])
        if show_text:
            args.append('-text')
        if show_subject:
            args.append('-subject')
        if show_issuer:
            args.append('-issuer')
        if show_dates:
            args.append('-dates')
        if show_serial:
            args.append('-serial')
        if show_fingerprint:
            args.append('-fingerprint')
        if show_extensions:
            args.append('-ext')
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'output': result.stdout, 'errors': result.stderr}

    @mcp.tool(tags={'cli', 'tls', 'openssl'}, annotations={'title': 'OpenSSL TLS Connect', 'readOnlyHint': True, 'openWorldHint': True})
    async def cli_openssl_connect(host: Annotated[str, 'Target hostname'], port: Annotated[int, 'Target port']=443, servername: Annotated[str | None, 'SNI hostname']=None, protocol: Annotated[Literal['tls1', 'tls1_1', 'tls1_2', 'tls1_3'] | None, 'Force TLS protocol version']=None, ciphers: Annotated[str | None, 'Cipher suite string']=None, show_certs: Annotated[bool, 'Display full certificate chain']=True, verify: Annotated[bool, 'Verify server certificate']=True, starttls: Annotated[str | None, 'STARTTLS protocol (smtp, imap, pop3, ftp, xmpp)']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=30, wait_for_previous: bool=False) -> dict:
        """Test a TLS/SSL connection to a server and inspect its certificate."""
        require_tool('openssl')
        args = ['openssl', 's_client', '-connect', f'{sanitize_target(host)}:{port}']
        if servername:
            args.extend(['-servername', sanitize_arg(servername, 'servername')])
        if protocol:
            args.append(f'-{protocol}')
        if ciphers:
            args.extend(['-cipher', sanitize_arg(ciphers, 'ciphers')])
        if show_certs:
            args.append('-showcerts')
        if not verify:
            args.append('-verify_quiet')
        if starttls:
            args.extend(['-starttls', sanitize_arg(starttls, 'starttls')])
        result = await run_command(args, timeout=cmd_timeout, stdin_data='Q\n')
        return {'command': result.command, 'return_code': result.return_code, 'output': result.stdout, 'errors': result.stderr}

    @mcp.tool(tags={'cli', 'tls', 'openssl', 'crypto'}, annotations={'title': 'OpenSSL Generate Key/CSR/Cert', 'readOnlyHint': False, 'openWorldHint': False})
    async def cli_openssl_generate(action: Annotated[Literal['key', 'csr', 'self-signed'], 'What to generate'], key_type: Annotated[Literal['rsa', 'ec'], 'Key type']='rsa', key_size: Annotated[int, 'RSA key size in bits']=2048, ec_curve: Annotated[str, 'EC curve name']='prime256v1', subject: Annotated[str | None, "Certificate subject (e.g. '/CN=example.com/O=Org')"]=None, days: Annotated[int, 'Validity period in days (for self-signed)']=365, output_key: Annotated[str | None, 'Output path for private key']=None, output_cert: Annotated[str | None, 'Output path for certificate/CSR']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=30, wait_for_previous: bool=False) -> dict:
        """Generate cryptographic keys, CSRs, or self-signed certificates."""
        require_tool('openssl')
        results = []
        key_out = output_key or '/dev/stdout'
        cert_out = output_cert or '/dev/stdout'
        if action == 'key':
            if key_type == 'rsa':
                args = ['openssl', 'genrsa', '-out', key_out, str(key_size)]
            else:
                args = ['openssl', 'ecparam', '-genkey', '-name', ec_curve, '-out', key_out]
            r = await run_command(args, timeout=cmd_timeout)
            results.append(r.to_dict())
        elif action in ('csr', 'self-signed'):
            key_out = output_key or '/tmp/generated_key.pem'
            if key_type == 'rsa':
                r = await run_command(['openssl', 'genrsa', '-out', key_out, str(key_size)], timeout=cmd_timeout)
            else:
                r = await run_command(['openssl', 'ecparam', '-genkey', '-name', ec_curve, '-out', key_out], timeout=cmd_timeout)
            results.append(r.to_dict())
            if action == 'csr':
                args = ['openssl', 'req', '-new', '-key', key_out, '-out', cert_out]
            else:
                args = ['openssl', 'req', '-new', '-x509', '-key', key_out, '-out', cert_out, '-days', str(days)]
            if subject:
                args.extend(['-subj', subject])
            else:
                args.extend(['-subj', '/CN=localhost'])
            r = await run_command(args, timeout=cmd_timeout)
            results.append(r.to_dict())
        return {'steps': results}