import unittest
import json
from app import create_app, db
from app.models import Usuario, Tablero, Lista, Tarjeta

class ClusteringVerificationTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            # Create user
            user = Usuario(username='testuser', email='test@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id
            
            # Create board
            tablero = Tablero(nombre="Test Board", creador_id=user.id)
            db.session.add(tablero)
            db.session.commit()
            self.tablero_id = tablero.id
            
            # Create initial list
            lista = Lista(nombre="Inbox", tablero_id=tablero.id)
            db.session.add(lista)
            db.session.commit()
            self.lista_id = lista.id
            
            # Create people with coordinates
            # Cluster 1 (Near 0,0)
            p1 = Tarjeta(nombre="P1", lista_id=lista.id, latitud=0.001, longitud=0.001)
            p2 = Tarjeta(nombre="P2", lista_id=lista.id, latitud=0.002, longitud=0.002)
            # Cluster 2 (Far away)
            p3 = Tarjeta(nombre="P3", lista_id=lista.id, latitud=10.0, longitud=10.0)
            p4 = Tarjeta(nombre="P4", lista_id=lista.id, latitud=10.001, longitud=10.001)
            
            db.session.add_all([p1, p2, p3, p4])
            db.session.commit()
            
            self.p1_id = p1.id
            self.p2_id = p2.id
            self.p3_id = p3.id
            self.p4_id = p4.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user_id
            sess['username'] = 'testuser'

    def test_apply_clustering(self):
        self.login()
        
        # Simulate the payload that the frontend would send after previewing
        # We manually construct clusters to match what the backend expects
        clusters_payload = [
            {
                'members': [{'id': self.p1_id}, {'id': self.p2_id}],
                'centroid': {'lat': 0.0015, 'lng': 0.0015},
                'is_outlier': False
            },
            {
                'members': [{'id': self.p3_id}, {'id': self.p4_id}],
                'centroid': {'lat': 10.0005, 'lng': 10.0005},
                'is_outlier': False
            }
        ]
        
        response = self.client.post('/tableros/api/clustering/apply', 
                                  json={
                                      'tablero_id': self.tablero_id,
                                      'clusters': clusters_payload
                                  })
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Data: {response.json}")
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
        self.assertEqual(response.json['created_lists'], 2)
        
        # Verify database state
        with self.app.app_context():
            tablero = Tablero.query.get(self.tablero_id)
            self.assertEqual(len(tablero.listas), 3) # Inbox + 2 new lists
            
            # Check list names
            new_lists = [l for l in tablero.listas if l.nombre.startswith("Grupo Geográfico")]
            self.assertEqual(len(new_lists), 2)
            
            # Check people moved
            for l in new_lists:
                self.assertEqual(len(l.tarjetas), 2)

if __name__ == '__main__':
    unittest.main()
