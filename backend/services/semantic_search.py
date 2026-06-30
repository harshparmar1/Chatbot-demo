import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# Re-use intents dictionary from nlp_engine for backward compatibility
from nlp_engine import INTENTS

class SemanticSearchService:
    def __init__(self):
        # Load local SentenceTransformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.corpus = []
        self.intent_labels = []
        
        # Flatten intents list for matching
        for intent, phrases in INTENTS.items():
            for phrase in phrases:
                self.corpus.append(phrase)
                self.intent_labels.append(intent)
                
        # Precompute and normalize training phrase embeddings
        print("Computing semantic embeddings for intent corpus...")
        self.trained_embeddings = self.model.encode(self.corpus, convert_to_numpy=True)
        norms = np.linalg.norm(self.trained_embeddings, axis=1, keepdims=True)
        self.trained_embeddings = self.trained_embeddings / np.maximum(norms, 1e-12)

    def predict_intent(self, query, threshold=0.40):
        """
        Classifies query into intent. Returns (intent, similarity_score).
        """
        if not query or not query.strip():
            return "fallback", 0.0
            
        # Get and normalize query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)[0]
        query_norm = np.linalg.norm(query_embedding)
        if query_norm > 1e-12:
            query_embedding = query_embedding / query_norm
            
        # Compute Cosine Similarity via dot product
        similarities = np.dot(self.trained_embeddings, query_embedding)
        max_idx = np.argmax(similarities)
        max_similarity = similarities[max_idx]
        
        if max_similarity >= threshold:
            return self.intent_labels[max_idx], float(max_similarity)
        else:
            return "fallback", float(max_similarity)

    def retrieve_relevant_rows(self, query, df, top_k=5):
        """
        Computes cosine similarity between query and all row Remarks in the dataset,
        returning the top_k matching rows and their similarity scores.
        """
        if df.empty:
            return pd.DataFrame(), []
            
        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True)[0]
        query_norm = np.linalg.norm(query_embedding)
        if query_norm > 1e-12:
            query_embedding = query_embedding / query_norm
            
        # Encode all Remarks
        remarks = df['Remarks'].fillna('').astype(str).tolist()
        remarks_embeddings = self.model.encode(remarks, convert_to_numpy=True)
        
        # Normalize remarks embeddings
        norms = np.linalg.norm(remarks_embeddings, axis=1, keepdims=True)
        remarks_embeddings = remarks_embeddings / np.maximum(norms, 1e-12)
        
        # Compute similarities
        similarities = np.dot(remarks_embeddings, query_embedding)
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        top_similarities = similarities[top_indices]
        
        # Retrieve rows
        relevant_df = df.iloc[top_indices].copy()
        relevant_df['similarity_score'] = top_similarities
        
        return relevant_df, list(top_similarities)
