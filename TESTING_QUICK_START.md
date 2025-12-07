# 快速测试指南

本文档提供最快速的测试步骤，让你在 5 分钟内验证项目是否正常运行。

---

## 🚀 快速测试步骤

### 第一步：测试前端（使用 Mock 数据）

**1. 启动前端：**
```bash
cd frontend
npm install  # 如果还没安装依赖
npm run dev
```

**2. 访问前端：**
打开浏览器访问：http://localhost:5173

**3. 测试功能：**
- 在左侧输入框输入："查北京天气"
- 点击发送或按 Enter
- 观察右侧工作流面板：
  - ✅ "任务总览"标签页应显示 4 个步骤
  - ✅ "工具日志"标签页应显示工具调用记录
  - ✅ "执行结果"标签页应显示天气数据和折线图

**预期结果：** 前端界面正常，Mock 数据正常展示

---

### 第二步：测试后端 API

**1. 启动后端：**
```bash
cd backend

# 创建并激活虚拟环境（如果还没有）
conda create -n lingxi_backend python=3.9 -y
conda activate lingxi_backend
# 或使用 venv
python -m venv venv
venv\Scripts\activate  # Windows

# 安装依赖（如果还没安装）
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**2. 测试 API：**

**方式 A：使用浏览器**
- 访问：http://localhost:8000/docs
- 在 Swagger UI 中点击 "GET /health" → "Try it out" → "Execute"
- 应该返回：`{"status": "ok"}`

**方式 B：使用命令行**
```bash
# Windows PowerShell
curl http://localhost:8000/health

# 应该返回：{"status":"ok"}
```

**方式 C：使用测试脚本**
```bash
cd backend
python test_api.py
```

**预期结果：** 后端服务正常启动，API 接口正常响应

---

### 第三步：测试前后端联调（可选）

**当前状态：** 前端使用 Mock 数据，后端返回 Mock 数据。如果要测试真实对接，需要：

1. **修改前端代码**，将 Mock 服务替换为真实 API 调用
2. **实现后端 Agent 逻辑**，返回真实数据

**详细步骤请参考：** `docs/TESTING_GUIDE.md`

---

## ✅ 快速检查清单

### 前端测试
- [ ] 前端服务正常启动（无错误）
- [ ] 浏览器能访问 http://localhost:5173
- [ ] 界面正常显示（无白屏）
- [ ] 可以发送消息
- [ ] 工作流面板正常展示
- [ ] 图表正常渲染

### 后端测试
- [ ] 后端服务正常启动（无错误）
- [ ] 能访问 http://localhost:8000/docs
- [ ] `/health` 接口返回 `{"status": "ok"}`
- [ ] `/api/workflow/execute` 接口能正常响应

---

## 🐛 常见问题

### 问题 1：前端启动失败

**错误信息：** `npm ERR!` 或端口被占用

**解决方法：**
```bash
# 检查端口占用（Windows）
netstat -ano | findstr :5173

# 或使用其他端口
npm run dev -- --port 3000
```

### 问题 2：后端启动失败

**错误信息：** `ModuleNotFoundError` 或 `ImportError`

**解决方法：**
```bash
# 确保已安装所有依赖
pip install -r requirements.txt

# 检查 Python 版本
python --version  # 应该是 3.9+
```

### 问题 3：API 请求失败

**错误信息：** `Connection refused` 或 `CORS error`

**解决方法：**
1. 确保后端服务已启动
2. 检查 `backend/app/main.py` 中的 CORS 配置
3. 检查前端 `vite.config.ts` 中的代理配置

---

## 📚 详细测试文档

如需更详细的测试步骤，请参考：
- **完整测试指南**：`docs/TESTING_GUIDE.md`
- **API 接口规范**：`docs/API_SPEC.md`
- **开发指南**：`backend/README.md` 和 `frontend/README.md`

---

**提示：** 如果快速测试都通过，说明项目基础架构正常，可以开始功能开发了！


