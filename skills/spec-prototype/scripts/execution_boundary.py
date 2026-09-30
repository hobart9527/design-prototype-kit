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

try:
    import jsonschema
except ImportError:  # Schema validation is best-effort; the boundary still holds.
    jsonschema = None

from handoff import packet_for

SKILL = Path(__file__).resolve().parents[1]


def admit_skill_root(value) -> Path:
    """Resolve an envelope's declared skill_root to an admitted Skill tree.

    The hook is loaded from wherever the Skill is installed for the operator
    (`~/.claude/skills/spec-prototype` or a project's `.claude/skills/...`),
    while a session may run a byte-identical copy staged inside its own
    workspace. Physical equality with this hook's own tree therefore cannot be
    the sole admission rule. Admit the same tree instead: the resolved root,
    or any `spec-prototype` tree carrying the installed scripts.
    """
    tree = Path(value).expanduser().resolve()
    if tree == SKILL or (tree.name == 'spec-prototype' and (tree / 'scripts' / 'execution_boundary.py').is_file()):
        return tree
    raise ValueError('Dispatch must use this same installed Skill root.')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def admits_lint_helper(args, root):
    """Bounded admission for the contract lint helper: one slice, canonical project root.

    The boundary authorizes the argument form only. It never approves the lint
    result and creates no permission receipt.
    """
    require(args['script'].name == 'lint_spec_contracts.py',
            'Only the installed contract lint helper is admitted through this seam.')
    require('--root' in args['argv'] and '--slice' in args['argv'],
            'Contract lint requires an explicit --root and a single --slice.')
    root_index = args['argv'].index('--root')
    slice_index = args['argv'].index('--slice')
    require(root_index + 1 < len(args['argv']) and slice_index + 1 < len(args['argv']),
            'Contract lint --root and --slice require a value.')
    lint_root = Path(args['argv'][root_index + 1]).resolve()
    require(lint_root == root.resolve(),
            'Contract lint must target the active discussion repository root.')
    slice_id = args['argv'][slice_index + 1]
    require(re.fullmatch(r'[A-Za-z0-9_-]+', slice_id or ''),
            'Contract lint accepts one bounded slice_id.')


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
    if args.get('subagent_type') in {'spec-prototype-critic', 'Explore', 'feature-dev:code-explorer'}:
        return
    require(args.get('subagent_type') in {'spec-prototype-builder', 'general-purpose', 'claude'},
            'Use bounded spec-prototype-builder, spec-prototype-critic, or fallback agent (general-purpose/claude) for design work.')
    data = json.loads(args['prompt'])
    root = Path(data['repository_root']).resolve()
    require(root == active, 'Dispatch must stay in the active discussion repository.')
    admit_skill_root(data['skill_root'])
    if data.get('mode') == 'direction-probe':
        probe(root, data)
    elif data.get('mode') == 'lean-builder-envelope':
        require(isinstance(data.get('slice_id'), str) and data.get('slice_id'),
                'Lean envelope must specify slice_id.')
        require(isinstance(data.get('target_html_path'), str) and data.get('target_html_path'),
                'Lean envelope must specify target_html_path.')
        target_html = (root / data['target_html_path']).resolve()
        require(target_html.is_relative_to(root / 'prototype/experiments') or target_html.is_relative_to(root / 'prototype/surfaces'),
                'target_html_path must reside inside prototype/experiments/ or prototype/surfaces/.')
        spec_sources = data.get('spec_sources', {})
        require(bool(spec_sources), 'Lean envelope must include spec_sources digests.')
        # P1-3: Stale Digest Guard - each digest key carries the real relative
        # path of the object it names, so the guard compares the bytes of the
        # object the envelope actually bound (canonical-only envelopes name
        # r1.spec.md/r1.spec.json and never demand legacy pillar files).
        for digest_key, bound in spec_sources.items():
            if isinstance(bound, str):
                # Legacy pre-path-binding envelope: it names no object, so the
                # guard cannot compare bytes without guessing a retired fixed
                # path. Nothing recorded means nothing to verify.
                continue
            if isinstance(bound, dict):
                expected_digest = bound.get('sha256')
                rel_path = bound.get('path')
            else:
                raise ValueError(f'Lean envelope spec_sources entry {digest_key} must be a digest or a path+sha256 binding.')
            require(isinstance(expected_digest, str) and expected_digest,
                    f'Lean envelope spec_sources entry {digest_key} must carry a sha256 digest.')
            require(isinstance(rel_path, str) and rel_path,
                    f'Lean envelope spec_sources entry {digest_key} must name the relative path it digests.')
            require(re.fullmatch(r'[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*', rel_path),
                    f'Lean envelope spec_sources entry {digest_key} carries an invalid relative path: {rel_path}')
            file_path = root / rel_path
            # Repository containment: canonical realpath, no symlink escape.
            require(not file_path.is_symlink(),
                    f'Stale contract: {file_path.name} is a symlink; bound sources must be regular files in this repository.')
            resolved = file_path.resolve()
            require(resolved.is_relative_to(root.resolve()),
                    f'Stale contract: {file_path.name} escapes the repository; bound sources must stay inside the repository.')
            require(resolved.is_file(),
                    f'Stale contract: {file_path.name} was deleted since envelope was compiled. Re-assemble envelope before dispatch.')
            actual = hashlib.sha256(resolved.read_bytes()).hexdigest()
            require(actual == expected_digest,
                    f'Stale contract: {file_path.name} changed since envelope was compiled ({actual[:8]} != {expected_digest[:8]}). Re-assemble envelope before dispatch.')

        # P0-1: Build Authority Gate in execution boundary
        # If the envelope targets formal release/freeze or is not explicitly probe,
        # it must not carry unconfirmed [Hypothesis] or [Unknown] actions.
        target_env = data.get('target_environment', 'formal-candidate')
        has_hyp = data.get('has_hypothesis_actions') or data.get('build_authority') == 'probe_only'
        if target_env in ('formal-candidate', 'formal') and has_hyp:
            raise ValueError('Build Authority Gate: Formal candidate build blocked because envelope contains unvalidated [Hypothesis] actions. Run as direction probe or confirm explicit authority.')
    else:
        require(data == packet_for(root, data['specification']['path']),
                'Pass the exact handoff.py packet JSON unchanged to Builder.')


