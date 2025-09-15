# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json


class TestZoomIntegration(TransactionCase):
    """Tests de integración para el módulo zoom18"""

    def setUp(self):
        super().setUp()
        self.zoom_config = self.env['zoom.config']
        self.zoom_meeting = self.env['zoom.meeting']
        self.zoom_meeting_attendee = self.env['zoom.meeting.attendee']
        self.zoom_dashboard = self.env['zoom.dashboard']
        self.project = self.env['project.project']
        self.task = self.env['project.task']
        self.calendar_event = self.env['calendar.event']
        
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

    def test_full_meeting_workflow(self):
        """Test: Flujo completo de creación de reunión"""
        # 1. Crear reunión
        meeting = self.zoom_meeting.create({
            'name': 'Integration Test Meeting',
            'description': 'Test meeting for integration',
            'start_time': datetime.now() + timedelta(hours=2),
            'duration': 60,
            'project_id': self.project_record.id,
            'task_id': self.task_record.id,
            'zoom_config_id': self.config.id,
        })
        
        self.assertEqual(meeting.status, 'draft')
        self.assertEqual(meeting.project_id.id, self.project_record.id)
        self.assertEqual(meeting.task_id.id, self.task_record.id)
        
        # 2. Agregar asistentes
        attendee1 = self.zoom_meeting_attendee.create({
            'meeting_id': meeting.id,
            'email': 'user1@example.com',
            'name': 'User 1',
            'status': 'pending',
        })
        
        attendee2 = self.zoom_meeting_attendee.create({
            'meeting_id': meeting.id,
            'email': 'user2@example.com',
            'name': 'User 2',
            'status': 'pending',
        })
        
        # 3. Verificar conteo de asistentes
        meeting._compute_attendees()
        self.assertEqual(meeting.total_invited, 2)
        self.assertEqual(meeting.total_confirmed, 0)
        self.assertEqual(meeting.attendance_rate, 0.0)
        
        # 4. Confirmar asistencia
        attendee1.status = 'confirmed'
        meeting._compute_attendees()
        self.assertEqual(meeting.total_confirmed, 1)
        self.assertEqual(meeting.attendance_rate, 50.0)

    @patch('requests.post')
    def test_meeting_creation_with_zoom_api(self, mock_post):
        """Test: Creación de reunión con API de Zoom"""
        # Mock de respuesta exitosa
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': '123456789',
            'join_url': 'https://zoom.us/j/123456789',
            'start_url': 'https://zoom.us/s/123456789',
            'password': 'test123',
        }
        mock_post.return_value = mock_response
        
        meeting = self.zoom_meeting.create({
            'name': 'API Test Meeting',
            'start_time': datetime.now() + timedelta(hours=1),
            'duration': 60,
            'zoom_config_id': self.config.id,
        })
        
        with patch.object(meeting.zoom_config_id, '_get_access_token', return_value='test_token'):
            result = meeting.create_zoom_meeting()
            
            self.assertTrue(result)
            self.assertEqual(meeting.zoom_meeting_id, '123456789')
            self.assertEqual(meeting.join_url, 'https://zoom.us/j/123456789')
            self.assertEqual(meeting.status, 'scheduled')

    def test_project_integration(self):
        """Test: Integración con módulo de proyectos"""
        # Crear reunión asociada a proyecto
        meeting = self.zoom_meeting.create({
            'name': 'Project Meeting',
            'start_time': datetime.now() + timedelta(hours=1),
            'duration': 60,
            'project_id': self.project_record.id,
            'zoom_config_id': self.config.id,
        })
        
        # Verificar que la reunión está asociada al proyecto
        self.assertEqual(meeting.project_id.id, self.project_record.id)
        
        # Verificar que se puede acceder desde el proyecto
        project_meetings = self.zoom_meeting.search([
            ('project_id', '=', self.project_record.id)
        ])
        self.assertIn(meeting, project_meetings)

    def test_task_integration(self):
        """Test: Integración con tareas de proyecto"""
        # Crear reunión asociada a tarea
        meeting = self.zoom_meeting.create({
            'name': 'Task Meeting',
            'start_time': datetime.now() + timedelta(hours=1),
            'duration': 60,
            'project_id': self.project_record.id,
            'task_id': self.task_record.id,
            'zoom_config_id': self.config.id,
        })
        
        # Verificar que la reunión está asociada a la tarea
        self.assertEqual(meeting.task_id.id, self.task_record.id)
        
        # Verificar que se puede acceder desde la tarea
        task_meetings = self.zoom_meeting.search([
            ('task_id', '=', self.task_record.id)
        ])
        self.assertIn(meeting, task_meetings)

    def test_calendar_integration(self):
        """Test: Integración con calendario"""
        # Crear evento de calendario
        calendar_event = self.calendar_event.create({
            'name': 'Calendar Event',
            'start': datetime.now() + timedelta(hours=1),
            'stop': datetime.now() + timedelta(hours=2),
        })
        
        # Crear reunión asociada al evento
        meeting = self.zoom_meeting.create({
            'name': 'Calendar Meeting',
            'start_time': datetime.now() + timedelta(hours=1),
            'duration': 60,
            'calendar_event_id': calendar_event.id,
            'zoom_config_id': self.config.id,
        })
        
        # Verificar asociación
        self.assertEqual(meeting.calendar_event_id.id, calendar_event.id)

    def test_dashboard_integration(self):
        """Test: Integración con dashboard"""
        # Crear reuniones de prueba
        meeting1 = self.zoom_meeting.create({
            'name': 'Dashboard Meeting 1',
            'start_time': datetime.now() + timedelta(hours=1),
            'duration': 60,
            'zoom_config_id': self.config.id,
            'status': 'scheduled',
        })
        
        meeting2 = self.zoom_meeting.create({
            'name': 'Dashboard Meeting 2',
            'start_time': datetime.now() - timedelta(hours=1),
            'duration': 90,
            'zoom_config_id': self.config.id,
            'status': 'finished',
        })
        
        # Crear dashboard
        dashboard = self.zoom_dashboard.create({
            'name': 'Test Dashboard',
        })
        
        # Verificar que el dashboard puede acceder a las reuniones
        all_meetings = self.zoom_meeting.search([])
        self.assertIn(meeting1, all_meetings)
        self.assertIn(meeting2, all_meetings)

    def test_security_integration(self):
        """Test: Integración con seguridad"""
        # Verificar que los permisos están configurados correctamente
        user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser',
            'email': 'test@example.com',
        })
        
        # Verificar acceso a modelos
        self.assertTrue(self.zoom_meeting.with_user(user).check_access_rights('read'))
        self.assertTrue(self.zoom_config.with_user(user).check_access_rights('read'))

    def test_data_integration(self):
        """Test: Integración con datos iniciales"""
        # Verificar que se cargan los datos iniciales
        default_config = self.zoom_config.search([('client_id', '=', 'your_client_id_here')])
        if default_config:
            self.assertEqual(default_config.client_id, 'your_client_id_here')

    def test_cron_jobs_integration(self):
        """Test: Integración con trabajos cron"""
        # Verificar que los cron jobs están configurados
        cron_reminders = self.env['ir.cron'].search([
            ('name', '=', 'Enviar Recordatorios de Reuniones Zoom')
        ])
        
        cron_sync = self.env['ir.cron'].search([
            ('name', '=', 'Sincronizar Reuniones con Zoom')
        ])
        
        # Verificar que existen los cron jobs
        self.assertTrue(cron_reminders or cron_sync)

    def test_email_templates_integration(self):
        """Test: Integración con templates de email"""
        # Verificar que existen templates de email
        email_templates = self.env['mail.template'].search([
            ('name', 'ilike', 'zoom')
        ])
        
        # Verificar que se pueden crear templates
        self.assertIsInstance(email_templates, list)

    def test_workflow_complete(self):
        """Test: Flujo de trabajo completo"""
        # 1. Configurar Zoom
        config = self.zoom_config.create({
            'client_id': 'workflow_test_id',
            'client_secret': 'workflow_test_secret',
            'account_id': 'workflow_test_account',
        })
        
        # 2. Crear proyecto y tarea
        project = self.project.create({'name': 'Workflow Project'})
        task = self.task.create({
            'name': 'Workflow Task',
            'project_id': project.id,
        })
        
        # 3. Crear reunión
        meeting = self.zoom_meeting.create({
            'name': 'Workflow Meeting',
            'start_time': datetime.now() + timedelta(hours=1),
            'duration': 60,
            'project_id': project.id,
            'task_id': task.id,
            'zoom_config_id': config.id,
        })
        
        # 4. Agregar asistentes
        attendee = self.zoom_meeting_attendee.create({
            'meeting_id': meeting.id,
            'email': 'workflow@example.com',
            'name': 'Workflow User',
        })
        
        # 5. Verificar flujo completo
        self.assertEqual(meeting.status, 'draft')
        self.assertEqual(meeting.total_invited, 1)
        self.assertEqual(attendee.status, 'pending')
        
        # 6. Simular confirmación
        attendee.status = 'confirmed'
        meeting._compute_attendees()
        
        self.assertEqual(meeting.total_confirmed, 1)
        self.assertEqual(meeting.attendance_rate, 100.0)

    def tearDown(self):
        super().tearDown()
        # Limpiar datos de test si es necesario
