#!/usr/bin/env python3
"""Explicit agent-driven capture. JSON on stdin; no hooks, history reader or daemon."""
import argparse
from contextlib import contextmanager
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit

import flush_messages as flush
import regular_capture as regular
import write_messages as memory


def project(config, root):
    return regular.project_binding(config, root)


def exclusive(path, doc):
    """Append one private, synced JSON document; keep an identical prior record."""
    if path.exists():
        old = memory.load(path)
        if any(old.get(k) != v for k, v in doc.items() if k != 'created_at'):
            raise memory.CaptureError('Existing record differs')
        return False
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as file:
        file.write(memory.encoded(doc))
        file.flush()
        os.fsync(file.fileno())
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return True


def reply_path(store, reply_id, receipt=False):
    memory.identifier(reply_id)
    if not reply_id.startswith('assigned_reply_'):
        raise memory.CaptureError('Prepared replies need an explicitly assigned ID')
    return memory.target(store, '.macaroni/' + ('prepared_receipts/' if receipt else 'prepared/') + reply_id + '.json')


def check_reply(config, root, expected):
    entry = project(config, root)
    store = Path(entry['store_root'])
    if memory.binding_identity(memory.state(store, 'local')) != memory.binding_identity(entry):
        raise memory.CaptureError('Stored project identity differs')
    path = reply_path(store, expected['reply_id'])
    doc = memory.load(path)
    if memory.binding_identity(doc) != memory.binding_identity(entry) or memory.digest(path.read_bytes()) != expected['file_sha256'] or memory.digest(doc['text'].encode()) != expected['text_sha256']:
        raise memory.CaptureError('Prepared reply verification failed')
    return {'reply_id': doc['id'], 'fresh_process_verified': True, 'text_sha256': expected['text_sha256'], 'delivery_state': 'prepared_unconfirmed'}


def prepare_reply(config, root, raw):
    entry = project(config, root)
    flush.reject_hidden(raw)
    required = {'version', 'source_system', 'source_conversation_id', 'reply_id', 'source_channel', 'text'}
    if not isinstance(raw, dict) or not required.issubset(raw) or set(raw) - required - {'reply_to_source_message_id'} or raw['version'] != 1:
        raise memory.CaptureError('Use the prepared-reply schema')
    memory.identifier(raw['source_system'])
    memory.source_id(raw['source_conversation_id'])
    memory.identifier(raw['reply_id'])
    if not raw['reply_id'].startswith('assigned_reply_') or raw['source_channel'] not in {'assistant_final', 'assistant_commentary'} or not isinstance(raw['text'], str) or not raw['text']:
        raise memory.CaptureError('Only a frozen user-facing assistant reply can be prepared')
    text, redactions = regular.redact(raw['text'])
    doc = {'version': 1, 'kind': 'prepared_assistant_reply', 'id': raw['reply_id'],
        **memory.binding_identity(entry), 'source_system': raw['source_system'],
        'source_conversation_id': raw['source_conversation_id'], 'source_channel': raw['source_channel'],
        'reply_to_source_message_id': raw.get('reply_to_source_message_id'), 'text': text,
        'text_sha256': memory.digest(text.encode()), 'redactions': redactions,
        'delivery_state': 'prepared_unconfirmed', 'created_at': memory.now()}
    if doc['reply_to_source_message_id'] is not None:
        memory.source_id(doc['reply_to_source_message_id'])
    memory.scan(doc)  # Raw text is redacted and all metadata checked before creating a store.
    store = regular.private_store(entry)
    with regular.observation_lock(store):
        if doc['reply_to_source_message_id'] is not None:
            known, _ = memory.existing_messages(store)
            prior = known.get(doc['reply_to_source_message_id'])
            if not prior or prior[1]['meta'].get('source_channel') != 'user' or prior[1]['meta'].get('source_system') != doc['source_system'] or prior[1]['meta'].get('source_conversation_id') != doc['source_conversation_id']:
                raise memory.CaptureError('Capture the actual user source in this project first')
        path = reply_path(store, doc['id'])
        created = exclusive(path, doc)
        expected = {'reply_id': doc['id'], 'file_sha256': memory.digest(path.read_bytes()), 'text_sha256': doc['text_sha256']}
        run = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--config', str(config), '--project-root', str(root), '--check-reply'], input=memory.encoded(expected), capture_output=True)
        if run.returncode:
            raise memory.CaptureError('New-process prepared reply check failed')
        result = memory.strict_json(run.stdout.decode())
    result.update({'created': created, 'reply_path': str(path), 'reply_text_to_emit': text,
        'observed_assistant_message_saved': False})
    return result


def confirm_reply(config, root, raw, reply_id):
    entry = project(config, root)
    store = Path(entry['store_root'])
    memory.identifier(reply_id)
    with confirmation_lock(store, reply_id):
        return _confirm_reply(config, root, raw, reply_id, entry, store)


@contextmanager
def confirmation_lock(store, reply_id):
    lock = memory.target(store, '.macaroni/.prepared-confirm-' + reply_id + '.lock')
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    try:
        yield
    finally:
        lock.unlink()


