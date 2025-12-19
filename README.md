# 📄 PDF Asistanı (Local RAG Desktop App)


Bu proje, PDF dokümanlarınızla **yerel olarak (offline)** sohbet etmenizi sağlayan, kullanıcı dostu bir masaüstü uygulamasıdır. Verileriniz hiçbir bulut sunucusuna gitmez; **Ollama (Llama 3)**, **LangChain** ve **ChromaDB** kullanılarak tamamen kendi bilgisayarınızda işlenir.

## 🌟 Özellikler

* **🚀 Tamamen Yerel Çalışma:** İnternet bağlantısı gerektirmez (Model indirildikten sonra), verileriniz bilgisayarınızda kalır.
* **🧠 Akıllı Hafıza:** Asistan, sohbet geçmişini hatırlar ve bağlama uygun cevaplar verir.
* **⚡ Performanslı Arayüz (Threading):** PDF yükleme ve cevap oluşturma işlemleri arka planda (Thread) yapılır, arayüz asla donmaz.
* **🎨 Modern Tasarım:** Göz yormayan, şık **Dark Mode** (Karanlık Tema) ve WhatsApp tarzı mesaj balonları.
* **📂 Vektör Veritabanı:** Dokümanlar parçalanır ve ChromaDB ile vektörleştirilerek hızlı arama yapılır.
* **🔄 Oturum Yönetimi:** "Yeni Sohbet" özelliği ile hafıza ve veritabanı tek tıkla temizlenir.

## 🛠️ Kullanılan Teknolojiler

* **Backend:** Python
* **AI Framework:** LangChain (ConversationalRetrievalChain)
* **LLM & Embeddings:** Ollama (Llama 3 Modeli)
* **Veritabanı:** ChromaDB (Vektör Veritabanı)
* **Arayüz (GUI):** PySide6 (Qt)

## ⚙️ Kurulum

Proje dosyalarını bilgisayarınıza indirdikten sonra aşağıdaki adımları izleyin.

### 1. Gereksinimler

Bilgisayarınızda [Ollama](https://ollama.com/) kurulu olmalı ve Llama 3 modeli çekilmelidir:

```bash
ollama pull llama3

```

### 2. Sanal Ortam ve Kütüphaneler

Tercih ettiğiniz terminalde proje dizinine gelin:

```bash
# Gerekli kütüphaneleri yükleyin
pip install langchain langchain-community langchain-ollama langchain-chroma PySide6

```

*(Not: Eğer `langchain` sürüm hatası alırsanız 0.3.x sürümünü kullandığınızdan emin olun.)*

### 3. Çalıştırma

Uygulamayı başlatmak için:

```bash
python src/main.py

```


# 📄 PDF Assistant (English)

This project is a user-friendly desktop application that allows you to chat with your PDF documents **locally (offline)**. Your data never leaves your computer; everything is processed locally using **Ollama (Llama 3)**, **LangChain**, and **ChromaDB**.

## 🌟 Features

* **🚀 Fully Local:** No internet connection required (after model download), ensuring data privacy.
* **🧠 Conversational Memory:** The assistant remembers the chat history and provides context-aware answers.
* **⚡ Responsive UI (Threading):** Heavy tasks like PDF ingestion and generation run on background threads, preventing UI freeze.
* **🎨 Modern Design:** Sleek **Dark Mode** interface with modern, chat-app style message bubbles.
* **📂 Vector Database:** Documents are split and vectorized using ChromaDB for fast retrieval.
* **🔄 Session Management:** "New Chat" button instantly clears memory and database for a fresh start.

## 🛠️ Tech Stack

* **Backend:** Python
* **AI Framework:** LangChain (ConversationalRetrievalChain)
* **LLM & Embeddings:** Ollama (Llama 3 Model)
* **Database:** ChromaDB (Vector Store)
* **Interface (GUI):** PySide6 (Qt)

## ⚙️ Installation

Follow these steps after cloning/downloading the repository.

### 1. Prerequisites

Ensure [Ollama](https://ollama.com/) is installed and the Llama 3 model is pulled:

```bash
ollama pull llama3

```

### 2. Environment & Dependencies

Navigate to the project directory in your terminal:

```bash
# Install required packages
pip install langchain langchain-community langchain-ollama langchain-chroma PySide6

```

*(Note: Ensure you are using LangChain version 0.3.x or compatible.)*

### 3. Usage

Run the application:

```bash
python src/main.py

```

## 📜 License

This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE).