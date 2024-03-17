import streamlit as st
from doc_loading import get_article_text, read_pdf_text
from utils import get_topics
from llm_functions import generate_qa_pairs, evaluate_answer, get_conversational_chain, get_topics_from_chunk

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()


# Setting up basics
st.set_page_config(page_title="LLM UC")
st.header("Let's check what you know")

# Greeting the user
st.write("Welcome!!")

st.session_state
# Sidebar with selectbox

if "option" not in st.session_state:
    option = st.selectbox("How are you going to input your document?",
             ("Upload PDF", "Blog link", "YouTube Link", "Paste copied article"))
# Conditionally show components based on user's choice
file_name = ""
main_text = ""

if option == "Upload PDF":
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"], key="uploading_pdf")
    if uploaded_file is not None:
        # Process the uploaded file
        st.write("PDF uploaded successfully!, we will read only first 5 pages")
        main_text = read_pdf_text(uploaded_file)
    
elif option == "Paste copied article":
    main_text = st.text_area("Paste your article here", key="article_key")
    if st.button('Submit'):
        # Process the pasted text
        st.write("Text submitted successfully!")
        
else:
    link_input = st.text_input("Paste your blog/youtube link here.", key='link_key')
    if st.button('Submit'):
        # Process the link
        st.write("link submitted")
        if option == "YouTube Link":
            st.write("This functionality in under construction.")
            main_text = ""
        else:    
            # lets try now
            article_text = get_article_text(link_input)
            if article_text:
                main_text = ""
                st.write("This functionality in under construction.")
            else:
                st.write("Unable to fetch text from url. Can you please check the link?")
            

# Show a warning if the user hasn't selected an option or if the uploaded file is not a PDF

if option == "Upload PDF":
    if uploaded_file is not None and uploaded_file.type != "application/pdf":
        st.error("Please choose a PDF file only.")

if "total_text" not in st.session_state:
    st.session_state['total_text'] = main_text

if len(main_text) > 0:
    # creating chunks of the given article
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False
    )
    texts = text_splitter.create_documents([main_text])

    # building vector database

    embeddings = OpenAIEmbeddings()
    # store in vector db
    db = FAISS.from_documents(texts, embeddings)

    hash_name = f"{option.replace(' ', '-')}"
    db.save_local(f'faiss_{hash_name}_index')

    # Create a toggle button
    toggle_button_state = st.checkbox("check this, if i should quiz you")
    
    # Display a message based on the toggle button state
    if toggle_button_state:
        # make the quiz
        st.write("Quiz incoming...")
        
        # give selection of toughness
        toughness_selection = None
        while "toughness_selection" not in st.session_state:
            toughness_selection = st.selectbox("Select the question toughness",
                                    ("Easy", "Moderate", "Tough"))
            st.session_state['toughness_selection'] = toughness_selection
        
        top_topics = None
        if "top_topics" not in st.session_state:
            topics_chain = get_topics_from_chunk()
            top_topics = get_topics(texts[:10], topics_chain)
            top_topics.append("Any")
            st.session_state['top_topics'] = top_topics
            
        topic_selection = None
        if "topic_selection" not in st.session_state:
            top_topics = st.session_state['top_topics']
            topic_selection = st.selectbox("Select the topic i should quiz from!!",
                                    tuple(top_topics), key="topic_selection")
            st.session_state['topics_selection'] = topic_selection
            toughness_selection = st.session_state['toughness_selection']
        
        

        if "response" not in st.session_state:
            ques_chain = generate_qa_pairs()
            topic_selection = st.session_state['topic_selection']
            toughness_selection = st.session_state['toughness_selection']
            # st.write(f"here we go, a {toughness_selection} level question from {topic_selection} topic.")
            docs_for_questions = db.similarity_search(topic_selection, k=5)
            response = ques_chain.invoke({"context": docs_for_questions,
                    "topic": topic_selection,
                    'toughness': toughness_selection})
            st.session_state['response'] = response[0]
        
        if "scoring" not in st.session_state:
            eval_chain = evaluate_answer()
            response = st.session_state['response']
            st.write(f"\n Question: {response['question']}")
            user_answer = st.text_input(f"Answer here: ", key="my_ans")
            
            if st.button(f"Evaluate"):
                score = eval_chain({"context": response['answer'],
                                "answer": user_answer})
                st.write(f"You scored {score['score']}/10")
                if int(score['score'])<6:
                    st.write(f"The correct answer would be: {response['answer']}")
                else:
                    st.write("Good Job!!!")
        
                st.session_state['scoring'] = score['score']
            elif st.button("Don't know"):
                st.write(f"The correct answer would be: {response['answer']}")
            
    else:
        st.write("What's your question?")
        # let the user ask question.

        
        if "input_question" not in st.session_state or st.session_state['input_question'] == "":
            input_question = st.text_input("Here, input your question and click `Answer this`", key="Question")
            st.session_state['input_question'] = input_question
        answer_button = st.button('Answer this', key='my_question')
        
        if answer_button:
            input_question = st.session_state['input_question']
            docs = db.similarity_search(input_question, k=5)
            chain = get_conversational_chain()
            response = chain({"input_documents" : docs, 
                            "question": input_question,
                                })
            st.write(response['output_text']) 
            del st.session_state['input_question']