def shell_read_single(command, root):
    # A small argv seam, not a heuristic shell-write detector.
    require(not any(c in command for c in '\n\r;|&><`$'),
            'Use one read command or an installed project helper.')
    args = shlex.split(command)
    require(bool(args), 'Missing command.')
    tool = args[0]
    if tool in {'pwd', 'ls', 'cat', 'head', 'tail', 'wc', 'rg', 'grep', 'pytest'}:
        require(not any(a.startswith('--pre') for a in args[1:]), 'Use Read/Grep without an external preprocessor.')
        return
    if tool == 'sed':
        require('-n' in args[1:], 'Only read-only `sed -n` is admitted; in-place editing is a write.')
        return
    if tool == 'cd':
        # Chaining from another directory is a read-navigation convenience, not
        # a write. Stay inside the active discussion root.
        require(len(args) == 2, 'Use `cd <one directory>` inside the project.')
        require((root / args[1]).resolve().is_relative_to(root.resolve()),
                'Stay inside the active discussion repository.')
        return
    if tool == 'git':
        require(args[1:] in (['status', '--short'], ['status', '--short', '--branch'],
                             ['rev-parse', '--show-toplevel']), 'Use the bounded Git status/root command.')
        return
    if tool in {'node', 'python3', 'python3.14'} and len(args) > 1:
        script = Path(args[1]).resolve()
        # The installed `scripts/` directory is the manifest. A per-name
        # whitelist drifted from the shipped set repeatedly (a retired helper
        # stayed listed, a live one went missing), so admission is now "a
        # helper that actually ships in this Skill tree". Write scope still
        # keeps the model out of `scripts/`, so this admits only shipped code.
        is_installed = (
            script.parent == SKILL/'scripts'
            or (script.parent.name == 'scripts' and script.parent.parent.name == 'spec-prototype')
            or script.resolve() == (SKILL/'scripts'/script.name).resolve()
        )
        shipped = {p.name for p in (SKILL/'scripts').iterdir() if p.is_file()}
        require(is_installed and script.name in shipped,
                'Only installed helpers run here; author prototype files with Write/Edit instead.')
        if script.name == 'compile_spec_ir.py':
            require(any(arg == '--slice' for arg in args), 'compile_spec_ir.py requires an explicit --slice.')
        if script.name == 'lint_spec_contracts.py':
            admits_lint_helper({'script': script, 'argv': args[2:]}, root)
        if script.name == 'handoff.py' and 'freeze' in args:
            # No admission flag can manufacture frozen-approved status: a failed
            # approval binding is repaired at its authoring owner, not bypassed.
            require(not any(arg == '--force' or arg.startswith('--force=') for arg in args),
                    'Freeze has no force/permissive form; record the actual approval decision.')
            freeze_root = None
            if '--root' in args:
                idx = args.index('--root')
                if idx + 1 < len(args):
                    freeze_root = Path(args[idx + 1]).resolve()
            require(freeze_root == root.resolve(), 'Freeze command must target the active discussion root.')
        return
    raise ValueError('Use read-only tools or an installed project helper for this command.')


