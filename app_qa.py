import streamlit as st
import time
import os
from rag import RagService
import config_data as config

from knowledge_base import KnowledgeBaseService
from file_parser import FileParser

os.makedirs(config.upload_dir, exist_ok=True)


def load_existing_files():
    """加载已上传的文件信息"""
    if "uploaded_files" in st.session_state and st.session_state["uploaded_files"]:
        return  # 已加载过，跳过
    
    uploaded_files = []
    
    if os.path.exists(config.upload_dir):
        for filename in os.listdir(config.upload_dir):
            file_path = os.path.join(config.upload_dir, filename)
            if os.path.isfile(file_path):
                try:
                    # 获取文件信息
                    file_size = os.path.getsize(file_path) / 1024
                    
                    # 读取文件内容计算md5
                    with open(file_path, 'rb') as f:
                        file_bytes = f.read()
                    
                    from knowledge_base import get_string_md5, check_md5
                    md5_hex = get_string_md5(file_bytes.decode('utf-8', errors='ignore'))
                    
                    # 检查是否在数据库中
                    if check_md5(md5_hex):
                        uploaded_files.append({
                            "name": filename,
                            "type": "application/octet-stream",
                            "size": file_size,
                            "save_path": file_path,
                            "doc_ids": [],  # 暂时为空，删除时会重新获取
                            "md5": md5_hex
                        })
                except Exception as e:
                    print(f"加载文件 {filename} 失败: {str(e)}")
    
    st.session_state["uploaded_files"] = uploaded_files


# 标题
st.title("建筑设计规范查询工具")
st.divider()          # 分隔符

# 增加文件上传部分
uploader_file = st.file_uploader(
    "请上传规范文件",
    type=['txt','pdf','doc','docx'],
    accept_multiple_files=False,   # False表示仅接受一个文件的上传
)

st.divider()          # 分隔符


# session_state就是一个字典，直接把KnowledgeBaseService示例对象存起来
if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()


if "rag" not in st.session_state:
    st.session_state["rag"] = RagService()

# 文件解析器对象
if "parser" not in st.session_state:
    st.session_state["parser"] = FileParser(ocr_lang=config.ocr_lang)

# 初始化文件处理状态
if "file_processed" not in st.session_state:
    st.session_state["file_processed"] = {}

# 初始化已上传文件列表
if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = []

# 加载已上传的文件信息
load_existing_files()


# 有文件上传时，执行以下代码
if uploader_file is not None:
    # 检查文件是否已处理
    file_key = f"{uploader_file.name}_{uploader_file.size}"
    if file_key in st.session_state["file_processed"]:        
        pass
        # st.info("该文件已处理过，无需重复上传")
    else:    
        # 提取文件的信息
        file_name = uploader_file.name
        file_type = uploader_file.type
        file_size = uploader_file.size / 1024  # KB

        # 文件处理
        with st.spinner("正在解析文件并载入知识库中......"):  # spinner内的代码在执行时，会有一个转圈动画
            try:
                # 将上传的文件转换为字节数据
                file_bytes = uploader_file.read()
                
                # 保存原始文件到本地 uploaded_files 目录
                save_path = os.path.join(config.upload_dir, file_name)
                with open(save_path, "wb") as f:
                    f.write(file_bytes)
                st.write(f"原始文件已保存: {save_path}")
                
                # 解析文件内容
                text, parse_mode = st.session_state["parser"].parse_file(file_bytes, file_name)
                st.write(f"解析模式：{parse_mode}")
                result = st.session_state["service"].upload_by_str(text, file_name)
                st.write(result['message'])

                # 标记该文件已处理
                st.session_state["file_processed"][file_key] = True
                
                # 保存文件信息到列表（避免重复添加）
                if not any(f["name"] == file_name and f["size"] == file_size for f in st.session_state["uploaded_files"]):
                    st.session_state["uploaded_files"].append({
                        "name": file_name,
                        "type": file_type,
                        "size": file_size,
                        "save_path": save_path,
                        "doc_ids": result['doc_ids'],
                        "md5": result['md5']
                    })

            except Exception as e:
                st.error(f"处理失败：{str(e)}")

# 侧边栏显示已上传文件列表
with st.sidebar:
    st.header("已上传规范文档")
    if st.session_state["uploaded_files"]:
        for idx, file_info in enumerate(st.session_state["uploaded_files"], 1):
            st.subheader(f"{idx}. {file_info['name']}")
            st.write(f"格式：{file_info['type']} | 大小：{file_info['size']:.2f}KB")
            st.write(f"保存路径：{file_info['save_path']}")
            # 打开文件按钮
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"打开文件", key=f"open_file_{idx}"):
                    try:
                        os.startfile(file_info['save_path'])
                    except Exception as e:
                        st.error(f"打开文件失败：{str(e)}")
            with col2:
                if st.button(f"删除", key=f"delete_file_{idx}", type="secondary"):
                    with st.spinner("正在删除文件..."):
                        try:
                            # 1. 从向量数据库删除（根据文件名查询并删除）
                            success, msg = st.session_state["service"].delete_by_filename(file_info['name'])
                            if not success:
                                raise Exception(f"向量数据库删除失败: {msg}")
                            st.write(msg)
                            
                            # 2. 删除本地文件
                            if os.path.exists(file_info['save_path']):
                                os.remove(file_info['save_path'])
                            
                            # 3. 从md5.txt删除
                            success, msg = st.session_state["service"].remove_md5(file_info['md5'])
                            if not success:
                                raise Exception(f"MD5删除失败: {msg}")
                            
                            # 4. 从session_state中移除
                            st.session_state["uploaded_files"].pop(idx - 1)
                            
                            # 5. 更新file_processed状态
                            file_key = f"{file_info['name']}_{file_info['size']}"
                            if file_key in st.session_state["file_processed"]:
                                del st.session_state["file_processed"][file_key]
                            
                            st.success(f"已删除文件: {file_info['name']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"删除失败：{str(e)}")
            st.divider()
    else:
        st.write("暂无上传文件")


if "message" not in st.session_state:
    st.session_state["message"] = [ {"role": "assistant", "content": "你好，有什么可以帮助你？" } ]

# 通过for循环把历史消息都显示出来，包括用户和和助手
for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])


# 在页面最下方提供用户输入栏
prompt = st.chat_input()

# 有用户输入时，执行以下代码
if prompt:

    # 在页面下方显示用户输入
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    with st.spinner("AI思考中......"):
        # 通过session_state获取rag服务对象，获取chain，然后调用invoke方法，获得模型回答
        res_stream = st.session_state["rag"].chain.stream({"input": prompt}, config.session_config)
        # yield
        ai_res_list = []
        def capture(generator, cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                yield chunk

        st.chat_message("assistant").write_stream(capture(res_stream, ai_res_list))
        st.session_state["message"].append({"role": "assistant", "content": "".join(ai_res_list)})
