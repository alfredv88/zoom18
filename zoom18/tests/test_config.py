# -*- coding: utf-8 -*-

"""
Configuración de tests para el módulo zoom18
"""

import os
import sys
from unittest.mock import patch

# Configuración de variables de entorno para tests
os.environ['TESTING'] = 'True'
os.environ['ODOO_TESTING'] = 'True'

# Configuración de mocks globales
def setup_test_environment():
    """Configurar entorno de pruebas"""
    
    # Mock de requests para evitar llamadas reales a APIs
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post, \
         patch('requests.patch') as mock_patch, \
         patch('requests.delete') as mock_delete:
        
        # Configurar respuestas por defecto
        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 201
        mock_patch.return_value.status_code = 204
        mock_delete.return_value.status_code = 204
        
        yield mock_get, mock_post, mock_patch, mock_delete

# Configuración de datos de prueba
TEST_DATA = {
    'zoom_config': {
        'client_id': 'test_client_id_123',
        'client_secret': 'test_client_secret_456',
        'account_id': 'test_account_id_789',
        'base_url': 'https://api.zoom.us/v2',
        'auto_record': False,
        'waiting_room': True,
        'join_before_host': False,
        'mute_on_entry': True,
        'use_webhooks': False,
    },
    'zoom_meeting': {
        'name': 'Test Meeting',
        'description': 'Test meeting description',
        'duration': 60,
        'auto_record': False,
        'waiting_room': True,
        'join_before_host': False,
        'mute_on_entry': True,
    },
    'zoom_meeting_attendee': {
        'email': 'test@example.com',
        'name': 'Test User',
        'status': 'pending',
    },
    'project': {
        'name': 'Test Project',
    },
    'task': {
        'name': 'Test Task',
    },
}

# Configuración de respuestas mock de Zoom API
ZOOM_API_RESPONSES = {
    'access_token': {
        'access_token': 'test_access_token_123',
        'expires_in': 3600,
        'token_type': 'Bearer'
    },
    'create_meeting': {
        'id': '123456789',
        'join_url': 'https://zoom.us/j/123456789',
        'start_url': 'https://zoom.us/s/123456789',
        'password': 'test123',
        'settings': {
            'waiting_room': True,
            'join_before_host': False,
            'mute_upon_entry': True,
        }
    },
    'user_info': {
        'id': 'test_user_id',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com'
    },
    'meeting_list': {
        'meetings': [
            {
                'id': '123456789',
                'topic': 'Test Meeting',
                'start_time': '2025-09-14T10:00:00Z',
                'duration': 60,
                'status': 'waiting'
            }
        ]
    }
}

# Configuración de errores de API
API_ERRORS = {
    'invalid_credentials': {
        'status_code': 401,
        'response': {'error': 'invalid_client'}
    },
    'meeting_not_found': {
        'status_code': 404,
        'response': {'error': 'meeting_not_found'}
    },
    'unauthorized': {
        'status_code': 401,
        'response': {'error': 'unauthorized'}
    }
}
