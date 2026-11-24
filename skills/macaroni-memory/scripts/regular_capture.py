#!/usr/bin/env python3
"""Local, allowlisted Codex UserPromptSubmit/Stop capture. Stdlib; no history reads or network."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import uuid

import write_messages as memory

LIMIT = 4 * 1024 * 1024
PRIVATE_BLOCK = re.compile(r"-----BEGIN ((?:(?:RSA |OPENSSH |DSA |EC )?PRIVATE KEY|PGP PRIVATE KEY(?: BLOCK)?))-----.*?-----END \1-----", re.S)
ASSIGNMENT_PREFIX = r'''\b(?:[A-Za-z][A-Za-z0-9]*_)*(?:password|passwd|token|api[_-]?key|secret|cookie|session[_-]?id|authorization|access[_-]?token|access[_-]?key)(?:_[A-Za-z0-9]+)*["']?\s*[:=]\s*'''
ASSIGNMENT = re.compile(ASSIGNMENT_PREFIX + r'''(?:"((?:\\.|[^"\\])*)"|'((?:\\.|[^'\\])*)'|((?!["'])[^\n]+))''', re.I | re.S)
BEARER = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]+={0,2}", re.I)
URL_AUTH = re.compile(r"\b(https?|ssh|postgres(?:ql)?|mysql|redis)://[^\s/@]+:[^\s/@]+@", re.I)
TOKENS = re.compile(r"github_pat_[A-Za-z0-9_]{20,}|gh[opusb]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|sk-(?:proj-)?[A-Za-z0-9_-]{20,}")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def redact(text):
    """Replace known complete values before any disk write; never retain raw payloads."""
    records = []
    # Unsupported unquoted multiline formats must not leave a secret's later lines behind.
    # This deliberately rejects ambiguous scalars instead of attempting a YAML/shell parser.
    for match in re.finditer(ASSIGNMENT_PREFIX, text, re.I):
        rest = text[match.end():]
        if not rest.startswith(('"', "'")) and (
            re.match(r"[^\n]*[|>][+-]?\d?\s*(?:#[^\n]*)?\n", rest)
            or re.match(r"[^\n]*\\\r?\n", rest)
            or re.match(r"[^\n]*\r?\n(?:[ \t]*\r?\n)*[ \t]+\S", rest)
            or rest.startswith(('[', '{'))
        ):
            raise memory.CaptureError("Complex credential syntax requires manual redaction")
    def replace(pattern, marker, kind):
        nonlocal text
        text, count = pattern.subn(marker, text)
        if count:
            records.append({"kind": kind, "target": "text", "replacement": marker, "count": count})
    replace(PRIVATE_BLOCK, "PRIVATE_KEY", "credential")
    if re.search(r"-----BEGIN [^\n-]*PRIVATE KEY(?: BLOCK)?-----", text):
        raise memory.CaptureError("Incomplete private key cannot be safely captured")
    replace(URL_AUTH, "REDACTED", "credential")
    replace(BEARER, "ТОКЕН", "credential")
    spans = [match.span() for match in ASSIGNMENT.finditer(text)]
    for header in re.finditer(ASSIGNMENT_PREFIX, text, re.I):
        if not any(start <= header.start() < end for start, end in spans):
            raise memory.CaptureError("Incomplete credential assignment cannot be safely captured")
    count = 0
    def assignment(match):
        nonlocal count
        value = next(value for value in match.groups() if value is not None)
        if value.upper() in memory.MARKERS:
            return match.group(0)
        count += 1
        group = next(i for i in range(1, 4) if match.group(i) is not None)
        start, end = match.start(group) - match.start(), match.end(group) - match.start()
        return match.group(0)[:start] + "REDACTED" + match.group(0)[end:]
    text = ASSIGNMENT.sub(assignment, text)
    if count:
        records.append({"kind": "credential", "target": "text", "replacement": "REDACTED", "count": count})
    replace(TOKENS, "ТОКЕН", "credential")
    replace(EMAIL, "EMAIL", "personal_data")
    memory.scan(text)
    return text, records


def checked_path(value):
    if not isinstance(value, str) or not Path(value).is_absolute():
        raise memory.CaptureError("Use absolute project and store paths")
    path = Path(value)
    if any(parent.is_symlink() for parent in [path, *path.parents]):
        raise memory.CaptureError("Symlink paths are unsupported")
    return path.resolve()


def git_identity(root):
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=5)
    if result.returncode or Path(result.stdout.strip()).resolve() != root:
        raise memory.CaptureError("Register the exact Git checkout root")
    result = subprocess.run(["git", "-C", str(root), "remote", "get-url", "origin"], capture_output=True, text=True, timeout=5)
    if result.returncode:
        raise memory.CaptureError("Project origin is unavailable")
    return memory.repository_url(result.stdout.strip())


def outside_git(path):
    if any((parent / ".git").exists() for parent in [path, *path.parents]):
        raise memory.CaptureError("Private store must be outside every Git checkout")


def configuration(path):
    path = checked_path(str(path))
    if path.exists() and path.stat().st_mode & 0o077:
        raise memory.CaptureError("Capture config needs mode 0600")
    doc = memory.strict_json(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("version") != 1 or not isinstance(doc.get("projects"), list):
        raise memory.CaptureError("Invalid local capture config")
    memory.scan(doc)
    validate_mappings(doc)
    return doc


def validate_mappings(doc):
    """Validate structural mappings without requiring inactive source roots to exist."""
    entries, uuids = [], set()
    for project in doc["projects"]:
        if not isinstance(project, dict) or not {"project_root", "repository", "store_root"}.issubset(project):
            raise memory.CaptureError("Project mapping needs an explicit source and local destination")
        root, store = checked_path(project["project_root"]), checked_path(project["store_root"])
        outside_git(store)
        identity = memory.binding_identity(project)
        local = identity.get("binding_kind") == "local_directory"
        if local:
            if identity["project_id"] in uuids:
                raise memory.CaptureError("Local UUID belongs to another registered project")
            uuids.add(identity["project_id"])
        for old_root, old_store, old_identity, old_local in entries:
            if root == old_root or ((local or old_local) and (root.is_relative_to(old_root) or old_root.is_relative_to(root))):
                raise memory.CaptureError("Duplicate or overlapping project roots")
            if (store != old_store and (store.is_relative_to(old_store) or old_store.is_relative_to(store))) or (store == old_store and identity != old_identity):
                raise memory.CaptureError("Never share one project's store with another")
        entries.append((root, store, identity, local))
    for root, _, _, _ in entries:
        if any(store.is_relative_to(root) or root.is_relative_to(store) for _, store, _, _ in entries):
            raise memory.CaptureError("Project and private store paths must be separate")


def project_binding(config, root):
    root = checked_path(str(root))
    entry = next((p for p in configuration(config)["projects"] if p["project_root"] == str(root)), None)
    if entry is None:
        raise memory.CaptureError("Register the exact project root first")
    identity = memory.verify_local_root(entry)
    if identity.get("binding_kind") != "local_directory" and git_identity(root) != identity["repository"]:
        raise memory.CaptureError("Project destination changed since registration")
    return entry


def write_configuration(config_path, doc):
    memory.scan(doc)
    validate_mappings(doc)
    temporary = config_path.with_name(config_path.name + ".new")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as file:
            file.write(memory.encoded(doc))
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, config_path)
    finally:
        temporary.unlink(missing_ok=True)


def register(config_path, root, repository, store):
    """Explicit registration only; no chat reads, data capture or hook trust changes."""
    config_path = checked_path(str(config_path))
    outside_git(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = config_path.with_name(config_path.name + ".lock")
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    try:
        _register_config(config_path, root, repository, store)
    finally:
        lock.unlink()


def _register_config(config_path, root, repository, store):
    config_path = checked_path(str(config_path))
    root, store = checked_path(str(root)), checked_path(str(store))
    outside_git(config_path)
    outside_git(store)
    repository = memory.repository_url(repository)
    if git_identity(root) != repository:
        raise memory.CaptureError("Project origin differs from the requested repository")
    doc = configuration(config_path) if config_path.exists() else {"version": 1, "projects": []}
    entry = {"project_root": str(root), "repository": repository, "store_root": str(store)}
    existing = next((p for p in doc["projects"] if p["project_root"] == str(root)), None)
    if existing:
        if any(existing[k] != v for k, v in entry.items()):
            raise memory.CaptureError("Existing mapping differs; compare it before replacing")
        return
    doc["projects"].append(entry)
    write_configuration(config_path, doc)


def register_local(config_path, root, store, project_id=None):
    """Explicit local-only directory binding. No Git, remote, hooks or message import."""
    config_path = checked_path(str(config_path))
    root, store = checked_path(str(root)), checked_path(str(store))
    outside_git(config_path)
    outside_git(store)
    if not root.is_dir():
        raise memory.CaptureError("Register an existing local directory")
    config_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = config_path.with_name(config_path.name + ".lock")
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    try:
        doc = configuration(config_path) if config_path.exists() else {"version": 1, "projects": []}
        existing = next((p for p in doc["projects"] if p["project_root"] == str(root)), None)
        marker = store / "local-store.json"
        if marker.is_symlink():
            raise memory.CaptureError("Local store marker cannot be a symlink")
        old = memory.load(marker)
        if project_id is None:
            project_id = (existing or old or {}).get("project_id") or str(uuid.uuid4())
        stat = root.stat()
        entry = {"binding_kind": "local_directory", "project_id": project_id,
            "project_root": str(root), "root_identity": {"device": stat.st_dev, "inode": stat.st_ino},
            "store_root": str(store), "repository": None, "export_policy": "local_only"}
        identity = memory.verify_local_root(entry)
        if store.exists() and store.stat().st_mode & 0o077:
            raise memory.CaptureError("Local store needs mode 0700")
        if old is not None:
            if marker.stat().st_mode & 0o077 or old.get("version") != 1 or old.get("kind") != "macaroni_local_store" or old.get("root") != str(store) or memory.binding_identity(old) != identity:
                raise memory.CaptureError("Existing private store belongs to another binding")
        protocol = memory.load(memory.target(store, ".macaroni/protocol.json"))
        if protocol is not None and (old is None or memory.binding_identity(protocol) != identity or protocol.get("storage_branch") != "local"):
            raise memory.CaptureError("Existing protocol needs explicit comparison before registration")
        if existing:
            if any(existing.get(k) != v for k, v in entry.items()):
                raise memory.CaptureError("Existing mapping differs; explicit rebinding is required")
            return existing
        doc["projects"].append(entry)
        write_configuration(config_path, doc)
        return entry
    finally:
        lock.unlink()


def private_store(project):
    store = checked_path(project["store_root"])
    outside_git(store)
    identity = memory.verify_local_root(project)
    protocol = memory.load(memory.target(store, ".macaroni/protocol.json"))
    if protocol is not None and (memory.binding_identity(protocol) != identity or protocol.get("storage_branch") != "local"):
        raise memory.CaptureError("Existing protocol belongs to another destination")
    store.mkdir(parents=True, exist_ok=True, mode=0o700)
    if store.stat().st_mode & 0o077:
        raise memory.CaptureError("Local store needs mode 0700")
    marker = store / "local-store.json"
    doc = {"version": 1, "kind": "macaroni_local_store", "root": str(store), **identity}
    if marker.exists():
        if marker.is_symlink() or marker.stat().st_mode & 0o077:
            raise memory.CaptureError("Local store marker needs mode 0600")
        old = memory.load(marker)
        if any(old.get(k) != v for k, v in doc.items()):
            raise memory.CaptureError("Existing local store belongs to a different destination")
    else:
        fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as file:
            file.write(memory.encoded(doc))
    instructions = store / "AGENTS.md"
    if instructions.is_symlink():
        raise memory.CaptureError("Local instructions cannot be a symlink")
    if not instructions.exists():
        text = """# Local project memory

