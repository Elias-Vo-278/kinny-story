"""Opt-in container cron, not a host crontab or Codex automation."""
import os
from pathlib import Path
import re
import shlex

schedule = os.getenv('CRON_SCHEDULE', '17 19 * * *')
if len(schedule.split()) != 5 or not re.fullmatch(r'[0-9*/,\- ]+', schedule):
    raise ValueError('CRON_SCHEDULE must contain five numeric cron fields')
keys = ['PGHOST', 'PGDATABASE', 'PGUSER', 'PGPASSWORD', 'IMPORT_USER_AGENT', 'REQUEST_DELAY', 'MAX_ITEMS']
env_file = Path('/run/importer.env')
env_file.write_text('\n'.join(f'export {key}={shlex.quote(os.environ[key])}' for key in keys if key in os.environ) + '\n')
env_file.chmod(0o600)
Path('/etc/cron.d/kinny-import').write_text('SHELL=/bin/sh\nPATH=/usr/local/bin:/usr/bin:/bin\n' +
    f'{schedule} root /app/run-import.sh >> /proc/1/fd/1 2>> /proc/1/fd/2\n')
print(f'Importer cron ready: {schedule} (UTC). No immediate import.', flush=True)
os.execvp('cron', ['cron', '-f'])
