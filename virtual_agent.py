#import all the libraries required
import csv, pickle, numpy as np, os, pandas as pd

from lingualytics.preprocessing import remove_lessthan, remove_punctuation, remove_stopwords
from lingualytics.stopwords import en_stopwords
from texthero.preprocessing import remove_digits

from sentence_transformers import SentenceTransformer, util

from torch.nn import CosineSimilarity
import torch
#Virtual Agent Model
class VAModel():
    def __init__(self, training_file, model_name="paraphrase-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name) #load pretrained model
        self.df = pd.read_csv(training_file, encoding_errors="ignore")
        # self.qa = dict()
        # self.emb = list()

    # #train virtual assistant
    # def train(self, training_file):
    #     # if model doesn't exist in the location, compute embeddings again and store as a model
    #     if not os.path.exists(r"models/model_va.pickle"):
    #         header = False
    #         dict_model = dict()
    #         with open(training_file, "r", encoding="utf-8", errors="ignore") as file:
    #             reader = csv.reader(file)
    #             for qa_pair in reader:
    #                 self.qa[qa_pair[0]] = qa_pair[1]
    #                 self.emb.append(self.model.encode(qa_pair[0])) #compute embeddings
    #             dict_model["qa"] = self.qa
    #             dict_model["embeddings"] = self.emb
    #         #persist trained model
    #         with open(r"models/model_va.pickle", "wb") as file:
    #             pickle.dump(dict_model, file)
    #train virtual assistant
    def train(self, model_path=r"models/model_va.pickle"):
        # if model doesn't exist in the location, compute embeddings again and store as a model
        if not os.path.exists(r"models/model_va.pickle"):
            self.df['procd_Q'] = self.df['Q'].pipe(remove_digits).pipe(remove_punctuation)#.pipe(remove_lessthan,length=3)\
                                                    #.pipe(remove_stopwords,stopwords=en_stopwords.union(hi_stopwords))
            q_embs = self.model.encode(self.df["procd_Q"])
            #persist trained model
            with open(model_path, "wb") as file:
                pickle.dump(q_embs, file)
    
    #predict answer to user query
    def pred_answer(self, usr_query, model_path=r"models/model_va.pickle"):
        with open(model_path, "rb") as file:
            q_embs = pickle.load(file)
        df_query = pd.DataFrame([usr_query], columns=["usr_query"]) # use similar pipeline that was used for computing embeddings from dataset
        df_query["clean_usr_q"] = df_query["usr_query"].pipe(remove_digits).pipe(remove_punctuation)
        usr_q_emb = self.model.encode(df_query["clean_usr_q"]) # compute embedding
        cosine_similarity = CosineSimilarity()
        q_idx = np.argmax(cosine_similarity(torch.from_numpy(usr_q_emb), torch.from_numpy(q_embs))) # compute cosine similarity and find the matched query
        return self.df['A'][q_idx.item()] # look up answer of the matched query from the dataframe of input dataset
    # #predict answer to user query
    # def pred_answer(self, usr_query):
    #     query_embedding = self.model.encode(usr_query) #compute embedding for the user query
    #     if not self.qa and not self.emb: #load trained model if not done already
    #         with open(r"models/model_va.pickle", "rb") as file:
    #             dict_model = pickle.load(file)
    #             self.qa = dict_model["qa"]
    #             self.emb = dict_model["embeddings"]
    #     sim_scores = util.pytorch_cos_sim(query_embedding, self.emb) #computet similarity scores
    #     matched_query = list(self.qa.keys())[np.argmax(sim_scores)] #identify matched query based on the best score
    #     answer = self.qa.get(matched_query) #get answer to the matched query
    #     return answer if answer else "Sorry, Would you rephrase it?"
    def free_up(self):
        # self.emb = None
        self.df = None
        self.model = None

    def run_app(self):
        # print("Hello! How can I help you?")
        # print("----------------------------")
        while True:
            usr_query = input("Ask a query(or type 'exit' to exit): ")
            if usr_query.lower() == "exit":
                self.free_up()
                break
            else:
                response = self.pred_answer(usr_query)
                print(f"Response: {response}")
