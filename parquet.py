import os
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader

os.environ["OPENAI_API_KEY"] = "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"

loader = TextLoader('/home/legioner/projects/Chat-Wiki/data/personality.txt')


documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

len(texts)
texts[3]

# Embed and store the texts
# Supplying a persist_directory will store the embeddings on disk
persist_directory = '/home/legioner/projects/Chat-Wiki/db_personality/tulgalar'

## here we are using OpenAI embeddings but in future we will swap out to local embeddings
embedding = OpenAIEmbeddings()

vectordb = Chroma.from_documents(documents=texts, 
                                 embedding=embedding,
                                 persist_directory=persist_directory)

# persiste the db to disk
vectordb.persist()
vectordb = None

# Now we can load the persisted database from disk, and use it as normal. 
vectordb = Chroma(persist_directory=persist_directory, 
                  embedding_function=embedding)

print("Finish")