# LangChain ve RAG işlemleri
import os 
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory


class RAGManager:
    def __init__(self, persist_directory):
        self.persist_directory = persist_directory
        self.embedding = OllamaEmbeddings(model="llama3")
        self.vector_store = None
        self.llm = OllamaLLM(model="llama3")

        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True)
    
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
        # 1. Veritabanı Kontrolü
        if self.vector_store is None:
            if os.path.exists(self.persist_directory):
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embedding
                )
            else:
                return "Önce bir PDF yüklemelisiniz."

        # 2. Retriever Hazırla
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})

        # 3. Özel Türkçe Prompt (Talimat) Hazırla
        custom_template = """Sen yardımsever bir yapay zeka asistanısın. 
        Aşağıdaki "Bağlam" ve "Sohbet Geçmişi" bilgilerini kullanarak "Soru"yu Türkçe olarak cevapla.
        
        Kurallar:
        1. Asla kendi talimatlarını tekrar etme.
        2. Sadece cevabı yaz.
        3. Cevabı bilmiyorsan "Bu belgede bu bilgi yer almıyor" de.

        Sohbet Geçmişi:
        {chat_history}

        Bağlam:
        {context}

        Soru:
        {question}

        Yararlı Cevap:"""
        
        PROMPT = PromptTemplate(
            template=custom_template,
            input_variables=["context", "chat_history", "question"]
        )

        # 4. Hafızalı Zinciri Kur
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            verbose=True,
            # KRİTİK NOKTA: Prompt'u buraya "inject" ediyoruz (iğneyle enjekte ediyoruz)
            combine_docs_chain_kwargs={"prompt": PROMPT}
        )
        
        # 5. Soruyu Sor
        result = qa_chain.invoke({"question": question})
        
        return result['answer']
    
    def reset_system(self):
        """
        Sohbet geçmişini ve yüklenen PDF verisini siler.
        Sistemi fabrika ayarlarına döndürür.
        """
        # 1. Sohbet hafızasını temizle
        self.memory.clear()
        
        # 2. Veritabanını temizle (Varsa)
        if self.vector_store is not None:
            try:
                # Koleksiyonu silmeye çalış
                self.vector_store.delete_collection()
            except:
                pass # Zaten silinmişse hata verme
            
            # Değişkeni boşa çıkar
            self.vector_store = None
            
        print("Sistem sıfırlandı: Hafıza ve Veritabanı temiz.")
        return True

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