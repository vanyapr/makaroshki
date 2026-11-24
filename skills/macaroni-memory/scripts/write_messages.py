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
import uuid
from urllib.parse import urlparse


class CaptureError(ValueError):
    pass


AGENT_ID = "AGENT"
# Older clients used this participant ID for assistant messages.
ASSISTANT_IDS = {AGENT_ID, "CODEX"}

SECRET = re.compile(
    r"github_pat_[A-Za-z0-9_]{20,}|gh[opusb]_[A-Za-z0-9]{20,}|"
    r"Authorization:\s*Bearer\s+[A-Za-z0-9._-]{20,}|"
    r"-----BEGIN (?:RSA |OPENSSH |PGP )?PRIVATE KEY-----|AKIA[0-9A-Z]{16}|"
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", re.I)
CREDENTIAL = re.compile(r"\b(?:password|passwd|token|api[_-]?key|cookie|session[_-]?id)\s*[:=]\s*[\"']?([^\s\"',;}]+)", re.I)
MARKERS = {"REDACTED", "ТОКЕН", "ПАРОЛЬ", "СЕКРЕТ", "КЛЮЧ", "PRIVATE_KEY", "EMAIL", "PHONE", "COOKIE", "SESSION"}
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}\Z")
MESSAGE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,191}\Z")
GAP_REASONS = {"unavailable_context", "unavailable_attachment", "unknown_history_boundary", "withheld_content"}
SOURCE_CHANNELS = {"user", "assistant_final", "assistant_commentary", "unknown"}
ID_ORIGINS = {"provider", "assigned_local", "unknown"}
ORDER_BASES = {"source_conversation", "available_fragment"}


