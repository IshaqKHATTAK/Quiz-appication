from langchain.prompts.prompt import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.llms import Replicate
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import CTransformers
import os
from ctransformers import AutoModelForCausalLM
import transformers

def set_custom_prompt(u_input, field):
    #create a prompt with the three perameters mentioned there as argument
    prompt = PromptTemplate(template=custom_prompt_template, input_variables=['context'], partial_variables={'field' : field, 'response': u_input})
    return prompt

def load_llm():
    #load model using model Replicate class of langchain
    llm = CTransformers(model="../../models/llama-2-7b-chat.ggmlv3.q8_0.bin", model_type='llama', config={'max_new_tokens': 600,
                              'temperature': 0.5,
                              'context_length': 4096})
    return llm

def retrieval_qa_chain(llm, prompt, db):
    #facilitates a retrieval-based question answering approach
    qa_chain = RetrievalQA.from_chain_type(
        llm = llm,
        chain_type="stuff", #stuff-It takes a list of documents, inserts them all into a prompt and passes that prompt to an LLM.
        retriever = db.as_retriever(search_kwargs={'k': 20}),#the db object to convert it into a retriever object. k=1 retrive one most relevent doc
        return_source_documents = True, #allows the LLM to potentially access the retrieved information
        chain_type_kwargs={"prompt":prompt}
    )

    return qa_chain


DB_FAISS_PATH = "vectorstores/db_faiss"
custom_prompt_template = """
<s>[INST] <<SYS>>
You have to ensure the student's understanding of the main concepts in the document by generating a quiz from ducument while considering the given instructions:
###INSTRUCTIONS
1. You have the role of a strict invigilator to check the student understrading of a all the concepts in the document.
2. Output 20 questions everytime using only the context provided in document.
3. every time you just need to generate questions and four options one must be correct option.
4. Make sure your questions include question from all the concepts in the document.
5. Always create a meaningful questions to check the student understading of the concepts in document.
6. Do not repeat question within span of 20 questions.
7. Your questions should cover all the concepts in the document.
8. Don`t add any explanation.
**Never generate same question again, so keep track of question generated**

Here are some examples :
Question1: question text that you will generate?
    A. 
    B. 
    C. 
    D. 
Question2: second question genereated text goes here?
    A. 
    B. 
    C. 
    D. 

***Do not say or add anything else*".

<</SYS>>
context: {context}
field: {field}
response: {response}

It is very important to keep track of number of questions and never repeat questions.
Question:
[/INST]
"""

def qa_bot(u_input, field):
    embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})
    db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    query_answer = db.similarity_search(u_input)
    llm = load_llm()
    qa_prompt = set_custom_prompt(u_input, field)
    qa = retrieval_qa_chain(llm, qa_prompt, db)
    return qa

def final_result(u_input, field):
    qa_result = qa_bot(u_input, field)
    response = qa_result({'query' : field})
    return response['result']

def extract_questions(question):
    questions_final_list = []
    i = 0
    for split in question.split("\n"):
        i += 1
        if split.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.","Question1","Question2","Question3","Question4","Question5","Question6","Question7","Question8","Question9","Question10")):
            q = {}
            q['question'] = split.strip()
            q['options'] = question.split("\n")[i:i+4]
            questions_final_list.append(q)

    return questions_final_list


    