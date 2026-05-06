"""
grep / awk / sed MCP Tools — Text processing utilities.
"""
from __future__ import annotations
from typing import Annotated, Literal
from tools._base import require_tool, run_command, sanitize_arg

def register_grep_awk_sed_tools(mcp):

    @mcp.tool(tags={'cli', 'text-processing', 'grep'}, annotations={'title': 'grep — Pattern Search', 'readOnlyHint': True, 'openWorldHint': False})
    async def cli_grep_search(pattern: Annotated[str, 'Search pattern (regex by default)'], file_path: Annotated[str | None, 'Path to file or directory to search']=None, input_text: Annotated[str | None, 'Text to search through (piped via stdin)']=None, recursive: Annotated[bool, 'Search directories recursively (-r)']=False, case_insensitive: Annotated[bool, 'Case-insensitive matching (-i)']=False, fixed_strings: Annotated[bool, 'Treat pattern as fixed string, not regex (-F)']=False, extended_regex: Annotated[bool, 'Use extended regex (-E)']=False, perl_regex: Annotated[bool, 'Use Perl-compatible regex (-P)']=False, invert: Annotated[bool, 'Invert match — show non-matching lines (-v)']=False, count_only: Annotated[bool, 'Only print count of matching lines (-c)']=False, line_number: Annotated[bool, 'Show line numbers (-n)']=True, files_only: Annotated[bool, 'Only print filenames with matches (-l)']=False, context_before: Annotated[int | None, 'Lines of context before match (-B)']=None, context_after: Annotated[int | None, 'Lines of context after match (-A)']=None, context: Annotated[int | None, 'Lines of context around match (-C)']=None, max_count: Annotated[int | None, 'Stop after N matches (-m)']=None, include_glob: Annotated[str | None, 'Only search files matching glob (--include)']=None, exclude_glob: Annotated[str | None, 'Exclude files matching glob (--exclude)']=None, word_match: Annotated[bool, 'Match whole words only (-w)']=False, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=60, wait_for_previous: bool=False) -> dict:
        """Search for patterns in files or text using grep."""
        require_tool('grep')
        args = ['grep']
        if case_insensitive:
            args.append('-i')
        if fixed_strings:
            args.append('-F')
        if extended_regex:
            args.append('-E')
        if perl_regex:
            args.append('-P')
        if recursive:
            args.append('-r')
        if invert:
            args.append('-v')
        if count_only:
            args.append('-c')
        if line_number:
            args.append('-n')
        if files_only:
            args.append('-l')
        if word_match:
            args.append('-w')
        if context_before:
            args.extend(['-B', str(context_before)])
        if context_after:
            args.extend(['-A', str(context_after)])
        if context:
            args.extend(['-C', str(context)])
        if max_count:
            args.extend(['-m', str(max_count)])
        if include_glob:
            args.extend(['--include', include_glob])
        if exclude_glob:
            args.extend(['--exclude', exclude_glob])
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        args.append(pattern)
        if file_path:
            args.append(sanitize_arg(file_path, 'file_path'))
        result = await run_command(args, timeout=cmd_timeout, stdin_data=input_text)
        return {'command': result.command, 'return_code': result.return_code, 'match_count': len(result.stdout.splitlines()), 'output': result.stdout, 'errors': result.stderr}

    @mcp.tool(tags={'cli', 'text-processing', 'awk'}, annotations={'title': 'awk — Text Processing', 'readOnlyHint': True, 'openWorldHint': False})
    async def cli_awk_process(program: Annotated[str, "AWK program/expression (e.g. '{print $1, $3}')"], file_path: Annotated[str | None, 'Path to input file']=None, input_text: Annotated[str | None, 'Text to process (piped via stdin)']=None, field_separator: Annotated[str | None, 'Field separator (-F)']=None, variables: Annotated[str | None, "Variables as 'var=value' pairs, separated by '||'"]=None, program_file: Annotated[str | None, 'Path to AWK program file (-f)']=None, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=60, wait_for_previous: bool=False) -> dict:
        """Process text using AWK pattern-action programs."""
        require_tool('awk')
        args = ['awk']
        if field_separator:
            args.extend(['-F', field_separator])
        if variables:
            for v in variables.split('||'):
                args.extend(['-v', v.strip()])
        if program_file:
            args.extend(['-f', sanitize_arg(program_file, 'program_file')])
        else:
            args.append(program)
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        if file_path:
            args.append(sanitize_arg(file_path, 'file_path'))
        result = await run_command(args, timeout=cmd_timeout, stdin_data=input_text)
        return {'command': result.command, 'return_code': result.return_code, 'output': result.stdout, 'errors': result.stderr}

    @mcp.tool(tags={'cli', 'text-processing', 'sed'}, annotations={'title': 'sed — Stream Editor', 'readOnlyHint': True, 'openWorldHint': False})
    async def cli_sed_transform(expression: Annotated[str, "sed expression (e.g. 's/old/new/g', '/pattern/d')"], file_path: Annotated[str | None, 'Path to input file']=None, input_text: Annotated[str | None, 'Text to transform (piped via stdin)']=None, in_place: Annotated[bool, 'Edit file in place (-i)']=False, in_place_backup: Annotated[str | None, 'In-place edit with backup suffix (-i.bak)']=None, extended_regex: Annotated[bool, 'Use extended regex (-E)']=False, quiet: Annotated[bool, 'Suppress automatic printing (-n)']=False, multiple_expressions: Annotated[str | None, "Additional expressions separated by '||'"]=None, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=60, wait_for_previous: bool=False) -> dict:
        """Transform text using sed stream editor."""
        require_tool('sed')
        args = ['sed']
        if extended_regex:
            args.append('-E')
        if quiet:
            args.append('-n')
        if in_place:
            args.append('-i')
        elif in_place_backup:
            args.append(f'-i{in_place_backup}')
        args.extend(['-e', expression])
        if multiple_expressions:
            for e in multiple_expressions.split('||'):
                args.extend(['-e', e.strip()])
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        if file_path:
            args.append(sanitize_arg(file_path, 'file_path'))
        result = await run_command(args, timeout=cmd_timeout, stdin_data=input_text)
        return {'command': result.command, 'return_code': result.return_code, 'output': result.stdout, 'errors': result.stderr}