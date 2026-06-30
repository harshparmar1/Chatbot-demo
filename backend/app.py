# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from nlp_engine import NLPIntentClassifier
from data_analyzer import HospitalAuditAnalyzer
import os

# Add local directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from services.semantic_search import SemanticSearchService
from services.chatbot_service import ChatbotService

app = Flask(__name__)
CORS(app)

# Initialize modules
try:
    analyzer = HospitalAuditAnalyzer("../verify_audit.csv")
except FileNotFoundError:
    try:
        analyzer = HospitalAuditAnalyzer("verify_audit.csv")
    except Exception as e:
        print("Could not load verify_audit.csv. Make sure the file exists.")
        raise e

nlp = NLPIntentClassifier()
semantic_search = SemanticSearchService()
chatbot = ChatbotService(analyzer, semantic_search)

def format_response(answer, reason_items, recommendation):
    """
    Formats the chatbot response in a structured Answer, Reason, and Recommendation format.
    """
    response_text = f"### Answer\n{answer}\n\n"
    response_text += "### Reason\n"
    for item in reason_items:
        response_text += f"- {item}\n"
    response_text += f"\n### Recommendation\n{recommendation}"
    return response_text

@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    try:
        analyzer.reload() # Reload CSV data to ensure dynamic updates
        data = analyzer.get_dashboard_data()
        df = analyzer.df
        
        # Compute the new AI metrics
        predicted_risk_score = float(df['risk_score'].mean())
        predicted_compliance_score = float(df['compliance_score'].mean())
        
        loc_risk = df.groupby('Location')['risk_score'].mean()
        highest_risk_loc = loc_risk.idxmax() if not loc_risk.empty else "N/A"
        highest_risk_loc_score = float(loc_risk.max()) if not loc_risk.empty else 0.0
        
        loc_comp = df.groupby('Location')['compliance_score'].mean()
        lowest_comp_loc = loc_comp.idxmin() if not loc_comp.empty else "N/A"
        lowest_comp_loc_score = float(loc_comp.min()) if not loc_comp.empty else 0.0
        
        failed_checklists = df[df['Status'].str.lower() == 'fail'].groupby('Checklist Name').size()
        most_failed_chk = failed_checklists.idxmax() if not failed_checklists.empty else "N/A"
        most_failed_chk_count = int(failed_checklists.max()) if not failed_checklists.empty else 0
        
        completed = df[df['Status'].str.lower().isin(['pass', 'fail'])]
        if not completed.empty:
            user_pass = completed.groupby('Created By').apply(lambda g: (g['Status'].str.lower() == 'pass').sum() / len(g))
            top_user = user_pass.idxmax()
            top_user_rate = float(user_pass.max()) * 100
        else:
            top_user = "N/A"
            top_user_rate = 0.0
            
        pending_df = df[df['Status'].str.lower() == 'pending']
        if not pending_df.empty:
            user_pending = pending_df.groupby('Created By').size()
            most_pending_user = user_pending.idxmax()
            most_pending_count = int(user_pending.max())
        else:
            most_pending_user = "None"
            most_pending_count = 0
            
        failed_df = df[df['Status'].str.lower() == 'fail']
        if not failed_df.empty:
            user_failed = failed_df.groupby('Created By').size()
            most_failed_user = user_failed.idxmax()
            most_failed_count = int(user_failed.max())
        else:
            most_failed_user = "None"
            most_failed_count = 0
            
        # Daily, Weekly, Monthly Trends
        daily_scores = df.groupby('date')['risk_score'].mean().sort_index()
        if len(daily_scores) >= 2:
            daily_diff = daily_scores.iloc[-1] - daily_scores.iloc[-2]
            daily_trend = f"{'+' if daily_diff >= 0 else ''}{daily_diff:.1f} risk score"
        else:
            daily_trend = "Stable"
            
        df['week'] = df['date'].dt.to_period('W').dt.start_time
        weekly_scores = df.groupby('week')['risk_score'].mean().sort_index()
        if len(weekly_scores) >= 2:
            weekly_diff = weekly_scores.iloc[-1] - weekly_scores.iloc[-2]
            weekly_trend = f"{'+' if weekly_diff >= 0 else ''}{weekly_diff:.1f} risk score"
        else:
            weekly_trend = "Stable"
            
        df['month'] = df['date'].dt.to_period('M').dt.start_time
        monthly_scores = df.groupby('month')['risk_score'].mean().sort_index()
        if len(monthly_scores) >= 2:
            monthly_diff = monthly_scores.iloc[-1] - monthly_scores.iloc[-2]
            monthly_trend = f"{'+' if monthly_diff >= 0 else ''}{monthly_diff:.1f} risk score"
        else:
            monthly_trend = "Stable"
            
        # Add new AI Dashboard metrics
        data["predicted_risk_score"] = round(predicted_risk_score, 1)
        data["predicted_compliance_score"] = round(predicted_compliance_score, 1)
        data["highest_risk_location"] = f"{highest_risk_loc} ({highest_risk_loc_score:.1f})"
        data["lowest_compliance_location"] = f"{lowest_comp_loc} ({lowest_comp_loc_score:.1f}%)"
        data["most_failed_checklist"] = f"{most_failed_chk} ({most_failed_chk_count} fails)"
        data["top_performing_user"] = f"{top_user} ({top_user_rate:.1f}% pass)"
        data["most_pending_audits"] = f"{most_pending_user} ({most_pending_count} pending)"
        data["most_failed_audits"] = f"{most_failed_user} ({most_failed_count} failed)"
        data["daily_trend"] = daily_trend
        data["weekly_trend"] = weekly_trend
        data["monthly_trend"] = monthly_trend
        
        # Weekly groupings using the Monday start date for clear x-axis labels
        df['week_start'] = df['date'] - pd.to_timedelta(df['date'].dt.weekday, unit='D')
        daily_trend_groups = df.groupby(df['week_start'].dt.strftime('%Y-%m-%d'))
        charts_risk_trend = []
        charts_comp_trend = []
        for week_str, group in sorted(daily_trend_groups):
            risk_vals = group['risk_score'].dropna()
            comp_vals = group['compliance_score'].dropna()
            
            risk_q1 = float(np.percentile(risk_vals, 25)) if len(risk_vals) > 0 else 0.0
            risk_median = float(np.percentile(risk_vals, 50)) if len(risk_vals) > 0 else 0.0
            risk_q3 = float(np.percentile(risk_vals, 75)) if len(risk_vals) > 0 else 0.0
            risk_mean = float(risk_vals.mean()) if len(risk_vals) > 0 else 0.0
            
            comp_q1 = float(np.percentile(comp_vals, 25)) if len(comp_vals) > 0 else 0.0
            comp_median = float(np.percentile(comp_vals, 50)) if len(comp_vals) > 0 else 0.0
            comp_q3 = float(np.percentile(comp_vals, 75)) if len(comp_vals) > 0 else 0.0
            comp_mean = float(comp_vals.mean()) if len(comp_vals) > 0 else 0.0
            
            charts_risk_trend.append({
                "date": week_str,
                "range": [round(risk_q1, 1), round(risk_q3, 1)],
                "median": round(risk_median, 1),
                "mean": round(risk_mean, 1)
            })
            charts_comp_trend.append({
                "date": week_str,
                "range": [round(comp_q1, 1), round(comp_q3, 1)],
                "median": round(comp_median, 1),
                "mean": round(comp_mean, 1)
            })
            
        status_counts = df['Status'].value_counts()
        charts_status_dist = []
        for status, count in status_counts.items():
            charts_status_dist.append({"status": status, "count": int(count)})
            
        chk_counts = df['Checklist Name'].value_counts().head(10)
        charts_chk_dist = []
        for name, count in chk_counts.items():
            charts_chk_dist.append({"name": name, "count": int(count)})
            
        df['city'] = df['Location'].apply(lambda x: str(x).split('/')[0] if '/' in str(x) else 'Other')
        loc_counts = df['city'].value_counts()
        charts_loc_dist = []
        for city, count in loc_counts.items():
            charts_loc_dist.append({"city": city, "count": int(count)})
            
        user_metrics = completed.groupby('Created By').agg({
            'Status': [lambda x: (x.str.lower() == 'pass').sum(), 'count']
        })
        user_metrics.columns = ['passed', 'total']
        user_metrics['pass_rate'] = (user_metrics['passed'] / user_metrics['total']) * 100
        user_metrics = user_metrics.reset_index().sort_values('pass_rate', ascending=False).head(5)
        charts_user_perf = []
        for _, row in user_metrics.iterrows():
            charts_user_perf.append({
                "username": row['Created By'],
                "pass_rate": round(float(row['pass_rate']), 1),
                "total": int(row['total'])
            })
            
        df['month_str'] = df['date'].dt.strftime('%b %Y')
        monthly_audits = df.groupby(['month_str', df['date'].dt.to_period('M')]).size().reset_index(name='count').sort_values('date')
        charts_monthly_audits = []
        for _, row in monthly_audits.iterrows():
            charts_monthly_audits.append({"month": row['month_str'], "count": int(row['count'])})
            
        # Update charts object
        data["charts"]["risk_trend"] = charts_risk_trend
        data["charts"]["compliance_trend"] = charts_comp_trend
        data["charts"]["status_distribution"] = charts_status_dist
        data["charts"]["checklist_distribution"] = charts_chk_dist
        data["charts"]["location_distribution"] = charts_loc_dist
        data["charts"]["user_performance"] = charts_user_perf
        data["charts"]["monthly_audits"] = charts_monthly_audits
        
        # Add remaining required fields
        data["critical_issues"] = int(len(df[df["priority"] == "Critical"]))
        data["pending_audits"] = int(len(df[df["status"] == "Pending"]))
        data["failed_audits"] = int(len(df[df["status"] == "Fail"]))
        data["open_escalations"] = int(len(df[df["escalation_status"] == "Open"]))
        
        return jsonify(data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        analyzer.reload() # Reload data
        req_data = request.get_json() or {}
        user_message = req_data.get("message", "").strip()
        
        if not user_message:
            return jsonify({"response": "Please enter a message.", "intent": "fallback", "data": {}})

        result = chatbot.get_response(user_message)
        
        return jsonify({
            "response": result["response"],
            "intent": result["intent"],
            "similarity": result["similarity"],
            "data": result["data"]
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/retrain", methods=["POST"])
def retrain():
    try:
        analyzer.reload()
        success = analyzer.predictor.train(analyzer.df)
        if success:
            analyzer.reload() # Reload analyzer with new models
            return jsonify({"success": True, "message": "ML models trained successfully."})
        else:
            return jsonify({"success": False, "message": "Failed to train ML models."}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