def shell_read(command, root):
    # `2>&1` only merges stderr into stdout; it opens no file and writes
    # nothing. Drop it before the redirection check so a diagnostic-preserving
    # read is not mistaken for a write. A real file redirection still fails.
    scrubbed = re.sub(r'\s*2>&1', '', command)
    if '&&' in scrubbed or '|' in scrubbed:
        # A chained read/helper sequence: every segment must pass
        # shell_read_single independently. Redirecting into a file, command
        # substitution and backgrounding remain forbidden.
        require(not any(c in scrubbed for c in '\n\r;><`$'),
                'Use one read command or an installed project helper.')
        segments = re.split(r'&&|\|', scrubbed)
        require(bool(segments) and all(s.strip() for s in segments), 'Empty command in chain.')
        for seg in segments:
            require('&' not in seg, 'Use one read command or an installed project helper.')
            shell_read_single(seg.strip(), root)
        return
    shell_read_single(scrubbed, root)


def boundary_status(record: Path) -> str | None:
    """Return 'active', 'released', or None from discussion.md declarations.

    Prefers the canonical ## Resume block if present; falls back to the tail of
    the document for minimal/legacy records.
    """
    try:
        text = record.read_text(encoding='utf-8')
    except OSError:
        return None
    resume_text = text.split("## Resume", 1)[1].split("\n## ", 1)[0] if "## Resume" in text else text
    values = re.findall(r'^- Execution boundary:\s*(active|released)\s*$', resume_text, re.M)
    if not values and "## Resume" in text:
        values = re.findall(r'^- Execution boundary:\s*(active|released)\s*$', text, re.M)
    if values:
        return values[-1]
    return 'active' if text.strip() else None


def _layered_anchor(root: Path) -> Path | None:
    """Return the layered design-record anchor file when one exists at this root.

    The layered layout (`truth.md` + `world.md` + `briefs/<slice>.md`) is a peer
    layout to the single `discussion.md`. The boundary must recognise either as
    "a design record exists at this root", or layered trees can never proceed
    past the record to their prototype.
    """
    for name in ('truth.md', 'world.md'):
        candidate = root / 'prototype' / name
        require(not candidate.is_symlink(),
                'Discussion scope must be a regular project record, not a symlink.')
        if candidate.is_file():
            return candidate
    return None


def active_root(cwd):
    # Shell cwd may be a child directory. The nearest existing design record owns
    # the scope; never infer lifecycle from a code file or tokens. A layered
    # tree anchors on `truth.md`/`world.md`; a single-record tree anchors on
    # `discussion.md` and consults its Resume block for the boundary status.
    for root in (cwd, *cwd.parents):
        record = root/'prototype/discussion.md'
        require(not record.is_symlink(), 'Discussion scope must be a regular project record, not a symlink.')
        if record.is_file():
            status = boundary_status(record)
            if status == 'active':
                return root
            if status in ('released', None):
                return None
        # A layered tree carries no discussion.md; the anchor's existence is
        # the record. An empty file is not yet a record (mirrors the
        # `boundary_status` "empty text is not active" rule).
        anchor = _layered_anchor(root)
        if anchor is not None and anchor.stat().st_size > 0:
            return root
    return None


def discussion_record(cwd):
    for root in (cwd, *cwd.parents):
        record = root/'prototype/discussion.md'
        if record.is_file() or record.is_symlink():
            return record
        anchor = _layered_anchor(root)
        if anchor is not None:
            return anchor
    return None


# The design record may be one `prototype/discussion.md`, or the layered
# `prototype/truth.md` + `prototype/world.md` + `prototype/briefs/<slice>.md`.
# Either way the record is written before any other design artifact, so the
# first-artifact gate admits every record path and no other.
_DESIGN_RECORD_NAMES = ('discussion.md', 'truth.md', 'world.md')


def is_design_record(target: Path, root: Path) -> bool:
    """Whether `target` is one of this root's design-record files."""
    if target.parent == root/'prototype' and target.name in _DESIGN_RECORD_NAMES:
        return True
    return target.parent == root/'prototype/briefs' and target.suffix == '.md'


def _pointer(error) -> str:
    """Render a jsonschema error as a JSON Pointer plus a readable path."""
    path = "/".join(str(p) for p in error.absolute_path) or "(root)"
    return f"{path}: {error.message}"


def validate_intent(path: Path, text: str) -> None:
    """Validate prototype/intent.json against the Stage 1 schema at write time.

    Feedback lands inside the same tool call that wrote the file: the author
    gets the failing JSON Pointer and the schema's own message instead of
    discovering the drift several commands later. Only the Stage 1 tier is
    checked here, so a Stage 1 write is never judged against Stage 3/4 fields.
    """
    require(path.name == 'intent.json', 'internal: not an intent contract path')
    try:
        instance = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(
            f'intent.json is not valid JSON at line {error.lineno} column {error.colno}: {error.msg}. '
            'JSON has no indentation semantics, so fix the syntax rather than the layout.'
        ) from error
    if jsonschema is None:
        return
    schema_path = SKILL / 'schemas' / 'intent.v1.json'
    if not schema_path.is_file():
        return
    schema = json.loads(schema_path.read_text(encoding='utf-8'))
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(instance),
                    key=lambda e: list(e.absolute_path))
    if errors:
        detail = '\n'.join(f'  - {_pointer(e)}' for e in errors)
        raise ValueError(
            'intent.json does not satisfy the Stage 1 intent contract:\n'
            f'{detail}\n'
            'Fix the named fields and write the file again.'
        )


