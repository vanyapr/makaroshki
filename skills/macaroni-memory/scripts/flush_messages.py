#!/usr/bin/env python3
"""Flush a supplied user/assistant-only project fragment and verify it in a new process.

Read the already authorized fragment from stdin. No chat history, tool exports,
network, Git writes or publication. Raw secret values never go to temporary files.
"""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys

import regular_capture as regular
import write_messages as memory


def reject_hidden(value):
    """Exclude internal/tool fields even when nested in metadata or attachments."""
    forbidden = {"tool_output", "tool_outputs", "reasoning", "analysis", "system", "system_prompt", "developer_prompt", "internal_report", "transcript_path", "agent_transcript_path"}
    if isinstance(value, dict):
        if set(value) & forbidden:
            raise memory.CaptureError("Hidden/tool fields are not accepted")
        for child in value.values():
            reject_hidden(child)
    elif isinstance(value, list):
        for child in value:
            reject_hidden(child)


def verify(store, expected):
    if memory.binding_identity(memory.state(store, "local")) != memory.binding_identity(expected):
        raise memory.CaptureError("Verification destination mismatch")
    known, _ = memory.existing_messages(store)
    missing, mismatched = [], []
    counts = {"user": 0, "assistant": 0}
    verified_messages = []
    seen = set()
    for row in expected["messages"]:
        source = memory.source_id(row["source_message_id"])
        if source in seen:
            raise memory.CaptureError("Duplicate expected source ID")
        seen.add(source)
        stored = known.get(source)
        if stored is None:
            missing.append(source)
            continue
        relative, doc = stored
        verified_messages.append({"source_message_id": source, "message_path": relative,
            "source_channel": doc["meta"].get("source_channel"), "text_sha256": memory.digest(doc["text"].encode())})
        if relative != row["message_path"] or memory.digest(memory.target(store, relative).read_bytes()) != row["sha256"]:
            mismatched.append(source)
        if doc["meta"].get("source_channel") == "user":
            counts["user"] += 1
        elif doc["meta"].get("source_channel") in {"assistant_final", "assistant_commentary"}:
            counts["assistant"] += 1
        else:
            mismatched.append(source)
    missing_files, mismatched_files = [], []
    for row in expected.get("files", []):
        path = memory.target(store, row["path"])
        if not path.is_file():
            missing_files.append(row["path"])
        elif memory.digest(path.read_bytes()) != row["sha256"]:
            mismatched_files.append(row["path"])
    return {"coverage_scope": "supplied_user_assistant_batch", "expected_count": len(seen), "saved_count": len(seen) - len(missing), "source_message_ids": sorted(seen), "verified_messages": verified_messages, "missing_ids": missing, "mismatched_ids": sorted(set(mismatched)), "user_count": counts["user"], "assistant_count": counts["assistant"], "planned_files_checked": len(expected.get("files", [])), "missing_planned_files": missing_files, "mismatched_planned_files": mismatched_files, "all_supplied_messages_saved": not missing and not mismatched and not missing_files and not mismatched_files}


def flush(config, project_root, raw, chat_id=None):
    root = regular.checked_path(str(project_root))
    project = regular.project_binding(config, root)
    if not isinstance(raw, dict) or set(raw) != {"version", "capture", "messages"} or not isinstance(raw["messages"], list) or not raw["messages"]:
        raise memory.CaptureError("Supply a provenance envelope of user/assistant messages only")
    batch = copy.deepcopy(raw)
    reject_hidden(batch)
    for message in batch["messages"]:
        if not isinstance(message, dict) or message.get("source_channel") not in {"user", "assistant_final", "assistant_commentary"}:
            raise memory.CaptureError("Tool, internal and system rows are not accepted")
        participants = {"HUMAN"} if message["source_channel"] == "user" else memory.ASSISTANT_IDS
        if message.get("from") not in participants:
            raise memory.CaptureError("Source role and participant disagree")
        text, replacements = regular.redact(message["text"])
        message["text"] = text
        message["redactions"] = list(message.get("redactions", [])) + replacements
        message["redacted"] = message.get("redacted", False) or bool(replacements)
    memory.scan(batch)
    memory.capture_input(batch, "partial")  # Entire supplied input passes before any store creation.
    store = regular.private_store(project)
    with regular.observation_lock(store):
        known, _ = memory.existing_messages(store)
        old_chats = {known[m["source_message_id"]][1]["chat_id"] for m in batch["messages"] if m["source_message_id"] in known}
        if chat_id is None:
            if len(old_chats) > 1:
                raise memory.CaptureError("Supplied fragment spans existing chats")
            identity = {key: batch["capture"][key] for key in ("source_system", "source_conversation_id")}
            chat_id = next(iter(old_chats)) if old_chats else "chat_available_" + memory.object_digest(identity)[:32]
        plan = memory.prepare(store, batch, chat_id, branch="local")
        pending = {change["content"]["meta"]["source_message_id"]: change for change in plan["changes"] if "/messages/" in change["path"]}
        rows = []
        for message in batch["messages"]:
            source = message["source_message_id"]
            if source in pending:
                change = pending[source]
                relative, checksum = change["path"], memory.digest(memory.encoded(change["content"]))
            else:
                relative, _ = known[source]
                checksum = memory.digest(memory.target(store, relative).read_bytes())
            rows.append({"source_message_id": source, "message_path": relative, "sha256": checksum})
        expected = {**memory.binding_identity(project), "messages": rows,
                    "files": [{"path": change["path"], "sha256": memory.digest(memory.encoded(change["content"]))} for change in plan["changes"]]}
        written = memory.apply(store, plan)
        child = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--verify-store", str(store)], input=memory.encoded(expected), capture_output=True, check=False)
        if child.returncode:
            raise memory.CaptureError("Fresh-process verification failed; inspect local store")
        result = memory.strict_json(child.stdout.decode())
        if not result.get("all_supplied_messages_saved"):
            raise memory.CaptureError("A supplied message is absent or changed after flush")
    result.update({**memory.binding_identity(project), "messages_new": plan["messages_new"], "messages_skipped": plan["messages_skipped"], "files_written": written, "fresh_process_verified": True, "store_root": str(store), "upstream_history_completeness": "not_established"})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--chat-id")
    parser.add_argument("--verify-store", type=Path)
    args = parser.parse_args()
    try:
        data = sys.stdin.buffer.read(regular.LIMIT + 1)
        if len(data) > regular.LIMIT:
            raise memory.CaptureError("Input exceeds size limit")
        doc = memory.strict_json(data.decode("utf-8"))
        if args.verify_store:
            result = verify(regular.checked_path(str(args.verify_store)), doc)
        else:
            if not args.config or not args.project_root:
                parser.error("Flush requires --config and --project-root")
            result = flush(args.config, args.project_root, doc, args.chat_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if not result.get("all_supplied_messages_saved"):
            parser.exit(1)
    except (memory.CaptureError, ValueError, TypeError, KeyError, OSError, subprocess.SubprocessError):
        # No original text, secret or input-derived exception is printed.
        parser.exit(1, "Flush blocked: validation or fresh-process verification failed; no history was read.\n")


if __name__ == "__main__":
    main()
