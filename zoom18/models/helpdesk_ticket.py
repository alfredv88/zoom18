# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
import requests

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # ========================================
    # CAMPOS INFORMATIVOS DE ZOOM
    # ========================================
    
    # 1. INFORMACIÓN BÁSICA DE REUNIÓN
    zoom_meeting_id = fields.Char(
        string='ID Reunión Zoom',
        readonly=True,
        help="Identificador único de la reunión en Zoom"
    )
    
    zoom_meeting_topic = fields.Char(
        string='Tema de Reunión',
        readonly=True,
        help="Título de la reunión en Zoom"
    )
    
    zoom_join_url = fields.Char(
        string='URL para Unirse',
        readonly=True,
        help="Enlace para participantes"
    )
    
    zoom_start_url = fields.Char(
        string='URL para Iniciar',
        readonly=True,
        help="Enlace para anfitrión"
    )
    
    meeting_status = fields.Selection([
        ('scheduled', 'Programada'),
        ('in_progress', 'En Curso'),
        ('finished', 'Finalizada'),
        ('cancelled', 'Cancelada')
    ], string='Estado de Reunión', readonly=True, default='scheduled')
    
    # 2. INFORMACIÓN DE PARTICIPANTES
    total_attendees = fields.Integer(
        string='Total Asistentes',
        readonly=True,
        default=0,
        help="Número total de asistentes a la reunión"
    )
    
    confirmed_attendees = fields.Integer(
        string='Asistentes Confirmados',
        readonly=True,
        default=0,
        help="Número de asistentes confirmados"
    )
    
    attendees_list = fields.Text(
        string='Lista de Asistentes',
        readonly=True,
        help="Lista de participantes de la reunión"
    )
    
    host_name = fields.Char(
        string='Anfitrión',
        readonly=True,
        help="Nombre del anfitrión de la reunión"
    )
    
    host_email = fields.Char(
        string='Email Anfitrión',
        readonly=True,
        help="Email del anfitrión"
    )
    
    # 3. INFORMACIÓN DE TIEMPO
    meeting_duration = fields.Integer(
        string='Duración Programada (min)',
        readonly=True,
        help="Duración planificada en minutos"
    )
    
    actual_duration = fields.Integer(
        string='Duración Real (min)',
        readonly=True,
        help="Duración real de la reunión"
    )
    
    meeting_start_time = fields.Datetime(
        string='Hora de Inicio',
        readonly=True,
        help="Hora programada de inicio"
    )
    
    meeting_end_time = fields.Datetime(
        string='Hora de Finalización',
        readonly=True,
        help="Hora programada de finalización"
    )
    
    actual_start_time = fields.Datetime(
        string='Inicio Real',
        readonly=True,
        help="Hora real de inicio"
    )
    
    actual_end_time = fields.Datetime(
        string='Finalización Real',
        readonly=True,
        help="Hora real de finalización"
    )
    
    # 4. INFORMACIÓN DE CONTROL Y SINCRONIZACIÓN
    zoom_created = fields.Boolean(
        string='Creada en Zoom',
        readonly=True,
        default=False,
        help="Indica si la reunión fue creada en Zoom"
    )
    
    zoom_synced = fields.Boolean(
        string='Sincronizada',
        readonly=True,
        default=False,
        help="Indica si los datos están sincronizados"
    )
    
    last_sync = fields.Datetime(
        string='Última Sincronización',
        readonly=True,
        help="Última vez que se sincronizaron los datos"
    )
    
    created_in_zoom = fields.Datetime(
        string='Creada en Zoom',
        readonly=True,
        help="Cuándo se creó la reunión en Zoom"
    )
    
    recording_available = fields.Boolean(
        string='Grabación Disponible',
        readonly=True,
        default=False,
        help="Indica si hay grabación de la reunión"
    )
    
    recording_url = fields.Char(
        string='URL de Grabación',
        readonly=True,
        help="Enlace a la grabación si está disponible"
    )

    # ========================================
    # MÉTODOS DE ACTUALIZACIÓN AUTOMÁTICA
    # ========================================
    
    @api.model
    def create(self, vals):
        """Crear ticket y asociar reunión Zoom automáticamente"""
        ticket = super(HelpdeskTicket, self).create(vals)
        
        # Crear reunión Zoom automáticamente si hay configuración
        try:
            ticket._create_zoom_meeting()
        except Exception as e:
            _logger.warning(f'Error creando reunión Zoom para ticket {ticket.id}: {e}')
        
        return ticket
    
    def _create_zoom_meeting(self):
        """Crear reunión Zoom asociada al ticket"""
        self.ensure_one()
        
        # Buscar configuración de Zoom
        zoom_config = self.env['zoom.config'].search([], limit=1)
        if not zoom_config:
            _logger.warning('No hay configuración de Zoom disponible')
            return
        
        # Preparar datos de la reunión
        meeting_data = {
            'name': f'Ticket #{self.id}: {self.name}',
            'start_time': fields.Datetime.now(),
            'duration': 60,  # Duración por defecto
            'description': f'Reunión de soporte para ticket: {self.name}\n\nDescripción: {self.description or "Sin descripción"}'
        }
        
        try:
            # Crear reunión en Zoom
            zoom_result = zoom_config.create_zoom_meeting(meeting_data)
            
            # Actualizar campos del ticket
            self.write({
                'zoom_meeting_id': zoom_result.get('id'),
                'zoom_join_url': zoom_result.get('join_url'),
                'zoom_start_url': zoom_result.get('start_url'),
                'zoom_created': True,
                'created_in_zoom': fields.Datetime.now(),
                'meeting_status': 'scheduled',
                'meeting_duration': meeting_data['duration'],
                'meeting_start_time': meeting_data['start_time'],
                'host_name': self.env.user.name,
                'host_email': self.env.user.email,
            })
            
            _logger.info(f'Reunión Zoom creada para ticket {self.id}: {zoom_result.get("id")}')
            
        except Exception as e:
            _logger.error(f'Error creando reunión Zoom: {e}')
            raise
    
    def _sync_zoom_data(self):
        """Sincronizar datos de Zoom con el ticket"""
        self.ensure_one()
        
        if not self.zoom_meeting_id:
            return
        
        # Buscar configuración de Zoom
        zoom_config = self.env['zoom.config'].search([], limit=1)
        if not zoom_config:
            return
        
        try:
            # Obtener información actualizada de la reunión desde Zoom API
            headers = {
                'Authorization': f'Bearer {zoom_config.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Obtener detalles de la reunión
            response = requests.get(
                f'{zoom_config.base_url}/meetings/{self.zoom_meeting_id}',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                meeting_data = response.json()
                
                # Actualizar campos con datos de Zoom
                update_vals = {
                    'last_sync': fields.Datetime.now(),
                    'zoom_synced': True,
                    'zoom_meeting_topic': meeting_data.get('topic', ''),
                    'meeting_duration': meeting_data.get('duration', 0),
                    'meeting_start_time': meeting_data.get('start_time'),
                    'host_name': meeting_data.get('host_email', ''),
                }
                
                # Actualizar estado según el estado de la reunión
                zoom_status = meeting_data.get('status', '')
                if zoom_status == 'waiting':
                    update_vals['meeting_status'] = 'scheduled'
                elif zoom_status == 'started':
                    update_vals['meeting_status'] = 'in_progress'
                elif zoom_status == 'finished':
                    update_vals['meeting_status'] = 'finished'
                elif zoom_status == 'cancelled':
                    update_vals['meeting_status'] = 'cancelled'
                
                # Obtener información de participantes
                participants_response = requests.get(
                    f'{zoom_config.base_url}/meetings/{self.zoom_meeting_id}/participants',
                    headers=headers,
                    timeout=10
                )
                
                if participants_response.status_code == 200:
                    participants_data = participants_response.json()
                    participants = participants_data.get('participants', [])
                    
                    update_vals.update({
                        'total_attendees': len(participants),
                        'confirmed_attendees': len([p for p in participants if p.get('status') == 'in_meeting']),
                        'attendees_list': '\n'.join([f"• {p.get('name', 'Sin nombre')} ({p.get('email', 'Sin email')})" for p in participants])
                    })
                
                # Verificar si hay grabación disponible
                recording_response = requests.get(
                    f'{zoom_config.base_url}/meetings/{self.zoom_meeting_id}/recordings',
                    headers=headers,
                    timeout=10
                )
                
                if recording_response.status_code == 200:
                    recording_data = recording_response.json()
                    recordings = recording_data.get('recording_files', [])
                    
                    if recordings:
                        update_vals.update({
                            'recording_available': True,
                            'recording_url': recordings[0].get('download_url', '')
                        })
                
                self.write(update_vals)
                _logger.info(f'Datos Zoom sincronizados para ticket {self.id}')
                
            else:
                _logger.warning(f'Error obteniendo datos de reunión {self.zoom_meeting_id}: {response.status_code}')
                
        except Exception as e:
            _logger.error(f'Error sincronizando datos Zoom: {e}')
    
    def action_sync_zoom_data(self):
        """Acción manual para sincronizar datos de Zoom"""
        self.ensure_one()
        self._sync_zoom_data()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sincronización Completada',
                'message': 'Los datos de Zoom han sido actualizados correctamente.',
                'type': 'success',
                'sticky': False,
            }
        }
    
    @api.model
    def _cron_sync_zoom_meetings(self):
        """Cron job para sincronizar todas las reuniones Zoom"""
        tickets = self.search([
            ('zoom_created', '=', True),
            ('meeting_status', 'in', ['scheduled', 'in_progress'])
        ])
        
        for ticket in tickets:
            try:
                ticket._sync_zoom_data()
            except Exception as e:
                _logger.error(f'Error sincronizando ticket {ticket.id}: {e}')
