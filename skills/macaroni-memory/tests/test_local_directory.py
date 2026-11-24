"""Synthetic local directory identities; no live projects, origins or messages."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import uuid

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
import regular_capture as regular
import write_messages as memory
import flush_messages as flush
import agent_capture as agent


class LocalDirectoryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='macaroni-local-synthetic-')
        self.base=Path(self.temp.name).resolve()
        self.root=self.base/'project';self.root.mkdir()
        self.store=self.base/'private-memory';self.config=self.base/'capture.json'

    def tearDown(self):
        self.temp.cleanup()

    def register(self,root=None,store=None,project_id=None):
        return regular.register_local(self.config,root or self.root,store or self.store,project_id)

    def batch(self,assistant=False):
        messages=[{'source_message_id':'fixture-user','from':'HUMAN','source_channel':'user','original_order':1,'original_created_at':None,'text':'SYNTHETIC_USER'}]
        if assistant:messages.append({'source_message_id':'fixture-assistant','from':'CODEX','source_channel':'assistant_final','original_order':2,'original_created_at':None,'text':'SYNTHETIC_REPLY'})
        return {'version':1,'capture':{'source_system':'synthetic_fixture','source_conversation_id':'fixture-thread','source_id_origin':'provider','order_basis':'available_fragment'},'messages':messages}

    def snapshot(self):
        return {p.relative_to(self.store).as_posix():p.read_bytes() for p in self.store.rglob('*') if p.is_file()}

    def test_registration_without_git_persists_uuid_and_unknown_fields(self):
        entry=self.register()
        self.assertEqual(entry['binding_kind'],'local_directory')
        self.assertIsNone(entry['repository'])
        self.assertEqual(entry['export_policy'],'local_only')
        self.assertEqual(str(uuid.UUID(entry['project_id'])),entry['project_id'])
        config=json.loads(self.config.read_text());config['future']={'keep':[1,2]};config['projects'][0]['future']={'keep':True}
        self.config.write_bytes(memory.encoded(config));before=self.config.read_bytes()
        again=self.register()
        self.assertEqual(again['project_id'],entry['project_id'])
        self.assertEqual(self.config.read_bytes(),before)
        self.assertFalse((self.root/'.git').exists())
        self.assertEqual(self.config.stat().st_mode&0o077,0)

    def test_cli_registration_does_not_create_git_or_capture(self):
        cmd=[sys.executable,str(SCRIPTS/'regular_capture.py'),'--config',str(self.config),'--register-local-project',str(self.root),'--store-root',str(self.store)]
        run=subprocess.run(cmd,text=True,capture_output=True)
        self.assertEqual(run.returncode,0,run.stderr)
        result=json.loads(run.stdout)
        self.assertTrue(result['registered']);self.assertFalse(result['capture_started'])
        self.assertFalse((self.root/'.git').exists());self.assertFalse(self.store.exists())

    def test_pair_capture_fresh_read_and_deduplication(self):
        entry=self.register()
        result=flush.flush(self.config,self.root,self.batch(True))
        self.assertEqual((result['saved_count'],result['user_count'],result['assistant_count']),(2,1,1))
        self.assertTrue(result['fresh_process_verified'])
        self.assertEqual(result['project_id'],entry['project_id'])
        protocol=memory.load(self.store/'.macaroni/protocol.json')
        self.assertEqual(protocol['project_id'],entry['project_id']);self.assertIsNone(protocol['repository'])
        before=self.snapshot();again=flush.flush(self.config,self.root,self.batch(True))
        self.assertEqual(again['files_written'],0);self.assertEqual(before,self.snapshot())
        state=agent.status(self.config,self.root)
        self.assertEqual(state['project_id'],entry['project_id']);self.assertEqual(state['observed_messages'],2)

    def test_preparation_and_confirmation_use_local_identity(self):
        entry=self.register();flush.flush(self.config,self.root,self.batch())
        raw={'version':1,'source_system':'synthetic_fixture','source_conversation_id':'fixture-thread','reply_id':'assigned_reply_local_fixture','source_channel':'assistant_final','reply_to_source_message_id':'fixture-user','text':'SYNTHETIC_REPLY'}
        prepared=agent.prepare_reply(self.config,self.root,raw)
        self.assertTrue(prepared['fresh_process_verified'])
        self.assertEqual(memory.load(Path(prepared['reply_path']))['project_id'],entry['project_id'])
        actual=self.batch(True);actual['messages']=actual['messages'][1:]
        confirmed=agent.confirm_reply(self.config,self.root,actual,raw['reply_id'])
        self.assertEqual(confirmed['delivery_state'],'observed')
        self.assertEqual(agent.status(self.config,self.root)['prepared_unconfirmed_replies'],[])

    def test_uuid_collision_and_foreign_store_rejected_before_registry_write(self):
        entry=self.register();before=self.config.read_bytes();other=self.base/'foreign';other.mkdir()
        for store,identity in [(self.base/'another-store',entry['project_id']),(self.store,str(uuid.uuid4()))]:
            with self.subTest(store=store),self.assertRaises(memory.CaptureError):
                self.register(other,store,identity)
            self.assertEqual(self.config.read_bytes(),before)

    def test_nested_roots_and_symlink_aliases_rejected(self):
        self.register();before=self.config.read_bytes();child=self.root/'nested';child.mkdir()
        with self.assertRaises(memory.CaptureError):self.register(child,self.base/'nested-memory')
        alias=self.base/'alias';alias.symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(memory.CaptureError):self.register(alias,self.base/'alias-memory')
        self.assertEqual(self.config.read_bytes(),before)

    def test_move_and_same_path_replacement_block_without_rebinding(self):
        entry=self.register();flush.flush(self.config,self.root,self.batch())
        before=self.snapshot();config=self.config.read_bytes();moved=self.base/'moved';self.root.rename(moved)
        with self.assertRaises((memory.CaptureError,OSError)):agent.status(self.config,self.root)
        with self.assertRaises(memory.CaptureError):self.register(moved,self.store,entry['project_id'])
        self.root.mkdir()
        with self.assertRaises(memory.CaptureError):flush.flush(self.config,self.root,self.batch())
        self.assertEqual(self.snapshot(),before);self.assertEqual(self.config.read_bytes(),config)

    def test_unrelated_repository_still_works_when_local_root_is_missing(self):
        self.register();self.root.rename(self.base/'moved')
        repo=self.base/'git-project';repo.mkdir()
        subprocess.run(['git','init','-q',str(repo)],check=True)
        subprocess.run(['git','-C',str(repo),'remote','add','origin','https://github.com/fixture/independent'],check=True)
        regular.register(self.config,repo,'https://github.com/fixture/independent',self.base/'git-memory')
        result=flush.flush(self.config,repo,self.batch())
        self.assertTrue(result['all_supplied_messages_saved'])

    def test_marker_uuid_or_root_tampering_cannot_capture(self):
        self.register();flush.flush(self.config,self.root,self.batch())
        marker=self.store/'local-store.json';old=memory.load(marker)
        for fault in ['project_id','project_root']:
            doc=dict(old);doc[fault]=str(uuid.uuid4()) if fault=='project_id' else str(self.base/'foreign')
            marker.write_bytes(memory.encoded(doc));before=self.snapshot()
            with self.subTest(fault=fault),self.assertRaises((memory.CaptureError,OSError)):flush.flush(self.config,self.root,self.batch(True))
            self.assertEqual(self.snapshot(),before)
        marker.write_bytes(memory.encoded(old))

    def test_repository_and_local_directory_cannot_share_store(self):
        self.register();before=self.config.read_bytes();repo=self.base/'git-project';repo.mkdir()
        subprocess.run(['git','init','-q',str(repo)],check=True)
        subprocess.run(['git','-C',str(repo),'remote','add','origin','https://github.com/fixture/foreign'],check=True)
        with self.assertRaises(memory.CaptureError):regular.register(self.config,repo,'https://github.com/fixture/foreign',self.store)
        self.assertEqual(self.config.read_bytes(),before)

    def test_local_identity_cannot_be_used_for_git_publication(self):
        self.register();flush.flush(self.config,self.root,self.batch())
        with self.assertRaises(memory.CaptureError):memory.prepare(self.store,self.batch(),'fixture-chat',branch='macaroni')

    def test_existing_private_preparations_are_retained_without_import(self):
        self.store.mkdir(mode=0o700);original=self.store/'existing-preparation.json';original.write_text('{"fixture":"keep"}')
        before=original.read_bytes();self.register();flush.flush(self.config,self.root,self.batch())
        self.assertEqual(original.read_bytes(),before);self.assertEqual(len(memory.existing_messages(self.store)[0]),1)


    def test_changed_source_body_is_rejected_without_mutation(self):
        self.register();flush.flush(self.config,self.root,self.batch());before=self.snapshot()
        changed=self.batch();changed['messages'][0]['text']='OTHER_SYNTHETIC_BODY'
        with self.assertRaises(memory.CaptureError):flush.flush(self.config,self.root,changed)
        self.assertEqual(self.snapshot(),before)

    def test_fresh_verifier_rejects_foreign_local_uuid(self):
        entry=self.register();flush.flush(self.config,self.root,self.batch())
        expected={**memory.binding_identity(entry),'messages':[]};expected['project_id']=str(uuid.uuid4())
        with self.assertRaises(memory.CaptureError):flush.verify(self.store,expected)

    def test_registry_recovery_reuses_original_store_uuid(self):
        entry=self.register();flush.flush(self.config,self.root,self.batch());before=self.snapshot()
        self.config.unlink();again=self.register()
        self.assertEqual(again['project_id'],entry['project_id']);self.assertEqual(self.snapshot(),before)

    def test_unknown_local_protocol_fields_survive_new_message(self):
        self.register();flush.flush(self.config,self.root,self.batch())
        path=self.store/'.macaroni/protocol.json';doc=memory.load(path);doc['future']={'nested':[1,{'keep':True}]}
        path.write_bytes(memory.encoded(doc));before=path.read_bytes()
        flush.flush(self.config,self.root,self.batch(True));self.assertEqual(path.read_bytes(),before)

    def test_foreign_protocol_is_rejected_before_setup_write(self):
        entry=self.register();self.store.mkdir(mode=0o700);(self.store/'.macaroni').mkdir()
        doc={'version':1,**memory.binding_identity(entry),'storage_branch':'local'};doc['project_id']=str(uuid.uuid4())
        (self.store/'.macaroni/protocol.json').write_bytes(memory.encoded(doc));before=self.snapshot()
        with self.assertRaises(memory.CaptureError):flush.flush(self.config,self.root,self.batch())
        self.assertEqual(self.snapshot(),before);self.assertFalse((self.store/'local-store.json').exists())

    def test_existing_git_without_remote_remains_unchanged(self):
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        before=(self.root/'.git/config').read_bytes();self.register();flush.flush(self.config,self.root,self.batch())
        self.assertEqual((self.root/'.git/config').read_bytes(),before)
        self.assertEqual(subprocess.run(['git','-C',str(self.root),'remote'],capture_output=True,text=True,check=True).stdout,'')

    def test_local_cli_rejects_repository_argument(self):
        cmd=[sys.executable,str(SCRIPTS/'regular_capture.py'),'--config',str(self.config),'--register-local-project',str(self.root),'--store-root',str(self.store),'--repository','https://github.com/fixture/pretend']
        run=subprocess.run(cmd,text=True,capture_output=True);self.assertNotEqual(run.returncode,0)
        self.assertFalse(self.config.exists());self.assertFalse(self.store.exists())

    def test_status_rejects_foreign_protocol_identity(self):
        self.register();flush.flush(self.config,self.root,self.batch())
        path=self.store/'.macaroni/protocol.json';doc=memory.load(path);doc['project_id']=str(uuid.uuid4());path.write_bytes(memory.encoded(doc))
        before=self.snapshot()
        with self.assertRaises(memory.CaptureError):agent.status(self.config,self.root)
        self.assertEqual(self.snapshot(),before)

    def test_prepared_check_rejects_foreign_store_marker(self):
        self.register();flush.flush(self.config,self.root,self.batch())
        raw={'version':1,'source_system':'synthetic_fixture','source_conversation_id':'fixture-thread','reply_id':'assigned_reply_local_fixture','source_channel':'assistant_final','reply_to_source_message_id':'fixture-user','text':'SYNTHETIC_REPLY'}
        prepared=agent.prepare_reply(self.config,self.root,raw);path=Path(prepared['reply_path'])
        expected={'reply_id':raw['reply_id'],'file_sha256':memory.digest(path.read_bytes()),'text_sha256':prepared['text_sha256']}
        marker=self.store/'local-store.json';doc=memory.load(marker);doc['project_id']=str(uuid.uuid4());marker.write_bytes(memory.encoded(doc));before=self.snapshot()
        with self.assertRaises(memory.CaptureError):agent.check_reply(self.config,self.root,expected)
        self.assertEqual(self.snapshot(),before)

if __name__=='__main__':unittest.main()