def spec_view_advisory(target: Path) -> str | None:
    """A canonical `.spec.md` view with no compiled IR yet: remind, never block.

    The IR is authored at Stage 5, so an absent IR is a legal intermediate
    state while the design is still converging. The advisory fires at the
    moment the view is written — when the reminder is still actionable —
    rather than at delivery, when the missing IR is only a verdict.
    """
    if not target.name.endswith('.spec.md'):
        return None
    parts = target.parts
    if 'specifications' not in parts:
        return None
    slice_id = parts[parts.index('specifications') + 1] if parts.index('specifications') + 1 < len(parts) else ''
    stem = target.name.removesuffix('.spec.md')
    ir = target.parents[2] / 'contracts/compiled' / slice_id / f'{stem}.spec.json'
    if ir.is_file():
        return None
    return (f'{target.name} written with no compiled IR '
            f'(contracts/compiled/{slice_id}/{stem}.spec.json absent). '
            "The canonical view is the IR's rendering; run "
            f'compile_spec_ir.py --slice {slice_id} at Stage 5 before handoff.')


def _edited_text(args, target: Path) -> str:
    """Reconstruct the post-edit text so validation sees the resulting file."""
    if 'content' in args:
        return args['content']
    try:
        current = target.read_text(encoding='utf-8')
    except OSError:
        return ''
    edits = args.get('edits') or [{'old_string': args.get('old_string', ''),
                                   'new_string': args.get('new_string', ''),
                                   'replace_all': args.get('replace_all', False)}]
    for edit in edits:
        old, new = edit.get('old_string', ''), edit.get('new_string', '')
        if not old:
            continue
        current = current.replace(old, new, -1 if edit.get('replace_all') else 1)
    return current


def check(payload):
    require(isinstance(payload, dict), 'Invalid native tool event.')
    if payload.get('agent_type') in {'spec-prototype-builder', 'spec-prototype-critic'}:
        tool = payload.get('tool_name')
        args = payload.get('tool_input', {})
        if tool == 'Bash':
            cmd = args.get('command', '')
            if 'http.server' in cmd:
                raise ValueError('A bounded helper must not launch background HTTP servers.')
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
                    require(is_design_record(target, cwd) and not target.is_symlink(),
                            'Create the design record (prototype/discussion.md, or '
                            'prototype/truth.md + prototype/world.md) first, before '
                            'other design artifacts.')
            return
        if boundary_status(record) == 'released':
            return
        if tool in {'Write', 'Edit', 'MultiEdit'}:
            target = (cwd/args['file_path']).resolve()
            if target.is_relative_to(record.parent) and (not record.is_file() or record.stat().st_size == 0):
                require(is_design_record(target, record.parent.parent),
                        'Update the design record before other design artifacts.')
        return
    if tool in {'Agent', 'Task'}:
        dispatch(args, root)
    elif tool == 'Bash':
        shell_read(args['command'], root)
    elif tool in {'Write', 'Edit', 'MultiEdit'}:
        target = (Path(payload['cwd'])/args['file_path']).resolve()
        require(target.is_relative_to(root/'prototype'),
                'Design and prototype artifacts must reside inside prototype/.')
        if target.name == 'intent.json':
            validate_intent(target, _edited_text(args, target))
        advisory = spec_view_advisory(target)
        if advisory:
            payload.setdefault('hookSpecificOutput', {}).update({
                'hookEventName': 'PreToolUse',
                'additionalContext': advisory,
            })
    elif tool == 'NotebookEdit':
        raise ValueError('Notebook execution is out of scope for design prototype authoring.')


def main():
    payload = {}
    try:
        payload = json.load(sys.stdin)
        check(payload)
        result = {}
        advisory = payload.get('hookSpecificOutput', {}).get('additionalContext')
        if advisory:
            result = {'hookSpecificOutput': {'hookEventName': 'PreToolUse',
                      'additionalContext': advisory}}
    except (ValueError, KeyError, TypeError, OSError) as error:
        result = {'hookSpecificOutput': {'hookEventName': 'PreToolUse',
                  'permissionDecision': 'deny',
                  'permissionDecisionReason': f'spec-prototype execution boundary: {error}'}}
    print(json.dumps(result))


if __name__ == '__main__':
    main()
