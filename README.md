# 宿舍费用查询系统

## 项目介绍
该项目是一个基于Flask的宿舍费用查询系统，通过上传Excel文件，可以自动识别并解析宿舍费用信息，支持用户按姓名查询费用详情。系统基于向量数据库和大语言模型，自动适应各种格式的Excel文件。

## 部署指南

### Railway部署
1. 在Railway平台创建新项目
2. 导入GitHub仓库
3. 添加以下环境变量:
   - `DEEPSEEK_API_KEY`: DeepSeek API密钥
   - `CHROMA_PERSIST_DIRECTORY`: `./knowledge_base`
   - `PORT`: `5000`
4. 设置健康检查路径为: `/status`
5. 点击部署按钮

### 本地开发
1. 克隆仓库
2. 创建虚拟环境: `python -m venv venv`
3. 激活虚拟环境: 
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. 安装依赖: `pip install -r requirements.txt`
5. 创建`.env`文件并添加必要环境变量
6. 启动后端: `python backend.py`
7. 访问: `http://localhost:5000`

## 项目文件说明
- `backend.py`: 主要后端应用程序
- `index.html`: 用户查询页面
- `admin.html`: 管理员上传页面
- `requirements.txt`: 项目依赖
- `Procfile`: Railway部署配置
- `railway.toml`: Railway配置文件
- `runtime.txt`: Python版本配置

## 使用方法
1. 访问管理页面 `/admin.html` 上传Excel文件
2. 系统自动解析文件并提取信息
3. 访问主页查询界面输入姓名进行查询
4. 系统返回该学生的费用详情

## 功能特点

- **管理员功能**：上传Excel格式的宿舍费用数据，预览数据，管理系统状态
- **住宿人员功能**：通过姓名查询个人费用信息
- **智能识别**：自动识别Excel文件中的姓名和费用相关列
- **数据分析**：显示详细的计算过程和费用明细
- **安全保障**：管理员界面权限控制

## 系统架构

- **前端**：纯HTML/CSS/JavaScript实现，无需额外框架
- **后端**：Flask + LangChain + Chroma向量数据库
- **AI集成**：大语言模型API用于自然语言处理和费用计算

## 技术栈

- **后端**：Python, Flask, LangChain, Chroma向量数据库
- **前端**：HTML5, CSS3, JavaScript, Bootstrap 5
- **AI**：大语言模型API

## 注意事项

- 首次使用请修改默认的安全设置
- 需要配置相应的API密钥才能使用AI功能
- 向量数据库文件保存在本地，备份时需要一并备份相关文件夹
- 生产环境部署时建议启用HTTPS和其他安全措施

