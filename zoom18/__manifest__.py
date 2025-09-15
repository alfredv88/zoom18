# -*- coding: utf-8 -*-
{
    'name': 'Zoom Integration',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Integración de Zoom con Odoo 18',
    'description': """
        Módulo de integración de Zoom para Odoo 18
        =============================================
        
        Funcionalidades:
        - Crear, iniciar y gestionar reuniones de Zoom desde Odoo
        - Sincronización automática de reuniones
        - Control total del equipo automático
        - Dashboard personalizado
        - Integración con tareas de proyecto
    """,
    'author': 'https://www.freelancer.com/u/alfredvasquez',
    'website': 'https://github.com/alfredv88/zoom18',
    'depends': [
        'base',
        'project',
        'calendar',
        'web',
        'helpdesk',
    ],
    'data': [
            'security/ir.model.access.csv',
            'static/src/assets.xml',
            'views/zoom_meeting_views.xml',
            'views/zoom_meeting_attendee_views.xml',
            'views/zoom_dashboard_views.xml',
            'views/zoom_config_views.xml',
            'views/calendar_event_views.xml',
            'views/helpdesk_ticket_views.xml',
            'data/zoom_data.xml',
            'data/email_templates.xml',
            'data/cron_jobs.xml',
            'data/helpdesk_data.xml',
        ],
    'demo': [],
    'test': [
        'tests/test_zoom_config.py',
        'tests/test_zoom_meeting.py',
        'tests/test_zoom_meeting_attendee.py',
        'tests/test_zoom_dashboard.py',
        'tests/test_integration.py',
        'tests/test_helpdesk_integration.py',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
    'price': 69.0,
    'currency': 'EUR',
    'support': 'alfredv88@gmail.com',
    'images': [
        'static/description/Captura desde 2025-09-14 01-30-27.png',
        'static/description/Captura desde 2025-09-14 01-31-03.png',
        'static/description/Captura desde 2025-09-14 01-31-13.png',
        'static/description/Captura desde 2025-09-14 01-31-30.png',
        'static/description/icon.png'
    ],
}


