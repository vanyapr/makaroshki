"""Synthetic hook events only. No production chat, host config or history paths."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import regular_capture as regular
import write_messages as memory


class RegularCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='macaroni-hooks-synthetic-')
        self.base = Path(self.temp.name).resolve()
        self.project = self.base / 'project'
        self.project.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.project)], check=True)
        subprocess.run(['git', '-C', str(self.project), 'remote', 'add', 'origin', 'https://github.com/fixture/hooks-test.git'], check=True)
        self.store = self.base / 'private-memory'
        self.config = self.base / 'capture.json'
        regular.register(self.config, self.project, 'https://github.com/fixture/hooks-test', self.store)

    def tearDown(self):
        self.temp.cleanup()

    def event(self, name='UserPromptSubmit', turn='synthetic-turn-1', text='OK'):
        return {'hook_event_name': name, 'cwd': str(self.project), 'session_id': 'synthetic-thread', 'turn_id': turn, 'prompt' if name == 'UserPromptSubmit' else 'last_assistant_message': text}

    def messages(self):
        return [doc for _, doc in memory.existing_messages(self.store)[0].values()]

    def snapshot(self):
        return {p.relative_to(self.store).as_posix(): p.read_bytes() for p in self.store.rglob('*') if p.is_file()}

    def test_events_capture_exact_text_without_inventory_or_gap_gate(self):
        self.assertEqual(regular.capture_event(self.config, self.event(text='Status?'))['messages_new'], 1)
        regular.capture_event(self.config, self.event('Stop', text='Done.'))
        docs = self.messages()
        self.assertEqual({d['text'] for d in docs}, {'Status?', 'Done.'})
        self.assertEqual({d['meta']['original_order'] for d in docs}, {1, 2})
        self.assertEqual({d['meta']['source_channel'] for d in docs}, {'user', 'assistant_final'})
        self.assertTrue(all(d['meta']['source_id_origin'] == 'assigned_local' and not d['meta']['completeness_audited'] and d['meta']['original_created_at'] is None for d in docs))
        self.assertFalse((self.store / '.git').exists())
        self.assertEqual(memory.load(self.store / '.macaroni/protocol.json')['storage_branch'], 'local')

    def test_replay_writes_zero_and_preserves_unknown_fields(self):
        event = self.event()
        regular.capture_event(self.config, event)
        path = self.store / '.macaroni/users/HUMAN.json'
        doc = memory.load(path)
        doc['fixture_extension'] = {'keep': True}
        path.write_bytes(memory.encoded(doc))
        before = self.snapshot()
        result = regular.capture_event(self.config, event)
        self.assertEqual(result, {'messages_new': 0, 'messages_skipped': 1, 'files_written': 0})
        self.assertEqual(before, self.snapshot())

    def test_repeated_text_in_distinct_turns_is_not_collapsed(self):
        for turn in ['synthetic-turn-1', 'synthetic-turn-2']:
            regular.capture_event(self.config, self.event(turn=turn))
        self.assertEqual(len(self.messages()), 2)
        self.assertEqual(len({d['meta']['source_message_id'] for d in self.messages()}), 2)

    def test_different_prompts_in_one_turn_have_distinct_assigned_ids(self):
        for text in ['First prompt.', 'Steering prompt.']:
            regular.capture_event(self.config, self.event(text=text))
        self.assertEqual(len(self.messages()), 2)

    def test_transcript_and_hidden_tool_fields_are_never_read_or_saved(self):
        event = self.event()
        event.update({'transcript_path': '/never-read-this-synthetic-path', 'agent_transcript_path': '/another-forbidden-fixture', 'reasoning': 'PRIVATE_REASONING_FIXTURE', 'system': 'HIDDEN_SYSTEM_FIXTURE', 'tool_output': 'SECRET_TOOL_FIXTURE'})
        original = Path.read_text
        def read(path, *args, **kwargs):
            self.assertNotIn('never-read', str(path))
            self.assertNotIn('forbidden-fixture', str(path))
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', read):
            regular.capture_event(self.config, event)
        data = b''.join(self.snapshot().values())
        for value in ['PRIVATE_REASONING_FIXTURE', 'HIDDEN_SYSTEM_FIXTURE', 'SECRET_TOOL_FIXTURE', 'never-read-this']:
            self.assertNotIn(value.encode(), data)

    def test_unregistered_and_nested_projects_never_write(self):
        other = self.base / 'other'
        other.mkdir()
        event = self.event()
        event['cwd'] = str(other)
        self.assertEqual(regular.capture_event(self.config, event)['skipped'], 'unregistered_project')
        nested = self.project / 'nested'
        subprocess.run(['git', 'init', '-q', str(nested)], check=True)
        event['cwd'] = str(nested)
        self.assertEqual(regular.capture_event(self.config, event)['skipped'], 'unregistered_project')
        self.assertFalse(self.store.exists())

    def test_registered_subdirectory_uses_its_project_store(self):
        child = self.project / 'src'
        child.mkdir()
        event = self.event()
        event['cwd'] = str(child)
        self.assertEqual(regular.capture_event(self.config, event)['messages_new'], 1)

    def test_subagents_other_events_and_delegation_are_excluded(self):
        events = [self.event('PreToolUse'), {**self.event('Stop'), 'agent_id': 'internal-agent'}, self.event(text='<codex_delegation>internal task</codex_delegation>')]
        for event in events:
            self.assertIn('skipped', regular.capture_event(self.config, event))
        self.assertFalse(self.store.exists())

    def test_redactions_remove_complete_credentials_before_disk_write(self):
        token = 'ghp_' + 'a' * 32
        label = "PRIVATE KEY"
        key = f"-----BEGIN {label}-----\nSYNTHETIC-KEY-CONTENT\n-----END {label}-----"
        text = 'Keep this. password="synthetic password with spaces"\nBearer ' + token + ' contact fixture@example.invalid\n' + key
        regular.capture_event(self.config, self.event(text=text))
        data = b''.join(self.snapshot().values())
        for value in [token, 'synthetic password with spaces', 'SYNTHETIC-KEY-CONTENT', 'fixture@example.invalid']:
            self.assertNotIn(value.encode(), data)
        doc = self.messages()[0]
        self.assertTrue(doc['meta']['redacted'])
        self.assertEqual({r['replacement'] for r in doc['meta']['redactions']}, {'REDACTED', 'ТОКЕН', 'PRIVATE_KEY', 'EMAIL'})
        self.assertIn('Keep this.', doc['text'])

    def test_unquoted_credential_redacts_the_whole_remaining_line(self):
        text, _ = regular.redact('Keep this. password=synthetic password with spaces\nKeep that.')
        self.assertEqual(text, 'Keep this. password=REDACTED\nKeep that.')

    def test_escaped_multiline_quotes_and_pgp_blocks_leave_no_fragments(self):
        for value in ['password="first\\"SYNTHETIC_SUFFIX"', 'password="first\nSYNTHETIC_SUFFIX"', '-----BEGIN PGP PRIVATE KEY BLOCK-----\nSYNTHETIC_SUFFIX\n-----END PGP PRIVATE KEY BLOCK-----']:
            with self.subTest(value=value):
                text, records = regular.redact(value)
                self.assertNotIn('SYNTHETIC_SUFFIX', text)
                self.assertTrue(records)
        with self.assertRaises(memory.CaptureError):
            regular.redact('password="REDACTED\nSYNTHETIC_SUFFIX')

    def test_yaml_block_scalars_block_before_writes_and_json_keys_redact(self):
        for text in ['password: |\n  SYNTHETIC_FIRST\n  SYNTHETIC_SECOND', 'secret: >\n  SYNTHETIC_FIRST\n  SYNTHETIC_SECOND']:
            with self.subTest(text=text), self.assertRaises(memory.CaptureError):
                regular.capture_event(self.config, self.event(text=text))
            self.assertFalse(self.store.exists())
        text, records = regular.redact('{"password": "SYNTHETIC_JSON_VALUE"}')
        self.assertNotIn('SYNTHETIC_JSON_VALUE', text)
        self.assertTrue(records)

    def test_basic_authorization_and_env_credential_names_redact(self):
        for text in ['Authorization: Basic SYNTHETIC_BASIC_VALUE', 'AWS_SECRET_ACCESS_KEY=SYNTHETIC_ACCESS_VALUE', 'OPENAI_API_KEY=SYNTHETIC_API_VALUE', 'MY_ACCESS_TOKEN=SYNTHETIC_TOKEN_VALUE']:
            value, records = regular.redact(text)
            self.assertNotIn('SYNTHETIC_', value)
            self.assertTrue(records)

    def test_tagged_anchored_plain_yaml_and_shell_continuations_block_before_writes(self):
        for text in ['password: !!str |\n  SYNTHETIC_TAGGED', 'password: &credential |\n  SYNTHETIC_ANCHORED', 'password=FIRST\\\nSYNTHETIC_SECOND', 'password: FIRST\n  SYNTHETIC_SECOND', 'password: FIRST\n\n  SYNTHETIC_SECOND']:
            with self.subTest(text=text), self.assertRaises(memory.CaptureError):
                regular.capture_event(self.config, self.event(text=text))
            self.assertFalse(self.store.exists())

    def test_incomplete_key_blocks_before_creating_any_store_file(self):
        with self.assertRaises(memory.CaptureError):
            regular.capture_event(self.config, self.event(text='-----BEGIN PRIVATE KEY-----\nSYNTHETIC-KEY-CONTENT'))
        self.assertFalse(self.store.exists())

    def test_private_store_modes_and_no_git_destination(self):
        regular.capture_event(self.config, self.event())
        self.assertEqual(self.store.stat().st_mode & 0o777, 0o700)
        for path in self.store.rglob('*'):
            self.assertEqual(path.stat().st_mode & 0o777, 0o700 if path.is_dir() else 0o600)
        with self.assertRaises(memory.CaptureError):
            regular.register(self.config, self.project, 'https://github.com/fixture/hooks-test', self.project / 'memory')

    def test_origin_change_blocks_capture(self):
        subprocess.run(['git', '-C', str(self.project), 'remote', 'set-url', 'origin', 'https://github.com/fixture/different-project'], check=True)
        with self.assertRaises(memory.CaptureError):
            regular.capture_event(self.config, self.event())
        self.assertFalse(self.store.exists())

    def test_symlinks_and_permissive_config_are_rejected(self):
        alias = self.base / 'alias'
        alias.symlink_to(self.project, target_is_directory=True)
        with self.assertRaises(memory.CaptureError):
            regular.register(self.config, alias, 'https://github.com/fixture/hooks-test', self.base / 'new-store')
        self.config.chmod(0o644)
        with self.assertRaises(memory.CaptureError):
            regular.capture_event(self.config, self.event())
        self.assertFalse(self.store.exists())

    def test_store_lock_failure_preserves_messages(self):
        regular.capture_event(self.config, self.event())
        lock = self.store / '.hook.lock'
        lock.write_text('synthetic-lock')
        before = self.snapshot()
        with self.assertRaises(FileExistsError):
            regular.capture_event(self.config, self.event(turn='next-turn'))
        self.assertEqual(before, self.snapshot())

    def test_unknown_config_fields_survive_registration_and_destination_conflicts_block(self):
        doc = memory.strict_json(self.config.read_text())
        doc['fixture_extension'] = {'keep': True}
        self.config.write_bytes(memory.encoded(doc))
        regular.register(self.config, self.project, 'https://github.com/fixture/hooks-test', self.store)
        self.assertEqual(memory.strict_json(self.config.read_text())['fixture_extension'], {'keep': True})
        with self.assertRaises(memory.CaptureError):
            regular.register(self.config, self.project, 'https://github.com/fixture/hooks-test', self.base / 'different')

    def test_registration_lock_preserves_existing_allowlist(self):
        before = self.config.read_bytes()
        lock = self.config.with_name(self.config.name + '.lock')
        lock.write_text('synthetic lock')
        with self.assertRaises(FileExistsError):
            regular.register(self.config, self.project, 'https://github.com/fixture/hooks-test', self.store)
        self.assertEqual(before, self.config.read_bytes())

    def test_same_project_checkouts_share_store_but_another_repository_cannot(self):
        other = self.base / 'second-checkout'
        subprocess.run(['git', 'init', '-q', str(other)], check=True)
        subprocess.run(['git', '-C', str(other), 'remote', 'add', 'origin', 'https://github.com/fixture/hooks-test'], check=True)
        regular.register(self.config, other, 'https://github.com/fixture/hooks-test', self.store)
        self.assertEqual(len(regular.configuration(self.config)['projects']), 2)
        regular.capture_event(self.config, self.event())
        event = self.event(turn='synthetic-turn-2')
        event['cwd'] = str(other)
        regular.capture_event(self.config, event)
        self.assertEqual(len(self.messages()), 2)
        third = self.base / 'foreign-project'
        subprocess.run(['git', 'init', '-q', str(third)], check=True)
        subprocess.run(['git', '-C', str(third), 'remote', 'add', 'origin', 'https://github.com/fixture/foreign-project'], check=True)
        with self.assertRaises(memory.CaptureError):
            regular.register(self.config, third, 'https://github.com/fixture/foreign-project', self.store)

    def test_hook_template_is_only_two_events_and_does_not_change_notify(self):
        template = regular.hooks_template(self.config)
        self.assertEqual(set(template['hooks']), {'UserPromptSubmit', 'Stop'})
        data = json.dumps(template)
        self.assertNotIn('notify', data)
        self.assertNotIn('transcript', data.replace('no transcript reads', ''))
        self.assertNotIn('bypass', data)

    def test_cli_failure_continues_without_payload_or_exception_leak(self):
        secret = 'SYNTHETIC-PRIVATE-CONTENT'
        event = self.event(text='-----BEGIN PRIVATE KEY-----\n' + secret)
        proc = subprocess.run([sys.executable, str(SCRIPTS / 'regular_capture.py'), '--config', str(self.config)], input=json.dumps(event), text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(json.loads(proc.stdout)['continue'])
        self.assertNotIn(secret, proc.stdout + proc.stderr)
        self.assertFalse(self.store.exists())


if __name__ == '__main__':
    unittest.main()