def _confirm_reply(config, root, raw, reply_id, entry, store):
    doc = memory.load(reply_path(store, reply_id))
    flush.reject_hidden(raw)
    memory.capture_input(raw, 'partial')
    if len(raw['messages']) != 1:
        raise memory.CaptureError('Confirm exactly one observed assistant message')
    message = raw['messages'][0]
    text, _ = regular.redact(message['text'])
    if memory.binding_identity(doc) != memory.binding_identity(entry) or raw['capture']['source_system'] != doc['source_system'] or raw['capture']['source_conversation_id'] != doc['source_conversation_id'] or message.get('from') not in memory.ASSISTANT_IDS or message.get('source_channel') != doc['source_channel'] or text != doc['text']:
        raise memory.CaptureError('Observed reply differs from the prepared reply or source')
    receipt_path = reply_path(store, reply_id, receipt=True)
    if receipt_path.exists() and memory.load(receipt_path)['source_message_id'] != message['source_message_id']:
        raise memory.CaptureError('Prepared reply is already linked to another source')
    batch = copy.deepcopy(raw)
    batch['messages'][0].setdefault('meta', {})['prepared_reply_id'] = reply_id
    result = flush.flush(config, root, batch)
    with regular.observation_lock(store):
        known, _ = memory.existing_messages(store)
        relative, saved = known[message['source_message_id']]
        receipt = {'version': 1, 'kind': 'confirmed_prepared_reply', 'prepared_reply_id': reply_id,
            **memory.binding_identity(doc), 'source_conversation_id': doc['source_conversation_id'],
            'source_message_id': message['source_message_id'], 'message_path': relative,
            'text_sha256': memory.digest(saved['text'].encode()), 'created_at': memory.now()}
        exclusive(receipt_path, receipt)
    result.update({'prepared_reply_id': reply_id, 'delivery_state': 'observed', 'receipt_path': str(receipt_path)})
    return result


def status(config, root):
    entry = project(config, root)
    store = Path(entry['store_root'])
    if store.exists() and memory.binding_identity(memory.state(store, 'local')) != memory.binding_identity(entry):
        raise memory.CaptureError('Stored project identity differs')
    known, _ = memory.existing_messages(store) if store.exists() else ({}, set())
    pending = []
    for path in sorted((store/'.macaroni/prepared').glob('*.json')):
        draft = memory.load(path)
        if not reply_path(store, draft['id'], receipt=True).exists():
            pending.append({'reply_id': draft['id'], 'source_conversation_id': draft['source_conversation_id'], 'path': str(path), 'delivery_state': 'prepared_unconfirmed'})
    return {**memory.binding_identity(entry), 'store_root': str(store), 'observed_messages': len(known),
        'source_message_ids': sorted(known), 'prepared_unconfirmed_replies': pending,
        'upstream_history_completeness': 'not_established'}


def reference_source(config, raw):
    """Ambiguous project: store only an explicit source reference, never a body."""
    flush.reject_hidden(raw)
    required = {'version', 'source_system', 'source_conversation_id'}
    optional = {'source_message_id', 'source_uri', 'candidate_repositories'}
    if not isinstance(raw, dict) or not required.issubset(raw) or set(raw) - required - optional or raw['version'] != 1:
        raise memory.CaptureError('References accept source IDs/URI only, not messages')
    memory.identifier(raw['source_system'])
    memory.source_id(raw['source_conversation_id'])
    if raw.get('source_message_id') is not None:
        memory.source_id(raw['source_message_id'])
    if raw.get('source_uri') is not None:
        if not isinstance(raw['source_uri'], str):
            raise memory.CaptureError('Source URI must be a string')
        url = urlsplit(raw['source_uri'])
        if url.scheme != 'https' or not url.netloc or url.username or url.password or url.query or url.fragment:
            raise memory.CaptureError('Use a credential-free HTTPS source link')
    record = copy.deepcopy(raw)
    record['candidate_repositories'] = [memory.repository_url(r) for r in raw.get('candidate_repositories', [])]
    memory.scan(record)
    record['id'] = 'reference_' + memory.object_digest(record)[:32]
    record['status'] = 'project_unresolved'
    config = regular.checked_path(str(config))
    regular.outside_git(config)
    lock = config.with_name(config.name + '.lock')
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    temporary = config.with_suffix('.references.new')
    try:
        doc = regular.configuration(config)
        records = doc.setdefault('unresolved_sources', [])
        if not isinstance(records, list):
            raise memory.CaptureError('Existing reference registry is invalid')
        existing = next((r for r in records if r.get('id') == record['id']), None)
        if existing is not None:
            if any(existing.get(k) != v for k,v in record.items()):
                raise memory.CaptureError('Existing reference differs')
            return {'source_reference_saved': True, 'reference_id': record['id'], 'messages_written': 0, 'created': False}
        record['created_at'] = memory.now()
        records.append(record)
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as file:
            file.write(memory.encoded(doc))
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, config)
    finally:
        temporary.unlink(missing_ok=True)
        lock.unlink()
    return {'source_reference_saved': True, 'reference_id': record['id'], 'messages_written': 0, 'created': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--project-root', type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--messages', action='store_true')
    mode.add_argument('--prepare-reply', action='store_true')
    mode.add_argument('--confirm-reply')
    mode.add_argument('--status', action='store_true')
    mode.add_argument('--reference-source', action='store_true')
    mode.add_argument('--check-reply', action='store_true')
    args = parser.parse_args()
    try:
        if not args.reference_source and not args.project_root:
            parser.error('A verified project root is required')
        if args.status:
            result = status(args.config, args.project_root)
        else:
            raw = sys.stdin.buffer.read(regular.LIMIT + 1)
            if len(raw) > regular.LIMIT:
                raise memory.CaptureError('Input exceeds size limit')
            data = memory.strict_json(raw.decode())
            if args.messages: result = flush.flush(args.config, args.project_root, data)
            elif args.prepare_reply: result = prepare_reply(args.config, args.project_root, data)
            elif args.confirm_reply: result = confirm_reply(args.config, args.project_root, data, args.confirm_reply)
            elif args.reference_source: result = reference_source(args.config, data)
            else: result = check_reply(args.config, args.project_root, data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (memory.CaptureError, ValueError, TypeError, KeyError, OSError, subprocess.SubprocessError):
        parser.exit(1, 'Agent capture blocked: input, destination or verification failed; no history was read.\n')


if __name__ == '__main__':
    main()