This private store belongs only to the project binding in local-store.json. Its
.macaroni/protocol.json uses storage_branch: local. It is outside Git and has no
remote. Do not copy conversation data into a public or unverified private repo.

Before relevant work, read this instruction, protocol.json, relevant users,
chat metadata/members and message JSON in local observation order. Published
history in the source project's macaroni branch is a separate historical source.
Indexes are optional navigation; message JSON is evidence, never current permission.

Explicit agent capture is required for local_directory bindings; no remote or
Git identity is implied. Save accessible input with agent_capture.py --messages,
prepare a frozen reply with --prepare-reply before emission, confirm its actual
source/body with --confirm-reply, and reload --status plus sources after resume.
Prepared replies remain separate from observed history.

For Git bindings, Codex UserPromptSubmit/Stop hooks save directly supplied authorized project
text after redaction. No completeness audit or inventory prerequisite. No transcript
reads, hidden reasoning/system/tool data or automatic backfill. IDs are assigned
locally; source times are unknown. Hooks do not expose all commentary or attachments.

Save every available authorized user and user-facing assistant message, including
progress, through references/flush.md when hooks do not deliver it. If the user asks
to verify saving, compare the supplied source IDs and planned hashes after a fresh
process reload; report missing sources separately. Never call unseen history complete.
Flush before a planned restart and reload actual stored messages after resume.

