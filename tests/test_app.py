import unittest
from unittest.mock import patch
import app
from conversation import recent_messages, fit_prompt

class Tests(unittest.TestCase):
 def setUp(self):
  app.app.config['TESTING']=True
  app._histories.clear()
 def test_isolated_reset(self):
  a,b=app.app.test_client(),app.app.test_client();a.get('/');b.get('/')
  with a.session_transaction() as s: aid=s['conversation']
  with b.session_transaction() as s: bid=s['conversation']
  self.assertNotEqual(aid,bid)
  app._histories.update({aid:(0,['A']),bid:(0,['B'])})
  self.assertEqual(a.post('/reset').status_code,200)
  self.assertNotIn(aid,app._histories);self.assertIn(bid,app._histories)
 def test_validation(self):
  c=app.app.test_client()
  for data in [{},{'prompt':3},{'prompt':' '},{'prompt':'x'*2001}]:
   self.assertEqual(c.post('/chatbot',json=data).status_code,400)
 def test_loading_failure(self):
  with patch('app.load_model',side_effect=RuntimeError('private detail')):
   r=app.app.test_client().post('/chatbot',json={'prompt':'Hello'})
   self.assertEqual(r.status_code,503);self.assertNotIn('private detail',r.text)
 def test_system_and_pairs(self):
  m=[{'role':'system','content':'S'}]+[{'role':r,'content':str(i)} for i in range(8) for r in ('user','assistant')]+[{'role':'user','content':'last'}]
  out=recent_messages(m);self.assertEqual(sum(x['role']=='system' for x in out),1)
  self.assertEqual(out[1]['role'],'user');self.assertEqual(out[-1]['content'],'last')
 def test_budget_preserves_current(self):
  class Tokenizer:
   def encode(self,s):return list(s)
  self.assertEqual(fit_prompt(Tokenizer(),['old'*30],'new',20),'User: new\nBot:')
  with self.assertRaises(ValueError):fit_prompt(Tokenizer(),[],'x'*30,20)
 def test_large_body(self):
  r=app.app.test_client().post('/chatbot',data='x'*20000,content_type='application/json')
  self.assertEqual(r.status_code,413);self.assertIn('error',r.json)
 def test_success_plain_text_and_session_history(self):
  import sys
  from types import SimpleNamespace
  from contextlib import nullcontext
  class Model:
   config=SimpleNamespace(max_position_embeddings=128)
   def generate(self,**kwargs):return [[1]]
  class Tokenizer:
   def encode(self,text):return text.split()
   def __call__(self,*args,**kwargs):return {}
   def decode(self,*args,**kwargs):return '<b>Test reply</b>'
  with patch('app.load_model',return_value=(Model(),Tokenizer())),patch.dict(sys.modules,{'torch':SimpleNamespace(inference_mode=nullcontext)}):
   c=app.app.test_client();r=c.post('/chatbot',json={'prompt':'Hello'})
   self.assertEqual(r.status_code,200);self.assertEqual(r.mimetype,'text/plain')
   self.assertEqual(r.headers['X-Content-Type-Options'],'nosniff')
   with c.session_transaction() as s: sid=s['conversation']
   self.assertEqual(len(app._histories[sid][1]),1)
