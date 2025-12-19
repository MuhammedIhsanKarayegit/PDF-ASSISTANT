# LangChain ve RAG işlemleri
import os 
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


class RAGManager:
    def __init__(self, persist_directory):
        self.persist_directory = persist_directory
        self.embedding = OllamaEmbeddings(model="llama3")
        self.vector_store = None

        self.llm = OllamaLLM(model="llama3")
    
    def load_and_index(self, pdf_path):
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
    
    
    def ask_question(self, question):
        # 1. Veritabanı Yükle
        if self.vector_store is None:
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding
            )
        
        # 2. Retriever (Daha fazla parça getirsin diye k=5 yapalım)
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
        # 3. Özel Prompt Şablonu (Türkçe konuşmaya zorluyoruz)
        template = """
        Aşağıdaki bağlam bilgisini kullanarak soruyu cevapla.
        Eğer cevabı bağlam içinde bulamazsan, "Bilmiyorum" de, uydurma.
        Cevabı Türkçe ver ve mümkün olduğunca detaylı açıkla.

        Bağlam: {context}

        Soru: {question}
        
        Cevap:
        """
        
        PROMPT = PromptTemplate(
            template=template, 
            input_variables=["context", "question"]
        )

        # 4. Zinciri Prompt ile Kur
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT} # Prompt'u buraya ekledik
        )
        
        response = qa_chain.invoke({"query": question})
        return response['result']
    

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_yolu = os.path.join(current_dir, "..", "..", "chroma_db")
    
    manager = RAGManager(persist_directory=db_yolu)
    
    # --- BU KISIM AKTİF OLMALI ---
    pdf_yolu = os.path.join(current_dir, "..", "..", "doc", "test.pdf")
    manager.load_and_index(pdf_yolu) 
    # -----------------------------
    
    # Soru sorma
    soru = "Bu dokümanın ana konusu nedir? Cevabı Türkçe ver." # Türkçe istedik
    cevap = manager.ask_question(soru)
    
    print("-" * 30)
    print(f"CEVAP:\n{cevap}")
    print("-" * 30)