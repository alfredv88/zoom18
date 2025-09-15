# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from unittest.mock import patch, MagicMock
import json


class TestZoomConfig(TransactionCase):
    """Tests para el modelo zoom.config"""

    def setUp(self):
        super().setUp()
        self.zoom_config = self.env['zoom.config']
        self.test_config_data = {
            'client_id': 'test_client_id_123',
            'client_secret': 'test_client_secret_456',
            'account_id': 'test_account_id_789',
            'base_url': 'https://api.zoom.us/v2',
            'auto_record': False,
            'waiting_room': True,
            'join_before_host': False,
            'mute_on_entry': True,
            'use_webhooks': False,
        }

    def test_create_zoom_config(self):
        """Test: Crear configuración de Zoom"""
        config = self.zoom_config.create(self.test_config_data)
        
        self.assertEqual(config.client_id, 'test_client_id_123')
        self.assertEqual(config.client_secret, 'test_client_secret_456')
        self.assertEqual(config.account_id, 'test_account_id_789')
        self.assertTrue(config.waiting_room)
        self.assertFalse(config.auto_record)
        self.assertTrue(config.installable)

    def test_zoom_config_required_fields(self):
        """Test: Campos requeridos en configuración"""
        with self.assertRaises(ValidationError):
            self.zoom_config.create({
                'client_id': 'test_id',
                # Falta client_secret y account_id
            })

    def test_zoom_config_default_values(self):
        """Test: Valores por defecto"""
        config = self.zoom_config.create({
            'client_id': 'test_id',
            'client_secret': 'test_secret',
            'account_id': 'test_account',
        })
        
        self.assertEqual(config.base_url, 'https://api.zoom.us/v2')
        self.assertFalse(config.auto_record)
        self.assertTrue(config.waiting_room)
        self.assertFalse(config.join_before_host)
        self.assertTrue(config.mute_on_entry)
        self.assertFalse(config.use_webhooks)

    @patch('requests.post')
    def test_get_access_token_success(self, mock_post):
        """Test: Obtener token de acceso exitosamente"""
        # Mock de respuesta exitosa
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_access_token_123',
            'expires_in': 3600,
            'token_type': 'Bearer'
        }
        mock_post.return_value = mock_response
        
        config = self.zoom_config.create(self.test_config_data)
        token = config._get_access_token()
        
        self.assertEqual(token, 'test_access_token_123')
        self.assertEqual(config.access_token, 'test_access_token_123')
        self.assertTrue(config.token_expires_at)

    @patch('requests.post')
    def test_get_access_token_failure(self, mock_post):
        """Test: Error al obtener token de acceso"""
        # Mock de respuesta con error
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'error': 'invalid_client'}
        mock_post.return_value = mock_response
        
        config = self.zoom_config.create(self.test_config_data)
        
        with self.assertRaises(UserError):
            config._get_access_token()

    @patch('requests.get')
    def test_test_connection_success(self, mock_get):
        """Test: Probar conexión exitosamente"""
        # Mock de respuesta exitosa
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'test_user_id',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com'
        }
        mock_get.return_value = mock_response
        
        config = self.zoom_config.create(self.test_config_data)
        
        with patch.object(config, '_get_access_token', return_value='test_token'):
            result = config.test_connection()
            self.assertTrue(result)
            self.assertTrue(config.connection_tested)

    @patch('requests.get')
    def test_test_connection_failure(self, mock_get):
        """Test: Error al probar conexión"""
        # Mock de respuesta con error
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'error': 'unauthorized'}
        mock_get.return_value = mock_response
        
        config = self.zoom_config.create(self.test_config_data)
        
        with patch.object(config, '_get_access_token', return_value='test_token'):
            result = config.test_connection()
            self.assertFalse(result)
            self.assertFalse(config.connection_tested)

    def test_validate_credentials(self):
        """Test: Validar credenciales"""
        config = self.zoom_config.create(self.test_config_data)
        
        # Credenciales válidas
        self.assertTrue(config._validate_credentials())
        
        # Credenciales inválidas
        config.client_id = ''
        self.assertFalse(config._validate_credentials())

    def test_get_meeting_settings(self):
        """Test: Obtener configuración de reunión"""
        config = self.zoom_config.create(self.test_config_data)
        settings = config._get_meeting_settings()
        
        expected_settings = {
            'auto_recording': 'none' if not config.auto_record else 'cloud',
            'waiting_room': config.waiting_room,
            'join_before_host': config.join_before_host,
            'mute_upon_entry': config.mute_on_entry,
        }
        
        self.assertEqual(settings, expected_settings)

    def test_zoom_config_constraints(self):
        """Test: Restricciones del modelo"""
        # Test de unicidad (si existe)
        config1 = self.zoom_config.create(self.test_config_data)
        
        # Intentar crear otra configuración con el mismo client_id
        with self.assertRaises(ValidationError):
            self.zoom_config.create(self.test_config_data)

    def test_zoom_config_name_get(self):
        """Test: Método name_get"""
        config = self.zoom_config.create(self.test_config_data)
        name = config.name_get()[0][1]
        
        self.assertIn('test_client_id_123', name)
        self.assertIn('Zoom', name)

    def test_zoom_config_compute_methods(self):
        """Test: Métodos compute"""
        config = self.zoom_config.create(self.test_config_data)
        
        # Test de métodos compute si existen
        if hasattr(config, '_compute_status'):
            config._compute_status()
            # Verificar que el status se calculó correctamente

    def tearDown(self):
        super().tearDown()
        # Limpiar datos de test si es necesario
