from retriever.vector_store import load_vector_store
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

# 建立查詢引擎

def get_query_engine():
    vector_store = load_vector_store()
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    llm = ChatOpenAI(temperature=0.3)
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    return chain

# 查詢範例：
# engine = get_query_engine()
# result = engine.run("什麼是 ISO 14064？")
# print(result)
