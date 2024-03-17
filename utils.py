from collections import Counter
import streamlit as st

def get_topics(texts, chain):
    all_topics = []
    for t in texts:
        response = chain(t.page_content)
        response = response['top_topics'].split(", ")
        all_topics.extend([x.strip() for x in response])
    most_common_words = Counter([x.lower() for  x in all_topics]).most_common(3)
    most_common_words_without_count = [word for word, _ in most_common_words]
    return most_common_words_without_count



# def question_answering(response, eval_chain):
#     for i in range(len(response)):
#         st.write(f"\n Question {i+1}: {response[i]['question']}")
#         user_answer = st.text_input(f"Answer {i+1} here: ")
#         if st.button(f"Evaluate {i+1}"):
#             score = eval_chain({"context": response[i]['answer'],
#                             "answer": user_answer})
#             st.write(f"You scored {score['score']}/10")
#             if int(score['score'])<6:
#                 st.write(f"The correct answer would be: {response[i]['answer']}")
#             else:
#                 st.write("Good Job!!!")

