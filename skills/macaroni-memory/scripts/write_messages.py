#!/usr/bin/env python3
"""Prepare, review and apply project-scoped Protocol v1 capture batches.

Python stdlib only. No network, commit or push; memory text is historical data.
"""
import argparse
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.parse import urlparse


class CaptureError(ValueError):
    pass


SECRET = re.compile(
    r"github_pat_[A-Za-z0-9_]{20,}|gh[opusb]_[A-Za-z0-9]{20,}|"
    r"Authorization:\s*Bearer\s+[A-Za-z0-9._-]{20,}|"
    r"-----BEGIN (?:RSA |OPENSSH |PGP )?PRIVATE KEY-----|AKIA[0-9A-Z]{16}|"
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", re.I)
CREDENTIAL = re.compile(r"\b(?:password|passwd|token|api[_-]?key|cookie|session[_-]?id)\s*[:=]\s*[\"']?([^\s\"',;}]+)", re.I)
MARKERS = {"REDACTED", "ТОКЕН", "ПАРОЛЬ", "СЕКРЕТ", "КЛЮЧ", "PRIVATE_KEY", "EMAIL", "PHONE", "COOKIE", "SESSION"}
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}\Z")
MESSAGE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,191}\Z")


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def encoded(doc):
    return (json.dumps(doc, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def scan(doc):
    if isinstance(doc, dict):
        for key, value in doc.items():
            scan(key)
            scan(value)
    elif isinstance(doc, list):
        for value in doc:
            scan(value)
    elif isinstance(doc, str):
        if SECRET.search(doc) or any(m.group(1).upper() not in MARKERS for m in CREDENTIAL.finditer(doc)):
            raise CaptureError("Sensitive pattern found; redact the complete batch before preparing it")


def identifier(value):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise CaptureError("Invalid participant or chat identifier")
    return value


def timestamp(value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise CaptureError("Original timestamp must be an ISO string or null")
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise CaptureError("Timestamp needs an explicit timezone")
    return value


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if result.returncode:
        raise CaptureError("Git state could not be verified")
    return result.stdout.strip()


def repository_url(value):
    if value.startswith("git@"):
        host, path = value[4:].split(":", 1)
        value = "https://" + host + "/" + path
    parsed = urlparse(value)
    if parsed.scheme not in {"https", "ssh"} or not parsed.hostname or (parsed.scheme == "https" and parsed.username) or parsed.password or parsed.query or parsed.fragment:
        raise CaptureError("Use a repository URL without credentials, query or fragment")
    path = parsed.path.rstrip("/").removesuffix(".git")
    if not path or ".." in path.split("/"):
        raise CaptureError("Invalid repository URL")
    return "https://" + parsed.hostname.lower() + path


def state(root, branch, writing=True):
    root = root.resolve()
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise CaptureError("repo-root must be the Git checkout root")
    actual_branch = git(root, "branch", "--show-current")
    if writing and actual_branch != branch:
        raise CaptureError("Capture must use the configured storage branch, not a product branch")
    return {"repo_root": str(root), "repository": repository_url(git(root, "remote", "get-url", "origin")), "branch": branch, "base_commit": git(root, "rev-parse", "HEAD")}


def target(root, relative):
    parts = Path(relative).parts
    if Path(relative).is_absolute() or not parts or parts[0] != ".macaroni" or any(piece in {"", ".", ".."} for piece in relative.split("/")) or "\\" in relative:
        raise CaptureError("Destination must be inside .macaroni")
    candidate = root
    for component in parts:
        candidate = candidate / component
        if candidate.is_symlink():
            raise CaptureError("Symlink destinations are not supported")
    if not candidate.resolve().is_relative_to((root / ".macaroni").resolve()):
        raise CaptureError("Destination escapes memory root")
    return candidate


def strict_json(text):
    def invalid_constant(value):
        raise CaptureError("Non-finite numbers are not valid JSON")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise CaptureError("Duplicate JSON field; inspect source without rewriting it")
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant)


def load(path):
    if not path.exists():
        return None
    doc = strict_json(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("version") != 1:
        raise CaptureError("Existing documents must be Protocol v1 objects")
    return doc


def existing_messages(root):
    messages = {}
    ids = set()
    for path in sorted((root / ".macaroni/chats").glob("*/messages/**/*.json")):
        target(root, path.relative_to(root).as_posix())
        doc = load(path)
        if not {"chat_id", "id", "from", "text", "created_at", "to"}.issubset(doc) or not isinstance(doc.get("meta", {}), dict):
            raise CaptureError("Existing message is incomplete; inspect it without rewriting history")
        key = (doc["chat_id"], doc["id"])
        if key in ids:
            raise CaptureError("Duplicate existing message ID")
        ids.add(key)
        source = doc.get("meta", {}).get("source_message_id")
        if source:
            if source in messages:
                raise CaptureError("Duplicate existing source_message_id")
            messages[source] = (path.relative_to(root).as_posix(), doc)
    return messages, ids


def unchanged_fields(old, new, allow_updated_at=True):
    """Existing values remain intact; updates may append members and set updated_at."""
    if isinstance(old, dict) and isinstance(new, dict):
        return all(key in new and ((allow_updated_at and key == "updated_at") or unchanged_fields(value, new[key], False)) for key, value in old.items())
    if isinstance(old, list) and isinstance(new, list):
        return len(new) >= len(old) and all(unchanged_fields(a, b, False) for a, b in zip(old, new))
    return old == new


def semantic(doc):
    meta = doc["meta"]
    return {key: doc.get(key) for key in ("chat_id", "from", "from_name", "to", "text", "reply_to", "attachments")} | {
        "source_message_id": meta["source_message_id"], "source": meta.get("source"),
        "original_created_at": meta.get("original_created_at"), "redacted": meta.get("redacted", False)}


def plan_digest(plan):
    unsigned = {key: value for key, value in plan.items() if key != "review_digest"}
    return digest(json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def prepare(root, raw_messages, chat_id, branch="macaroni", repo_url=None, completeness="partial", chat_title="AGENT_ROOM"):
    destination = state(root, branch)
    if repo_url and repository_url(repo_url) != destination["repository"]:
        raise CaptureError("Requested repository does not match origin")
    identifier(chat_id)
    if completeness not in {"partial", "complete"}:
        raise CaptureError("Capture completeness must be partial or complete")
    protocol = load(target(root, ".macaroni/protocol.json"))
    if protocol is not None and (repository_url(protocol["repository"]) != destination["repository"] or protocol["storage_branch"] != branch):
        raise CaptureError("Protocol repository or storage branch does not match destination")
    scan(raw_messages)  # No setup files or plans written before the entire input passes.
    if not isinstance(raw_messages, list) or not raw_messages:
        raise CaptureError("Capture needs a non-empty JSON array")
    existing, ids = existing_messages(root)
    normal = []
    source_ids = set()
    for order, raw in enumerate(raw_messages, 1):
        if not isinstance(raw, dict):
            raise CaptureError("Each source message must be an object")
        source = raw.get("source_message_id")
        if not isinstance(source, str) or not source.strip() or len(source) > 256 or source in source_ids:
            raise CaptureError("Every message needs a unique stable source_message_id")
        source_ids.add(source)
        sender = identifier(raw.get("from", "CODEX"))
        recipients = raw.get("to", ["CODEX" if sender == "HUMAN" else "HUMAN"])
        if not isinstance(recipients, list) or not recipients or len(recipients) != len(set(recipients)):
            raise CaptureError("to must be a non-empty array of unique participant IDs")
        recipients = [identifier(value) for value in recipients]
        if not isinstance(raw.get("text"), str):
            raise CaptureError("Exact source text is required")
        if not isinstance(raw.get("redacted", False), bool) or not isinstance(raw.get("attachments", []), list):
            raise CaptureError("redacted must be boolean and attachments must be an array")
        original = timestamp(raw.get("original_created_at", raw.get("created_at")))
        captured = now()
        explicit_id = raw.get("id")
        msg_id = explicit_id or captured.replace(":", "-") + "_" + sender + "_" + digest(source.encode())[:12]
        if not MESSAGE_ID.fullmatch(msg_id):
            raise CaptureError("Invalid message ID")
        old = existing.get(source)
        if old:
            if old[1]["chat_id"] != chat_id or (explicit_id and explicit_id != old[1]["id"]):
                raise CaptureError("Source already belongs to a different chat or message ID")
            msg_id = old[1]["id"]
            captured = old[1]["created_at"]
        elif (chat_id, msg_id) in ids:
            raise CaptureError("Message ID collision; no existing message will be overwritten")
        ids.add((chat_id, msg_id))
        metadata = copy.deepcopy(raw.get("meta", {}))
        if not isinstance(metadata, dict):
            raise CaptureError("meta must be an object")
        metadata.update({"captured_by": "CODEX", "source": raw.get("source", "user_message" if sender == "HUMAN" else "assistant_message"), "source_message_id": source, "redacted": bool(raw.get("redacted", False)), "original_created_at": original, "original_timestamp_status": "known" if original else "unknown", "created_at_basis": "capture_time", "original_order": order, "capture_completeness": completeness})
        reply_source = raw.get("reply_to_source_id")
        if reply_source:
            metadata["source_reply_to_message_id"] = reply_source
        normal.append({"version": 1, "id": msg_id, "chat_id": chat_id, "type": "text", "from": sender, "from_name": raw.get("from_name", "Human" if sender == "HUMAN" else "Codex"), "to": recipients, "created_at": captured, "text": raw["text"], "reply_to": raw.get("reply_to"), "attachments": copy.deepcopy(raw.get("attachments", [])), "meta": metadata, "signature": None})
    source_to_id = {source: doc["id"] for source, (_, doc) in existing.items() if doc["chat_id"] == chat_id}
    source_to_id.update({doc["meta"]["source_message_id"]: doc["id"] for doc in normal})
    changes = {}
    skipped = 0
    def propose(relative, payload):
        path = target(root, relative)
        old = load(path)
        if old == payload:
            return
        if old is not None and not unchanged_fields(old, payload):
            raise CaptureError("Existing fields would change: " + relative)
        scan(payload)
        changes[relative] = {"path": relative, "before_sha256": digest(path.read_bytes()) if old is not None else None, "content": payload}
    for doc in normal:
        source = doc["meta"]["source_message_id"]
        reply_source = doc["meta"].get("source_reply_to_message_id")
        if reply_source:
            if reply_source not in source_to_id:
                raise CaptureError("reply_to_source_id is missing from the supplied fragment and stored memory")
            doc["reply_to"] = source_to_id[reply_source]
        old = existing.get(source)
        if old:
            if semantic(old[1]) != semantic(doc) or any(old[1]["meta"].get(k) != v for k, v in next(r for r in raw_messages if r["source_message_id"] == source).get("meta", {}).items()):
                raise CaptureError("Source ID was reused with different content; append a correction instead")
            relative, doc = old
            skipped += 1
        else:
            day = dt.datetime.fromisoformat(doc["created_at"].replace("Z", "+00:00")).strftime("%Y/%m/%d")
            relative = f".macaroni/chats/{chat_id}/messages/{day}/{doc['id']}.json"
            if target(root, relative).exists():
                raise CaptureError("Message path already exists")
            propose(relative, doc)
        for recipient in doc["to"]:
            pointer_path = f".macaroni/inbox/{recipient}/{doc['id']}.json"
            pointer = {"version": 1, "recipient": recipient, "message_id": doc["id"], "chat_id": chat_id, "message_path": relative, "created_at": doc["created_at"]}
            old_pointer = load(target(root, pointer_path))
            if old_pointer is not None:
                if any(old_pointer.get(k) != v for k, v in pointer.items()):
                    raise CaptureError("Existing inbox pointer conflicts with message")
            else:
                propose(pointer_path, pointer)
    if changes:
        stamp = now()
        protocol_path = ".macaroni/protocol.json"
        protocol = load(target(root, protocol_path))
        if protocol is None:
            propose(protocol_path, {"version": 1, "name": "Macaroni Project Memory", "repository": destination["repository"], "storage_branch": branch, "created_at": stamp, "updated_at": stamp, "meta": {}})
        elif repository_url(protocol["repository"]) != destination["repository"] or protocol["storage_branch"] != branch:
            raise CaptureError("Protocol repository or storage branch does not match destination")
        people = {doc["from"]: doc["from_name"] for doc in normal}
        for doc in normal:
            for recipient in doc["to"]:
                people.setdefault(recipient, "Human" if recipient == "HUMAN" else recipient.title())
        for participant, name in people.items():
            path = f".macaroni/users/{participant}.json"
            user = load(target(root, path))
            if user is None:
                propose(path, {"version": 1, "id": participant, "display_name": name, "role": "owner" if participant == "HUMAN" else "agent", "created_at": stamp, "updated_at": stamp, "meta": {}})
            elif user.get("id") != participant:
                raise CaptureError("Existing user ID mismatch")
        meta_path = f".macaroni/chats/{chat_id}/meta.json"
        chat = load(target(root, meta_path))
        if chat is None:
            propose(meta_path, {"version": 1, "id": chat_id, "title": chat_title, "kind": "agent_room", "created_at": stamp, "updated_at": stamp, "meta": {"capture_completeness": completeness, "timestamp_policy": "created_at is capture time; original_created_at is source time or null when unknown"}})
        elif chat.get("id") != chat_id:
            raise CaptureError("Existing chat ID mismatch")
        member_path = f".macaroni/chats/{chat_id}/members.json"
        members = load(target(root, member_path)) or {"version": 1, "chat_id": chat_id, "members": [], "updated_at": stamp}
        if members.get("chat_id") != chat_id or not isinstance(members.get("members"), list):
            raise CaptureError("Existing members document mismatch")
        members = copy.deepcopy(members)
        known = {member["id"] for member in members["members"]}
        for participant in people:
            if participant not in known:
                members["members"].append({"id": participant, "role": "owner" if participant == "HUMAN" else "agent", "joined_at": stamp})
                members["updated_at"] = stamp
        propose(member_path, members)
    plan = {"version": 1, "destination": destination, "chat_id": chat_id, "messages_new": len(normal) - skipped, "messages_skipped": skipped, "changes": list(changes.values())}
    plan["review_digest"] = plan_digest(plan)
    validate_plan(root, plan)
    return plan


def validate_plan(root, plan):
    if not isinstance(plan, dict) or plan.get("version") != 1 or plan.get("review_digest") != plan_digest(plan):
        raise CaptureError("Plan digest mismatch; prepare and review again")
    if state(root, plan["destination"]["branch"]) != plan["destination"]:
        raise CaptureError("Checkout, destination or base commit changed since preparation")
    identifier(plan["chat_id"])
    if not isinstance(plan.get("changes"), list):
        raise CaptureError("Plan changes must be an array")
    protocol = load(target(root, ".macaroni/protocol.json"))
    if protocol is not None and (repository_url(protocol["repository"]) != plan["destination"]["repository"] or protocol["storage_branch"] != plan["destination"]["branch"]):
        raise CaptureError("Existing protocol destination mismatch")
    known, stored_ids = existing_messages(root)
    pending = {}
    message_ids = {msg_id for chat, msg_id in stored_ids if chat == plan["chat_id"]}
    source_ids = set(known)
    for change in plan["changes"]:
        relative = change["path"]
        if relative in pending:
            raise CaptureError("Duplicate plan destination")
        path = target(root, relative)
        old_bytes = path.read_bytes() if path.exists() else None
        before = digest(old_bytes) if old_bytes is not None else None
        if before != change["before_sha256"]:
            raise CaptureError("Destination changed since preparation: " + relative)
        doc = change["content"]
        if not isinstance(doc, dict) or doc.get("version") != 1:
            raise CaptureError("Plan contains an invalid Protocol v1 document")
        scan(doc)
        parts = Path(relative).parts
        if relative == ".macaroni/protocol.json":
            if repository_url(doc["repository"]) != plan["destination"]["repository"] or doc["storage_branch"] != plan["destination"]["branch"]:
                raise CaptureError("Protocol destination mismatch")
        elif len(parts) == 3 and parts[1] == "users":
            if identifier(doc["id"]) + ".json" != parts[2] or not isinstance(doc.get("display_name"), str) or not isinstance(doc.get("role"), str):
                raise CaptureError("User path mismatch")
        elif len(parts) == 4 and parts[1] == "chats" and parts[3] in {"meta.json", "members.json"}:
            if parts[2] != plan["chat_id"] or doc.get("id", doc.get("chat_id")) != parts[2]:
                raise CaptureError("Chat path mismatch")
            if parts[3] == "members.json":
                if not isinstance(doc.get("members"), list):
                    raise CaptureError("Members must be an array")
                member_ids = [identifier(member["id"]) for member in doc["members"] if isinstance(member, dict)]
                if len(member_ids) != len(doc["members"]) or len(member_ids) != len(set(member_ids)):
                    raise CaptureError("Invalid or duplicate members")
            elif not isinstance(doc.get("title"), str) or not isinstance(doc.get("kind"), str):
                raise CaptureError("Invalid chat metadata")
        elif len(parts) == 8 and parts[1] == "chats" and parts[3] == "messages":
            required = {"id", "chat_id", "type", "from", "from_name", "to", "created_at", "text", "reply_to", "attachments", "meta", "signature"}
            if old_bytes is not None or not required.issubset(doc) or doc["type"] != "text" or doc["chat_id"] != plan["chat_id"] or parts[2] != doc["chat_id"] or parts[-1] != doc["id"] + ".json" or not MESSAGE_ID.fullmatch(doc["id"]):
                raise CaptureError("Message shape/path mismatch or overwrite attempt")
            identifier(doc["from"])
            if not isinstance(doc["text"], str) or not isinstance(doc["from_name"], str) or not isinstance(doc["to"], list) or not doc["to"] or len(doc["to"]) != len(set(doc["to"])) or not isinstance(doc["attachments"], list) or not isinstance(doc["meta"], dict):
                raise CaptureError("Invalid message field types or recipients")
            for recipient in doc["to"]:
                identifier(recipient)
            stamp = dt.datetime.fromisoformat(timestamp(doc["created_at"]).replace("Z", "+00:00"))
            if stamp.utcoffset() != dt.timedelta(0) or "/".join(parts[4:7]) != stamp.strftime("%Y/%m/%d"):
                raise CaptureError("Message UTC date/path mismatch")
            source = doc["meta"].get("source_message_id")
            if not isinstance(source, str) or not source.strip() or len(source) > 256 or source in source_ids or doc["id"] in message_ids:
                raise CaptureError("Duplicate source or message ID")
            timestamp(doc["meta"].get("original_created_at"))
            expected_status = "known" if doc["meta"].get("original_created_at") else "unknown"
            if doc["meta"].get("original_timestamp_status") != expected_status or doc["meta"].get("created_at_basis") != "capture_time" or not isinstance(doc["meta"].get("redacted"), bool) or doc["meta"].get("capture_completeness") not in {"partial", "complete"} or type(doc["meta"].get("original_order")) is not int or doc["meta"]["original_order"] < 1:
                raise CaptureError("Invalid capture provenance metadata")
            source_ids.add(source)
            message_ids.add(doc["id"])
        elif len(parts) == 4 and parts[1] == "inbox":
            if old_bytes is not None or identifier(doc["recipient"]) != parts[2] or parts[-1] != doc["message_id"] + ".json":
                raise CaptureError("Inbox overwrite or path mismatch")
        else:
            raise CaptureError("Unsupported capture destination")
        if old_bytes is not None and not unchanged_fields(strict_json(old_bytes.decode("utf-8")), doc):
            raise CaptureError("Plan would discard existing fields")
        pending[relative] = doc
    for relative, doc in pending.items():
        if "/messages/" in relative:
            for participant in [doc["from"], *doc["to"]]:
                user_path = f".macaroni/users/{participant}.json"
                user = pending.get(user_path) or load(target(root, user_path))
                if not user or user.get("id") != participant:
                    raise CaptureError("Missing participant record")
            member_path = f".macaroni/chats/{doc['chat_id']}/members.json"
            members = pending.get(member_path) or load(target(root, member_path))
            if not members or not set([doc["from"], *doc["to"]]).issubset({member["id"] for member in members["members"]}):
                raise CaptureError("Missing chat membership")
        if "/inbox/" in relative:
            message_path = doc["message_path"]
            message = pending.get(message_path) or load(target(root, message_path))
            if not message or "/messages/" not in message_path or doc["recipient"] not in message["to"] or message["id"] != doc["message_id"] or message["chat_id"] != doc["chat_id"] or message["created_at"] != doc.get("created_at"):
                raise CaptureError("Inbox does not reference its recipient's message")
        if "/messages/" in relative:
            if doc["reply_to"] and doc["reply_to"] not in message_ids:
                raise CaptureError("Missing reply target")
            for recipient in doc["to"]:
                pointer_path = f".macaroni/inbox/{recipient}/{doc['id']}.json"
                if pointer_path not in pending and not target(root, pointer_path).exists():
                    raise CaptureError("Missing recipient inbox pointer")


def apply(root, plan):
    validate_plan(root, plan)
    if not plan["changes"]:
        return 0
    lock = Path(git(root, "rev-parse", "--git-path", "macaroni-capture.lock"))
    if not lock.is_absolute():
        lock = root / lock
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise CaptureError("Another capture owns the lock; inspect it, do not delete it blindly") from exc
    os.close(fd)
    stage = None
    published = []
    directories = []
    try:
        validate_plan(root, plan)
        stage = Path(tempfile.mkdtemp(prefix="macaroni-stage-", dir=lock.parent))
        for number, change in enumerate(plan["changes"]):
            staged = stage / str(number)
            staged.write_bytes(encoded(change["content"]))
            os.chmod(staged, 0o600)
        for number, change in enumerate(plan["changes"]):
            path = target(root, change["path"])
            old = path.read_bytes() if path.exists() else None
            if (digest(old) if old is not None else None) != change["before_sha256"]:
                raise CaptureError("Concurrent destination change")
            missing = []
            parent = path.parent
            while not parent.exists():
                missing.append(parent)
                parent = parent.parent
            for directory in reversed(missing):
                directory.mkdir()
                directories.append(directory)
            target(root, change["path"])
            if old is None:
                os.link(stage / str(number), path)  # Exclusive publication; never overwrite.
            else:
                os.replace(stage / str(number), path)
            published.append((path, old, encoded(change["content"])))
    except Exception:
        for path, old, written in reversed(published):
            if path.read_bytes() != written:
                raise CaptureError("Rollback stopped: another writer changed a published file; inspect checkout")
            if old is None:
                path.unlink()
            else:
                restore = stage / "restore"
                restore.write_bytes(old)
                os.replace(restore, path)
        for directory in reversed(directories):
            directory.rmdir()
        raise
    finally:
        if stage:
            shutil.rmtree(stage)
        lock.unlink()
    return len(published)


def index(root, query=None):
    """Navigation only: source paths and metadata, no inferred decisions or authority."""
    rows = []
    for path in sorted((root / ".macaroni/chats").glob("*/messages/**/*.json")):
        target(root, path.relative_to(root).as_posix())
        doc = load(path)
        if query and query.casefold() not in doc.get("text", "").casefold():
            continue
        meta = doc.get("meta", {})
        row = {"path": path.relative_to(root).as_posix(), "id": doc["id"], "chat_id": doc["chat_id"], "from": doc["from"], "created_at": doc["created_at"], "source_message_id": meta.get("source_message_id"), "original_created_at": meta.get("original_created_at"), "topics": meta.get("topics", [])}
        scan(row)
        rows.append(row)
    return {"version": 1, "kind": "derived_source_index", "messages": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", metavar="PLAN_JSON")
    mode.add_argument("--apply-plan", metavar="PLAN_JSON")
    mode.add_argument("--index", action="store_true")
    parser.add_argument("--search")
    parser.add_argument("--batch-json")
    parser.add_argument("--chat-id")
    parser.add_argument("--chat-title", default="AGENT_ROOM")
    parser.add_argument("--storage-branch", default="macaroni")
    parser.add_argument("--repo-url")
    parser.add_argument("--completeness", choices=["partial", "complete"], default="partial")
    parser.add_argument("--source-message-id")
    parser.add_argument("--from-id", default="CODEX")
    parser.add_argument("--from-name")
    parser.add_argument("--to")
    parser.add_argument("--source")
    parser.add_argument("--text-file")
    parser.add_argument("--text")
    parser.add_argument("--created-at", help="Known original source time; omit when unknown")
    parser.add_argument("--redacted", action="store_true")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    try:
        if args.index:
            print(json.dumps(index(root, args.search), ensure_ascii=False, indent=2))
        elif args.apply_plan:
            plan = strict_json(Path(args.apply_plan).read_text(encoding="utf-8"))
            count = apply(root, plan)
            print(json.dumps({"files_written": count, "review_digest": plan["review_digest"]}))
        else:
            if args.batch_json:
                raw = strict_json(Path(args.batch_json).read_text(encoding="utf-8"))
            else:
                text = Path(args.text_file).read_text(encoding="utf-8") if args.text_file else args.text
                sender_name = args.from_name or ("Human" if args.from_id == "HUMAN" else "Codex")
                source_kind = args.source or ("user_message" if args.from_id == "HUMAN" else "assistant_message")
                recipients = args.to.split(",") if args.to else ["CODEX" if args.from_id == "HUMAN" else "HUMAN"]
                raw = [{"source_message_id": args.source_message_id, "from": args.from_id, "from_name": sender_name, "to": recipients, "source": source_kind, "text": text, "original_created_at": args.created_at, "redacted": args.redacted}]
            chat = args.chat_id or "chat_" + now()[:10].replace("-", "") + "_agent_room"
            plan = prepare(root, raw, chat, args.storage_branch, args.repo_url, args.completeness, args.chat_title)
            output = Path(args.prepare)
            if output.resolve().is_relative_to(root):
                raise CaptureError("Keep review plans outside the repository")
            fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(fd, "wb") as file:
                file.write(encoded(plan))
            print(json.dumps({"plan": str(output), "review_digest": plan["review_digest"], "destination": plan["destination"], "messages_new": plan["messages_new"], "messages_skipped": plan["messages_skipped"], "files_proposed": len(plan["changes"]), "memory_written": False}, ensure_ascii=False, indent=2))
    except (CaptureError, ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, "Capture blocked: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
