"""Skill-local native adapter; role/reference checks are not user approval.

The existing discussion record scopes the persistent native Skill hook. No
Runtime state, transcript inference or separate permission receipt is created.
"""
from pathlib import Path
import hashlib
import json
import re
import shlex
import sys

from handoff import packet

SKILL = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def probe(root, data):
    identity = data.get('probe_id', '')
    require(isinstance(identity, str) and re.fullmatch(r'[A-Za-z0-9_-]+', identity),
            'Use a single probe_id and a bounded direction brief.')
    for key, folder in [('prototype_write_scope', 'experiments'), ('evidence_write_scope', 'evidence')]:
        expected = root/'prototype'/folder/'probes'/identity
        require((root/data[key]).resolve() == expected,
                'Probe output belongs to its own experiments/probes and evidence/probes directories.')
    brief = data['brief']
    source = (root/brief['path']).resolve()
    require(source.is_relative_to(root) and source.suffix == '.md', 'Retain a Markdown probe brief inside the project.')
    expected_digest = brief['sha256'].removeprefix('sha256:')
    require(hashlib.sha256(source.read_bytes()).hexdigest() == expected_digest,
            'Probe brief digest changed; retain the intended brief before dispatch.')


def dispatch(args, active):
    require(args.get('isolation') != 'worktree',
            'Prototype helpers use the current project and exact packet scopes. Omit worktree isolation.')
    if args.get('subagent_type') == 'spec-prototype-critic':
        return
    require(args.get('subagent_type') == 'spec-prototype-builder',
            'Use the bounded spec-prototype-builder or spec-prototype-critic for this design work.')
    data = json.loads(args['prompt'])
    root = Path(data['repository_root']).resolve()
    require(root == active, 'Dispatch must stay in the active discussion repository.')
    require(Path(data['skill_root']).resolve() == SKILL,
            'Dispatch must use this same installed Skill root.')
    if data.get('mode') == 'direction-probe':
        probe(root, data)
    else:
        require(data == packet(root, data['specification']['path']),
                'Pass the exact handoff.py packet JSON unchanged to Builder.')


def shell_read(command, root):
    # A small argv seam, not a heuristic shell-write detector.
    require(not any(c in command for c in '\n\r;|&><`$'),
            'Use a single read command or installed helper; delegate shell execution to Builder.')
    args = shlex.split(command)
    require(bool(args), 'Missing command.')
    tool = args[0]
    if tool in {'pwd', 'ls', 'cat', 'head', 'tail', 'wc', 'rg'}:
        require(not any(a.startswith('--pre') for a in args[1:]), 'Use Read/Grep without an external preprocessor.')
        return
    if tool == 'git':
        require(args[1:] in (['status', '--short'], ['status', '--short', '--branch'],
                             ['rev-parse', '--show-toplevel']), 'Use the bounded Git status/root command.')
        return
    if tool in {'node', 'python3', 'python3.14'} and len(args) > 1:
        script = Path(args[1]).resolve()
        if tool in {'python3', 'python3.14'} and script == SKILL/'scripts/export-tokens.py':
            require(len(args) == 5 and args[3] == '--output',
                    'Token export requires one retained source and --output revision.json.')
            source, output = Path(args[2]), Path(args[4])
            require(source.is_absolute() and output.is_absolute(),
                    'Token export paths must be absolute.')
            require(source.parent.resolve() == root/'prototype/contracts/tokens'
                    and source.suffix == '.md' and source.is_file() and not source.is_symlink(),
                    'Export a retained Markdown token revision in this project.')
            require(not output.is_symlink() and output.resolve() == source.resolve().with_suffix('.json'),
                    'Token export belongs beside its source with the same revision name.')
            return
        permitted = {'node': {'detect-design-assets.mjs', 'resolve-change.mjs', 'preview.mjs'},
                     'python3': {'check-discussion.py', 'handoff.py', 'compile_tokens.py', 'verify_prototype_quality.py'},
                     'python3.14': {'check-discussion.py', 'handoff.py', 'compile_tokens.py', 'verify_prototype_quality.py'}}
        require(script.parent == SKILL/'scripts' and script.name in permitted[tool],
                'Only installed helpers run in the main designer; use Builder for code/setup.')
        if script.name == 'handoff.py' and 'freeze' in args:
            freeze_root = None
            if '--root' in args:
                idx = args.index('--root')
                if idx + 1 < len(args):
                    freeze_root = Path(args[idx + 1]).resolve()
            require(freeze_root == root.resolve(), 'Freeze command must target the active discussion root.')
        return
    raise ValueError('Use read-only tools or a bounded Builder for this command.')


def active_root(cwd):
    # Shell cwd may be a child directory. The nearest existing discussion owns
    # the scope; never infer lifecycle from a code file or tokens.
    for root in (cwd, *cwd.parents):
        record = root/'prototype/discussion.md'
        require(not record.is_symlink(), 'Discussion scope must be a regular project record, not a symlink.')
        if record.is_file():
            values = re.findall(r'^- Execution boundary: (active|released)\s*$', record.read_text(), re.M)
            if not values:
                return None  # Legacy records can be updated through native Write/Edit.
            if values == ['released']:
                return None
            require(values == ['active'], 'Record Execution boundary: active or released once in discussion.md.')
            return root
    return None


def discussion_record(cwd):
    for root in (cwd, *cwd.parents):
        record = root/'prototype/discussion.md'
        if record.is_file() or record.is_symlink():
            return record
    return None


def check(payload):
    require(isinstance(payload, dict), 'Invalid native tool event.')
    if payload.get('agent_type') in {'spec-prototype-builder', 'spec-prototype-critic'}:
        return
    tool = payload.get('tool_name')
    args = payload.get('tool_input', {})
    require(isinstance(args, dict), 'Invalid native tool input.')
    cwd = Path(payload['cwd']).resolve()
    root = active_root(cwd)
    record = discussion_record(cwd)
    if root is None:
        if record is None:
            if tool in {'Write', 'Edit', 'MultiEdit'}:
                target = (cwd/args['file_path']).resolve()
                if target.is_relative_to(cwd/'prototype'):
                    discussion = cwd/'prototype/discussion.md'
                    require(target == discussion and not discussion.is_symlink(),
                            'Create prototype/discussion.md first, before other design artifacts.')
            return
        if 'Execution boundary: released' in record.read_text():
            return
        if tool in {'Write', 'Edit', 'MultiEdit'}:
            target = (cwd/args['file_path']).resolve()
            if target.is_relative_to(record.parent):
                require(target == record.resolve(),
                        'Update the legacy prototype/discussion.md record before other design artifacts.')
        return
    if tool in {'Agent', 'Task'}:
        dispatch(args, root)
    elif tool == 'Bash':
        shell_read(args['command'], root)
    elif tool in {'Write', 'Edit', 'MultiEdit'}:
        target = (Path(payload['cwd'])/args['file_path']).resolve()
        require(target.is_relative_to(root/'prototype') and target.suffix == '.md',
                'Main designer writes prototype Markdown records. Send runnable output to Builder.')
    elif tool == 'NotebookEdit':
        raise ValueError('Notebook execution belongs to a bounded Builder.')


def main():
    try:
        check(json.load(sys.stdin))
        result = {}
    except (ValueError, KeyError, TypeError, OSError) as error:
        result = {'hookSpecificOutput': {'hookEventName': 'PreToolUse',
                  'permissionDecision': 'deny',
                  'permissionDecisionReason': f'spec-prototype execution boundary: {error}'}}
    print(json.dumps(result))


if __name__ == '__main__':
    main()
