import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Define intents and training phrases
INTENTS = {
    "highest_risk_ward": [
        "Which ward has highest risk?",
        "ward with highest risk",
        "what ward is most risky",
        "highest risk ward",
        "highest risk in which ward",
        "show ward highest risk"
    ],
    "highest_risk_floor": [
        "Which floor has highest risk?",
        "floor with highest risk",
        "what floor is the most risky",
        "highest risk floor",
        "risk score by floor",
        "highest floor risk"
    ],
    "hospital_risk_score": [
        "Show hospital risk score.",
        "what is the hospital risk score",
        "average risk of the hospital",
        "hospital risk level",
        "overall risk score",
        "average hospital risk"
    ],
    "icu_risk_score": [
        "Show ICU risk score.",
        "what is the risk in icu",
        "icu risk level",
        "icu average risk score",
        "icu risk score"
    ],
    "predict_future_risk": [
        "Predict future risk.",
        "what is the future risk prediction",
        "forecast hospital risk",
        "predict risk trends",
        "risk forecast",
        "future risk"
    ],
    "compliance_score": [
        "Show compliance score.",
        "what is the compliance score",
        "overall compliance",
        "compliance rate",
        "average compliance score"
    ],
    "nabh_compliance": [
        "Show NABH compliance.",
        "nabh compliance score",
        "what is the nabh rating",
        "nabh standards compliance",
        "nabh audits",
        "nabh score"
    ],
    "lowest_compliance_dept": [
        "Which department has lowest compliance?",
        "lowest compliance department",
        "worst compliance dept",
        "department with lowest compliance score",
        "department with lowest compliance"
    ],
    "compliance_trend": [
        "Compliance trend.",
        "show compliance trend",
        "compliance over time",
        "compliance trend analysis",
        "trending compliance"
    ],
    "pending_audits": [
        "Show pending audits.",
        "pending audits",
        "how many audits are pending",
        "list pending audits",
        "uncompleted audits",
        "how many pending audits do we have"
    ],
    "completed_audits": [
        "Show completed audits.",
        "completed audits",
        "how many audits are completed",
        "finished audits list",
        "audits done"
    ],
    "failed_audits": [
        "Show failed audits.",
        "failed audits",
        "how many audits failed",
        "list failed audits",
        "audits that failed"
    ],
    "todays_audits": [
        "Show today's audits.",
        "today's audits",
        "audits scheduled for today",
        "how many audits today",
        "audits today"
    ],
    "weeks_audits": [
        "Show this week's audits.",
        "this week's audits",
        "audits for this week",
        "audits done this week",
        "audits this week"
    ],
    "audit_summary": [
        "Show audit summary.",
        "audit summary",
        "summarize hospital audits",
        "audits report",
        "audit statistics",
        "summary of audits"
    ],
    "open_escalations": [
        "Show open escalations.",
        "open escalations",
        "how many escalations are open",
        "active escalations",
        "pending escalations"
    ],
    "closed_escalations": [
        "Show closed escalations.",
        "closed escalations",
        "how many escalations are closed",
        "resolved escalations"
    ],
    "most_escalations_floor": [
        "Which floor has most escalations?",
        "floor with most escalations",
        "most escalations by floor",
        "escalations floor list"
    ],
    "critical_escalations": [
        "Show critical escalations.",
        "critical escalations",
        "how many critical escalations",
        "list critical issues",
        "critical open issues"
    ],
    "escalation_summary": [
        "Escalation summary.",
        "show escalation report",
        "escalations summary",
        "escalation statistics"
    ],
    "best_staff": [
        "Best performing staff.",
        "who is the best staff",
        "top performing staff members",
        "best staff member",
        "who has the best performance",
        "top staff"
    ],
    "worst_staff": [
        "Lowest performing staff.",
        "who is the worst staff",
        "lowest performing staff member",
        "worst performing staff",
        "underperforming staff"
    ],
    "staff_failed_audits": [
        "Staff with most failed audits.",
        "who has the most failed audits",
        "failed audits by staff",
        "staff member with most failures"
    ],
    "staff_performance_report": [
        "Staff performance report.",
        "show staff performance summary",
        "staff report",
        "staff score summary"
    ],
    "staff_needs_attention": [
        "Which staff needs attention?",
        "staff needing training or attention",
        "who is underperforming",
        "staff needs attention",
        "which staff has poor metrics"
    ],
    "hygiene_audits": [
        "Show hygiene audit results.",
        "hygiene audits",
        "how are the hygiene audits",
        "hygiene checklist",
        "hygiene score"
    ],
    "safety_audits": [
        "Show safety audit results.",
        "safety audits",
        "safety audit performance",
        "safety checklist status"
    ],
    "waste_audits": [
        "Show waste audit results.",
        "waste audits",
        "how are the waste audits doing",
        "waste compliance score"
    ],
    "fire_safety_audits": [
        "Show fire safety audit results.",
        "fire safety audits",
        "fire safety audit details",
        "fire safety performance"
    ],
    "checklist_completion": [
        "Checklist completion status.",
        "checklist status",
        "are the checklists complete",
        "checklist completion"
    ],
    "recommendations": [
        "Show recommendations.",
        "what are the recommendations",
        "suggest improvements",
        "give recommendations",
        "audit recommendations"
    ],
    "icu_performance": [
        "Show ICU performance.",
        "icu performance",
        "icu department results",
        "how is icu doing"
    ],
    "floor_wise_risk": [
        "Show floor-wise risk.",
        "floor-wise risk score",
        "risk by floor",
        "what is the risk on each floor"
    ],
    "critical_issues": [
        "Show critical issues.",
        "what are the critical issues",
        "critical audits",
        "any critical errors",
        "list critical checklist items"
    ],
    "delayed_audits": [
        "Show delayed audits.",
        "what audits are delayed",
        "delayed audits list",
        "overdue audits",
        "audits that took too long"
    ],
    "risk_trends": [
        "Show risk trends.",
        "risk trends",
        "risk trend chart",
        "how is risk trending"
    ],
    "icu_hygiene_risk": [
        "ICU hygiene risk increasing continuously during night shifts",
        "Is ICU hygiene risk increasing during night shifts?",
        "ICU hygiene risk",
        "hygiene risk in ICU",
        "icu hygiene risk trend"
    ],
    "nabh_compliance_trend": [
        "NABH compliance score showing steady improvement this week",
        "Is NABH compliance score improving?",
        "NABH compliance trend this week",
        "steady improvement in NABH",
        "nabh compliance trend"
    ],
    "greeting": [
        "Hi",
        "Hello",
        "Hey",
        "How can you help me",
        "What can you do",
        "Greetings",
        "Good morning",
        "Good afternoon"
    ]
}

class NLPIntentClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', lowercase=True)
        self.corpus = []
        self.intent_labels = []
        
        # Flatten intents list for training
        for intent, phrases in INTENTS.items():
            for phrase in phrases:
                self.corpus.append(phrase)
                self.intent_labels.append(intent)
                
        # Fit vectorizer
        self.vectorizer.fit(self.corpus)
        self.trained_vectors = self.vectorizer.transform(self.corpus)

    def predict(self, query):
        if not query or not query.strip():
            return "fallback", 0.0
            
        # Transform the user's query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarities
        similarities = cosine_similarity(query_vector, self.trained_vectors).flatten()
        max_idx = np.argmax(similarities)
        max_similarity = similarities[max_idx]
        
        # Set a reasonable similarity threshold
        threshold = 0.20
        if max_similarity >= threshold:
            return self.intent_labels[max_idx], float(max_similarity)
        else:
            return "fallback", float(max_similarity)
