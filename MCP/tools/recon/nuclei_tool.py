"""
Nuclei MCP Tool — Vulnerability scanner with custom template support.

Provides:
- recon_nuclei_scan: run scans with built-in or custom templates
- recon_nuclei_template_create: write custom YAML templates
- recon_nuclei_template_list: list available custom templates
- recon_nuclei_template_validate: validate a template before using it
"""
from __future__ import annotations
import contextlib
import os
from typing import Annotated, Literal
from tools._base import TEMPLATES_DIR, parse_json_lines, require_tool, run_command, sanitize_arg, sanitize_target
NUCLEI_TEMPLATES_DIR = TEMPLATES_DIR / 'nuclei'
NUCLEI_TEMPLATES_DIR.mkdir(exist_ok=True)

def register_nuclei_tools(mcp):
    """Register all Nuclei tools on the given FastMCP instance."""

    @mcp.tool(tags={'recon', 'scanning', 'nuclei', 'vulnerability'}, annotations={'title': 'Nuclei Vulnerability Scanner', 'readOnlyHint': True, 'openWorldHint': True})
    async def recon_nuclei_scan(target: Annotated[str, 'Target URL or host to scan'], target_list: Annotated[str | None, 'Path to file containing list of targets']=None, templates: Annotated[str | None, 'Comma-separated template IDs or paths']=None, template_tags: Annotated[str | None, "Comma-separated tags to filter templates (e.g. 'cve,rce')"]=None, exclude_tags: Annotated[str | None, 'Tags to exclude']=None, severity: Annotated[str | None, 'Filter by severity: info, low, medium, high, critical (comma-sep)']=None, template_type: Annotated[str | None, 'Protocol type filter: http, dns, file, network, headless']=None, author: Annotated[str | None, 'Filter templates by author']=None, template_id: Annotated[str | None, 'Filter by template ID (comma-separated)']=None, exclude_id: Annotated[str | None, 'Exclude template IDs']=None, use_custom_templates: Annotated[bool, 'Include custom templates from templates/nuclei/ dir']=False, custom_template_path: Annotated[str | None, 'Path to a specific custom template file']=None, new_templates: Annotated[bool, 'Run only new templates added in latest release']=False, automatic_scan: Annotated[bool, 'Automatic web scan using Wappalyzer technology detection (-as)']=False, headless: Annotated[bool, 'Enable headless browser-based templates']=False, rate_limit: Annotated[int | None, 'Maximum requests per second']=None, bulk_size: Annotated[int | None, 'Maximum hosts to process in parallel']=None, concurrency: Annotated[int | None, 'Maximum templates to execute in parallel']=None, retries: Annotated[int | None, 'Number of retries for failed requests']=None, timeout_secs: Annotated[int | None, 'Timeout for each request in seconds']=None, proxy: Annotated[str | None, 'HTTP/SOCKS5 proxy URL']=None, headers: Annotated[str | None, "Custom headers (Header: Value). Sep multiple with '||'"]=None, follow_redirects: Annotated[bool, 'Follow HTTP redirects']=False, max_redirects: Annotated[int | None, 'Maximum number of redirects to follow']=None, interactsh_server: Annotated[str | None, 'Custom Interactsh server URL for OOB testing']=None, no_interactsh: Annotated[bool, 'Disable Interactsh server for OOB testing']=False, json_output: Annotated[bool, 'Output in JSON format']=True, silent: Annotated[bool, 'Show only results in output']=False, verbose: Annotated[bool, 'Show verbose output']=False, no_color: Annotated[bool, 'Disable output coloring']=True, system_resolvers: Annotated[bool, 'Use system DNS resolvers as error fallback']=False, env_vars: Annotated[str | None, 'Environment vars for templates (key=val,key=val)']=None, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=600, wait_for_previous: bool=False) -> dict:
        """
        Run a Nuclei vulnerability scan against target(s).

        Supports built-in templates, custom templates, tag/severity/type filtering,
        rate limiting, proxy, Interactsh OOB testing, and JSON output parsing.
        """
        require_tool('nuclei')
        args = ['nuclei']
        if target_list:
            args.extend(['-l', sanitize_arg(target_list, 'target_list')])
        else:
            args.extend(['-u', sanitize_target(target)])
        if templates:
            args.extend(['-t', sanitize_arg(templates, 'templates')])
        if use_custom_templates:
            args.extend(['-t', str(NUCLEI_TEMPLATES_DIR)])
        if custom_template_path:
            args.extend(['-t', sanitize_arg(custom_template_path, 'custom_template_path')])
        if template_tags:
            args.extend(['-tags', sanitize_arg(template_tags, 'tags')])
        if exclude_tags:
            args.extend(['-etags', sanitize_arg(exclude_tags, 'exclude_tags')])
        if severity:
            args.extend(['-severity', sanitize_arg(severity, 'severity')])
        if template_type:
            args.extend(['-type', sanitize_arg(template_type, 'type')])
        if author:
            args.extend(['-author', sanitize_arg(author, 'author')])
        if template_id:
            args.extend(['-id', sanitize_arg(template_id, 'template_id')])
        if exclude_id:
            args.extend(['-eid', sanitize_arg(exclude_id, 'exclude_id')])
        if new_templates:
            args.append('-nt')
        if automatic_scan:
            args.append('-as')
        if headless:
            args.append('-headless')
        if rate_limit:
            args.extend(['-rl', str(rate_limit)])
        if bulk_size:
            args.extend(['-bs', str(bulk_size)])
        if concurrency:
            args.extend(['-c', str(concurrency)])
        if retries:
            args.extend(['-retries', str(retries)])
        if timeout_secs:
            args.extend(['-timeout', str(timeout_secs)])
        if proxy:
            args.extend(['-proxy', sanitize_arg(proxy, 'proxy')])
        if headers:
            for h in headers.split('||'):
                args.extend(['-H', h.strip()])
        if follow_redirects:
            args.append('-fr')
        if max_redirects:
            args.extend(['-mr', str(max_redirects)])
        if interactsh_server:
            args.extend(['-iserver', sanitize_arg(interactsh_server, 'interactsh')])
        if no_interactsh:
            args.append('-ni')
        if json_output:
            args.append('-jsonl')
        if silent:
            args.append('-silent')
        if verbose:
            args.append('-v')
        if no_color:
            args.append('-nc')
        if system_resolvers:
            args.append('-sr')
        if env_vars:
            args.extend(['-env-vars', sanitize_arg(env_vars, 'env_vars')])
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        result = await run_command(args, timeout=cmd_timeout)
        findings = []
        if json_output and result.stdout:
            findings = parse_json_lines(result.stdout)
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'findings_count': len(findings), 'findings': findings, 'raw_output': result.stdout if not findings else '', 'errors': result.stderr}

    @mcp.tool(tags={'recon', 'scanning', 'nuclei', 'vulnerability'}, annotations={'title': 'Nuclei Custom Scan (Direct YAML)', 'readOnlyHint': False, 'openWorldHint': True})
    async def recon_nuclei_scan_custom(target: Annotated[str, 'Target URL or host to scan'], template_yaml: Annotated[str, 'Full YAML content of the custom Nuclei template'], target_list: Annotated[str | None, 'Path to file containing list of targets']=None, rate_limit: Annotated[int | None, 'Maximum requests per second']=None, timeout_secs: Annotated[int | None, 'Timeout for each request in seconds']=None, proxy: Annotated[str | None, 'HTTP/SOCKS5 proxy URL']=None, headers: Annotated[str | None, "Custom headers (Header: Value). Sep multiple with '||'"]=None, verbose: Annotated[bool, 'Show verbose output']=False, cmd_timeout: Annotated[int, 'Command timeout in seconds']=600, wait_for_previous: bool=False) -> dict:
        """
        Write a custom Nuclei YAML template and immediately run it against a target.
        An all-in-one convenience tool avoiding the two-step create+scan process.
        """
        import uuid
        safe_name = f'custom_scan_{uuid.uuid4().hex[:8]}.yaml'
        filepath = NUCLEI_TEMPLATES_DIR / safe_name
        filepath.write_text(template_yaml, encoding='utf-8')
        try:
            return await recon_nuclei_scan(target=target, target_list=target_list, custom_template_path=str(filepath), rate_limit=rate_limit, timeout_secs=timeout_secs, proxy=proxy, headers=headers, verbose=verbose, cmd_timeout=cmd_timeout)
        finally:
            with contextlib.suppress(FileNotFoundError):
                filepath.unlink()

    @mcp.tool(tags={'recon', 'nuclei', 'template'}, annotations={'title': 'Nuclei Custom Template Creator', 'readOnlyHint': False, 'openWorldHint': False})
    async def recon_nuclei_template_create(template_name: Annotated[str, 'Template filename (without .yaml extension)'], template_content: Annotated[str, 'Full YAML content of the Nuclei template'], overwrite: Annotated[bool, 'Overwrite if template already exists']=False, wait_for_previous: bool=False) -> dict:
        """
        Create a custom Nuclei template file in the templates/nuclei/ directory.

        The agent can write any valid Nuclei YAML template — the full Nuclei
        template specification is supported.  After creation, use
        recon_nuclei_scan with use_custom_templates=True or
        custom_template_path to execute it.

        Example template structure:
        ```yaml
        id: my-custom-check
        info:
          name: My Custom Check
          author: agent
          severity: medium
          description: Custom vulnerability check
        http:
          - method: GET
            path:
              - "{{BaseURL}}/admin"
            matchers:
              - type: status
                status:
                  - 200
        ```
        """
        safe_name = sanitize_arg(template_name, 'template_name')
        if not safe_name.endswith('.yaml'):
            safe_name += '.yaml'
        filepath = NUCLEI_TEMPLATES_DIR / safe_name
        if filepath.exists() and (not overwrite):
            return {'success': False, 'error': f"Template '{safe_name}' already exists. Set overwrite=True to replace.", 'path': str(filepath)}
        filepath.write_text(template_content, encoding='utf-8')
        return {'success': True, 'path': str(filepath), 'message': f"Template '{safe_name}' created successfully."}

    @mcp.tool(tags={'recon', 'nuclei', 'template'}, annotations={'title': 'List Custom Nuclei Templates', 'readOnlyHint': True, 'openWorldHint': False})
    async def recon_nuclei_template_list(wait_for_previous: bool=False) -> dict:
        """
        List all custom Nuclei templates in the templates/nuclei/ directory.
        Returns the filename and first few lines of each template.
        """
        templates = []
        for f in sorted(NUCLEI_TEMPLATES_DIR.glob('*.yaml')):
            content = f.read_text(encoding='utf-8')
            preview = '\n'.join(content.splitlines()[:15])
            templates.append({'name': f.name, 'path': str(f), 'size_bytes': f.stat().st_size, 'preview': preview})
        return {'templates_dir': str(NUCLEI_TEMPLATES_DIR), 'count': len(templates), 'templates': templates}

    @mcp.tool(tags={'recon', 'nuclei', 'template'}, annotations={'title': 'Validate Nuclei Template', 'readOnlyHint': True, 'openWorldHint': False})
    async def recon_nuclei_template_validate(template_path: Annotated[str, 'Path to the template file to validate'], wait_for_previous: bool=False) -> dict:
        """
        Validate a Nuclei template for correctness before running it.
        Uses 'nuclei -validate' on the given template path.
        """
        require_tool('nuclei')
        result = await run_command(['nuclei', '-validate', '-t', sanitize_arg(template_path, 'template_path'), '-nc'], timeout=30)
        return {'command': result.command, 'valid': result.return_code == 0, 'output': result.stdout, 'errors': result.stderr}