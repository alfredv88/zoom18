#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

def check_module():
    """Verificar que el módulo esté correctamente estructurado para Odoo.sh"""
    
    # Ruta relativa al directorio actual (compatible con Odoo.sh)
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Archivos requeridos completos para Odoo.sh
    required_files = [
        "__manifest__.py",
        "__init__.py",
        "requirements.txt",
        "models/__init__.py",
        "models/zoom_meeting.py",
        "models/zoom_config.py",
        "models/zoom_dashboard.py",
        "models/zoom_meeting_attendee.py",
        "models/calendar_event.py",
        "models/project_task.py",
        "views/zoom_meeting_views.xml",
        "views/zoom_config_views.xml",
        "views/zoom_dashboard_views.xml",
        "views/zoom_meeting_attendee_views.xml",
        "views/calendar_event_views.xml",
        "security/ir.model.access.csv",
        "data/zoom_data.xml",
        "data/email_templates.xml",
        "data/cron_jobs.xml",
        "static/src/assets.xml",
        "tests/__init__.py",
        "tests/test_zoom_config.py",
        "tests/test_zoom_meeting.py",
        "tests/test_zoom_meeting_attendee.py",
        "tests/test_zoom_dashboard.py",
        "tests/test_integration.py"
    ]
    
    print("🔍 Verificando estructura del módulo para Odoo.sh...")
    print(f"📁 Directorio base: {base_path}")
    print("=" * 60)
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
            print(f"❌ {file_path}")
        else:
            existing_files.append(file_path)
            print(f"✅ {file_path}")
    
    print("=" * 60)
    print(f"📊 RESUMEN:")
    print(f"   ✅ Archivos encontrados: {len(existing_files)}")
    print(f"   ❌ Archivos faltantes: {len(missing_files)}")
    
    if missing_files:
        print(f"\n❌ ARCHIVOS FALTANTES:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print(f"\n⚠️  El módulo NO está completo para Odoo.sh")
        return False
    else:
        print(f"\n✅ MÓDULO COMPLETO PARA ODOO.SH")
        print(f"   Todos los {len(required_files)} archivos requeridos están presentes")
        return True

if __name__ == "__main__":
    check_module()


