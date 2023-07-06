import os
import time
import openai
import pymongo
import streamlit as st
from datetime import datetime
from streamlit_chat import message
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain import PromptTemplate
from dotenv import load_dotenv
from bson.objectid import ObjectId
load_dotenv()
st.markdown("<h1 style='text-align: center; color: White;'>TarihShy AI</h1>", unsafe_allow_html=True)

buff, col, buff2 = st.columns([1, 3, 1])

openai_key = st.secrets['OPENAI_API_KEY']
openai.api_key = openai_key
embedding = OpenAIEmbeddings()
template = """
I can answer questions about different periods, including the Stone Age, as well as events, individuals, battles, and governments that were significant in Central Asia. 
Remember, my purpose is to assist you in studying the history and provide reliable information.
Please ask your questions respectfully and concisely.
Question: {question}
"""

functions = [
    {
        "name": "get_bot_response_tulga",
        "description": "вызывайте эту функцию, когда запрос пользователья примерно как 'кто вы', 'когда вы', 'Сколько у вас', 'кто для вас', 'расскажите про себя' ",
        "parameters": {
            "type": "object",
            "properties": {
                "user_query": {
                    "type": "string",
                    "description": "warrior's name",
                },
            },
            "required": ["user_query"],
        },
    },
    {
        "name": "get_bot_response_tarih",
        "description": " вызывайте эту функцию, когда запрос пользователья примерно как 'Ханство' 'Каганат' 'Имя челововека' 'Сражение, битва' 'государство' 'история' 'событие' . ",
        "parameters": {
            "type": "object",
            "properties": {
                "user_query": {
                    "type": "string",
                    "description": "users input",
                },
            },
            "required": ["user_query"],
        },
    },
]

def mongo_client():
    url = st.secrets['MONGO_URL']
    client = pymongo.MongoClient(url)
    return client



client = mongo_client()
db = client.fastapi

shoqan = "Чокан Валиханов"
tole_bi = "Толе Би, вы не хан, вы би"
kazybek_bi = "Казыбек Би, вы не хан, вы би"
aiteke_bi = "Айтеке Би, вы не хан, вы би"
abylay_khan = "Абылай Хан, Хан Казахского Ханство"
kasym_khan = "Касым Хан, Хан Казахского Ханство"
zhangir_khan = "Жангир Хан, Хан Казахского Ханство"
haqnazar_khan = "Хак-Назар Хан, Хан Казахского Ханство"
esim_khan = "Есим Хан, Хан Казахского Ханство"

with st.sidebar:
    st.header('Tulgalar')
    tulga = st.selectbox('От кого вы хотите узнать об истории Казахстана', 
                        ('Касым Хан', 'Хак-Назар Хан', 'Есим Хан','Салкам Жангир Хан',
                        'Абылай Хан', 'Толе Би', 'Казыбек Би', 'Айтеке Би', 'Чокан Валиханов'), 
                        index=8
                        )
    st.markdown("<p style='text-align: left; color: White;'> Чат-бот TarihShy AI с искусственным интеллектом предназначен для изучения истории Казахстана от имени известных личностей.Вы можете задать вопросы об истории Казахстана и личные вопросы историческим личностям. На данный момент чат-бот находится на ранней стадии тестирования, cобрана небольшая база данных и написана значительная часть чат-бота. Я хотел бы получить от вас обратную связь для улучшения и подготовки к основному приложению. Если бот дал неверный ответ или произошли другие ошибки, пожалуйста, отправьте свой идентификатор conversqtion_id мне в Telegram. </p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: left; color: White;'>Telegram: https://t.me/z_altynbek_q</p>", unsafe_allow_html=True)

persist_directory_personality = "db_personality/shoqan"

if tulga == "Касым Хан":
    personality = kasym_khan
    persist_directory_personality = "db_personality/kasym_khan"
elif tulga == "Хак-Назар Хан":
    personality = haqnazar_khan
    persist_directory_personality = "db_personality/haqnazar_khan"
elif tulga == "Есим Хан":
    personality = esim_khan
    persist_directory_personality = "db_personality/esim_khan"
elif tulga == "Салкам Жангир Хан":
    personality = zhangir_khan
    persist_directory_personality = "db_personality/zhangir_khan"
elif tulga == "Абылай Хан":
    personality = abylay_khan
    persist_directory_personality = "db_personality/abylay_khan"
elif tulga == "Толе Би":
    personality = tole_bi
    persist_directory_personality = "db_personality/tole_bi"
elif tulga == "Казыбек Би":
    personality = kazybek_bi
    persist_directory_personality = "db_personality/kazybek_bi"
elif tulga == "Айтеке Би":
    personality = aiteke_bi
    persist_directory_personality = "db_personality/aiteke_bi"
elif tulga == "Чокан Валиханов":
    personality = shoqan
    persist_directory_personality = "db_personality/shoqan"

persist_directory_tarih = "db"


