import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('capture', Path(__file__).parents[1] / 'scripts/write_messages.py')
capture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capture)


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        self.git('init', '-b', 'macaroni')
        self.git('config', 'user.name', 'Synthetic test')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('remote', 'add', 'origin', 'https://github.com/example/project.git')
        (self.root / 'AGENTS.md').write_text('Synthetic fixture.\n')
        self.git('add', 'AGENTS.md')
        self.git('commit', '-m', 'fixture')
        self.chat = 'chat_20261003_agent_room'
        self.batch = [
            {'source_message_id': 'fixture-user-1', 'from': 'HUMAN', 'text': 'Keep the importer change scoped.', 'original_created_at': None},
            {'source_message_id': 'fixture-agent-1', 'from': 'CODEX', 'text': 'I will check the importer.', 'original_created_at': '2026-10-02T18:00:00.123456+00:00', 'reply_to_source_id': 'fixture-user-1'},
        ]

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.DEVNULL).decode().strip()

    def prepare(self, batch=None, **options):
        return capture.prepare(self.root, self.batch if batch is None else batch, self.chat, **options)

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in (self.root / '.macaroni').rglob('*') if p.is_file()}

    def write(self, path, doc):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(capture.encoded(doc))

    def committed(self):
        self.git('add', '.macaroni')
        self.git('commit', '-m', 'synthetic capture')

    def messages(self):
        return [json.loads(p.read_text()) for p in sorted((self.root / '.macaroni/chats').glob('*/messages/**/*.json'))]

    def test_prepare_never_writes_memory(self):
        plan = self.prepare()
        self.assertEqual(plan['messages_new'], 2)
        self.assertFalse((self.root / '.macaroni').exists())

    def test_apply_records_exact_text_time_source_order_and_reply(self):
        plan = self.prepare()
        capture.apply(self.root, plan)
        docs = self.messages()
        self.assertEqual([d['text'] for d in docs], [d['text'] for d in self.batch])
        self.assertIsNone(docs[0]['meta']['original_created_at'])
        self.assertEqual(docs[0]['meta']['original_timestamp_status'], 'unknown')
        self.assertEqual(docs[1]['meta']['original_created_at'], self.batch[1]['original_created_at'])
        self.assertEqual(docs[1]['reply_to'], docs[0]['id'])
        self.assertEqual([d['meta']['original_order'] for d in docs], [1, 2])
        self.assertTrue(all(d['meta']['created_at_basis'] == 'capture_time' for d in docs))
        for doc in docs:
            for recipient in doc['to']:
                pointer = json.loads((self.root / f".macaroni/inbox/{recipient}/{doc['id']}.json").read_text())
                self.assertEqual(json.loads((self.root / pointer['message_path']).read_text()), doc)

    def test_retry_is_noop_even_after_git_commit(self):
        capture.apply(self.root, self.prepare())
        self.committed()
        before = self.snapshot()
        retry = self.prepare()
        self.assertEqual(retry['messages_skipped'], 2)
        self.assertEqual(retry['changes'], [])
        self.assertEqual(capture.apply(self.root, retry), 0)
        self.assertEqual(self.snapshot(), before)

    def test_changed_source_text_blocks_without_writes(self):
        capture.apply(self.root, self.prepare())
        before = self.snapshot()
        changed = copy.deepcopy(self.batch)
        changed[0]['text'] = 'Different requirement.'
        with self.assertRaises(capture.CaptureError):
            self.prepare(changed)
        self.assertEqual(self.snapshot(), before)

    def test_unknown_fields_and_existing_messages_are_preserved(self):
        capture.apply(self.root, self.prepare())
        for name in ['protocol.json', 'users/HUMAN.json', f'chats/{self.chat}/meta.json', f'chats/{self.chat}/members.json']:
            path = '.macaroni/' + name
            doc = json.loads((self.root / path).read_text())
            doc['extension'] = {'nested': [1, {'keep': True}]}
            doc.setdefault('meta', {})['extension'] = {'custom': 'preserve'}
            if 'members' in doc:
                doc['members'][0]['extension'] = 'also preserve'
            self.write(path, doc)
        before = self.snapshot()
        additional = [{'source_message_id': 'fixture-third', 'from': 'HUMAN', 'to': ['CODEX', 'CLAUDE'], 'text': 'Synthetic additional requirement.'}]
        capture.apply(self.root, self.prepare(additional))
        for path, content in before.items():
            actual = (self.root / path).read_bytes()
            if path.endswith('members.json'):
                old, new = json.loads(content), json.loads(actual)
                self.assertTrue(capture.unchanged_fields(old, new))
                self.assertEqual(new['members'][:-1], old['members'])
            else:
                self.assertEqual(actual, content)

    def test_secret_in_last_message_or_metadata_blocks_entire_batch(self):
        for location in ['text', 'meta', 'attachments']:
            with self.subTest(location=location):
                raw = copy.deepcopy(self.batch)
                value = 'ghp_' + 'A' * 32  # Synthetic detection fixture only.
                if location == 'text': raw[-1]['text'] = value
                else: raw[-1][location] = {'value': value} if location == 'meta' else [{'value': value}]
                with self.assertRaises(capture.CaptureError): self.prepare(raw)
                self.assertFalse((self.root / '.macaroni').exists())

    def test_chat_traversal_and_absolute_ids_are_rejected(self):
        for chat in ['../outside', '/tmp/outside', 'chat/child', 'chat\\child', '..']:
            with self.subTest(chat=chat), self.assertRaises(capture.CaptureError):
                capture.prepare(self.root, self.batch, chat)
        self.assertFalse((self.root / '.macaroni').exists())

    def test_symlink_escape_is_rejected_without_writes(self):
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        (self.root / '.macaroni').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(capture.CaptureError): self.prepare()
        self.assertEqual(list(outside.iterdir()), [])

    def test_duplicate_source_in_batch_and_explicit_message_collision(self):
        with self.assertRaises(capture.CaptureError): self.prepare([self.batch[0], self.batch[0]])
        capture.apply(self.root, self.prepare())
        before = self.snapshot()
        collision = [{'source_message_id': 'new-source', 'id': self.messages()[0]['id'], 'from': 'HUMAN', 'text': 'Different message.'}]
        with self.assertRaises(capture.CaptureError): self.prepare(collision)
        self.assertEqual(self.snapshot(), before)

    def test_wrong_branch_repository_and_protocol_block(self):
        with self.assertRaises(capture.CaptureError): self.prepare(repo_url='https://github.com/example/other')
        self.git('switch', '-c', 'main')
        with self.assertRaises(capture.CaptureError): self.prepare()
        self.git('switch', 'macaroni')
        self.write('.macaroni/protocol.json', {'version': 1, 'repository': 'https://github.com/example/other', 'storage_branch': 'macaroni'})
        before = self.snapshot()
        with self.assertRaises(capture.CaptureError): self.prepare()
        self.assertEqual(self.snapshot(), before)

    def test_stale_plan_and_concurrent_file_block(self):
        plan = self.prepare()
        self.git('commit', '--allow-empty', '-m', 'head changed')
        with self.assertRaises(capture.CaptureError): capture.apply(self.root, plan)
        plan = self.prepare()
        first = plan['changes'][0]
        self.write(first['path'], {'version': 1, 'custom': 'another writer'})
        before = self.snapshot()
        with self.assertRaises(capture.CaptureError): capture.apply(self.root, plan)
        self.assertEqual(self.snapshot(), before)

    def test_plan_digest_and_field_loss_guard(self):
        plan = self.prepare()
        plan['changes'][0]['content']['text'] = 'Unreviewed change'
        with self.assertRaises(capture.CaptureError): capture.apply(self.root, plan)
        capture.apply(self.root, self.prepare())
        additional = [{'source_message_id': 'fixture-third', 'from': 'CLAUDE', 'text': 'Synthetic additional context.'}]
        plan = self.prepare(additional)
        change = next(c for c in plan['changes'] if c['path'].endswith('members.json'))
        change['content']['members'] = []
        plan['review_digest'] = capture.plan_digest(plan)
        before = self.snapshot()
        with self.assertRaises(capture.CaptureError): capture.apply(self.root, plan)
        self.assertEqual(self.snapshot(), before)

    def test_write_failure_rolls_back_entire_batch(self):
        plan = self.prepare()
        original = capture.os.link
        calls = 0
        def fail_second(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2: raise OSError('Synthetic disk failure')
            return original(*args, **kwargs)
        with patch.object(capture.os, 'link', side_effect=fail_second):
            with self.assertRaises(OSError): capture.apply(self.root, plan)
        self.assertFalse((self.root / '.macaroni').exists())
        self.assertFalse((self.root / '.git/macaroni-capture.lock').exists())

    def test_lock_blocks_cooperating_writer(self):
        plan = self.prepare()
        lock = self.root / '.git/macaroni-capture.lock'
        lock.write_text('Synthetic held lock')
        with self.assertRaises(capture.CaptureError): capture.apply(self.root, plan)
        self.assertTrue(lock.exists())
        self.assertFalse((self.root / '.macaroni').exists())

    def test_index_is_read_only_and_finds_source_paths(self):
        capture.apply(self.root, self.prepare())
        before = self.snapshot()
        result = capture.index(self.root, 'importer')
        self.assertEqual(len(result['messages']), 2)
        self.assertTrue(all((self.root / row['path']).exists() for row in result['messages']))
        self.assertTrue(all('text' not in row for row in result['messages']))
        self.assertEqual(before, self.snapshot())

    def test_naive_time_missing_id_and_missing_reply_block(self):
        for extra in [{'original_created_at': '2026-10-02T18:00:00'}, {'source_message_id': None}, {'reply_to_source_id': 'missing-source'}]:
            raw = copy.deepcopy(self.batch)
            raw[0].update(extra)
            with self.subTest(extra=extra), self.assertRaises((capture.CaptureError, ValueError)):
                self.prepare(raw)
        self.assertFalse((self.root / '.macaroni').exists())

    def test_nested_unknown_updated_at_cannot_be_changed(self):
        capture.apply(self.root, self.prepare())
        member_path = f'.macaroni/chats/{self.chat}/members.json'
        doc = json.loads((self.root / member_path).read_text())
        doc['extension'] = {'updated_at': 'preserve exactly'}
        self.write(member_path, doc)
        plan = self.prepare([{'source_message_id': 'new-member', 'from': 'CLAUDE', 'text': 'Synthetic message.'}])
        change = next(c for c in plan['changes'] if c['path'] == member_path)
        change['content']['extension']['updated_at'] = 'altered'
        plan['review_digest'] = capture.plan_digest(plan)
        before = self.snapshot()
        with self.assertRaises(capture.CaptureError): capture.apply(self.root, plan)
        self.assertEqual(before, self.snapshot())

    def test_legacy_message_can_be_reply_target_without_rewriting(self):
        capture.apply(self.root, self.prepare())
        path = next((self.root / '.macaroni/chats').glob('*/messages/**/*.json'))
        doc = json.loads(path.read_text())
        del doc['meta']['source_message_id']
        path.write_bytes(capture.encoded(doc))
        before = path.read_bytes()
        plan = self.prepare([{'source_message_id': 'new-reply', 'from': 'HUMAN', 'text': 'Synthetic follow-up.', 'reply_to': doc['id']}])
        capture.apply(self.root, plan)
        self.assertEqual(before, path.read_bytes())

    def test_rollback_restores_existing_metadata(self):
        capture.apply(self.root, self.prepare())
        plan = self.prepare([{'source_message_id': 'new-member', 'from': 'CLAUDE', 'text': 'Synthetic message.'}])
        # Put the permitted existing metadata update before an injected new-file failure.
        plan['changes'].sort(key=lambda c: c['before_sha256'] is None)
        plan['review_digest'] = capture.plan_digest(plan)
        before = self.snapshot()
        with patch.object(capture.os, 'link', side_effect=OSError('Synthetic failure')):
            with self.assertRaises(OSError): capture.apply(self.root, plan)
        self.assertEqual(before, self.snapshot())

    def test_duplicate_json_fields_block(self):
        with self.assertRaises(capture.CaptureError):
            capture.strict_json('{"version":1,"version":1}')
        for number in ['NaN', 'Infinity', '-Infinity']:
            with self.subTest(number=number), self.assertRaises(capture.CaptureError):
                capture.strict_json('{"value":' + number + '}')

    def test_apply_revalidates_setup_membership_and_provenance(self):
        for fault in ['missing-user', 'empty-members', 'wrong-order']:
            with self.subTest(fault=fault):
                plan = self.prepare()
                if fault == 'missing-user':
                    plan['changes'] = [c for c in plan['changes'] if c['path'] != '.macaroni/users/HUMAN.json']
                elif fault == 'empty-members':
                    next(c for c in plan['changes'] if c['path'].endswith('members.json'))['content']['members'] = []
                else:
                    plan['changes'][0]['content']['meta']['original_order'] = 0
                plan['review_digest'] = capture.plan_digest(plan)
                with self.assertRaises(capture.CaptureError): capture.apply(self.root, plan)
                self.assertFalse((self.root / '.macaroni').exists())

    def test_cli_private_plan_rejects_overwrite_and_applies_once(self):
        batch = Path(self.temp.name) / 'batch.json'
        batch.write_bytes(capture.encoded(self.batch))
        plan_path = Path(self.temp.name) / 'plan.json'
        script = Path(__file__).parents[1] / 'scripts/write_messages.py'
        command = [sys.executable, '-B', str(script), '--repo-root', str(self.root)]
        prep = command + ['--batch-json', str(batch), '--chat-id', self.chat, '--prepare', str(plan_path)]
        result = subprocess.run(prep, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)['memory_written'])
        self.assertEqual(plan_path.stat().st_mode & 0o777, 0o600)
        self.assertFalse((self.root / '.macaroni').exists())
        original = plan_path.read_bytes()
        self.assertNotEqual(subprocess.run(prep, capture_output=True).returncode, 0)
        self.assertEqual(original, plan_path.read_bytes())
        apply_result = subprocess.run(command + ['--apply-plan', str(plan_path)], capture_output=True, text=True)
        self.assertEqual(apply_result.returncode, 0, apply_result.stderr)
        before = self.snapshot()
        self.assertNotEqual(subprocess.run(command + ['--apply-plan', str(plan_path)], capture_output=True).returncode, 0)
        self.assertEqual(before, self.snapshot())

    def test_inbox_collision_never_overwrites_pointer(self):
        capture.apply(self.root, self.prepare())
        path = next((self.root / '.macaroni/inbox').glob('*/*.json'))
        pointer = json.loads(path.read_text())
        pointer['chat_id'] = 'chat_other'
        path.write_bytes(capture.encoded(pointer))
        before = self.snapshot()
        with self.assertRaises(capture.CaptureError): self.prepare()
        self.assertEqual(before, self.snapshot())

    def test_single_message_cli_has_correct_human_defaults(self):
        path = Path(self.temp.name) / 'single-plan.json'
        script = Path(__file__).parents[1] / 'scripts/write_messages.py'
        result = subprocess.run([sys.executable, '-B', str(script), '--repo-root', str(self.root), '--from-id', 'HUMAN', '--source-message-id', 'single-user-message', '--text', 'Synthetic requirement.', '--prepare', str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        doc = next(c['content'] for c in json.loads(path.read_text())['changes'] if '/messages/' in c['path'])
        self.assertEqual(doc['from_name'], 'Human')
        self.assertEqual(doc['to'], ['CODEX'])
        self.assertEqual(doc['meta']['source'], 'user_message')


if __name__ == '__main__':
    unittest.main()
