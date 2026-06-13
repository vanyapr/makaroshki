#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path


HIGH_CONFIDENCE_SECRET = re.compile(
    r"(github_pat_[A-Za-z0-9_]{20,}|"
    r"gh[opusb]_[A-Za-z0-9]{20,}|"
    r"Authorization:\s*Bearer\s+[A-Za-z0-9._-]{20,}|"
    r"BEGIN (RSA|OPENSSH|PGP) PRIVATE KEY|"
    r"AKIA[0-9A-Z]{16})"
)


def utc_now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_time(value):
    if not value:
        return utc_now()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = dt.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def path_time(created_at):
    value = created_at[:-1] + "+00:00" if created_at.endswith("Z") else created_at
    return dt.datetime.fromisoformat(value).astimezone(dt.timezone.utc)


def safe_id(value):
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    return cleaned or "AGENT"


def message_id(created_at, from_id, text, index):
    stamp = created_at.replace(":", "-")
    digest = hashlib.sha1((str(index) + "\n" + text).encode("utf-8")).hexdigest()[:6]
    return f"{stamp}_{safe_id(from_id)}_{digest}"


def write_json(root, relative, payload):
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_protocol(root, repo_url, storage_branch, now):
    path = root / ".macaroni/protocol.json"
    existing = read_json(path) or {}
    payload = {
        "version": existing.get("version", 1),
        "name": existing.get("name", "Macaroni Memory"),
        "repository": existing.get("repository", repo_url or ""),
        "storage_branch": existing.get("storage_branch", storage_branch),
        "created_at": existing.get("created_at", now),
        "updated_at": now,
        "meta": existing.get("meta", {}),
    }
    payload["meta"].setdefault("purpose", "Git-native agent memory using .macaroni messages.")
    write_json(root, ".macaroni/protocol.json", payload)


def ensure_user(root, user_id, display_name, role, now):
    user_id = safe_id(user_id)
    rel = f".macaroni/users/{user_id}.json"
    existing = read_json(root / rel) or {}
    payload = {
        "version": existing.get("version", 1),
        "id": existing.get("id", user_id),
        "display_name": existing.get("display_name", display_name or user_id),
        "role": existing.get("role", role),
        "created_at": existing.get("created_at", now),
        "updated_at": now,
        "meta": existing.get("meta", {}),
    }
    payload["meta"].setdefault("source", "macaroni-memory-skill")
    write_json(root, rel, payload)


def ensure_chat(root, chat_id, title, members, now):
    meta_rel = f".macaroni/chats/{chat_id}/meta.json"
    members_rel = f".macaroni/chats/{chat_id}/members.json"
    existing_meta = read_json(root / meta_rel) or {}
    meta = {
        "version": existing_meta.get("version", 1),
        "id": existing_meta.get("id", chat_id),
        "title": existing_meta.get("title", title),
        "kind": existing_meta.get("kind", "agent_room"),
        "created_at": existing_meta.get("created_at", now),
        "updated_at": now,
        "description": existing_meta.get("description", "Captured user-agent conversation."),
        "meta": existing_meta.get("meta", {}),
    }
    meta["meta"].setdefault("captured_by", "CODEX")
    write_json(root, meta_rel, meta)

    existing_members = read_json(root / members_rel) or {}
    existing_by_id = {item.get("id"): item for item in existing_members.get("members", [])}
    for member in members:
        existing_by_id.setdefault(member["id"], member)
    payload = {
        "version": existing_members.get("version", 1),
        "chat_id": chat_id,
        "members": list(existing_by_id.values()),
        "updated_at": now,
    }
    write_json(root, members_rel, payload)


def normalize_message(raw, defaults):
    text = raw.get("text")
    if text is None and raw.get("text_file"):
        text = Path(raw["text_file"]).read_text(encoding="utf-8")
    if text is None:
        raise SystemExit("message is missing text or text_file")
    to = raw.get("to", defaults["to"])
    if isinstance(to, str):
        to = [part.strip() for part in to.split(",") if part.strip()]
    return {
        "from": safe_id(raw.get("from", defaults["from_id"])),
        "from_name": raw.get("from_name", defaults["from_name"]),
        "to": [safe_id(item) for item in to],
        "source": raw.get("source", defaults["source"]),
        "text": text,
        "redacted": bool(raw.get("redacted", defaults["redacted"])),
        "created_at": parse_time(raw.get("created_at")),
    }