def source_id(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise CaptureError("Every message needs a stable source_message_id")
    return value


def validate_redactions(value, redacted, required=False):
    if not isinstance(value, list) or (not redacted and value) or (required and redacted and not value):
        raise CaptureError("Redactions must describe replacements truthfully")
    for item in value:
        if not isinstance(item, dict) or not {"kind", "target", "replacement"}.issubset(item) or set(item) - {"kind", "target", "replacement", "count"}:
            raise CaptureError("Redaction records cannot contain original values or free-form payloads")
        if item["kind"] not in {"credential", "personal_data", "sensitive_project_data", "attachment"} or item["target"] not in {"text", "meta", "attachments"} or item["replacement"] not in MARKERS:
            raise CaptureError("Invalid redaction category, target or replacement")
        if "count" in item and (type(item["count"]) is not int or item["count"] < 1):
            raise CaptureError("Redaction count must be positive")


def capture_input(raw, completeness):
    """Validate supplied messages; no runtime history or completeness audit."""
    if isinstance(raw, list):
        if completeness != "partial":
            raise CaptureError("Complete capture requires an inventory envelope; legacy arrays are partial")
        return raw, None, completeness
    if not isinstance(raw, dict) or set(raw) != {"version", "capture", "messages"} or raw["version"] != 1:
        raise CaptureError("Use a legacy array or a version 1 capture envelope")
    spec = raw["capture"]
    required = {"source_system", "source_conversation_id", "source_id_origin", "order_basis"}
    optional = {"completeness", "available_source_message_ids", "gaps"}
    if not isinstance(spec, dict) or not required.issubset(spec) or set(spec) - required - optional:
        raise CaptureError("Capture envelope needs source provenance")
    spec = copy.deepcopy(spec)
    spec.setdefault("completeness", "partial")  # Compatibility metadata, not an audited claim.
    spec.setdefault("gaps", [])
    identifier(spec["source_system"])
    source_id(spec["source_conversation_id"])
    if spec["source_id_origin"] not in ID_ORIGINS - {"unknown"} or spec["order_basis"] not in ORDER_BASES or spec["completeness"] not in {"partial", "complete"}:
        raise CaptureError("Declare source ID origin and fragment completeness")
    messages = raw["messages"]
    if not isinstance(messages, list):
        raise CaptureError("Messages must be an array")
    spec.setdefault("available_source_message_ids", [message.get("source_message_id") if isinstance(message, dict) else None for message in messages])
    available = spec["available_source_message_ids"]
    if not isinstance(messages, list) or not isinstance(available, list) or len(set(source_id(s) for s in available)) != len(available):
        raise CaptureError("Available source inventory must contain unique IDs")
    if any(not isinstance(message, dict) for message in messages) or [message.get("source_message_id") for message in messages] != available:
        raise CaptureError("Capture must include every available project message in inventory order")
    orders = [message.get("original_order") for message in messages]
    if any(type(order) is not int or order < 1 for order in orders) or any(a >= b for a, b in zip(orders, orders[1:])):
        raise CaptureError("Full capture needs explicit increasing original source order")
    for message in messages:
        if message.get("source_channel") not in SOURCE_CHANNELS - {"unknown"}:
            raise CaptureError("Full capture includes only user or user-facing assistant channels")
        expected_source = "user_message" if message["source_channel"] == "user" else "assistant_message"
        if message.get("source", expected_source) != expected_source:
            raise CaptureError("Capture source must match its user-facing channel")
    validate_gaps(spec["gaps"], available, spec["completeness"])
    return messages, copy.deepcopy(spec), spec["completeness"]


def validate_gaps(gaps, available, completeness):
    if not isinstance(gaps, list) or (completeness == "complete" and gaps):
        raise CaptureError("Optional gaps must be an array; a complete claim cannot also declare gaps")
    seen = set()
    for gap in gaps:
        allowed = {"id", "reason", "source_message_id", "after_source_message_id", "before_source_message_id", "original_order"}
        if not isinstance(gap, dict) or not {"id", "reason"}.issubset(gap) or set(gap) - allowed:
            raise CaptureError("Gap records describe missing context, never reconstructed text")
        identifier(gap["id"])
        if gap["id"] in seen or gap["reason"] not in GAP_REASONS:
            raise CaptureError("Invalid or duplicate gap record")
        seen.add(gap["id"])
        missing = gap.get("source_message_id")
        if missing is not None:
            source_id(missing)
            if missing in available and gap["reason"] != "unavailable_attachment":
                raise CaptureError("An available message cannot be replaced by a gap")
        if gap["reason"] == "unavailable_attachment" and missing not in available:
            raise CaptureError("An attachment gap must identify its available source message")
        for key in ("after_source_message_id", "before_source_message_id"):
            if gap.get(key) is not None and gap[key] not in available:
                raise CaptureError("Gap boundaries must reference this fragment's source messages")
        if "original_order" in gap and (type(gap["original_order"]) is not int or gap["original_order"] < 1):
            raise CaptureError("Gap order must be positive when known")


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
    if not isinstance(value, str):
        raise CaptureError("A Git binding needs an actual repository URL")
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


def binding_identity(doc):
    """Structural identity only: inactive local mappings must not block other projects."""
    kind = doc.get("binding_kind", "git_repository")
    if kind == "git_repository":
        return {"repository": repository_url(doc.get("repository"))}
    if kind != "local_directory" or "repository" not in doc or doc["repository"] is not None or doc.get("export_policy") != "local_only":
        raise CaptureError("Unsupported project binding")
    identity = doc.get("project_id")
    try:
        if not isinstance(identity, str) or str(uuid.UUID(identity)) != identity:
            raise ValueError()
    except (ValueError, AttributeError):
        raise CaptureError("Local project identity needs a canonical UUID") from None
    root = doc.get("project_root")
    if not isinstance(root, str) or not Path(root).is_absolute() or str(Path(root).resolve()) != root:
        raise CaptureError("Local project identity needs an exact absolute path")
    if any(p.is_symlink() for p in [Path(root), *Path(root).parents]):
        raise CaptureError("Local project paths cannot be symlinks")
    stat = doc.get("root_identity")
    if not isinstance(stat, dict) or set(stat) != {"device", "inode"} or any(type(v) is not int or v < 0 for v in stat.values()):
        raise CaptureError("Local project identity needs directory device and inode")
    return {"binding_kind": kind, "project_id": identity, "project_root": root,
            "root_identity": dict(stat), "repository": None, "export_policy": "local_only"}


def verify_local_root(doc):
    identity = binding_identity(doc)
    if identity.get("binding_kind") == "local_directory":
        root = Path(identity["project_root"])
        if not root.is_dir():
            raise CaptureError("Registered local project is missing; explicit rebinding is required")
        stat = root.stat()
        if identity["root_identity"] != {"device": stat.st_dev, "inode": stat.st_ino}:
            raise CaptureError("Registered local directory changed; explicit rebinding is required")
    return identity


def state(root, branch, writing=True):
    root = root.resolve()
    if branch == "local":
        if any((parent / ".git").exists() for parent in [root, *root.parents]):
            raise CaptureError("Local memory must be outside every Git checkout")
        marker = root / "local-store.json"
        if marker.is_symlink():
            raise CaptureError("Local store marker cannot be a symlink")
        doc = load(marker)
        if not doc or doc.get("kind") != "macaroni_local_store" or doc.get("root") != str(root):
            raise CaptureError("Local capture requires an explicitly registered private store")
        scan(doc)
        identity = verify_local_root(doc)
        if identity.get("binding_kind") == "local_directory" and (root.stat().st_mode & 0o077 or marker.stat().st_mode & 0o077):
            raise CaptureError("Local directory memory needs private store and marker permissions")
        protocol = load(target(root, ".macaroni/protocol.json"))
        if protocol is not None and (binding_identity(protocol) != identity or protocol.get("storage_branch") != "local"):
            raise CaptureError("Local protocol differs from the registered store identity")
        return {"repo_root": str(root), **identity, "branch": "local", "base_commit": None, "store_identity": digest(marker.read_bytes())}
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
        "original_created_at": meta.get("original_created_at"), "redacted": meta.get("redacted", False),
        "source_system": meta.get("source_system", "unknown"), "source_conversation_id": meta.get("source_conversation_id"),
        "source_id_origin": meta.get("source_id_origin", "unknown"), "source_channel": meta.get("source_channel", "unknown"),
        "redactions": meta.get("redactions", [])}


