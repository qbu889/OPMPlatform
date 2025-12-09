from datetime import datetime

from flask import render_template

import app


@app.route('/chat')
def chat_page():
    """提供聊天页面访问"""
    now = datetime.now()
    return render_template('chat.html', now=now)
