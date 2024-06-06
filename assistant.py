from injest import Injest
from model import final_result, extract_questions

def generate_quiz():
        i = Injest()
        i.clear_folder()
        u_input = "20 questions"
        field = "Generate 20 questions with four options A, B, C, D from given document ensure the 20 questions should cover all the concept in the document."
    
        #creating embedings
        data = i.load_documents()
        texts = i.split_text(data)
        emb = i.get_embeddings(texts)
        i.save_embeddings(texts, emb)

        #run model to generate quiz
        response = final_result(u_input, field)
        return extract_questions(response)
