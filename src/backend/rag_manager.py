# LangChain ve RAG işlemleri
import os 
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA


class RAGManager:
    def __init__(self, persist_directory):
        self.persist_directory = persist_directory
        self.embedding = OllamaEmbeddings(model="llama3")
        self.vector_store = None

        self.llm = OllamaLLM(model="llama3")
    
    """def load_and_index(self, pdf_path):
        if not os.path.exists(pdf_path):
            print(f"Hata: '{pdf_path}' dosyası bulunamadı.")
            return False
        
        print(f"İşleniyor: {pdf_path}")

        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        print(f"PDf yüklendi. Sayfa saysı: {len(docs)}")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 200
        )
        splits = text_splitter.split_documents(docs)
        print(f"Metin {len(splits)} parçaya bölündü.")

        print("Vektör veritabanı oluşturuluyor (Bu biraz sürebilir)...")

        self.vector_store = Chroma.from_documents(
            documents = splits,
            embedding = self.embedding,
            persist_directory = self.persist_directory
        )

        print("Tamamlandı! Veritabanı hazır.")
        return True
    """
    
    def ask_question(self, question):
        if self.vector_store is None:
            self.vector_store = Chroma(
                persist_directory = self.persist_directory,
                embedding_function = self.embedding
            )

        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

        qa_chain = RetrievalQA.from_chain_type(
            llm = self.llm,
            chain_type = "stuff",
            retriever = retriever
        )

        response = qa_chain.invoke({"query": question})
        return response['result']

if __name__ == "__main__":
    # Test kodları
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # doc klasörü src'nin bir üstünde olduğu için yolu ayarlıyoruz:
    #pdf_yolu = os.path.join(current_dir, "..", "..", "doc", "test.pdf")
    
    # Veritabanı klasörü de ana dizinde olsun
    db_yolu = os.path.join(current_dir, "..", "..", "chroma_db")
    
    manager = RAGManager(persist_directory=db_yolu)
    #manager.load_and_index(pdf_yolu)

    soru = "Bu dokümanın ana konusu nedir?"
    cevap = manager.ask_question(soru)
    
    print("--------------------------------------------------")
    print(f"SORU: {soru}")
    print(f"CEVAP: {cevap}")
    print("--------------------------------------------------")