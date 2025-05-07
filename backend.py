from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAI
from langchain.chains import RetrievalQA
import pandas as pd
from openai import OpenAI as OpenAIClient
import os
import logging
import traceback
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()  # 从.env文件加载环境变量（如果存在）

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 获取 DeepSeek API Key从环境变量
deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
if not deepseek_api_key:
    logger.warning("DEEPSEEK_API_KEY 环境变量未设置，尝试使用默认值（不推荐用于生产环境）")
    deepseek_api_key = "sk-0e9b5e34997846e49a8047046f5e7e9a"  # 默认值，仅用于开发环境

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # 允许跨域请求

# 初始化嵌入模型
try:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    logger.info("嵌入模型初始化成功")
except Exception as e:
    logger.error(f"嵌入模型初始化失败: {str(e)}")
    traceback.print_exc()

# 初始化 Chroma 向量数据库（Railway 持久化存储）
persist_directory = os.environ.get('CHROMA_PERSIST_DIRECTORY', './knowledge_base')
try:
    vectorstore = Chroma(embedding_function=embeddings, persist_directory=persist_directory)
    logger.info(f"向量数据库初始化成功，存储路径: {persist_directory}")
    # 检查向量数据库中的文档数量
    collection = vectorstore._collection
    logger.info(f"向量数据库中已有 {collection.count()} 个文档")
except Exception as e:
    logger.error(f"向量数据库初始化失败: {str(e)}")
    traceback.print_exc()

# 初始化 DeepSeek API 客户端
try:
    deepseek_client = OpenAIClient(api_key=deepseek_api_key, base_url="https://api.deepseek.com")
    logger.info("DeepSeek API 客户端初始化成功")
except Exception as e:
    logger.error(f"DeepSeek API 客户端初始化失败: {str(e)}")
    traceback.print_exc()

# 初始化 LangChain 的 LLM（兼容 DeepSeek）
try:
    llm = OpenAI(
        openai_api_key=deepseek_api_key,
        openai_api_base="https://api.deepseek.com",  # API地址
        model_name="deepseek-chat"
    )
    logger.info("LangChain LLM 初始化成功")
except Exception as e:
    logger.error(f"LangChain LLM 初始化失败: {str(e)}")
    traceback.print_exc()

# 创建 RAG 链
try:
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3})  # 增加返回的相关文档数量
    )
    logger.info("RAG 链初始化成功")
except Exception as e:
    logger.error(f"RAG 链初始化失败: {str(e)}")
    traceback.print_exc()

# 存储对话历史（模拟多轮对话）
conversation_history = []

# 存储上传的文件预览信息
file_preview_data = {}