def write_message(root, chat_id, message, index, captured_by, fail_on_secret):
    if fail_on_secret and HIGH_CONFIDENCE_SECRET.search(message["text"]):
        raise SystemExit(f"high-confidence secret pattern found in message {index}; redact before writing")

    created_at = message["created_at"]
    parsed = path_time(created_at)
    msg_id = message_id(created_at, message["from"], message["text"], index)
    msg_rel = (
        f".macaroni/chats/{chat_id}/messages/"
        f"{parsed:%Y/%m/%d}/{msg_id}.json"
    )
    doc = {
        "version": 1,
        "id": msg_id,
        "chat_id": chat_id,
        "type": "text",
        "from": message["from"],
        "from_name": message["from_name"],
        "to": message["to"],
        "created_at": created_at,
        "text": message["text"],
        "reply_to": None,
        "attachments": [],
        "meta": {
            "captured_by": captured_by,
            "source": message["source"],
            "redacted": message["redacted"],
            "capture_batch": "macaroni-memory-skill",
            "original_order": index,
        },
        "signature": None,
    }
    write_json(root, msg_rel, doc)

    for recipient in message["to"]:
        inbox_rel = f".macaroni/inbox/{recipient}/{msg_id}.json"
        write_json(root, inbox_rel, {
            "version": 1,
            "recipient": recipient,
            "message_id": msg_id,
            "chat_id": chat_id,
            "message_path": msg_rel,
            "created_at": created_at,
            "meta": {
                "captured_by": captured_by,
                "source": "macaroni-memory-skill",
            },
        })
    return msg_rel


def main():
    parser = argparse.ArgumentParser(description="Write Protocol v1 .macaroni messages.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--chat-id")
    parser.add_argument("--chat-title", default="AGENT_ROOM")
    parser.add_argument("--repo-url", default="")
    parser.add_argument("--storage-branch", default="macaroni")
    parser.add_argument("--captured-by", default="CODEX")
    parser.add_argument("--from-id", default="CODEX")
    parser.add_argument("--from-name", default="Codex")
    parser.add_argument("--to", default="HUMAN")
    parser.add_argument("--source", default="assistant_message")
    parser.add_argument("--text-file")
    parser.add_argument("--text")
    parser.add_argument("--created-at")
    parser.add_argument("--redacted", action="store_true")
    parser.add_argument("--batch-json")
    parser.add_argument("--allow-sensitive", action="store_true")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    if not root.exists():
        raise SystemExit(f"repo root does not exist: {root}")

    now = utc_now()
    chat_id = args.chat_id or f"chat_{now[:10].replace('-', '')}_agent_room"
    defaults = {
        "from_id": args.from_id,
        "from_name": args.from_name,
        "to": args.to,
        "source": args.source,
        "redacted": args.redacted,
    }

    if args.batch_json:
        raw_messages = json.loads(Path(args.batch_json).read_text(encoding="utf-8"))
        if not isinstance(raw_messages, list):
            raise SystemExit("--batch-json must contain a JSON array")
    else:
        if args.text_file:
            text = Path(args.text_file).read_text(encoding="utf-8")
        elif args.text is not None:
            text = args.text
        else:
            raise SystemExit("provide --text, --text-file, or --batch-json")
        raw_messages = [{
            "from": args.from_id,
            "from_name": args.from_name,
            "to": args.to,
            "source": args.source,
            "text": text,
            "created_at": args.created_at,
            "redacted": args.redacted,
        }]

    messages = [normalize_message(item, defaults) for item in raw_messages]

    ensure_protocol(root, args.repo_url, args.storage_branch, now)
    member_ids = {}
    for message in messages:
        member_ids[message["from"]] = {
            "id": message["from"],
            "role": "agent" if message["from"] != "HUMAN" else "owner",
            "joined_at": now,
        }
        ensure_user(root, message["from"], message["from_name"], member_ids[message["from"]]["role"], now)
        for recipient in message["to"]:
            member_ids.setdefault(recipient, {
                "id": recipient,
                "role": "participant",
                "joined_at": now,
            })
            ensure_user(root, recipient, recipient.title(), member_ids[recipient]["role"], now)

    ensure_chat(root, chat_id, args.chat_title, list(member_ids.values()), now)

    written = []
    for index, message in enumerate(messages, start=1):
        written.append(write_message(root, chat_id, message, index, args.captured_by, not args.allow_sensitive))

    print(json.dumps({
        "chat_id": chat_id,
        "messages_written": len(written),
        "message_paths": written,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