def plan_digest(plan):
    unsigned = {key: value for key, value in plan.items() if key != "review_digest"}
    return object_digest(unsigned)


def object_digest(doc):
    return digest(json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def prepare(root, raw_messages, chat_id, branch="macaroni", repo_url=None, completeness="partial", chat_title="AGENT_ROOM"):
    destination = state(root, branch)
    if repo_url and repository_url(repo_url) != destination["repository"]:
        raise CaptureError("Requested repository does not match origin")
    identifier(chat_id)
    if completeness not in {"partial", "complete"}:
        raise CaptureError("Capture completeness must be partial or complete")
    protocol = load(target(root, ".macaroni/protocol.json"))
    if protocol is not None and (binding_identity(protocol) != binding_identity(destination) or protocol["storage_branch"] != branch):
        raise CaptureError("Protocol repository or storage branch does not match destination")
    scan(raw_messages)  # No setup files or plans written before the entire input passes.
    raw_messages, capture_spec, completeness = capture_input(raw_messages, completeness)
    if not isinstance(raw_messages, list) or not raw_messages:
        raise CaptureError("Capture needs a non-empty JSON array")
    existing, ids = existing_messages(root)
    normal = []
    source_ids = set()
    known_orders = {}
    if capture_spec:
        for old_source, (_, old_doc) in existing.items():
            old_meta = old_doc["meta"]
            if old_meta.get("source_system") == capture_spec["source_system"] and old_meta.get("source_conversation_id") == capture_spec["source_conversation_id"] and old_meta.get("original_order_basis") == capture_spec["order_basis"]:
                if old_meta["original_order"] in known_orders and known_orders[old_meta["original_order"]] != old_source:
                    raise CaptureError("Stored source conversation has conflicting original order")
                known_orders[old_meta["original_order"]] = old_source
    for order, raw in enumerate(raw_messages, 1):
        if not isinstance(raw, dict):
            raise CaptureError("Each source message must be an object")
        source = source_id(raw.get("source_message_id"))
        if source in source_ids:
            raise CaptureError("Every message needs a unique stable source_message_id")
        source_ids.add(source)
        old = existing.get(source)
        # Replaying an older batch must keep the original implicit participants.
        prior = old[1] if old else {}
        default_sender = "CODEX" if prior.get("from") == "CODEX" else AGENT_ID
        sender = identifier(raw.get("from", default_sender))
        assistant_recipient = "CODEX" if prior.get("to") == ["CODEX"] else AGENT_ID
        recipients = raw.get("to", [assistant_recipient if sender == "HUMAN" else "HUMAN"])
        sender_name = raw.get("from_name", sender.title())
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
        original_order = raw.get("original_order", order)
        if type(original_order) is not int or original_order < 1:
            raise CaptureError("Original order must be a positive integer")
        if capture_spec and original_order in known_orders and known_orders[original_order] != source:
            raise CaptureError("Original source order already belongs to another message")
        redactions = copy.deepcopy(raw.get("redactions", metadata.get("redactions", [])))
        validate_redactions(redactions, raw.get("redacted", False), required=capture_spec is not None)
        source_kind = "user_message" if (raw.get("source_channel") == "user" if capture_spec else sender == "HUMAN") else "assistant_message"
        metadata.update({"captured_by": AGENT_ID, "source": raw.get("source", source_kind), "source_message_id": source, "redacted": bool(raw.get("redacted", False)), "original_created_at": original, "original_timestamp_status": "known" if original else "unknown", "created_at_basis": "capture_time", "original_order": order, "capture_completeness": completeness})
        metadata.update({"original_order": original_order, "original_order_basis": capture_spec["order_basis"] if capture_spec else ("source_conversation" if "original_order" in raw else "capture_batch"), "redactions": redactions,
                         "source_system": capture_spec["source_system"] if capture_spec else metadata.get("source_system", "unknown"),
                         "source_conversation_id": capture_spec["source_conversation_id"] if capture_spec else metadata.get("source_conversation_id"),
                         "source_id_origin": capture_spec["source_id_origin"] if capture_spec else metadata.get("source_id_origin", "unknown"),
                         "source_channel": raw.get("source_channel", metadata.get("source_channel", "unknown"))})
        reply_source = raw.get("reply_to_source_id")
        if reply_source:
            metadata["source_reply_to_message_id"] = reply_source
        normal.append({"version": 1, "id": msg_id, "chat_id": chat_id, "type": "text", "from": sender, "from_name": sender_name, "to": recipients, "created_at": captured, "text": raw["text"], "reply_to": raw.get("reply_to"), "attachments": copy.deepcopy(raw.get("attachments", [])), "meta": metadata, "signature": None})
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
            raw = next(r for r in raw_messages if r["source_message_id"] == source)
            if semantic(old[1]) != semantic(doc) or ("original_order" in raw and old[1]["meta"].get("original_order") != raw["original_order"]) or any(old[1]["meta"].get(k) != v for k, v in raw.get("meta", {}).items()):
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
    manifest_path = None
    if capture_spec:
        rows = []
        for doc in normal:
            source = doc["meta"]["source_message_id"]
            if source in existing:
                relative, stored = existing[source]
                message_hash = digest(target(root, relative).read_bytes())
            else:
                stored = doc
                day = dt.datetime.fromisoformat(doc["created_at"].replace("Z", "+00:00")).strftime("%Y/%m/%d")
                relative = f".macaroni/chats/{chat_id}/messages/{day}/{doc['id']}.json"
                message_hash = digest(encoded(doc))
            rows.append({"source_message_id": source, "message_id": stored["id"], "message_path": relative, "message_sha256": message_hash, "original_order": stored["meta"]["original_order"]})
        manifest = {"version": 1, "kind": "conversation_capture", "chat_id": chat_id, "policy": "all_available_project_messages", **capture_spec, "messages": rows}
        capture_id = "capture_" + object_digest(manifest)[:32]
        manifest.update({"id": capture_id, "prepared_at": now()})
        relative = f".macaroni/chats/{chat_id}/captures/{capture_id}.json"
        manifest_path = relative
        old_manifest = load(target(root, relative))
        if old_manifest:
            if any(old_manifest.get(k) != v for k, v in manifest.items() if k != "prepared_at"):
                raise CaptureError("Capture inventory collision; existing manifests are immutable")
        else:
            propose(relative, manifest)
    if changes:
        stamp = now()
        protocol_path = ".macaroni/protocol.json"
        protocol = load(target(root, protocol_path))
        if protocol is None:
            propose(protocol_path, {"version": 1, "name": "Macaroni Project Memory", **binding_identity(destination), "storage_branch": branch, "created_at": stamp, "updated_at": stamp, "meta": {}})
        elif binding_identity(protocol) != binding_identity(destination) or protocol["storage_branch"] != branch:
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
    plan = {"version": 1, "destination": destination, "chat_id": chat_id, "messages_new": len(normal) - skipped, "messages_skipped": skipped, "capture_policy": "all_available_project_messages" if capture_spec else "legacy_partial_fragment", "changes": list(changes.values())}
    if manifest_path:
        plan["capture_manifest_path"] = manifest_path
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
    if protocol is not None and (binding_identity(protocol) != binding_identity(plan["destination"]) or protocol["storage_branch"] != plan["destination"]["branch"]):
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
            if binding_identity(doc) != binding_identity(plan["destination"]) or doc["storage_branch"] != plan["destination"]["branch"]:
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
        elif len(parts) == 5 and parts[1] == "chats" and parts[3] == "captures":
            if old_bytes is not None or parts[2] != plan["chat_id"] or parts[-1] != doc.get("id", "") + ".json":
                raise CaptureError("Capture manifest overwrite or path mismatch")
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
            meta = doc["meta"]
            if "source_system" in meta:
                identifier(meta["source_system"])
            if meta.get("source_conversation_id") is not None:
                source_id(meta["source_conversation_id"])
            if meta.get("source_id_origin", "unknown") not in ID_ORIGINS or meta.get("source_channel", "unknown") not in SOURCE_CHANNELS or meta.get("original_order_basis", "capture_batch") not in ORDER_BASES | {"capture_batch"}:
                raise CaptureError("Invalid source provenance")
            validate_redactions(meta.get("redactions", []), meta["redacted"])
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
    manifests = {relative for relative in pending if "/captures/" in relative}
    manifest_path = plan.get("capture_manifest_path")
    if plan.get("capture_policy") == "all_available_project_messages":
        if not manifest_path or manifests - {manifest_path}:
            raise CaptureError("Full capture needs its exact inventory manifest")
        manifest = pending.get(manifest_path) or load(target(root, manifest_path))
        validate_manifest(root, plan, manifest_path, manifest, pending)
        covered = {row["message_path"] for row in manifest["messages"]}
        if any("/messages/" in relative and relative not in covered for relative in pending):
            raise CaptureError("Message is absent from the capture inventory")
    elif manifests or manifest_path:
        raise CaptureError("Capture manifests require the full capture policy")


def validate_manifest(root, plan, relative, doc, pending):
    required = {"version", "kind", "id", "chat_id", "policy", "source_system", "source_conversation_id", "source_id_origin", "order_basis", "completeness", "available_source_message_ids", "gaps", "messages", "prepared_at"}
    if not isinstance(doc, dict) or not required.issubset(doc) or doc["version"] != 1 or doc["kind"] != "conversation_capture" or doc["policy"] != "all_available_project_messages" or doc["chat_id"] != plan["chat_id"]:
        raise CaptureError("Invalid capture inventory manifest")
    identity = {k: v for k, v in doc.items() if k in required - {"id", "prepared_at"}}
    expected_id = "capture_" + object_digest(identity)[:32]
    if doc["id"] != expected_id or relative != f".macaroni/chats/{plan['chat_id']}/captures/{expected_id}.json":
        raise CaptureError("Capture inventory identity or path mismatch")
    timestamp(doc["prepared_at"])
    identifier(doc["source_system"])
    source_id(doc["source_conversation_id"])
    if doc["source_id_origin"] not in ID_ORIGINS - {"unknown"} or doc["order_basis"] not in ORDER_BASES or doc["completeness"] not in {"partial", "complete"}:
        raise CaptureError("Invalid capture source provenance")
    available = doc["available_source_message_ids"]
    rows = doc["messages"]
    if not isinstance(available, list) or not available or len(set(source_id(s) for s in available)) != len(available) or not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows) or [row.get("source_message_id") for row in rows] != available:
        raise CaptureError("Capture inventory does not cover every available message")
    validate_gaps(doc["gaps"], available, doc["completeness"])
    previous_order = 0
    for row in rows:
        if set(row) != {"source_message_id", "message_id", "message_path", "message_sha256", "original_order"} or type(row["original_order"]) is not int or row["original_order"] <= previous_order:
            raise CaptureError("Capture inventory order or fields are invalid")
        previous_order = row["original_order"]
        path = target(root, row["message_path"])
        message = pending.get(row["message_path"]) or load(path)
        data = encoded(message) if row["message_path"] in pending else path.read_bytes()
        if not message or "/messages/" not in row["message_path"] or message["chat_id"] != doc["chat_id"] or message["id"] != row["message_id"] or digest(data) != row["message_sha256"]:
            raise CaptureError("Capture inventory message reference or hash mismatch")
        meta = message["meta"]
        for key in ("source_system", "source_conversation_id", "source_id_origin"):
            if meta.get(key) != doc[key]:
                raise CaptureError("Capture inventory disagrees with message provenance")
        if meta.get("source_message_id") != row["source_message_id"] or meta.get("original_order") != row["original_order"] or meta.get("original_order_basis") != doc["order_basis"] or meta.get("source_channel") not in SOURCE_CHANNELS - {"unknown"}:
            raise CaptureError("Capture inventory disagrees with source order or channel")
        validate_redactions(meta.get("redactions", []), meta.get("redacted", False), required=True)