if len(openai_key):

    chat = ChatOpenAI(temperature=0.4, openai_api_key=openai_key, model_name="text-davinci-003")

    if 'all_messages' not in st.session_state:
        st.session_state.all_messages = []
    
    prompt = PromptTemplate(
        input_variables=["question"],
        template=template,
    )

    def get_completion(all_messages):
        messages = [
            {"role": all_messages[0]['role'], "content": all_messages[0]['content']},
        ]
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613", messages=messages, functions=functions, temperature=0.0, function_call='auto',)
        return response

    # Create a function to get bot response
    def get_bot_response_tulga(user_query):
        final_prompt = prompt.format(question=user_query)
        vectordb = Chroma(
            persist_directory=persist_directory_personality, embedding_function=embedding
        )   
        retriever = vectordb.as_retriever()
        docs = retriever.get_relevant_documents(personality + ", " + user_query)
        main_content = final_prompt + "\n\n"
        for doc in docs:
            main_content += doc.page_content + "\n\n"

        messages.append(HumanMessage(content=main_content))
        ai_response = chat(messages).content
        messages.pop()
        messages.append(HumanMessage(content=user_query))
        messages.append(AIMessage(content=ai_response))
        return ai_response

    def get_bot_response_tarih(user_query):
        final_prompt = prompt.format(question=user_query)
        vectordb = Chroma(
            persist_directory=persist_directory_personality, embedding_function=embedding
        )   
        print(1)
        retriever = vectordb.as_retriever()
        print(2)
        docs = retriever.get_relevant_documents(personality + ", " + user_query)
        main_content = final_prompt + "\n\n"
        print(3)
        for doc in docs:
            main_content += doc.page_content + "\n\n"
        print(4)
        # vectordb = Chroma(
        #     persist_directory=persist_directory_tarih, embedding_function=embedding
        # )
        # print(5)
        # retriever_tarih = vectordb.as_retriever()
        # print(6)
        # docs_tarih = retriever_tarih.get_relevant_documents("История коротко, " + user_query, )
        # print(7)
        # for doc in docs_tarih:
        #     main_content += doc.page_content + "\n\n"
        print(8)
        messages.append(HumanMessage(content=main_content))
        ai_response = chat(messages).content
        print(9)
        messages.pop()
        messages.append(HumanMessage(content=user_query))
        messages.append(AIMessage(content=ai_response))
        print(10)
        return ai_response

    # Create a function to display messages
    def display_messages(all_messages):
        print("display")
        for msg in all_messages:
            if msg['role'] == 'user':
                message(f"You ({msg['time']}): {msg['content']}", is_user=True, key=int(time.time_ns()))
            else:
                message(f"Tarihshy ({msg['time']}): {msg['content']}", key=int(time.time_ns()))
        print("Message")

    # Create a function to send messages
    def send_message(user_query, all_messages):
        if "conversation_id" not in st.session_state:
            conversation_data = db["tarih"].insert_one(
                {"history": st.session_state.all_messages}
            )
            conversation_id = conversation_data.inserted_id
            st.session_state.conversation_id = conversation_id
            print(conversation_id)
        else:
            db["tarih"].update_one(
                filter={"_id": ObjectId(st.session_state.conversation_id)},
                update={
                    "$set": {"history": st.session_state.all_messages},
                },
            )
        print("send")
        if user_query:
            all_messages.append({'role': 'user', 'time': datetime.now().strftime("%H:%M"), 'content': user_query})
            # response = get_completion(all_messages)
            # response_message = response["choices"][0]["message"]
            # print(response_message)
            # if response_message.get("function_call"):
            #     print("HELLO")
            #     fn_name = response_message["function_call"]["name"]
            #     print("LOH")
            #     if fn_name == "get_bot_response_tulga":
            #         print('fn_name_condition')
            #         bot_response = get_bot_response_tulga(user_query)
            #         print('fn_name_post_condition')
            #     elif fn_name == "get_bot_response_tarih":
            #         print('fn_name_elif')
            #         bot_response = get_bot_response_tarih(user_query)
            #         print('fn_name_post_elif')
            # else:
            #     print("Something is wrong")
            bot_response = get_bot_response_tarih(user_query)
            all_messages.append({'role': 'bot', 'time': datetime.now().strftime("%H:%M"), 'content': bot_response})
            print("mid")
            st.session_state.all_messages = all_messages
            print("aft")

            db["tarih"].update_one(
                filter={"_id": ObjectId(st.session_state.conversation_id)},
                update={
                    "$set": {"history": st.session_state.all_messages},
                },
            )
        print("message")     
        return st.session_state.conversation_id

    # Create a list to store messages

    messages = [
        SystemMessage(
            content=f'You are {personality}. Answer questions with respect and accuracy. Answer only the question, if possible, and provide a brief response. To question "Кто Вы"answer shortly. Always answer in the first person. The answer is in Russian. Additionally, You have to provide you with more structural information about Kazakh history and renowned figures.'
        )
    ]
    # Create input text box for user to send messages
    user_query = st.text_input("You: ", "", key="input")
    send_button = st.button("Send")


if len(user_query) and send_button:
    conversation_id = send_message(user_query, st.session_state.all_messages)
    display_messages(st.session_state.all_messages)
    with st.sidebar:
        st.markdown(f"<p style='text-align: left; color: White;'> Conversation ID : {conversation_id}</p>", unsafe_allow_html=True)
