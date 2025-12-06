# 项目运行

## 🛠️ 环境准备

为了不污染您的本机环境，本项目推荐使用 **Anaconda** 或 **Miniconda** 来管理 Node.js 环境。

**前置要求：**

- 已安装 [Anaconda](https://www.anaconda.com/) 或 [Miniconda](https://docs.conda.io/en/latest/miniconda.html)。
- 终端 (Terminal / PowerShell / CMD)。

## 🚀 快速开始

请按照以下步骤操作，即可在 5 分钟内启动项目。

### 第一步：创建并激活环境

打开终端，创建一个独立的虚拟环境（包含 Node.js v20）：

```
# 1. 创建名为 lingxi_env 的环境，并安装 Node.js 20
conda create -n lingxi_env nodejs=20 -c conda-forge -y

# 2. 激活环境
conda activate lingxi_env
```

*(激活成功后，你的命令行前缀应显示 `(lingxi_env)`)*

### 第二步：安装项目依赖

进入项目根目录，运行安装命令：

```
# 进入项目目录 (如果你还没在目录下)
# cd path/to/yulian-lingxi

# 安装依赖
npm install
```

### 第三步：启动项目

依赖安装完成后，启动开发服务器：

```
npm run dev
```

终端将输出访问地址（通常为 `http://localhost:5173/`）。按住 `Ctrl` 并点击链接，即可在浏览器中查看项目。

## 📂 前端项目结构

```
src/
├── api/
│   ├── mockWorkflow.ts   # 核心 Mock 逻辑：模拟后端延时与数据生成
│   └── types.ts          # TS 类型定义 (Task, Step, Message 等)
├── components/
│   ├── chat/             # 左侧对话框组件
│   ├── workflow/         # 右侧工作流面板 (日志、图表、步骤条)
│   └── common/           # 公共组件 (如 Header)
├── layouts/
│   └── MainLayout.tsx    # 核心布局与状态管理容器
└── App.tsx               # 应用入口
```

## 🧹 环境清理 (项目结束后)

当你演示完毕，不再需要此项目时，可以按照以下步骤彻底删除环境，不留垃圾文件。

1. **停止运行**：在终端按 `Ctrl + C`。

2. **退出环境**：

   ```
   conda deactivate
   ```

3. **删除环境**：

   ```
   conda env remove -n lingxi_env
   ```

4. **删除文件**：手动删除项目文件夹即可。