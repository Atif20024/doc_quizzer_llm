from langchain.chains.question_answering import load_qa_chain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
import streamlit as st


def get_conversational_chain():
    prompt_template = """Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is present in the document
    feel free to say, "try ansking something else, this information is not available", don't provide the wrong answer no matter what is present in the question\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """
    model = ChatOpenAI(temperature=0.7)
    prompt = PromptTemplate(template=prompt_template, 
                            input_variables=["context", "Question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt = prompt)

    return chain


def get_topics_from_chunk():
    prompt_template = """
            I will give a context, and you have to tell me what top 3 topics the text might belong to.
            if you unable to find any, you can respond with <no_topic>, but dont output any rubbish topics.
            do not write anything other than the topics names. also, give the topics in a comma separted way.\n\n
            context:\n{context}\n
            Answer:
            """
    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)
    prompt = PromptTemplate(template=prompt_template, 
                            input_variables=['context'])
    response = LLMChain(llm=model, prompt=prompt, output_key='top_topics')
    return response
    



def generate_qa_pairs():
    prompt_template = """
        Given a context, i want you to generate 1 question of toughness level: {toughness} out of these three levels
        Easy, Moderate and Tough. The question must belong to topic: {topic}. 
        Make sure the answer to the question you generate belong to the context provided.
        give me the list of question answer pair in json format, with each element of list containing a dict with keys "question" and "answer".\n\n
        context:\n{context}\n
        """
    model = ChatOpenAI(model='gpt-3.5-turbo', temperature=1)
    parser = JsonOutputParser()
    prompt = PromptTemplate(template = prompt_template,
                            input_variables=['context', 'topic', 'toughness'],
                            partial_variables={'format_instructions': parser.get_format_instructions()})

    chain = prompt | model | parser

    return chain


def evaluate_answer():
    prompt_template = """
        You are good teacher, suppose there are two texts, 1. real_answer  and 2. user_answer. i want you to score the user_answer based on real_answer
        you have to give integer score. max score can be 10, and min score can be 0. Be lenient in scoring,
        but if someone give rubbish answer/out of context answer, feel free to give 0 score. 
        give final output as an integer value only. we dont want an explanation from you.

        real_answer:\n{context}\n
        user_answer:\n{answer}\n

        score:
    """
    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
    prompt = PromptTemplate(template=prompt_template, 
                            input_variables=['context', 'answer'])
    response = LLMChain(llm=model, prompt=prompt, output_key = "score")
    return response