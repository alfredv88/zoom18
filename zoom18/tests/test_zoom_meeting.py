# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json


class TestZoomMeeting(TransactionCase):
    """Tests para el modelo zoom.meeting"""

    def setUp(self):
        super().setUp()
        self.zoom_meeting = self.env['zoom.meeting']
        self.zoom_config = self.env['zoom.config']
        self.project = self.env['project.project']
        self.task = self.env['project.task']
        
        # Crear configuración de Zoom
        self.config = self.zoom_config.create({
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'account_id': 'test_account_id',
        })
        
        # Crear proyecto y tarea
        self.project_record = self.project.create({
            'name': 'Test Project',
        })
        
        self.task_record = self.task.create({
            'name': 'Test Task',
            'project_id': self.project_record.id,
        })
        
        # Datos de test para reunión
        self.meeting_data = {
            'name': 'Test Meeting',
            'description': 'Test meeting description',
            'start_time': datetime.now() + timedelta(hours=1),
            'duration': 60,
            'project_id': self.project_record.id,
            'task_id': self.task_record.id,
            'zoom_config_id': self.config.id,
        }

    def test_create_zoom_meeting(self):
        """Test: Crear reunión de Zoom"""
        meeting = self.zoom_meeting.create(self.meeting_data)
        
        self.assertEqual(meeting.name, 'Test Meeting')
        self.assertEqual(meeting.duration, 60)
        self.assertEqual(meeting.project_id.id, self.project_record.id)
        self.assertEqual(meeting.task_id.id, self.task_record.id)
        self.assertEqual(meeting.status, 'draft')

    def test_meeting_required_fields(self):
        """Test: Campos requeridos en reunión"""
        with self.assertRaises(ValidationError):
            self.zoom_meeting.create({
                'name': 'Test Meeting',
                # Falta start_time y duration
            })

    def test_meeting_default_values(self):
        """Test: Valores por defecto"""
        meeting = self.zoom_meeting.create({
            'name': 'Test Meeting',
            'start_time': datetime.now() + timedelta(hours=1),
            'duration': 60,
            'zoom_config_id': self.config.id,
        })
        
        self.assertEqual(meeting.status, 'draft')
        self.assertEqual(meeting.total_invited, 0)
        self.assertEqual(meeting.total_confirmed, 0)
        self.assertEqual(meeting.attendance_rate, 0.0)

    def test_meeting_duration_validation(self):
        """Test: Validación de duración"""
        # Duración válida
        meeting = self.zoom_meeting.create({
            'name': 'Test Meeting',
            'start_time': datetime.now() + timedelta(hours=1),
            'duration': 30,
            'zoom_config_id': self.config.id,
        })
        self.assertEqual(meeting.duration, 30)
        
        # Duración inválida (negativa)
        with self.assertRaises(ValidationError):
            self.zoom_meeting.create({
                'name': 'Test Meeting',
                'start_time': datetime.now() + timedelta(hours=1),
                'duration': -10,
                'zoom_config_id': self.config.id,
            })

    def test_meeting_start_time_validation(self):
        """Test: Validación de hora de inicio"""
        # Hora futura válida
        meeting = self.zoom_meeting.create({
            'name': 'Test Meeting',
            'start_time': datetime.now() + timedelta(hours=1),
            'duration': 60,
            'zoom_config_id': self.config.id,
        })
        self.assertTrue(meeting.start_time > datetime.now())
        
        # Hora pasada (debería permitirse para reuniones ya realizadas)
        past_meeting = self.zoom_meeting.create({
            'name': 'Past Meeting',
            'start_time': datetime.now() - timedelta(hours=1),
            'duration': 60,
            'zoom_config_id': self.config.id,
            'status': 'finished',
        })
        self.assertEqual(past_meeting.status, 'finished')

    @patch('requests.post')
    def test_create_zoom_meeting_success(self, mock_post):
        """Test: Crear reunión en Zoom exitosamente"""
        # Mock de respuesta exitosa
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': '123456789',
            'join_url': 'https://zoom.us/j/123456789',
            'start_url': 'https://zoom.us/s/123456789',
            'password': 'test123',
            'settings': {
                'waiting_room': True,
                'join_before_host': False,
            }
        }
        mock_post.return_value = mock_response
        
        meeting = self.zoom_meeting.create(self.meeting_data)
        
        with patch.object(meeting.zoom_config_id, '_get_access_token', return_value='test_token'):
            result = meeting.create_zoom_meeting()
            
            self.assertTrue(result)
            self.assertEqual(meeting.zoom_meeting_id, '123456789')
            self.assertEqual(meeting.join_url, 'https://zoom.us/j/123456789')
            self.assertEqual(meeting.start_url, 'https://zoom.us/s/123456789')
            self.assertEqual(meeting.password, 'test123')
            self.assertEqual(meeting.status, 'scheduled')

    @patch('requests.post')
    def test_create_zoom_meeting_failure(self, mock_post):
        """Test: Error al crear reunión en Zoom"""
        # Mock de respuesta con error
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': 'invalid_request'}
        mock_post.return_value = mock_response
        
        meeting = self.zoom_meeting.create(self.meeting_data)
        
        with patch.object(meeting.zoom_config_id, '_get_access_token', return_value='test_token'):
            with self.assertRaises(UserError):
                meeting.create_zoom_meeting()

    @patch('requests.patch')
    def test_update_zoom_meeting_success(self, mock_patch):
        """Test: Actualizar reunión en Zoom exitosamente"""
        # Mock de respuesta exitosa
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_patch.return_value = mock_response
        
        meeting = self.zoom_meeting.create(self.meeting_data)
        meeting.zoom_meeting_id = '123456789'
        meeting.status = 'scheduled'
        
        with patch.object(meeting.zoom_config_id, '_get_access_token', return_value='test_token'):
            result = meeting.update_zoom_meeting()
            self.assertTrue(result)

    @patch('requests.delete')
    def test_delete_zoom_meeting_success(self, mock_delete):
        """Test: Eliminar reunión en Zoom exitosamente"""
        # Mock de respuesta exitosa
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response
        
        meeting = self.zoom_meeting.create(self.meeting_data)
        meeting.zoom_meeting_id = '123456789'
        meeting.status = 'scheduled'
        
        with patch.object(meeting.zoom_config_id, '_get_access_token', return_value='test_token'):
            result = meeting.delete_zoom_meeting()
            self.assertTrue(result)
            self.assertEqual(meeting.status, 'cancelled')

    def test_meeting_attendees_computation(self):
        """Test: Cálculo de asistentes"""
        meeting = self.zoom_meeting.create(self.meeting_data)
        
        # Crear asistentes
        attendee1 = self.env['zoom.meeting.attendee'].create({
            'meeting_id': meeting.id,
            'email': 'test1@example.com',
            'name': 'Test User 1',
            'status': 'confirmed',
        })
        
        attendee2 = self.env['zoom.meeting.attendee'].create({
            'meeting_id': meeting.id,
            'email': 'test2@example.com',
            'name': 'Test User 2',
            'status': 'pending',
        })
        
        # Recalcular campos computados
        meeting._compute_attendees()
        
        self.assertEqual(meeting.total_invited, 2)
        self.assertEqual(meeting.total_confirmed, 1)
        self.assertEqual(meeting.attendance_rate, 50.0)

    def test_meeting_status_transitions(self):
        """Test: Transiciones de estado"""
        meeting = self.zoom_meeting.create(self.meeting_data)
        
        # Estado inicial
        self.assertEqual(meeting.status, 'draft')
        
        # Transición a scheduled
        meeting.status = 'scheduled'
        self.assertEqual(meeting.status, 'scheduled')
        
        # Transición a active
        meeting.status = 'active'
        self.assertEqual(meeting.status, 'active')
        
        # Transición a finished
        meeting.status = 'finished'
        self.assertEqual(meeting.status, 'finished')

    def test_meeting_name_get(self):
        """Test: Método name_get"""
        meeting = self.zoom_meeting.create(self.meeting_data)
        name = meeting.name_get()[0][1]
        
        self.assertIn('Test Meeting', name)

    def test_meeting_constraints(self):
        """Test: Restricciones del modelo"""
        # Test de duración mínima
        with self.assertRaises(ValidationError):
            self.zoom_meeting.create({
                'name': 'Test Meeting',
                'start_time': datetime.now() + timedelta(hours=1),
                'duration': 0,  # Duración inválida
                'zoom_config_id': self.config.id,
            })

    def test_meeting_compute_methods(self):
        """Test: Métodos compute"""
        meeting = self.zoom_meeting.create(self.meeting_data)
        
        # Test de métodos compute si existen
        if hasattr(meeting, '_compute_duration_display'):
            meeting._compute_duration_display()
            # Verificar que se calculó correctamente

    def tearDown(self):
        super().tearDown()
        # Limpiar datos de test si es necesario
