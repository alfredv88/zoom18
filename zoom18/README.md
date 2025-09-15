# 🎥 Módulo Zoom18 - Integración con Zoom API

## 📋 **Descripción**

Módulo de integración de Zoom para Odoo 18 que permite crear, gestionar y sincronizar reuniones de Zoom directamente desde Odoo.

## ✨ **Funcionalidades Principales**

- ✅ **Crear reuniones programadas e instantáneas**
- ✅ **Sincronización automática** con Zoom API
- ✅ **Integración con calendario** de Odoo
- ✅ **Gestión de asistentes** y confirmaciones
- ✅ **Dashboard personalizado** con estadísticas
- ✅ **Integración con proyectos** y tareas
- ✅ **Notificaciones automáticas** por email
- ✅ **Control total del equipo** automático

## 🚀 **Instalación**

### **Requisitos**
- Odoo 18.0
- Python 3.8+
- Dependencias: `requests>=2.25.0`

### **Pasos de Instalación**

#### **Para Odoo.sh (Recomendado):**
1. **Subir el módulo** a tu repositorio Git
2. **Hacer commit y push** de los cambios
3. **Instalar desde Apps** en tu instancia Odoo.sh

#### **Para Odoo Local:**
1. **Copiar el módulo** a la carpeta de addons:
```bash
cp -r zoom18 /opt/odoo/custom-addons/
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Reiniciar Odoo** y actualizar la lista de módulos

4. **Instalar el módulo** desde Apps

## ⚙️ **Configuración**

### **1. Configurar Credenciales de Zoom**

1. Ir a **Zoom > Configuración**
2. Completar los campos requeridos:
   - **Client ID** (API Key)
   - **Client Secret** (API Secret)
   - **Account ID**
3. **Probar conexión** para verificar credenciales

### **2. Configurar Permisos**

El módulo crea automáticamente grupos de seguridad:
- **Usuario Zoom**: Acceso básico a reuniones
- **Administrador Zoom**: Acceso completo y configuración

## 📖 **Uso del Módulo**

### **Crear Reunión**

1. **Desde Dashboard**: Botón "Crear Reunión Rápida"
2. **Desde Proyectos**: Botón "Crear Reunión Zoom" en tareas
3. **Desde Calendario**: Crear evento y asociar con Zoom

### **Gestionar Asistentes**

1. **Agregar participantes** por email
2. **Enviar invitaciones** automáticamente
3. **Confirmar asistencia** desde email
4. **Registrar asistencia** real

### **Sincronización**

- **Automática**: Cada 10 minutos (configurable)
- **Manual**: Botón "Sincronizar" en dashboard
- **Webhooks**: Para actualizaciones en tiempo real

## 🎨 **Características del Diseño**

- **Dashboard híbrido** con tarjetas y tablas
- **Gráficos visuales** para estadísticas
- **Colores diferenciados** por estado de reunión
- **Botones contextuales** según el estado
- **Integración completa** con calendario nativo
- **Toast notifications** modernas
- **Tema responsive** para móviles
- **Icono personalizado** SVG con logo de Zoom y colores corporativos

## 🔧 **Configuración Avanzada**

### **Cron Jobs**

- **Recordatorios**: Cada hora
- **Sincronización**: Cada 10 minutos
- **Limpieza**: Diaria (opcional)

### **Templates de Email**

- **Invitaciones** personalizables
- **Recordatorios** automáticos
- **Confirmaciones** de asistencia
- **Notificaciones** al organizador

## 🐛 **Solución de Problemas**

### **Error de Conexión**
1. Verificar credenciales de Zoom
2. Comprobar conectividad a internet
3. Revisar logs de Odoo

### **Sincronización Fallida**
1. Verificar token de acceso
2. Comprobar permisos de API
3. Revisar configuración de webhooks

### **Emails No Enviados**
1. Configurar servidor SMTP en Odoo
2. Verificar templates de email
3. Comprobar permisos de usuario

## 📊 **Estadísticas y Reportes**

- **Total de reuniones** por período
- **Tasa de asistencia** promedio
- **Tiempo total** en reuniones
- **Participantes más activos**
- **Reuniones por proyecto**

## 🔒 **Seguridad**

- **Credenciales encriptadas** (recomendado)
- **Validación de webhooks** con firma
- **Permisos granulares** por usuario
- **Logs de auditoría** para operaciones

## 📱 **Compatibilidad**

- **Odoo 18.0** (requerido)
- **Navegadores modernos** (Chrome, Firefox, Safari, Edge)
- **Dispositivos móviles** (responsive design)
- **Zoom API v2** (compatible)

## 🤝 **Contribución**

Para contribuir al desarrollo:

1. **Fork** el repositorio
2. **Crear branch** para feature
3. **Commit** cambios con mensajes descriptivos
4. **Pull request** con descripción detallada

## 📄 **Licencia**

Este módulo está licenciado bajo **GNU LGPL v3**.

## 👨‍💻 **Autor**

**Alfred Vasquez**
- GitHub: [@alfredv88](https://github.com/alfredv88)
- Email: [contacto]

## 📞 **Soporte**

Para soporte técnico:
- **Issues**: Crear issue en GitHub
- **Documentación**: [Enlace a docs]
- **Comunidad**: [Enlace a foro]

---

**Versión**: 18.0.1.0.0  
**Última actualización**: $(date)  
**Estado**: En desarrollo activo
