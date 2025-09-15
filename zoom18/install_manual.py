#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

def install_module():
    """Verificar compatibilidad del módulo para Odoo.sh"""
    
    print("🔧 Verificando módulo zoom18 para Odoo.sh...")
    
    # Verificar que estamos en el directorio correcto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    manifest_path = os.path.join(current_dir, "__manifest__.py")
    
    if not os.path.exists(manifest_path):
        print("❌ Error: No se encontró __manifest__.py")
        print("   Asegúrate de ejecutar este script desde el directorio del módulo")
        return False
    
    print(f"✅ Módulo encontrado en: {current_dir}")
    
    # Comando de verificación (no instalación real)
    print("📋 Verificando estructura del módulo...")
    
    # Archivos críticos para Odoo.sh
    critical_files = [
        "__manifest__.py",
        "__init__.py",
        "requirements.txt",
        "models/__init__.py",
        "security/ir.model.access.csv"
    ]
    
    missing_files = []
    for file_path in critical_files:
        full_path = os.path.join(current_dir, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
            print(f"❌ {file_path}")
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Archivos críticos faltantes: {len(missing_files)}")
        print("   El módulo NO es compatible con Odoo.sh")
        return False
    else:
        print(f"\n✅ MÓDULO COMPATIBLE CON ODOO.SH")
        print("   Todos los archivos críticos están presentes")
        print("\n📋 INSTRUCCIONES PARA ODOO.SH:")
        print("   1. Subir el módulo a tu repositorio Git")
        print("   2. Hacer commit y push")
        print("   3. Instalar desde Apps en Odoo.sh")
        return True

if __name__ == "__main__":
    install_module()