def apply(root, plan):
    validate_plan(root, plan)
    if not plan["changes"]:
        return 0
    lock = root / ".capture.lock" if plan["destination"]["branch"] == "local" else Path(git(root, "rev-parse", "--git-path", "macaroni-capture.lock"))
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
                directory.mkdir(mode=0o700 if plan["destination"]["branch"] == "local" else 0o777)
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
                if plan["destination"]["branch"] == "local":
                    os.chmod(restore, 0o600)
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
        row.update({key: meta.get(key) for key in ("source_system", "source_conversation_id", "source_id_origin", "source_channel", "original_order", "original_order_basis", "capture_completeness", "redacted")})
        scan(row)
        rows.append(row)
    captures = []
    matched = {row["path"] for row in rows}
    for path in sorted((root / ".macaroni/chats").glob("*/captures/*.json")):
        target(root, path.relative_to(root).as_posix())
        doc = load(path)
        if query and not any(row.get("message_path") in matched for row in doc.get("messages", [])):
            continue
        row = {"path": path.relative_to(root).as_posix(), "id": doc["id"], "chat_id": doc["chat_id"], "source_conversation_id": doc.get("source_conversation_id"), "completeness": doc.get("completeness"), "messages_count": len(doc.get("messages", [])), "gaps_count": len(doc.get("gaps", []))}
        scan(row)
        captures.append(row)
    return {"version": 1, "kind": "derived_source_index", "messages": rows, "captures": captures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", metavar="PLAN_JSON")
    mode.add_argument("--apply-plan", metavar="PLAN_JSON")
    mode.add_argument("--index", action="store_true")
    parser.add_argument("--search")
    parser.add_argument("--batch-json", help="Source-provenance envelope (inventory optional), or a legacy partial message array")
    parser.add_argument("--chat-id")
    parser.add_argument("--chat-title", default="AGENT_ROOM")
    parser.add_argument("--storage-branch", default="macaroni")
    parser.add_argument("--repo-url")
    parser.add_argument("--completeness", choices=["partial", "complete"], default="partial", help="Legacy arrays must be partial; envelopes declare their own completeness")
    parser.add_argument("--source-message-id")
    parser.add_argument("--from-id")
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
                row = {"source_message_id": args.source_message_id, "text": text, "original_created_at": args.created_at, "redacted": args.redacted}
                if args.from_id:
                    row["from"] = args.from_id
                if args.from_name:
                    row["from_name"] = args.from_name
                if args.to:
                    row["to"] = args.to.split(",")
                if args.source:
                    row["source"] = args.source
                raw = [row]
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
