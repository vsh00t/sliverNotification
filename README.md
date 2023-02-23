# sliverNotification
Este script de Python es un monitor que verifica un archivo de registro de eventos de Sliver C2 y envía alertas de Telegram en tiempo real sobre nuevas conexiones.  

El script utiliza el módulo watchdog para monitorear cambios en el archivo de registro (audit.json) y el módulo logging para generar un archivo de registro separado. Cuando detecta una nueva conexión en el archivo de registro, extrae la información relevante (como el nombre del equipo, el nombre de usuario, la dirección IP y el puerto) y la envía como mensaje de alerta de Telegram utilizando el módulo telegram-send.  

Para utilizar este script, es necesario reemplazar la ruta del archivo de registro de eventos de Sliver en la variable audit_file. Además, se debe proporcionar una ruta para el archivo de registro de este script en la variable filename en la sección de configuración del logger.
