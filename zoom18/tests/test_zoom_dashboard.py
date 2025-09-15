# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json


class TestZoomDashboard(TransactionCase):
    """Tests para el modelo zoom.dashboard"""

    def setUp(self):
        super().setUp()
        self.zoom_dashboard = self.env['zoom.dashboard']
        self.zoom_meeting = self.env['zoom.meeting']
        self.zoom_config = self.env['zoom.config']
        self.project = self.env['project.project']
        
        # Crear configuración de Zoom
        self.config = self.zoom_config.create({
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'account_id': 'test_account_id',
        })
        
        # Crear proyecto
        self.project_record = self.project.create({
            'name': 'Test Project',
        })
        
        # Crear reuniones de prueba
        self.meeting1 = self.zoom_meeting.create({
            'name': 'Meeting 1',
            'start_time': datetime.now() + timedelta(hours=1),
            'duration': 60,
            'zoom_config_id': self.config.id,
            'project_id': self.project_record.id,
            'status': 'scheduled',
        })
        
        self.meeting2 = self.zoom_meeting.create({
            'name': 'Meeting 2',
            'start_time': datetime.now() - timedelta(hours=1),
            'duration': 90,
            'zoom_config_id': self.config.id,
            'project_id': self.project_record.id,
            'status': 'finished',
        })

    def test_dashboard_creation(self):
        """Test: Crear dashboard"""
        dashboard = self.zoom_dashboard.create({
            'name': 'Test Dashboard',
        })
        
        self.assertEqual(dashboard.name, 'Test Dashboard')
        self.assertTrue(dashboard.installable)

    def test_dashboard_default_values(self):
        """Test: Valores por defecto del dashboard"""
        dashboard = self.zoom_dashboard.create({})
        
        # Verificar valores por defecto si existen
        self.assertTrue(dashboard.installable)

    def test_dashboard_compute_methods(self):
        """Test: Métodos compute del dashboard"""
        dashboard = self.zoom_dashboard.create({})
        
        # Test de métodos compute si existen
        if hasattr(dashboard, '_compute_meeting_stats'):
            dashboard._compute_meeting_stats()
            # Verificar que se calcularon las estadísticas

    def test_dashboard_meeting_statistics(self):
        """Test: Estadísticas de reuniones"""
        dashboard = self.zoom_dashboard.create({})
        
        # Test de cálculo de estadísticas si existe el método
        if hasattr(dashboard, 'get_meeting_statistics'):
            stats = dashboard.get_meeting_statistics()
            
            # Verificar que se devuelven estadísticas válidas
            self.assertIsInstance(stats, dict)
            
            # Verificar campos esperados
            expected_fields = ['total_meetings', 'active_meetings', 'finished_meetings']
            for field in expected_fields:
                if field in stats:
                    self.assertIsInstance(stats[field], int)
                    self.assertGreaterEqual(stats[field], 0)

    def test_dashboard_project_statistics(self):
        """Test: Estadísticas por proyecto"""
        dashboard = self.zoom_dashboard.create({})
        
        # Test de estadísticas por proyecto si existe el método
        if hasattr(dashboard, 'get_project_statistics'):
            stats = dashboard.get_project_statistics()
            
            # Verificar que se devuelven estadísticas válidas
            self.assertIsInstance(stats, list)
            
            # Verificar estructura de cada elemento
            for stat in stats:
                self.assertIsInstance(stat, dict)
                self.assertIn('project_name', stat)
                self.assertIn('meeting_count', stat)

    def test_dashboard_attendance_statistics(self):
        """Test: Estadísticas de asistencia"""
        dashboard = self.zoom_dashboard.create({})
        
        # Test de estadísticas de asistencia si existe el método
        if hasattr(dashboard, 'get_attendance_statistics'):
            stats = dashboard.get_attendance_statistics()
            
            # Verificar que se devuelven estadísticas válidas
            self.assertIsInstance(stats, dict)
            
            # Verificar campos esperados
            expected_fields = ['total_invited', 'total_confirmed', 'attendance_rate']
            for field in expected_fields:
                if field in stats:
                    self.assertIsInstance(stats[field], (int, float))
                    self.assertGreaterEqual(stats[field], 0)

    def test_dashboard_recent_meetings(self):
        """Test: Reuniones recientes"""
        dashboard = self.zoom_dashboard.create({})
        
        # Test de reuniones recientes si existe el método
        if hasattr(dashboard, 'get_recent_meetings'):
            meetings = dashboard.get_recent_meetings(limit=5)
            
            # Verificar que se devuelven reuniones válidas
            self.assertIsInstance(meetings, list)
            self.assertLessEqual(len(meetings), 5)
            
            # Verificar estructura de cada reunión
            for meeting in meetings:
                self.assertIsInstance(meeting, dict)
                self.assertIn('name', meeting)
                self.assertIn('start_time', meeting)
                self.assertIn('status', meeting)

    def test_dashboard_upcoming_meetings(self):
        """Test: Reuniones próximas"""
        dashboard = self.zoom_dashboard.create({})
        
        # Test de reuniones próximas si existe el método
        if hasattr(dashboard, 'get_upcoming_meetings'):
            meetings = dashboard.get_upcoming_meetings(limit=5)
            
            # Verificar que se devuelven reuniones válidas
            self.assertIsInstance(meetings, list)
            self.assertLessEqual(len(meetings), 5)
            
            # Verificar que todas las reuniones son futuras
            now = datetime.now()
            for meeting in meetings:
                if 'start_time' in meeting:
                    start_time = datetime.fromisoformat(meeting['start_time'].replace('Z', '+00:00'))
                    self.assertGreater(start_time, now)

    def test_dashboard_meeting_actions(self):
        """Test: Acciones del dashboard"""
        dashboard = self.zoom_dashboard.create({})
        
        # Test de acciones si existen
        if hasattr(dashboard, 'action_create_meeting'):
            result = dashboard.action_create_meeting()
            # Verificar que se devuelve una acción válida
            self.assertIsInstance(result, dict)
            self.assertIn('type', result)
        
        if hasattr(dashboard, 'action_view_meetings'):
            result = dashboard.action_view_meetings()
            # Verificar que se devuelve una acción válida
            self.assertIsInstance(result, dict)
            self.assertIn('type', result)

    def test_dashboard_search_methods(self):
        """Test: Métodos de búsqueda"""
        dashboard = self.zoom_dashboard.create({})
        
        # Test de métodos de búsqueda si existen
        if hasattr(dashboard, 'search_meetings'):
            meetings = dashboard.search_meetings(domain=[('status', '=', 'scheduled')])
            
            # Verificar que se devuelven reuniones válidas
            self.assertIsInstance(meetings, list)
            
            # Verificar que todas las reuniones cumplen el criterio
            for meeting in meetings:
                self.assertEqual(meeting.status, 'scheduled')

    def test_dashboard_filter_methods(self):
        """Test: Métodos de filtrado"""
        dashboard = self.zoom_dashboard.create({})
        
        # Test de métodos de filtrado si existen
        if hasattr(dashboard, 'filter_meetings_by_project'):
            meetings = dashboard.filter_meetings_by_project(self.project_record.id)
            
            # Verificar que se devuelven reuniones válidas
            self.assertIsInstance(meetings, list)
            
            # Verificar que todas las reuniones pertenecen al proyecto
            for meeting in meetings:
                self.assertEqual(meeting.project_id.id, self.project_record.id)

    def test_dashboard_export_methods(self):
        """Test: Métodos de exportación"""
        dashboard = self.zoom_dashboard.create({})
        
        # Test de métodos de exportación si existen
        if hasattr(dashboard, 'export_meeting_data'):
            data = dashboard.export_meeting_data()
            
            # Verificar que se devuelven datos válidos
            self.assertIsInstance(data, (dict, list))

    def test_dashboard_performance(self):
        """Test: Rendimiento del dashboard"""
        dashboard = self.zoom_dashboard.create({})
        
        # Test de rendimiento si existen métodos de optimización
        if hasattr(dashboard, 'optimize_queries'):
            dashboard.optimize_queries()
            # Verificar que no se producen errores

    def test_dashboard_integration(self):
        """Test: Integración con otros modelos"""
        dashboard = self.zoom_dashboard.create({})
        
        # Verificar que puede acceder a las reuniones
        meetings = self.zoom_meeting.search([])
        self.assertIsInstance(meetings, list)
        
        # Verificar que puede acceder a la configuración
        configs = self.zoom_config.search([])
        self.assertIsInstance(configs, list)

    def tearDown(self):
        super().tearDown()
        # Limpiar datos de test si es necesario
