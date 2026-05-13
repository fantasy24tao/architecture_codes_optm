'''
知识库
'''

import os
import hashlib
import config_data as config
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime



def get_string_md5(input_str:str, encoding='utf-8'):
    """将传入的字符串转换为md5"""
    # 先将字符串转换为bytes字节数组
    str_bytes = input_str.encode(encoding=encoding)

    # 创建md5对象
    md5_obj = hashlib.md5()
    # 调用md5对象的update方法进行转换
    md5_obj.update(str_bytes)

    # 得到md5的十六进制字符串
    md5_hex = md5_obj.hexdigest()

    return md5_hex

def check_md5(md5_str:str):
    '''检查传入的md5字符串是否已经被处理过了'''
    # 如果文件还不存在，直接返回False
    if not os.path.exists(config.md5_path):
        # 创建一个空文件，然后关闭
        open(config.md5_path, 'w', encoding='utf-8').close()  # 以“w"模式打开，如果文件不存在，会自动创建
        return False
    # 文件存在的情况下。就打开文件读取，然后逐行比较
    for line in open(config.md5_path, 'r', encoding='utf-8').readlines():
        line = line.strip()  # 处理字符串前后的空格和回车，比较更精准
        if line == md5_str:
            return True
    return False

def save_md5(md5_str:str):
    """将传入的md5字符串，记录到文件内保存"""
    with open(config.md5_path, 'a', encoding='utf-8') as f:
        f.write(md5_str + '\n')




# 实现一个类，包含两个属性和一个方法
class KnowledgeBaseService():
    def __init__(self):
        # 如果文件夹不存在则创建，如果存在则跳过
        # 如果文件夹不存在则创建，如果存在则跳过
        os.makedirs(config.persist_directory, exist_ok=True)

        self.chroma = Chroma(
            collection_name=config.collection_name,  # 数据库的表名
            embedding_function=DashScopeEmbeddings(model=config.embedding_model_name),
            persist_directory=config.persist_directory  # 数据库本地存储文件夹
        )  # 记录向量存储的实例，也就是Chroma向量库对象
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,  # 分割后文本段的最大长度
            chunk_overlap=config.chunk_overlap,  # 连续文本段之间的字符重叠数量
            separators=config.separators,  # 自然段落的划分符号
            length_function=len  # 长度统计的依据，使用python自带的len函数
        )  # 文本分割器对象


    def upload_by_str(self, data, filename):
        """将当前传入的字符串进行向量化，存入向量库"""
        # 不要直接传入数据库，先去重
        # 先获得md5值
        md5_hex = get_string_md5(data)

        # 然后判断是否已经存在
        if check_md5(md5_hex):
            return {'status': 'skip', 'message': '[跳过]内容已存在数据库中', 'doc_ids': [], 'md5': md5_hex}

        # 判断文本长度是否超过阈值，超过再分割处理
        if len(data) > config.max_split_char_number:
            knowledge_trunks: list[str] = self.spliter.split_text(data)
        else:
            knowledge_trunks = [data]

        # 创建元数据
        metadata = {
            'source': filename,
            'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'operator': 'Zen'
        }

        # 处理数据，内容就加载到向量库中了，用add_text方法更简单
        # 保存返回的文档ID
        doc_ids = self.chroma.add_texts(
            knowledge_trunks,
            metadatas=[metadata for _ in knowledge_trunks],
        )

        # 保存已存储文件的md5
        save_md5(md5_hex)

        # 返回一个json文件，里面要包含文档的doc_ids和md5，用于后续删除
        return {'status': 'success', 'message': '[成功]内容已成功载入向量库', 'doc_ids': doc_ids, 'md5': md5_hex}

    def delete_by_doc_ids(self, doc_ids):
        """根据文档ID删除向量数据库中的内容"""
        try:
            self.chroma.delete(doc_ids)
            return True, '删除成功'
        except Exception as e:
            return False, str(e)

    def remove_md5(self, md5_str):
        """从md5.txt中删除指定的md5值"""
        try:
            if os.path.exists(config.md5_path):
                with open(config.md5_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                with open(config.md5_path, 'w', encoding='utf-8') as f:
                    for line in lines:
                        if line.strip() != md5_str:
                            f.write(line)
            return True, 'MD5记录已删除'
        except Exception as e:
            return False, str(e)

    def delete_by_filename(self, filename):
        """根据文件名删除向量数据库中的所有相关文档"""
        try:
            # 获取所有文档
            docs = self.chroma.get()
            
            ids_to_delete = []
            md5_to_delete = None
            
            # 查找所有匹配该文件名的文档
            for i, metadata in enumerate(docs.get('metadatas', [])):
                if metadata and metadata.get('source') == filename:
                    ids_to_delete.append(docs['ids'][i])
            
            if ids_to_delete:
                # 删除文档
                self.chroma.delete(ids_to_delete)
                return True, f'已删除 {len(ids_to_delete)} 个文档'
            else:
                return True, '未找到匹配的文档'
        except Exception as e:
            return False, str(e)