@app.route('/upload', methods=['POST'])
def upload_file():
    global file_preview_data
    if 'file' not in request.files:
        logger.warning("未上传文件")
        return jsonify({"error": "未上传文件"}), 400
    
    file = request.files['file']
    logger.info(f"收到文件上传请求: {file.filename}")
    
    try:
        # 解析 Excel 文件
        df = pd.read_excel(file)
        logger.info(f"成功解析 Excel 文件，包含 {len(df)} 行和 {len(df.columns)} 列")
        
        # 保存文件预览数据
        preview_rows = min(5, len(df))  # 最多预览5行
        columns = df.columns.tolist()
        rows = []
        for i in range(preview_rows):
            row_data = {}
            for col in columns:
                value = df.iloc[i][col]
                # 处理不可序列化的数据类型
                if pd.isna(value):
                    row_data[col] = None
                elif isinstance(value, (int, float, str, bool)):
                    row_data[col] = value
                else:
                    row_data[col] = str(value)
            rows.append(row_data)
        
        file_preview_data = {
            "columns": columns,
            "rows": rows,
            "total_rows": len(df)
        }
        
        # 生成文档说明
        file_description = f"文件包含以下列: {', '.join(df.columns.tolist())}"
        vectorstore.add_texts([file_description])
        logger.info("添加文件结构描述到向量数据库")
        
        # 处理每一行数据，不再假设特定的列名
        docs = []
        
        # 智能识别姓名和费用列
        name_cols = []
        fee_cols = []
        
        # 打印全部列名以便调试
        logger.info(f"文件列名: {df.columns.tolist()}")
        
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['姓名', '名字', '姓', '名', '人员']):
                name_cols.append(col)
                logger.info(f"识别到可能的姓名列: {col}")
            if any(keyword in col_lower for keyword in ['费', '款', '金', '电', '水', '租', '价', '钱', '元']):
                fee_cols.append(col)
                logger.info(f"识别到可能的费用列: {col}")
        
        # 处理每一行数据
        for idx, row in df.iterrows():
            # 将行转换为字符串，格式为"列名:值"
            row_data = []
            for col_name, value in row.items():
                # 跳过 NaN 值
                if pd.notna(value):
                    row_data.append(f"{col_name}: {value}")
            
            # 将所有非空值组合成文本
            if row_data:
                row_text = f"数据行 {idx+1}: " + ", ".join(row_data)
                docs.append(row_text)
                logger.debug(f"添加行数据: {row_text[:100]}...")
                
                # 提取姓名相关信息
                person_name = None
                for name_col in name_cols:
                    if pd.notna(row.get(name_col)):
                        person_name = row[name_col]
                        break
                
                # 如果找到姓名和费用信息，生成特定的费用说明
                if person_name:
                    fee_details = []
                    for fee_col in fee_cols:
                        if pd.notna(row.get(fee_col)):
                            fee_details.append(f"{fee_col}为{row[fee_col]}")
                    
                    if fee_details:
                        fee_text = f"{person_name}的费用信息: " + ", ".join(fee_details)
                        docs.append(fee_text)
                        logger.debug(f"添加费用信息: {fee_text}")
        
        # 更新 Chroma 向量数据库
        if docs:
            vectorstore.add_texts(docs)
            collection = vectorstore._collection
            logger.info(f"向量数据库更新成功，当前共有 {collection.count()} 个文档")
            return jsonify({
                "message": "文件上传成功", 
                "rows_processed": len(df),
                "preview": file_preview_data
            })
        else:
            logger.warning("文件未包含有效数据")
            return jsonify({"error": "文件未包含有效数据"}), 400
    except Exception as e:
        logger.error(f"文件处理失败: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"文件处理失败: {str(e)}"}), 500

@app.route('/preview', methods=['GET'])
def get_preview():
    """获取最近上传文件的预览数据"""
    if not file_preview_data:
        return jsonify({"error": "没有可用的文件预览"}), 404
    return jsonify(file_preview_data)

@app.route('/query', methods=['POST'])
def query():
    global conversation_history
    try:
        data = request.json
        user_query = data.get('query')  # 例如："张三的宿舍费用"
        if not user_query:
            logger.warning("查询内容为空")
            return jsonify({"error": "查询内容为空"}), 400

        logger.info(f"收到查询请求: {user_query}")
        
        # 测试向量数据库是否包含数据
        collection = vectorstore._collection
        doc_count = collection.count()
        logger.info(f"向量数据库中有 {doc_count} 个文档")
        
        if doc_count == 0:
            return jsonify({"error": "知识库为空，请先上传数据"}), 400
        
        # 初始化计算过程记录
        calculation_steps = []
        calculation_steps.append(f"1. 收到查询：'{user_query}'")
        
        # 改用直接检索替代RAG链
        try:
            # 直接使用向量搜索而不是RAG链
            calculation_steps.append(f"2. 开始向量检索，查找相关信息...")
            docs = vectorstore.similarity_search(user_query, k=5)
            if docs:
                rag_result = "\n".join([doc.page_content for doc in docs])
                logger.info(f"检索结果: {rag_result[:100]}...")
                calculation_steps.append(f"3. 找到 {len(docs)} 条相关信息")
                
                # 提取关键数据并计算
                fee_info = {}
                person_name = None
                calculation_steps.append(f"4. 分析检索到的信息...")
                
                for doc in docs:
                    content = doc.page_content
                    if "的费用信息" in content or "的相关费用信息" in content:
                        # 提取姓名
                        name_match = content.split("的费用信息")[0]
                        if not person_name:
                            person_name = name_match
                            calculation_steps.append(f"   - 识别到人员：{person_name}")
                        
                        # 提取费用信息
                        fee_parts = content.split(":", 1)[1].strip() if ":" in content else content
                        fee_items = [item.strip() for item in fee_parts.split(",")]
                        
                        for item in fee_items:
                            if "为" in item:
                                fee_type, fee_value = item.split("为", 1)
                                fee_type = fee_type.strip()
                                try:
                                    fee_value = float(fee_value.strip())
                                    fee_info[fee_type] = fee_value
                                    calculation_steps.append(f"   - 提取费用项：{fee_type} = {fee_value}")
                                except:
                                    # 非数值型费用信息
                                    fee_info[fee_type] = fee_value
                                    calculation_steps.append(f"   - 提取费用描述：{fee_type} = {fee_value}")
                
                # 添加计算总结
                if fee_info:
                    calculation_steps.append(f"5. 费用信息汇总:")
                    for fee_type, value in fee_info.items():
                        calculation_steps.append(f"   - {fee_type}: {value}")
                
                calculation_process = "\n".join(calculation_steps)
                logger.info(f"计算过程: {calculation_process}")
            else:
                rag_result = "未找到相关信息"
                calculation_steps.append(f"3. 未找到任何相关信息")
                calculation_process = "\n".join(calculation_steps)
                logger.warning("未找到相关信息")
        except Exception as e:
            logger.error(f"检索失败: {str(e)}")
            traceback.print_exc()
            calculation_steps.append(f"错误: 检索失败 - {str(e)}")
            calculation_process = "\n".join(calculation_steps)
            return jsonify({"error": f"检索失败: {str(e)}"}), 500
        
        # 构造 DeepSeek API 的 messages，包含对话历史
        messages = conversation_history + [
            {"role": "system", "content": "你是一个专业的宿舍费用查询助手，请根据提供的信息准确回答用户的问题。如果是费用查询，请明确列出具体金额。同时，如果可以，请展示计算过程，包括各项费用是如何相加得到总费用的。"},
            {"role": "user", "content": f"根据以下信息回答用户问题：\n{rag_result}\n\n用户问题：{user_query}"}
        ]
        
        try:
            # 调用 DeepSeek API
            calculation_steps.append(f"6. 调用AI助手生成回答...")
            response = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.3  # 降低温度以获得更确定性的回答
            )
            
            # 获取回答
            answer = response.choices[0].message.content
            logger.info(f"DeepSeek API 回答: {answer[:100]}...")
            calculation_steps.append(f"7. 生成回答完成")
            calculation_process = "\n".join(calculation_steps)
        except Exception as e:
            logger.error(f"DeepSeek API 调用失败: {str(e)}")
            traceback.print_exc()
            calculation_steps.append(f"错误: AI回答生成失败 - {str(e)}")
            calculation_process = "\n".join(calculation_steps)
            return jsonify({"error": f"AI 回答生成失败: {str(e)}"}), 500
        
        # 更新对话历史
        conversation_history.append({"role": "user", "content": user_query})
        conversation_history.append({"role": "assistant", "content": answer})
        
        # 限制历史长度（例如保留最近 10 轮对话）
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        
        return jsonify({
            "answer": answer,
            "source_documents": rag_result[:500] + "..." if len(rag_result) > 500 else rag_result,
            "calculation_process": calculation_process
        })
    except Exception as e:
        logger.error(f"查询处理失败: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"查询失败: {str(e)}"}), 500

@app.route('/clear', methods=['POST'])
def clear_history():
    """清除对话历史"""
    global conversation_history
    conversation_history = []
    return jsonify({"message": "对话历史已清除"})

@app.route('/status', methods=['GET'])
def get_status():
    """获取系统状态信息"""
    try:
        collection = vectorstore._collection
        doc_count = collection.count()
        return jsonify({
            "status": "运行中",
            "document_count": doc_count,
            "conversation_turns": len(conversation_history) // 2  # 每问一次，历史增加两个条目
        })
    except Exception as e:
        logger.error(f"获取状态失败: {str(e)}")
        return jsonify({"error": f"获取状态失败: {str(e)}"}), 500

# 添加根路由，提供静态文件服务
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"启动 Flask 服务器，监听端口 {port}")
    app.run(debug=False, host='0.0.0.0', port=port)

# Vercel Serverless函数处理程序
def handler(event, context):
    """Vercel Serverless函数处理程序"""
    return app