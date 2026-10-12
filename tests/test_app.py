import os, tempfile, unittest
from app import app,init_db,db

class CupcakeTests(unittest.TestCase):
    def setUp(self):
        fd,self.path=tempfile.mkstemp(suffix='.db');os.close(fd)
        app.config.update(TESTING=True,DATABASE=self.path,SECRET_KEY='test-secret')
        with app.app_context():init_db()
        self.client=app.test_client()

    def tearDown(self):os.unlink(self.path)
    def register(self,email='teste@exemplo.com'):
        return self.client.post('/cadastro',data={'name':'Cliente Teste','email':email,'password':'senha-segura-123'},follow_redirects=True)
    def test_catalog(self):
        response=self.client.get('/');self.assertEqual(response.status_code,200);self.assertIn('Chocolate Belga',response.get_data(as_text=True))
    def test_register_and_duplicate_email(self):
        self.assertIn('Cadastro realizado',self.register().get_data(as_text=True));self.assertIn('cadastrado',self.register().get_data(as_text=True))
    def test_cart_and_checkout(self):
        self.register();self.client.post('/carrinho/adicionar/1',data={'quantity':'2'});self.assertIn('R$ 25,80',self.client.get('/carrinho').get_data(as_text=True));resp=self.client.post('/finalizar',data={'address':'Rua das Flores, 100, São Paulo','payment':'Pix simulado'},follow_redirects=True);self.assertIn('Pedido #1',resp.get_data(as_text=True))
        with app.app_context():self.assertEqual(db().execute('SELECT COUNT(*) FROM orders').fetchone()[0],1)
    def test_checkout_requires_login(self):
        self.client.post('/carrinho/adicionar/2',data={'quantity':'1'});resp=self.client.get('/finalizar');self.assertEqual(resp.status_code,302);self.assertIn('/entrar',resp.location)
    def test_invalid_quantity(self):
        self.client.post('/carrinho/adicionar/1',data={'quantity':'-2'});self.assertIn('vazio',self.client.get('/carrinho').get_data(as_text=True))
    def test_invalid_address_rejected(self):
        self.register();self.client.post('/carrinho/adicionar/1');self.client.post('/finalizar',data={'address':'rua','payment':'Pix simulado'});
        with app.app_context():self.assertEqual(db().execute('SELECT COUNT(*) FROM orders').fetchone()[0],0)
    def test_password_is_hashed(self):
        self.register()
        with app.app_context():self.assertNotEqual(db().execute('SELECT password_hash FROM users').fetchone()[0],'senha-segura-123')

if __name__=='__main__':unittest.main()
