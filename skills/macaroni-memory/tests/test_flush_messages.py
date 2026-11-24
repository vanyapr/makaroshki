"""Isolated synthetic exports; no runtime history or host configuration."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import flush_messages as flush
import regular_capture as regular
import write_messages as memory


class FlushTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='macaroni-flush-synthetic-')
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / 'project'
        self.root.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        subprocess.run(['git', '-C', str(self.root), 'remote', 'add', 'origin', 'https://github.com/fixture/flush-test'], check=True)
        self.store, self.config = self.base / 'private-store', self.base / 'capture.json'
        regular.register(self.config, self.root, 'https://github.com/fixture/flush-test', self.store)

    def tearDown(self):
        self.temp.cleanup()

    def batch(self):
        return {'version': 1, 'capture': {'source_system': 'synthetic_export', 'source_conversation_id': 'synthetic-thread', 'source_id_origin': 'provider', 'order_basis': 'available_fragment'}, 'messages': [
            {'source_message_id': 'fixture-user-1', 'from': 'HUMAN', 'source_channel': 'user', 'original_order': 1, 'text': 'Status?'},
            {'source_message_id': 'fixture-progress-1', 'from': 'CODEX', 'source_channel': 'assistant_commentary', 'original_order': 2, 'text': 'Checking.'},
            {'source_message_id': 'fixture-final-1', 'from': 'CODEX', 'source_channel': 'assistant_final', 'original_order': 3, 'text': 'Done.'}]}

    def test_all_supplied_user_progress_and_final_saved_and_reloaded(self):
        result = flush.flush(self.config, self.root, self.batch())
        self.assertEqual((result['expected_count'], result['saved_count'], result['user_count'], result['assistant_count']), (3, 3, 1, 2))
        self.assertTrue(result['fresh_process_verified'])
        self.assertEqual(result['missing_ids'], [])
        self.assertEqual(result['upstream_history_completeness'], 'not_established')
        self.assertEqual(result['source_message_ids'], ['fixture-final-1', 'fixture-progress-1', 'fixture-user-1'])

    def test_replay_changes_zero_files(self):
        flush.flush(self.config, self.root, self.batch())
        before = {str(p.relative_to(self.store)): p.read_bytes() for p in self.store.rglob('*') if p.is_file()}
        result = flush.flush(self.config, self.root, self.batch())
        self.assertEqual((result['messages_new'], result['messages_skipped'], result['files_written']), (0, 3, 0))
        self.assertEqual(before, {str(p.relative_to(self.store)): p.read_bytes() for p in self.store.rglob('*') if p.is_file()})

    def test_secret_values_redact_before_persistence(self):
        raw = self.batch()
        value = 'ghp_' + 'a' * 32
        raw['messages'][0]['text'] = 'token="' + value + '"'
        result = flush.flush(self.config, self.root, raw)
        self.assertTrue(result['all_supplied_messages_saved'])
        data = b''.join(p.read_bytes() for p in self.store.rglob('*') if p.is_file())
        self.assertNotIn(value.encode(), data)
        known, _ = memory.existing_messages(self.store)
        self.assertTrue(known['fixture-user-1'][1]['meta']['redacted'])
        self.assertTrue(all(r['replacement'] in memory.MARKERS for r in known['fixture-user-1'][1]['meta']['redactions']))

    def test_last_unsafe_credential_prevents_whole_batch_store_creation(self):
        raw = self.batch()
        raw['messages'][-1]['text'] = 'password: !!str |\n  SYNTHETIC_SECRET'
        with self.assertRaises(memory.CaptureError):
            flush.flush(self.config, self.root, raw)
        self.assertFalse(self.store.exists())

    def test_tool_system_internal_rows_and_fields_are_rejected(self):
        for fault in ['tool', 'analysis', 'hidden_field', 'role']:
            raw = self.batch()
            if fault in ['tool', 'analysis']:
                raw['messages'][1]['source_channel'] = fault
            elif fault == 'hidden_field':
                raw['messages'][1]['tool_output'] = 'SYNTHETIC_TOOL_SECRET'
            else:
                raw['messages'][1]['from'] = 'TOOL'
            with self.subTest(fault=fault), self.assertRaises(memory.CaptureError):
                flush.flush(self.config, self.root, raw)
            self.assertFalse(self.store.exists())

    def test_new_process_detects_missing_or_changed_messages(self):
        flush.flush(self.config, self.root, self.batch())
        known, _ = memory.existing_messages(self.store)
        expected = {'repository': 'https://github.com/fixture/flush-test', 'messages': [{'source_message_id': source, 'message_path': rel, 'sha256': memory.digest((self.store / rel).read_bytes())} for source, (rel, _) in known.items()]}
        path = self.store / known['fixture-final-1'][0]
        doc = memory.load(path)
        doc['text'] = 'Altered by a synthetic external writer.'
        path.write_bytes(memory.encoded(doc))
        proc = subprocess.run([sys.executable, str(SCRIPTS / 'flush_messages.py'), '--verify-store', str(self.store)], input=json.dumps(expected), text=True, capture_output=True)
        self.assertEqual(proc.returncode, 1)
        report = json.loads(proc.stdout)
        self.assertFalse(report['all_supplied_messages_saved'])
        self.assertEqual(report['mismatched_ids'], ['fixture-final-1'])
        path.unlink()
        report = flush.verify(self.store, expected)
        self.assertEqual(report['missing_ids'], ['fixture-final-1'])

    def test_nested_hidden_metadata_and_attachment_fields_block_before_writes(self):
        for location in ('metadata', 'attachment'):
            raw = self.batch()
            hidden = {'nested': [{'reasoning': 'SYNTHETIC_INTERNAL', 'tool_output': 'SYNTHETIC_TOOL'}]}
            if location == 'metadata':
                raw['messages'][0]['meta'] = hidden
            else:
                raw['messages'][0]['attachments'] = [hidden]
            with self.subTest(location=location), self.assertRaises(memory.CaptureError):
                flush.flush(self.config, self.root, raw)
            self.assertFalse(self.store.exists())

    def test_fresh_process_detects_deleted_planned_inbox_pointer(self):
        apply = memory.apply
        def external_delete(root, plan):
            written = apply(root, plan)
            pointer = next(c['path'] for c in plan['changes'] if '/inbox/' in c['path'])
            (root / pointer).unlink()
            return written
        with patch.object(memory, 'apply', external_delete), self.assertRaises(memory.CaptureError):
            flush.flush(self.config, self.root, self.batch())

    def test_changed_source_text_is_not_overwritten(self):
        flush.flush(self.config, self.root, self.batch())
        raw = self.batch()
        raw['messages'][0]['text'] = 'Changed source.'
        with self.assertRaises(memory.CaptureError):
            flush.flush(self.config, self.root, raw)
        known, _ = memory.existing_messages(self.store)
        self.assertEqual(known['fixture-user-1'][1]['text'], 'Status?')

    def test_cli_end_to_end_uses_stdin_and_new_process(self):
        proc = subprocess.run([sys.executable, str(SCRIPTS / 'flush_messages.py'), '--config', str(self.config), '--project-root', str(self.root)], input=json.dumps(self.batch()), text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertTrue(result['all_supplied_messages_saved'] and result['fresh_process_verified'])


if __name__ == '__main__':
    unittest.main()
