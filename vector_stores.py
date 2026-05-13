import config_data as config
from langchain_chroma import Chroma

class VectorStoreService:
    def __init__(self, embedding):
        """
        嵌入模型的传入
        """
        self.embedding = embedding

        self.vector_store = Chroma(
            collection_name = config.collection_name,
            embedding_function = self.embedding,
            persist_directory = config.persist_directory
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={'k': config.similarity_threshold})




