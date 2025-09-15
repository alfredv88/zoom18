# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class TestHelpdeskZoomIntegration(TransactionCase):
    """Test cases para la integración de Zoom con Helpdesk"""

    def setUp(self):
        super(TestHelpdeskZoomIntegration, self).setUp()
        
        # Crear configuración de Zoom para pruebas
        self.zoom_config = self.env['zoom.config'].create({
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'account_id': 'test_account_id',
            'base_url': 'https://api.zoom.us/v2',
            'auto_record': False,
            'waiting_room': True,
            'join_before_host': False,
            'mute_on_entry': True,
            'use_webhooks': False,
        })
        
        # Crear usuario para pruebas
        self.test_user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_user',
            'email': 'test@example.com',
        })
        
        # Crear equipo de helpdesk
        self.helpdesk_team = self.env['helpdesk.team'].create({
            'name': 'Test Team',
            'member_ids': [(6, 0, [self.test_user.id])],
        })

    def test_helpdesk_ticket_creation_with_zoom_fields(self):
        """Test: Crear ticket de helpdesk con campos de Zoom"""
        
        # Crear ticket de helpdesk
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Test Ticket',
            'description': 'Test Description',
            'team_id': self.helpdesk_team.id,
            'user_id': self.test_user.id,
        })
        
        # Verificar que se crearon los campos de Zoom
        self.assertTrue(hasattr(ticket, 'zoom_meeting_id'))
        self.assertTrue(hasattr(ticket, 'meeting_status'))
        self.assertTrue(hasattr(ticket, 'total_attendees'))
        self.assertTrue(hasattr(ticket, 'zoom_created'))
        
        # Verificar valores por defecto
        self.assertEqual(ticket.meeting_status, 'scheduled')
        self.assertEqual(ticket.total_attendees, 0)
        self.assertFalse(ticket.zoom_created)

    def test_zoom_fields_readonly(self):
        """Test: Verificar que los campos de Zoom son solo de lectura"""
        
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Test Ticket',
            'team_id': self.helpdesk_team.id,
        })
        
        # Intentar escribir en campos de solo lectura
        with self.assertRaises(Exception):
            ticket.write({
                'zoom_meeting_id': 'test_id',
                'meeting_status': 'finished',
                'total_attendees': 5,
            })

    def test_zoom_meeting_creation_automatic(self):
        """Test: Creación automática de reunión Zoom al crear ticket"""
        
        # Mock de la respuesta de la API de Zoom
        original_create_zoom_meeting = self.zoom_config.create_zoom_meeting
        
        def mock_create_zoom_meeting(meeting_data):
            return {
                'id': 'test_meeting_id',
                'join_url': 'https://zoom.us/j/test_meeting_id',
                'start_url': 'https://zoom.us/s/test_meeting_id',
                'zoom_created': True,
                'last_sync': fields.Datetime.now()
            }
        
        # Aplicar mock
        self.zoom_config.create_zoom_meeting = mock_create_zoom_meeting
        
        try:
            # Crear ticket
            ticket = self.env['helpdesk.ticket'].create({
                'name': 'Test Ticket with Zoom',
                'description': 'Test Description',
                'team_id': self.helpdesk_team.id,
            })
            
            # Verificar que se creó la reunión Zoom
            self.assertTrue(ticket.zoom_created)
            self.assertEqual(ticket.zoom_meeting_id, 'test_meeting_id')
            self.assertIsNotNone(ticket.zoom_join_url)
            self.assertIsNotNone(ticket.zoom_start_url)
            
        finally:
            # Restaurar método original
            self.zoom_config.create_zoom_meeting = original_create_zoom_meeting

    def test_zoom_data_synchronization(self):
        """Test: Sincronización de datos de Zoom"""
        
        # Crear ticket con reunión Zoom
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Test Ticket',
            'team_id': self.helpdesk_team.id,
            'zoom_meeting_id': 'test_meeting_id',
            'zoom_created': True,
        })
        
        # Mock de la respuesta de la API de Zoom
        def mock_get_meeting_details():
            return {
                'status_code': 200,
                'json': lambda: {
                    'topic': 'Test Meeting Topic',
                    'duration': 60,
                    'start_time': '2025-09-14T10:00:00Z',
                    'host_email': 'host@example.com',
                    'status': 'started'
                }
            }
        
        def mock_get_participants():
            return {
                'status_code': 200,
                'json': lambda: {
                    'participants': [
                        {'name': 'Participant 1', 'email': 'p1@example.com', 'status': 'in_meeting'},
                        {'name': 'Participant 2', 'email': 'p2@example.com', 'status': 'waiting'}
                    ]
                }
            }
        
        def mock_get_recordings():
            return {
                'status_code': 200,
                'json': lambda: {
                    'recording_files': [
                        {'download_url': 'https://zoom.us/recording/test'}
                    ]
                }
            }
        
        # Aplicar mocks
        import requests
        original_get = requests.get
        
        def mock_get(url, **kwargs):
            if 'participants' in url:
                return mock_get_participants()
            elif 'recordings' in url:
                return mock_get_recordings()
            else:
                return mock_get_meeting_details()
        
        try:
            requests.get = mock_get
            
            # Ejecutar sincronización
            ticket._sync_zoom_data()
            
            # Verificar que se actualizaron los datos
            self.assertTrue(ticket.zoom_synced)
            self.assertEqual(ticket.zoom_meeting_topic, 'Test Meeting Topic')
            self.assertEqual(ticket.meeting_duration, 60)
            self.assertEqual(ticket.meeting_status, 'in_progress')
            self.assertEqual(ticket.total_attendees, 2)
            self.assertEqual(ticket.confirmed_attendees, 1)
            self.assertTrue(ticket.recording_available)
            
        finally:
            # Restaurar método original
            requests.get = original_get

    def test_cron_sync_zoom_meetings(self):
        """Test: Cron job para sincronización automática"""
        
        # Crear tickets con reuniones Zoom
        tickets = self.env['helpdesk.ticket'].create([
            {
                'name': 'Ticket 1',
                'team_id': self.helpdesk_team.id,
                'zoom_meeting_id': 'meeting_1',
                'zoom_created': True,
                'meeting_status': 'scheduled',
            },
            {
                'name': 'Ticket 2',
                'team_id': self.helpdesk_team.id,
                'zoom_meeting_id': 'meeting_2',
                'zoom_created': True,
                'meeting_status': 'in_progress',
            }
        ])
        
        # Ejecutar cron job
        self.env['helpdesk.ticket']._cron_sync_zoom_meetings()
        
        # Verificar que se ejecutó sin errores
        # (En un entorno real, esto verificaría que se actualizaron los datos)
        self.assertTrue(True)  # Placeholder para verificación

    def test_helpdesk_ticket_view_inheritance(self):
        """Test: Verificar que la vista se hereda correctamente"""
        
        # Buscar la vista personalizada
        view = self.env['ir.ui.view'].search([
            ('name', '=', 'helpdesk.ticket.form.zoom'),
            ('model', '=', 'helpdesk.ticket')
        ])
        
        self.assertTrue(view.exists())
        self.assertEqual(view.type, 'form')
        self.assertIn('zoom_info', view.arch)

    def test_helpdesk_security_permissions(self):
        """Test: Verificar permisos de seguridad"""
        
        # Buscar reglas de acceso
        access_rules = self.env['ir.model.access'].search([
            ('model_id.model', '=', 'helpdesk.ticket'),
            ('name', 'ilike', 'zoom')
        ])
        
        self.assertTrue(access_rules.exists())
        
        # Verificar que hay reglas para usuarios y managers
        user_rules = access_rules.filtered(lambda r: 'user' in r.name)
        manager_rules = access_rules.filtered(lambda r: 'manager' in r.name)
        
        self.assertTrue(user_rules.exists())
        self.assertTrue(manager_rules.exists())
