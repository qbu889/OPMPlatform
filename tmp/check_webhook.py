import sys
sys.path.insert(0, '/project/wordToWord')
from app import create_app
from models import db

app = create_app('production')
app.app_context().push()

result = db.session.execute(db.text('SELECT id, description, LEFT(webhook_url, 30) as webhook_prefix FROM dingtalk_schedule_config WHERE id=1')).fetchone()
print(f'ID: {result[0]}')
print(f'Description: {result[1]}')
print(f'Webhook prefix: {result[2]}')
print(f'Starts with gAAAAA: {result[2].startswith("gAAAAA")}')
