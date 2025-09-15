# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json


class TestZoomMeetingAttendee(TransactionCase):
    """Tests para el modelo zoom.meeting.attendee"""

    def setUp(self):
        super().setUp()
        self.zoom_meeting_attendee = self.env['zoom.meeting.attendee']
        self.zoom_meeting = self.env['zoom.meeting']
        self.zoom_config = self.env['zoom.config']
        
        # Crear configuración de Zoom
        self.config = self.zoom_config.create({
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'account_id': 'test_account_id',
        })
        
        # Crear reunión
        self.meeting = self.zoom_meeting.create({
            'name': 'Test Meeting',
            'start_time': datetime.now() + timedelta(hours=1),
            'duration': 60,
            'zoom_config_id': self.config.id,
        })
        
        # Datos de test para asistente
        self.attendee_data = {
            'meeting_id': self.meeting.id,
            'email': 'test@example.com',
            'name': 'Test User',
            'status': 'pending',
        }

    def test_create_zoom_meeting_attendee(self):
        """Test: Crear asistente de reunión"""
        attendee = self.zoom_meeting_attendee.create(self.attendee_data)
        
        self.assertEqual(attendee.email, 'test@example.com')
        self.assertEqual(attendee.name, 'Test User')
        self.assertEqual(attendee.status, 'pending')
        self.assertEqual(attendee.meeting_id.id, self.meeting.id)

    def test_attendee_required_fields(self):
        """Test: Campos requeridos en asistente"""
        with self.assertRaises(ValidationError):
            self.zoom_meeting_attendee.create({
                'meeting_id': self.meeting.id,
                # Falta email y name
            })

    def test_attendee_email_validation(self):
        """Test: Validación de email"""
        # Email válido
        attendee = self.zoom_meeting_attendee.create({
            'meeting_id': self.meeting.id,
            'email': 'valid@example.com',
            'name': 'Test User',
        })
        self.assertEqual(attendee.email, 'valid@example.com')
        
        # Email inválido
        with self.assertRaises(ValidationError):
            self.zoom_meeting_attendee.create({
                'meeting_id': self.meeting.id,
                'email': 'invalid-email',
                'name': 'Test User',
            })

    def test_attendee_default_values(self):
        """Test: Valores por defecto"""
        attendee = self.zoom_meeting_attendee.create({
            'meeting_id': self.meeting.id,
            'email': 'test@example.com',
            'name': 'Test User',
        })
        
        self.assertEqual(attendee.status, 'pending')
        self.assertFalse(attendee.attended)
        self.assertFalse(attendee.confirmed)

    def test_attendee_status_transitions(self):
        """Test: Transiciones de estado"""
        attendee = self.zoom_meeting_attendee.create(self.attendee_data)
        
        # Estado inicial
        self.assertEqual(attendee.status, 'pending')
        self.assertFalse(attendee.confirmed)
        
        # Transición a confirmed
        attendee.status = 'confirmed'
        self.assertEqual(attendee.status, 'confirmed')
        self.assertTrue(attendee.confirmed)
        
        # Transición a declined
        attendee.status = 'declined'
        self.assertEqual(attendee.status, 'declined')
        self.assertFalse(attendee.confirmed)

    def test_attendee_attendance_tracking(self):
        """Test: Seguimiento de asistencia"""
        attendee = self.zoom_meeting_attendee.create(self.attendee_data)
        
        # Marcar como asistido
        attendee.attended = True
        attendee.attendance_time = datetime.now()
        
        self.assertTrue(attendee.attended)
        self.assertIsNotNone(attendee.attendance_time)

    def test_attendee_name_get(self):
        """Test: Método name_get"""
        attendee = self.zoom_meeting_attendee.create(self.attendee_data)
        name = attendee.name_get()[0][1]
        
        self.assertIn('Test User', name)
        self.assertIn('test@example.com', name)

    def test_attendee_constraints(self):
        """Test: Restricciones del modelo"""
        # Test de email único por reunión
        attendee1 = self.zoom_meeting_attendee.create(self.attendee_data)
        
        with self.assertRaises(ValidationError):
            self.zoom_meeting_attendee.create({
                'meeting_id': self.meeting.id,
                'email': 'test@example.com',  # Email duplicado
                'name': 'Another User',
            })

    def test_attendee_compute_methods(self):
        """Test: Métodos compute"""
        attendee = self.zoom_meeting_attendee.create(self.attendee_data)
        
        # Test de métodos compute si existen
        if hasattr(attendee, '_compute_display_name'):
            attendee._compute_display_name()
            # Verificar que se calculó correctamente

    def test_attendee_bulk_operations(self):
        """Test: Operaciones en lote"""
        # Crear múltiples asistentes
        attendees_data = [
            {
                'meeting_id': self.meeting.id,
                'email': f'test{i}@example.com',
                'name': f'Test User {i}',
                'status': 'pending',
            }
            for i in range(1, 4)
        ]
        
        attendees = self.zoom_meeting_attendee.create(attendees_data)
        
        self.assertEqual(len(attendees), 3)
        
        # Cambiar estado en lote
        attendees.write({'status': 'confirmed'})
        
        for attendee in attendees:
            self.assertEqual(attendee.status, 'confirmed')
            self.assertTrue(attendee.confirmed)

    def test_attendee_search_methods(self):
        """Test: Métodos de búsqueda"""
        attendee = self.zoom_meeting_attendee.create(self.attendee_data)
        
        # Buscar por email
        found_attendees = self.zoom_meeting_attendee.search([
            ('email', '=', 'test@example.com')
        ])
        
        self.assertIn(attendee, found_attendees)
        
        # Buscar por reunión
        meeting_attendees = self.zoom_meeting_attendee.search([
            ('meeting_id', '=', self.meeting.id)
        ])
        
        self.assertIn(attendee, meeting_attendees)

    def test_attendee_workflow_methods(self):
        """Test: Métodos de flujo de trabajo"""
        attendee = self.zoom_meeting_attendee.create(self.attendee_data)
        
        # Test de métodos de workflow si existen
        if hasattr(attendee, 'action_confirm'):
            attendee.action_confirm()
            self.assertEqual(attendee.status, 'confirmed')
        
        if hasattr(attendee, 'action_decline'):
            attendee.action_decline()
            self.assertEqual(attendee.status, 'declined')

    def test_attendee_integration_with_meeting(self):
        """Test: Integración con reunión"""
        attendee = self.zoom_meeting_attendee.create(self.attendee_data)
        
        # Verificar relación con reunión
        self.assertEqual(attendee.meeting_id.id, self.meeting.id)
        self.assertIn(attendee, self.meeting.attendee_ids)
        
        # Verificar que se actualiza el conteo en la reunión
        self.meeting._compute_attendees()
        self.assertEqual(self.meeting.total_invited, 1)

    def tearDown(self):
        super().tearDown()
        # Limpiar datos de test si es necesario
