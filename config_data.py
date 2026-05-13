md5_path = './md5.txt'

# uploaded files
upload_dir = "./uploaded_files"

# Chroma
collection_name = 'rag'
persist_directory = './chromadb'

# Splitter
chunk_size = 1000
chunk_overlap = 100
separators = ['\n\n', '\n', '.', '?', '!', '。', '？', '！', ' ', '']  # 空字符串用来兜底
max_split_char_number = 1000

# vector_store
similarity_threshold = 2  # 检索返回匹配的文档数量

# model
embedding_model_name = "text-embedding-v4"
chat_model_name = "qwen3-max"

session_config = {
    "configurable": {
        "session_id": "user_001"
    }
}

# File Parser
ocr_lang = 'ch_sim,en'
min_text_length_for_regular_pdf = 100