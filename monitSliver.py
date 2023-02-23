import os
import time
import json
import codecs
import logging
import logging.handlers
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import telegram_send

# Configuración del logger
logger = logging.getLogger('monitorSliver')
logger.setLevel(logging.DEBUG)

# Configuración del handler para el logger
handler = logging.handlers.RotatingFileHandler(
    # Cambiar por la ruta en la que se guardará un log de lo registrado por el script.
    filename='/path/log/file',
    maxBytes=1024*1024,
    backupCount=3)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class MyHandler(FileSystemEventHandler):
    def __init__(self, audit_file):
        self.audit_file = audit_file
        self.filesize = os.path.getsize(self.audit_file)
        self.logger = logging.getLogger('monitorSliver.MyHandler')

    def on_modified(self, event):
        if event.src_path == self.audit_file:
            with codecs.open(self.audit_file, 'rb', encoding='utf-8', errors='ignore') as f:
                f.seek(self.filesize)
                while True:
                    line = f.readline()
                    if not line:
                        break
                    try:
                        record = line.replace('\\"', '')
                        record = record.replace('https://','')
                        record = record.strip('"')

                        msg_json = json.loads(record)

                        if msg_json['level'] == 'warning':
                            data = msg_json['msg']
                            data = re.sub(r'([{\[,])\s*([\w]+)\s*:', r'\1"\2":', data)
                            data = re.sub(r':\s*([\w\d\s\S]*?)([,}\]])', r':"\1"\2', data)
                            data = re.sub(r'"({)', r'\1', data)
                            data = re.sub(r'(\d+):(\d+)', r'\1 port \2', data)
                            data = re.sub(r':([a-zA-Z0-9])', r':"\1', data)

                            json_data = json.loads(data)

                            pc_name = json_data['Beacon']['Hostname']
                            username = json_data['Register']['Username']
                            implant = json_data['Beacon']['Name']
                            ip_port = json_data ['Beacon']['RemoteAddress']
                            filename = json_data ['Beacon']['Filename']
                            self.logger.debug(f'PC name: {pc_name}, Username: {username}, Implant: {implant}, IpPort: {ip_port}')
                            report = f"⚠️ Nueva Conexión ⚠️\n\n 🖥️  PC Name: {pc_name}\n👤 Username: {username}\n🔍 Implant: {implant}\n📡 IP:Port: {ip_port}\n🗒 Process: {filename}"
                            #print(report)
                            telegram_send.send(messages=[report])
                    except Exception as e:
                        self.logger.error(f'Error parsing JSON: {e}')
            self.filesize = os.path.getsize(self.audit_file)

if __name__ == "__main__":
    # Reemplazar por la ruta del archivo audit.json de sliver
    audit_file = '/root/.sliver/logs/audit.json'
    event_handler = MyHandler(audit_file)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(audit_file), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
