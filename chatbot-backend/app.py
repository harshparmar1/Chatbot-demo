from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from nlp_engine import NLPIntentClassifier
from data_analyzer import HospitalAuditAnalyzer

app = Flask(__name__)
# Enable CORS for frontend requests
CORS(app)

# Initialize modules
try:
    analyzer = HospitalAuditAnalyzer("../hospital_audit_500.csv")
except FileNotFoundError:
    try:
        analyzer = HospitalAuditAnalyzer("hospital_audit_500.csv")
    except Exception as e:
        print("Could not load hospital_audit_500.csv. Make sure the file exists.")
        raise e

nlp = NLPIntentClassifier()

@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    try:
        analyzer.reload() # Reload CSV data to ensure dynamic updates
        data = analyzer.get_dashboard_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        analyzer.reload() # Reload data
        req_data = request.get_json() or {}
        user_message = req_data.get("message", "").strip()
        
        if not user_message:
            return jsonify({"response": "Please enter a message.", "intent": "fallback", "data": {}})

        # Detect Intent
        intent, similarity = nlp.predict(user_message)
        print(f"Query: '{user_message}' -> Intent: '{intent}' (Similarity: {similarity:.2f})")

        # Initialize default response content
        response_text = ""
        structured_data = {}

        if intent == "greeting":
            response_text = (
                "Hello! I am the **Reallist AI Audit Assistant**.\n\n"
                "I can analyze the hospital audit logs dynamically and answer questions about:\n"
                "- **Risk Analysis** (e.g., *'Which ward has highest risk?'*, *'Predict future risk'*, *'Floor-wise risk'*, *'ICU risk score'*)\n"
                "- **Compliance** (e.g., *'Show compliance score'*, *'Show NABH compliance'*, *'Lowest compliance department'*)\n"
                "- **Audit Status** (e.g., *'Show pending audits'*, *'Show failed audits'*, *'Show audit summary'*)\n"
                "- **Escalation & Critical Issues** (e.g., *'Show open escalations'*, *'Floor with most escalations'*, *'Show critical issues'*)\n"
                "- **Staff Performance** (e.g., *'Best performing staff'*, *'Staff performance report'*, *'Who needs attention?'*)\n"
                "- **Checklist Insights** (e.g., *'Show hygiene audit results'*, *'Fire safety audit results'*)\n\n"
                "How can I help you with your audit data today?"
            )
            
        elif intent == "highest_risk_ward":
            ward, score = analyzer.get_highest_risk_ward()
            response_text = f"The ward with the highest risk is the **{ward}** ward, with an average risk score of **{score:.1f}** out of 100."
            structured_data = {"ward": ward, "score": score}

        elif intent == "highest_risk_floor":
            floor, score = analyzer.get_highest_risk_floor()
            response_text = f"The floor with the highest risk is **Floor {floor}**, with an average risk score of **{score:.1f}** out of 100."
            structured_data = {"floor": floor, "score": score}

        elif intent == "hospital_risk_score":
            score = analyzer.get_hospital_risk_score()
            response_text = f"The overall hospital average risk score is **{score:.1f}** out of 100. Lower is better."
            structured_data = {"score": score}

        elif intent == "icu_risk_score":
            score = analyzer.get_icu_risk_score()
            response_text = f"The average risk score for the **ICU** ward is **{score:.1f}** out of 100."
            structured_data = {"score": score}

        elif intent == "predict_future_risk":
            pred_data = analyzer.predict_future_risk()
            slope = pred_data["slope"]
            trend = "upward (increasing risk)" if slope > 0 else "downward (decreasing risk)"
            comparison = pred_data["comparison_change"]
            comp_text = (
                f"ICU risk has increased by {comparison:.1f}% compared to previous audits."
                if comparison > 0 else 
                f"ICU risk has decreased by {abs(comparison):.1f}% compared to previous audits."
            )
            response_text = (
                f"### Future Risk Prediction (Linear Regression Model)\n\n"
                f"- **Current Hospital Risk Score**: **{analyzer.get_hospital_risk_score():.1f}**\n"
                f"- **Predicted Risk in 7 Days**: **{pred_data['prediction_7d']:.1f}**\n"
                f"- **Predicted Risk in 30 Days**: **{pred_data['prediction_30d']:.1f}**\n"
                f"- **Trend Direction**: **{trend}** (slope: {slope:.3f} per day)\n\n"
                f"**Historical Comparison**: {comp_text}"
            )
            structured_data = pred_data

        elif intent == "compliance_score":
            score = analyzer.get_compliance_score()
            response_text = f"The overall compliance score for the hospital is **{score:.1f}%**."
            structured_data = {"compliance_score": score}

        elif intent == "nabh_compliance":
            score = analyzer.get_nabh_compliance()
            response_text = (
                f"The hospital's compliance score under **NABH standards** is **{score:.1f}%**.\n\n"
                f"This is calculated as the percentage of audits that scored 80% or above in compliance. "
                f"The NABH standard benchmark is 85%."
            )
            structured_data = {"nabh_compliance": score}

        elif intent == "lowest_compliance_dept":
            dept, score = analyzer.get_lowest_compliance_dept()
            response_text = f"The department with the lowest compliance is **{dept}** with an average compliance score of **{score:.1f}%**."
            structured_data = {"department": dept, "score": score}

        elif intent == "compliance_trend":
            trend_data = analyzer.get_compliance_trend()
            direction = trend_data["trend_direction"]
            slope = trend_data["slope"]
            response_text = (
                f"The hospital's compliance score trend is **{direction}**.\n\n"
                f"The linear regression slope of average daily compliance scores is **{slope:.4f}**."
            )
            structured_data = trend_data

        elif intent == "pending_audits":
            pending = analyzer.get_pending_audits()
            count = len(pending)
            if count == 0:
                response_text = "There are no pending audits. All audits are completed."
            else:
                sample_list = pending.head(5)[['audit_id', 'ward', 'checklist_type', 'priority']].to_dict(orient='records')
                response_text = f"There are currently **{count}** pending audits in the system."
                if count > 0:
                    response_text += "\n\n**Here are some of the pending audits:**\n"
                    for item in sample_list:
                        response_text += f"- **{item['audit_id']}**: {item['checklist_type']} in {item['ward']} ({item['priority']} priority)\n"
            structured_data = {"count": count, "pending": pending.head(10).to_dict(orient='records')}

        elif intent == "completed_audits":
            completed = analyzer.get_completed_audits()
            count = len(completed)
            response_text = f"There are a total of **{count}** completed audits in the system."
            structured_data = {"count": count}

        elif intent == "failed_audits":
            failed = analyzer.get_failed_audits()
            count = len(failed)
            if count == 0:
                response_text = "Good news! There are no failed audits recorded."
            else:
                wards_affected = failed['ward'].unique()
                sample_list = failed.head(5)[['audit_id', 'ward', 'checklist_type', 'assigned_staff']].to_dict(orient='records')
                response_text = f"There are **{count}** failed audits in the system.\n\n"
                response_text += f"**Affected Wards**: {', '.join(wards_affected)}\n\n"
                response_text += "**Sample of Failed Audits:**\n"
                for item in sample_list:
                    response_text += f"- **{item['audit_id']}**: {item['checklist_type']} in {item['ward']} (Assigned: {item['assigned_staff']})\n"
            structured_data = {"count": count, "failed": failed.head(10).to_dict(orient='records')}

        elif intent == "todays_audits":
            todays = analyzer.get_todays_audits()
            count = len(todays)
            date_str = analyzer.max_date.strftime("%Y-%m-%d")
            if count == 0:
                response_text = f"There are no audits recorded for today ({date_str})."
            else:
                response_text = f"There are **{count}** audits recorded for today ({date_str}):\n\n"
                for _, row in todays.head(10).iterrows():
                    response_text += f"- **{row['audit_id']}**: {row['checklist_type']} in {row['ward']} - Status: **{row['status']}**\n"
            structured_data = {"count": count, "date": date_str}

        elif intent == "weeks_audits":
            weeks = analyzer.get_weeks_audits()
            count = len(weeks)
            response_text = f"There are **{count}** audits recorded for this week (last 7 days of the log):\n\n"
            if count > 0:
                summary_status = weeks['status'].value_counts().to_dict()
                response_text += f"- **Pass**: {summary_status.get('Pass', 0)}\n"
                response_text += f"- **Fail**: {summary_status.get('Fail', 0)}\n"
                response_text += f"- **Pending**: {summary_status.get('Pending', 0)}\n"
            structured_data = {"count": count}

        elif intent == "audit_summary":
            summary = analyzer.get_audit_summary()
            response_text = (
                f"### Overall Audit Summary\n\n"
                f"- **Total Audits**: **{summary['total_audits']}**\n"
                f"- **Completed Audits**: **{summary['completed_audits']}**\n"
                f"  - Passed: **{summary['passed_audits']}**\n"
                f"  - Failed: **{summary['failed_audits']}**\n"
                f"- **Pending Audits**: **{summary['pending_audits']}**\n"
                f"- **Audit Pass Rate**: **{summary['pass_rate']:.1f}%**\n"
                f"- **Avg Completion Time**: **{summary['avg_completion_time_mins']:.1f} minutes**"
            )
            structured_data = summary

        elif intent == "open_escalations":
            open_esc = analyzer.get_open_escalations()
            count = len(open_esc)
            response_text = f"There are currently **{count}** open escalations in the system."
            if count > 0:
                critical_count = len(open_esc[open_esc['priority'].str.lower() == 'critical'])
                response_text += f" Of these, **{critical_count}** are classified as Critical priority."
            structured_data = {"count": count}

        elif intent == "closed_escalations":
            closed_esc = analyzer.get_closed_escalations()
            count = len(closed_esc)
            response_text = f"There are **{count}** closed escalations in the system."
            structured_data = {"count": count}

        elif intent == "most_escalations_floor":
            floor, count = analyzer.get_most_escalations_floor()
            response_text = f"**Floor {floor}** has the most escalations, with **{count}** active cases."
            structured_data = {"floor": floor, "count": count}

        elif intent == "critical_escalations":
            crit = analyzer.get_critical_escalations()
            count = len(crit)
            if count == 0:
                response_text = "Excellent! There are no critical escalations currently open."
            else:
                response_text = f"There are **{count}** critical escalations open in the system:\n\n"
                for _, row in crit.iterrows():
                    response_text += f"- **{row['audit_id']}**: {row['checklist_type']} in {row['ward']} on Floor {row['floor']} (Assigned: {row['assigned_staff']})\n"
            structured_data = {"count": count}

        elif intent == "escalation_summary":
            summary = analyzer.get_escalation_summary()
            open_by_p = summary["open_by_priority"]
            response_text = (
                f"### Escalation Summary Report\n\n"
                f"- **Total Escalations**: **{summary['total_escalations']}**\n"
                f"- **Open Escalations**: **{summary['open_escalations']}**\n"
                f"- **Closed/Resolved**: **{summary['closed_escalations']}**\n\n"
                f"**Open Escalations by Priority:**\n"
                f"- Critical: **{open_by_p.get('Critical', 0) or open_by_p.get('critical', 0)}**\n"
                f"- High: **{open_by_p.get('High', 0) or open_by_p.get('high', 0)}**\n"
                f"- Medium: **{open_by_p.get('Medium', 0) or open_by_p.get('medium', 0)}**\n"
                f"- Low: **{open_by_p.get('Low', 0) or open_by_p.get('low', 0)}**"
            )
            structured_data = summary

        elif intent == "best_staff":
            staff, pass_rate, comp = analyzer.get_best_staff()
            response_text = f"The best performing staff member is **{staff}**, achieving a **{pass_rate:.1f}%** audit pass rate and an average compliance score of **{comp:.1f}%**."
            structured_data = {"staff": staff, "pass_rate": pass_rate, "compliance": comp}

        elif intent == "worst_staff":
            staff, pass_rate, comp = analyzer.get_lowest_performing_staff()
            response_text = (
                f"The lowest performing staff member is **{staff}**, with a **{pass_rate:.1f}%** audit pass rate "
                f"and an average compliance score of **{comp:.1f}%**."
            )
            structured_data = {"staff": staff, "pass_rate": pass_rate, "compliance": comp}

        elif intent == "staff_failed_audits":
            staff, count = analyzer.get_staff_with_most_failed_audits()
            response_text = f"Staff member **{staff}** has the most failed audits, with **{count}** failures."
            structured_data = {"staff": staff, "count": count}

        elif intent == "staff_performance_report":
            metrics = analyzer.get_staff_metrics()
            top_5 = metrics.sort_values('pass_rate', ascending=False).head(3)
            bottom_5 = metrics.sort_values('pass_rate', ascending=True).head(3)
            
            response_text = "### Staff Performance Summary Report\n\n"
            response_text += "**Top 3 Performing Staff (by Pass Rate):**\n"
            for _, row in top_5.iterrows():
                response_text += f"- **{row['assigned_staff']}**: Pass Rate: {row['pass_rate']:.1f}% | Avg Compliance: {row['avg_compliance_score']:.1f}% | Total Audits: {row['total_audits']}\n"
                
            response_text += "\n**Bottom 3 Performing Staff (Needs Attention):**\n"
            for _, row in bottom_5.iterrows():
                response_text += f"- **{row['assigned_staff']}**: Pass Rate: {row['pass_rate']:.1f}% | Avg Compliance: {row['avg_compliance_score']:.1f}% | Total Audits: {row['total_audits']}\n"
                
            structured_data = {"top": top_5.to_dict(orient='records'), "bottom": bottom_5.to_dict(orient='records')}

        elif intent == "staff_needs_attention":
            attention = analyzer.get_staff_needs_attention()
            if not attention:
                response_text = "All staff members currently meet the minimum audit performance thresholds."
            else:
                response_text = "### Staff Members Requiring Attention / Training:\n\n"
                for row in attention[:5]:
                    response_text += f"- **{row['assigned_staff']}**: Pass Rate: **{row['pass_rate']:.1f}%**, Failed Audits: **{row['failed_audits']}** (Total: {row['total_audits']})\n"
            structured_data = {"attention": attention}

        elif intent == "hygiene_audits":
            metrics = analyzer.get_checklist_metrics("Hygiene Audit")
            response_text = (
                f"### Hygiene Audit Results\n\n"
                f"- Total Audits: **{metrics['total_audits']}**\n"
                f"- Passed: **{metrics['passed_audits']}**\n"
                f"- Failed: **{metrics['failed_audits']}**\n"
                f"- Pending: **{metrics['pending_audits']}**\n"
                f"- Pass Rate: **{metrics['pass_rate']:.1f}%**\n"
                f"- Avg Compliance: **{metrics['avg_compliance_score']:.1f}%**\n"
                f"- Avg Risk Score: **{metrics['avg_risk_score']:.1f}**"
            )
            structured_data = metrics

        elif intent == "safety_audits":
            metrics = analyzer.get_checklist_metrics("Safety Audit")
            response_text = (
                f"### Safety Audit Results\n\n"
                f"- Total Audits: **{metrics['total_audits']}**\n"
                f"- Passed: **{metrics['passed_audits']}**\n"
                f"- Failed: **{metrics['failed_audits']}**\n"
                f"- Pending: **{metrics['pending_audits']}**\n"
                f"- Pass Rate: **{metrics['pass_rate']:.1f}%**\n"
                f"- Avg Compliance: **{metrics['avg_compliance_score']:.1f}%**\n"
                f"- Avg Risk Score: **{metrics['avg_risk_score']:.1f}**"
            )
            structured_data = metrics

        elif intent == "waste_audits":
            metrics = analyzer.get_checklist_metrics("Waste Audit")
            response_text = (
                f"### Waste Audit Results\n\n"
                f"- Total Audits: **{metrics['total_audits']}**\n"
                f"- Passed: **{metrics['passed_audits']}**\n"
                f"- Failed: **{metrics['failed_audits']}**\n"
                f"- Pending: **{metrics['pending_audits']}**\n"
                f"- Pass Rate: **{metrics['pass_rate']:.1f}%**\n"
                f"- Avg Compliance: **{metrics['avg_compliance_score']:.1f}%**\n"
                f"- Avg Risk Score: **{metrics['avg_risk_score']:.1f}**"
            )
            structured_data = metrics

        elif intent == "fire_safety_audits":
            metrics = analyzer.get_checklist_metrics("Fire Safety Audit")
            response_text = (
                f"### Fire Safety Audit Results\n\n"
                f"- Total Audits: **{metrics['total_audits']}**\n"
                f"- Passed: **{metrics['passed_audits']}**\n"
                f"- Failed: **{metrics['failed_audits']}**\n"
                f"- Pending: **{metrics['pending_audits']}**\n"
                f"- Pass Rate: **{metrics['pass_rate']:.1f}%**\n"
                f"- Avg Compliance: **{metrics['avg_compliance_score']:.1f}%**\n"
                f"- Avg Risk Score: **{metrics['avg_risk_score']:.1f}**"
            )
            structured_data = metrics

        elif intent == "checklist_completion":
            status_map = analyzer.get_checklist_completion_status()
            response_text = "### Checklist Completion & Pass Rates:\n\n"
            for name, metrics in status_map.items():
                response_text += f"- **{name}**: {metrics['passed_audits']}/{metrics['total_audits']} Passed ({metrics['pass_rate']:.1f}% pass rate) | Avg Compliance: {metrics['avg_compliance_score']:.1f}%\n"
            structured_data = status_map

        elif intent == "recommendations":
            recs = analyzer.generate_recommendations()
            response_text = "### Recommended Corrective Actions:\n\n"
            for idx, r in enumerate(recs, 1):
                response_text += f"{idx}. **[{r['target']}]**: {r['recommendation']}\n"
            structured_data = {"recommendations": recs}

        elif intent == "icu_performance":
            icu_df = analyzer.df[analyzer.df['ward'] == 'ICU']
            total = len(icu_df)
            passed = len(icu_df[icu_df['status'].str.lower() == 'pass'])
            failed = len(icu_df[icu_df['status'].str.lower() == 'fail'])
            pass_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0.0
            avg_risk = icu_df['risk_score'].mean()
            avg_comp = icu_df['compliance_score'].mean()
            
            response_text = (
                f"### ICU Audit Performance\n\n"
                f"- **Total Audits**: {total}\n"
                f"- **Pass Rate**: {pass_rate:.1f}% ({passed} Passed, {failed} Failed)\n"
                f"- **Average Risk Score**: {avg_risk:.1f} (Hospital Avg: {analyzer.get_hospital_risk_score():.1f})\n"
                f"- **Average Compliance**: {avg_comp:.1f}% (Hospital Avg: {analyzer.get_compliance_score():.1f}%)"
            )
            structured_data = {"total": total, "pass_rate": pass_rate, "avg_risk": avg_risk, "avg_comp": avg_comp}

        elif intent == "floor_wise_risk":
            floor_risk = analyzer.df.groupby('floor')['risk_score'].mean().reset_index()
            response_text = "### Average Risk Score by Floor:\n\n"
            for _, row in floor_risk.iterrows():
                response_text += f"- **Floor {int(row['floor'])}**: Risk score of **{row['risk_score']:.1f}**\n"
            structured_data = floor_risk.to_dict(orient='records')

        elif intent == "critical_issues":
            crit_esc = analyzer.get_critical_escalations()
            failed_audits = analyzer.get_failed_audits()
            # Find overlaps or combine
            crit_count = len(crit_esc)
            fail_count = len(failed_audits)
            
            response_text = (
                f"### Critical Issues Report\n\n"
                f"- **Open Critical Escalations**: **{crit_count}**\n"
                f"- **Failed Audits**: **{fail_count}**\n\n"
                f"Immediate intervention is advised for the following critical escalations:\n"
            )
            for _, row in crit_esc.head(5).iterrows():
                response_text += f"- **Audit {row['audit_id']}** in {row['ward']} ward (Floor {row['floor']}): '{row['checklist_type']}' failed (Risk Score: {row['risk_score']}). Assigned to: {row['assigned_staff']}.\n"
            structured_data = {"critical_escalations": crit_count, "failed_audits": fail_count}

        elif intent == "delayed_audits":
            # Let's say audits taking > 45 minutes are delayed
            delayed = analyzer.df[analyzer.df['completion_time'] > 45]
            count = len(delayed)
            response_text = f"We have identified **{count}** audits that experienced significant delays (completion time > 45 minutes).\n\n"
            if count > 0:
                response_text += "**Sample of Delayed Audits:**\n"
                for _, row in delayed.head(5).iterrows():
                    response_text += f"- **{row['audit_id']}**: {row['checklist_type']} in {row['ward']} took **{row['completion_time']} mins** (Assigned: {row['assigned_staff']})\n"
            structured_data = {"count": count}

        elif intent == "risk_trends":
            trends = analyzer.get_predictive_analytics()
            overall_risk = analyzer.get_hospital_risk_score()
            
            response_text = (
                f"### Risk Trend Analysis\n\n"
                f"- **Overall average risk**: **{overall_risk:.1f}**\n"
                f"- **ICU risk trend**: {trends['icu_risk_change']}\n"
                f"- **Failure trend**: {trends['failure_trend']}\n"
                f"- **Staff risk patterns**: {trends['staff_risk_pattern']}"
            )
            structured_data = trends

        elif intent == "icu_hygiene_risk":
            trend = analyzer.get_icu_hygiene_risk_trend()
            response_text = (
                f"### ICU Hygiene Risk Status\n\n"
                f"- **Analysis**: {trend['text']}\n"
                f"- **Detail**: The linear regression of ICU hygiene risk scores shows a **{trend['direction']}** trend over our audit timeline."
            )
            structured_data = trend

        elif intent == "nabh_compliance_trend":
            trend = analyzer.get_nabh_compliance_weekly_trend()
            response_text = (
                f"### NABH Compliance Weekly Trend\n\n"
                f"- **Analysis**: {trend['text']}\n"
                f"- **Detail**: The weekly moving average of our compliance score is **{trend['direction']}**."
            )
            structured_data = trend

        else: # Fallback / Default HELP
            response_text = (
                "I'm not completely sure I understood that question in the context of our audit logs. "
                "Here are some examples of questions you can ask me:\n\n"
                "- *\"Which ward has highest risk?\"*\n"
                "- *\"Show pending audits\"*\n"
                "- *\"Show failed audits\"*\n"
                "- *\"Show open escalations\"*\n"
                "- *\"Show compliance score\"*\n"
                "- *\"Best performing staff?\"*\n"
                "- *\"Show floor-wise risk\"*\n"
                "- *\"Show audit summary\"*\n"
                "- *\"Predict future risk\"*\n"
                "- *\"Show recommendations\"*"
            )

        return jsonify({
            "response": response_text,
            "intent": intent,
            "similarity": similarity if 'similarity' in locals() else 1.0,
            "data": structured_data
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
