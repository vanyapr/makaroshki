"""Synthetic only: no live messages, hooks, histories or host settings."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0, str(SCRIPTS))
import agent_capture as agent
import flush_messages as flush
import regular_capture as regular
import write_messages as memory


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='macaroni-agent-synthetic-')
        self.base = Path(self.temp.name).resolve()
        self.root = self.base/'project'
        self.root.mkdir()
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        self.repository = 'https://github.com/fixture/agent-capture'
        subprocess.run(['git','-C',str(self.root),'remote','add','origin',self.repository],check=True)
        self.store,self.config = self.base/'private-store',self.base/'capture.json'
        regular.register(self.config,self.root,self.repository,self.store)

    def tearDown(self):
        self.temp.cleanup()

    def batch(self, role='user', body='SYNTHETIC_USER', source='fixture-user', order=1):
        return {'version':1,'capture':{'source_system':'synthetic_fixture','source_conversation_id':'fixture-thread','source_id_origin':'provider','order_basis':'available_fragment'},'messages':[{'source_message_id':source,'from':'HUMAN' if role=='user' else 'AGENT','source_channel':role,'original_order':order,'original_created_at':None,'text':body}]}

    def reply(self, body='SYNTHETIC_REPLY'):
        return {'version':1,'source_system':'synthetic_fixture','source_conversation_id':'fixture-thread','reply_id':'assigned_reply_fixture_1','source_channel':'assistant_final','reply_to_source_message_id':'fixture-user','text':body}

    def capture_user(self):
        flush.flush(self.config,self.root,self.batch())

    def test_cli_observed_pair_has_ids_text_hashes_and_fresh_reload(self):
        batch=self.batch()
        batch['messages']+=self.batch('assistant_final','SYNTHETIC_REPLY','fixture-assistant',2)['messages']
        cmd=[sys.executable,str(SCRIPTS/'agent_capture.py'),'--config',str(self.config),'--project-root',str(self.root),'--messages']
        run=subprocess.run(cmd,input=json.dumps(batch),text=True,capture_output=True)
        self.assertEqual(run.returncode,0,run.stderr)
        result=json.loads(run.stdout)
        self.assertTrue(result['fresh_process_verified'])
        self.assertEqual((result['user_count'],result['assistant_count']),(1,1))
        self.assertEqual({r['source_message_id']:r['text_sha256'] for r in result['verified_messages']},{'fixture-user':memory.digest(b'SYNTHETIC_USER'),'fixture-assistant':memory.digest(b'SYNTHETIC_REPLY')})

    def test_prepared_reply_is_private_durable_and_not_observed_history(self):
        self.capture_user()
        prepared=agent.prepare_reply(self.config,self.root,self.reply())
        self.assertTrue(prepared['fresh_process_verified'])
        self.assertEqual(prepared['reply_text_to_emit'],'SYNTHETIC_REPLY')
        state=agent.status(self.config,self.root)
        self.assertEqual(state['observed_messages'],1)
        self.assertEqual(len(state['prepared_unconfirmed_replies']),1)
        self.assertEqual(Path(prepared['reply_path']).stat().st_mode&0o077,0)
        before=Path(prepared['reply_path']).read_bytes()
        again=agent.prepare_reply(self.config,self.root,self.reply())
        self.assertFalse(again['created'])
        self.assertEqual(Path(prepared['reply_path']).read_bytes(),before)

    def test_confirmation_preserves_preparation_and_links_real_observed_id(self):
        self.capture_user()
        prepared=agent.prepare_reply(self.config,self.root,self.reply())
        before=Path(prepared['reply_path']).read_bytes()
        actual=self.batch('assistant_final','SYNTHETIC_REPLY','fixture-assistant',2)
        result=agent.confirm_reply(self.config,self.root,actual,'assigned_reply_fixture_1')
        self.assertEqual(result['delivery_state'],'observed')
        state=agent.status(self.config,self.root)
        self.assertEqual((state['observed_messages'],state['prepared_unconfirmed_replies']),(2,[]))
        self.assertEqual(Path(prepared['reply_path']).read_bytes(),before)
        receipt=memory.load(Path(result['receipt_path']))
        self.assertEqual(receipt['source_message_id'],'fixture-assistant')
        again=agent.confirm_reply(self.config,self.root,actual,'assigned_reply_fixture_1')
        self.assertEqual(again['files_written'],0)

    def test_changed_reply_or_conversation_blocks_before_history_capture(self):
        self.capture_user()
        agent.prepare_reply(self.config,self.root,self.reply())
        for fault in ('body','conversation','channel'):
            raw=self.batch('assistant_final','SYNTHETIC_REPLY','fixture-assistant',2)
            if fault=='body':raw['messages'][0]['text']='DIFFERENT_SYNTHETIC_REPLY'
            elif fault=='conversation':raw['capture']['source_conversation_id']='foreign-thread'
            else:raw['messages'][0]['source_channel']='assistant_commentary'
            with self.subTest(fault=fault),self.assertRaises(memory.CaptureError):
                agent.confirm_reply(self.config,self.root,raw,'assigned_reply_fixture_1')
            self.assertEqual(len(memory.existing_messages(self.store)[0]),1)

    def test_another_observed_id_cannot_replace_existing_receipt(self):
        self.capture_user()
        agent.prepare_reply(self.config,self.root,self.reply())
        agent.confirm_reply(self.config,self.root,self.batch('assistant_final','SYNTHETIC_REPLY','fixture-assistant',2),'assigned_reply_fixture_1')
        with self.assertRaises(memory.CaptureError):
            agent.confirm_reply(self.config,self.root,self.batch('assistant_final','SYNTHETIC_REPLY','other-assistant',3),'assigned_reply_fixture_1')
        self.assertEqual(len(memory.existing_messages(self.store)[0]),2)

    def test_busy_confirmation_lock_does_not_capture_observed_reply(self):
        self.capture_user()
        agent.prepare_reply(self.config,self.root,self.reply())
        lock=self.store/'.macaroni/.prepared-confirm-assigned_reply_fixture_1.lock'
        lock.write_text('synthetic lock')
        with self.assertRaises(FileExistsError):
            agent.confirm_reply(self.config,self.root,self.batch('assistant_final','SYNTHETIC_REPLY','fixture-assistant',2),'assigned_reply_fixture_1')
        self.assertTrue(lock.exists())
        self.assertEqual(len(memory.existing_messages(self.store)[0]),1)

    def test_secret_redacts_before_preparation_and_emission(self):
        self.capture_user()
        secret='ghp_'+'a'*32
        prepared=agent.prepare_reply(self.config,self.root,self.reply('token="'+secret+'"'))
        self.assertNotIn(secret,prepared['reply_text_to_emit'])
        self.assertNotIn(secret.encode(),Path(prepared['reply_path']).read_bytes())

    def test_missing_user_source_cannot_be_fabricated(self):
        with self.assertRaises(memory.CaptureError):
            agent.prepare_reply(self.config,self.root,self.reply())
        self.assertEqual(len(memory.existing_messages(self.store)[0]),0)

    def test_reply_to_requires_the_same_source_system(self):
        self.capture_user()
        raw=self.reply()
        raw['source_system']='foreign_fixture'
        with self.assertRaises(memory.CaptureError):
            agent.prepare_reply(self.config,self.root,raw)
        self.assertEqual(len(memory.existing_messages(self.store)[0]),1)
        self.assertFalse((self.store/'.macaroni/prepared').exists())

    def test_nested_internal_fields_and_path_traversal_block(self):
        for fault in ('hidden','path'):
            raw=self.reply()
            raw.pop('reply_to_source_message_id')
            if fault=='hidden':raw['meta']={'nested':{'tool_output':'SYNTHETIC_TOOL'}}
            else:raw['reply_id']='assigned_reply_../../escape'
            with self.subTest(fault=fault),self.assertRaises(memory.CaptureError):
                agent.prepare_reply(self.config,self.root,raw)
            self.assertFalse(self.store.exists())

    def reference(self):
        return {'version':1,'source_system':'synthetic_fixture','source_conversation_id':'fixture-thread','source_message_id':'fixture-source','source_uri':'https://example.test/fixture','candidate_repositories':[self.repository]}

    def test_ambiguous_reference_has_no_body_and_preserves_unknown_registry(self):
        doc=json.loads(self.config.read_text())
        doc['future']={'nested':[{'keep':True}]}
        self.config.write_bytes(memory.encoded(doc))
        result=agent.reference_source(self.config,self.reference())
        self.assertEqual(result['messages_written'],0)
        after=json.loads(self.config.read_text())
        self.assertEqual(after['projects'],doc['projects'])
        self.assertEqual(after['future'],doc['future'])
        self.assertNotIn('text',after['unresolved_sources'][0])
        again=agent.reference_source(self.config,self.reference())
        self.assertFalse(again['created'])
        self.assertEqual(len(json.loads(self.config.read_text())['unresolved_sources']),1)

    def test_reference_body_hidden_data_and_credential_uri_rejected(self):
        for fault in ('text','nested','uri','query','bad_type'):
            raw=self.reference()
            if fault=='text':raw['text']='SYNTHETIC_BODY'
            elif fault=='nested':raw['meta']={'reasoning':'SYNTHETIC_INTERNAL'}
            elif fault=='uri':raw['source_uri']='https://synthetic:credential@example.test/path'
            elif fault=='query':raw['source_uri']='https://example.test/path?token=synthetic'
            else:raw['source_uri']=[]
            before=self.config.read_bytes()
            with self.subTest(fault=fault),self.assertRaises(memory.CaptureError):
                agent.reference_source(self.config,raw)
            self.assertEqual(self.config.read_bytes(),before)

    def test_reference_respects_same_lock_as_registration(self):
        lock=self.config.with_name(self.config.name+'.lock')
        lock.write_text('synthetic lock')
        before=self.config.read_bytes()
        with self.assertRaises(FileExistsError):
            agent.reference_source(self.config,self.reference())
        self.assertEqual(self.config.read_bytes(),before)
        self.assertTrue(lock.exists())


if __name__=='__main__':
    unittest.main()
