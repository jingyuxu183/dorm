# 宿舍费用管理系统

一个简单易用的宿舍费用管理和查询系统，支持管理员上传Excel数据文件和住宿人员通过姓名查询费用信息。

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

## 安装指南

### 后端安装

1. 克隆代码库
```bash
git clone [仓库地址]
cd [项目目录]
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/MacOS
source venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入您的API密钥
```

5. 启动后端服务
```bash
python backend.py
```

### 前端部署

前端为纯静态文件，可以通过以下方式部署：

1. 使用Python内置HTTP服务器（开发环境）
```bash
python -m http.server [端口号]
```

2. 或使用任何静态文件服务器（生产环境）
```bash
# 例如使用Nginx或Apache配置静态文件服务
```

## 使用指南

### 管理员操作流程

1. 访问登录页面，选择"管理员入口"
2. 完成身份验证
3. 上传包含宿舍费用信息的Excel文件
4. 预览并确认数据正确
5. 检查系统状态，确保数据已更新

### 住宿人员查询流程

1. 访问登录页面，选择"住宿人员入口"
2. 在查询界面输入姓名
3. 查看费用信息和计算过程

## 技术栈

- **后端**：Python, Flask, LangChain, Chroma向量数据库
- **前端**：HTML5, CSS3, JavaScript, Bootstrap 5
- **AI**：大语言模型API

## 注意事项

- 首次使用请修改默认的安全设置
- 需要配置相应的API密钥才能使用AI功能
- 向量数据库文件保存在本地，备份时需要一并备份相关文件夹
- 生产环境部署时建议启用HTTPS和其他安全措施