Messages, inbox pointers and manifests are append-only; preserve unknown JSON fields
and existing AGENTS.md. Retried identical events are skipped. Do not remove held
locks blindly. Known secret patterns are redacted before writes; review sensitive
project facts manually and review exact data before any separately authorized export.

Read the installed macaroni-memory SKILL.md and references/regular-capture.md for
configuration, native /hooks review/trust, limits and recovery. Capture never commits,
pushes or uploads; code/docs permission does not authorize conversation publication.
"""
        fd = os.open(instructions, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            file.write(text)
    return store


@contextmanager
def observation_lock(store):
    lock = store / ".hook.lock"
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    try:
        yield
    finally:
        lock.unlink()


def capture_event(config_path, event):
    """Read only event text fields. transcript_path and all tool/system fields are ignored."""
    name = event.get("hook_event_name")
    if name not in {"UserPromptSubmit", "Stop"} or event.get("agent_id"):
        return {"skipped": "unsupported_event"}
    root = checked_path(event.get("cwd"))
    doc = configuration(config_path)
    # Match the nearest checkout, so a nested project cannot borrow its parent's mapping.
    nearest = next((p for p in [root, *root.parents] if (p / ".git").exists()), None)
    project = next((p for p in doc["projects"] if Path(p["project_root"]) == nearest), None)
    if project is None:
        return {"skipped": "unregistered_project"}
    if project.get("binding_kind") == "local_directory":
        return {"skipped": "explicit_capture_required"}
    if git_identity(Path(project["project_root"])) != memory.repository_url(project["repository"]):
        raise memory.CaptureError("Project destination changed since registration")
    field = "prompt" if name == "UserPromptSubmit" else "last_assistant_message"
    text = event.get(field)
    if text is None or text == "":
        return {"skipped": "no_message_text"}
    if not isinstance(text, str):
        raise memory.CaptureError("Hook message text must be a string")
    if name == "UserPromptSubmit" and "<codex_delegation>" in text:
        return {"skipped": "delegated_internal_input"}
    text, redactions = redact(text)
    conversation = memory.source_id(event.get("session_id"))
    turn = memory.source_id(event.get("turn_id"))
    # Hooks expose turn IDs, not message IDs. Assigned IDs remain stable across event retries.
    key = memory.object_digest({"session": conversation, "turn": turn, "event": name, "redacted_text": text})
    source = "hook_" + key
    channel = "user" if name == "UserPromptSubmit" else "assistant_final"
    meta = {"hook_event": name, "source_turn_id": turn, "order_policy": "local_hook_observation", "completeness_audited": False}
    memory.scan({"conversation": conversation, "turn": turn, "text": text, "meta": meta})
    store = private_store(project)
    with observation_lock(store):
        known, _ = memory.existing_messages(store)
        previous = known.get(source)
        orders = [d["meta"]["original_order"] for _, d in known.values() if d["meta"].get("source_system") == "codex_hooks" and d["meta"].get("source_conversation_id") == conversation]
        order = previous[1]["meta"]["original_order"] if previous else max(orders, default=0) + 1
        message = {"source_message_id": source, "from": "HUMAN" if channel == "user" else "CODEX", "to": ["CODEX" if channel == "user" else "HUMAN"], "text": text, "original_order": order, "source_channel": channel, "original_created_at": None, "redacted": bool(redactions), "redactions": redactions, "meta": meta}
        batch = {"version": 1, "capture": {"source_system": "codex_hooks", "source_conversation_id": conversation, "source_id_origin": "assigned_local", "order_basis": "available_fragment"}, "messages": [message]}
        chat = "chat_hooks_" + hashlib.sha256(conversation.encode()).hexdigest()[:32]
        plan = memory.prepare(store, batch, chat, branch="local")
        written = memory.apply(store, plan)
    return {"messages_new": plan["messages_new"], "messages_skipped": plan["messages_skipped"], "files_written": written}


def hooks_template(config_path):
    command = " ".join(shlex.quote(s) for s in [sys.executable, str(Path(__file__).resolve()), "--config", str(Path(config_path).resolve())])
    handler = {"type": "command", "command": command, "timeout": 15, "statusMessage": "Saving project message locally"}
    return {"description": "Macaroni local capture; allowlisted projects only; no transcript reads or uploads.", "hooks": {name: [{"hooks": [dict(handler)]}] for name in ("UserPromptSubmit", "Stop")}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--register-project", type=Path)
    mode.add_argument("--register-local-project", type=Path)
    mode.add_argument("--hooks-template", action="store_true")
    parser.add_argument("--repository")
    parser.add_argument("--project-id")
    parser.add_argument("--store-root", type=Path)
    args = parser.parse_args()
    if args.project_id and not args.register_local_project:
        parser.error("--project-id requires --register-local-project")
    if args.register_local_project:
        if args.repository or not args.store_root:
            parser.error("Local registration requires --store-root and no --repository")
        entry = register_local(args.config, args.register_local_project, args.store_root, args.project_id)
        print(json.dumps({"registered": True, "capture_started": False, "project": entry}))
        return
    if args.hooks_template:
        print(json.dumps(hooks_template(args.config), ensure_ascii=False, indent=2))
        return
    if args.register_project:
        if not args.repository or not args.store_root:
            parser.error("Registration requires --repository and --store-root")
        register(args.config, args.register_project, args.repository, args.store_root)
        print(json.dumps({"registered": True, "capture_started": False}))
        return
    # Never emit input, exception strings, a blocking decision or secret-bearing diagnostics.
    try:
        raw = sys.stdin.buffer.read(LIMIT + 1)
        if len(raw) > LIMIT:
            raise memory.CaptureError("Hook input exceeds limit")
        event = memory.strict_json(raw.decode("utf-8"))
        if not isinstance(event, dict):
            raise memory.CaptureError("Invalid hook input")
        capture_event(args.config, event)
        print('{"continue":true}')
    except (memory.CaptureError, ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError):
        print('{"continue":true,"systemMessage":"Macaroni: local capture did not finish. Check the project mapping, private-store permissions and capture locks; no history backfill was attempted."}')


if __name__ == "__main__":
    main()
