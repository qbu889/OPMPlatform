# 启动脚本说明

## 📋 快速启动

### 方式一：只启动后端（推荐用于测试 API）

**macOS/Linux:**
```bash
chmod +x start_es_to_excel.sh
./start_es_to_excel.sh
```

**Windows:**
```cmd
start_es_to_excel.bat
```

访问地址：`http://localhost:5001/es-to-excel`

---

### 方式二：只启动前端（需要后端已运行）

**macOS/Linux:**
```bash
chmod +x start_frontend.sh
./start_frontend.sh
```

**Windows:**
```cmd
start_frontend.bat
```

访问地址：`http://localhost:5173`

---

### 方式三：同时启动前后端（推荐用于开发）

**macOS/Linux:**
```bash
chmod +x start_all.sh
./start_all.sh
```

**注意：** Windows 用户可以使用 WSL 或 Git Bash 运行此脚本。

访问地址：
- 前端页面：`http://localhost:5173`
- ES转Excel：`http://localhost:5173/es-to-excel`
- 后端 API：`http://localhost:5001`

---

## 🔧 手动启动

### 后端启动

```bash
# 1. 激活虚拟环境（如果有）
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows

# 2. 安装依赖
pip install -r requirements.txt
pip install pandas openpyxl

# 3. 创建必要目录
mkdir -p uploads/es_to_excel
mkdir -p downloads/es_to_excel

# 4. 启动应用
python app.py
```

### 前端启动

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

---

## 📊 服务管理

### 使用 tmux（推荐）

```bash
# 查看所有会话
tmux list-sessions

# 连接到会话
tmux attach -t opm-backend

# 在会话中切换窗口
# Ctrl+B, 然后按 0 (后端) 或 1 (前端)

# 停止所有服务
tmux kill-session -t opm-backend
```

### 使用后台模式

```bash
# 查看进程
ps aux | grep python
ps aux | grep npm

# 查看日志
tail -f logs/backend.log
tail -f logs/frontend.log

# 停止服务
kill <PID>
```

---

## ⚠️ 常见问题

### Q1: 端口被占用
```bash
# 查找占用端口的进程
lsof -i :5001  # 后端
lsof -i :5173  # 前端

# 杀死进程
kill -9 <PID>
```

### Q2: 依赖安装失败
```bash
# 升级 pip
pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt
```

### Q3: 前端依赖安装慢
```bash
# 使用国内镜像
npm install --registry=https://registry.npmmirror.com
```

### Q4: Python 版本不兼容
```bash
# 检查 Python 版本
python3 --version

# 需要使用 Python 3.13+
# 如果版本过低，请升级 Python
```

---

## 🚀 生产环境部署

### 使用 Gunicorn（后端）

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### 使用 Nginx（前端）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📝 环境变量配置

创建 `.env` 文件配置以下变量：

```env
# Flask 配置
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5001

# 日志配置
LOG_LEVEL=INFO
LOG_TO_CONSOLE=True
LOG_TO_FILE=True

# 数据库配置
DATABASE_URL=mysql://user:password@localhost/schedule

# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
```

---

## 🔗 相关链接

- 项目文档：`docs/EsToExcel/README.md`
- API 文档：启动后访问 `http://localhost:5001/api/es-to-excel`
- 前端页面：`http://localhost:5173/es-to-excel`
