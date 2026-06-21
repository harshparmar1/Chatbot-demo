# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from nlp_engine import NLPIntentClassifier
from data_analyzer import HospitalAuditAnalyzer
import os

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
        # Add additional required dashboard metrics
        df = analyzer.df
        data["critical_issues"] = int(len(df[df["priority"] == "Critical"]))
        data["pending_audits"] = int(len(df[df["status"] == "Pending"]))
        data["failed_audits"] = int(len(df[df["status"] == "Fail"]))
        data["open_escalations"] = int(len(df[df["escalation_status"] == "Open"]))
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

        # Initialize response content
        response_text = ""
        structured_data = {}
        df = analyzer.df

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
            structured_data = {}
            
        elif intent == "highest_risk_ward":
            ward, score = analyzer.get_highest_risk_ward()
            ward_df = df[df["ward"] == ward]
            fails = len(ward_df[ward_df["status"] == "Fail"])
            opens = len(ward_df[ward_df["escalation_status"] == "Open"])
            criticals = len(ward_df[ward_df["priority"] == "Critical"])
            
            response_text = format_response(
                answer=f"The ward with the highest risk is the **{ward}** ward, with an average risk score of **{score:.1f}**.",
                reason_items=[
                    f"**{fails} failed audits** recorded in this ward.",
                    f"**{opens} open escalations** remain active.",
                    f"**{criticals} audits** are flagged with Critical priority."
                ],
                recommendation=f"Increase inspection frequency and deploy senior supervisors to the {ward} ward immediately."
            )
            structured_data = {"ward": ward, "score": score}

        elif intent == "highest_risk_floor":
            floor, score = analyzer.get_highest_risk_floor()
            floor_df = df[df["floor"] == floor]
            fails = len(floor_df[floor_df["status"] == "Fail"])
            opens = len(floor_df[floor_df["escalation_status"] == "Open"])
            criticals = len(floor_df[floor_df["priority"] == "Critical"])
            
            response_text = format_response(
                answer=f"**Floor {floor}** has the highest average risk score of **{score:.1f}**.",
                reason_items=[
                    f"**{fails} failed audits** on this floor.",
                    f"**{opens} active escalations** awaiting supervisor resolution.",
                    f"**{criticals} critical issues** require immediate attention."
                ],
                recommendation=f"Establish targeted compliance sweeps and additional safety checks on Floor {floor}."
            )
            structured_data = {"floor": floor, "score": score}

        elif intent == "hospital_risk_score":
            score = analyzer.get_hospital_risk_score()
            fails = len(df[df["status"] == "Fail"])
            pendings = len(df[df["status"] == "Pending"])
            opens = len(df[df["escalation_status"] == "Open"])
            
            response_text = format_response(
                answer=f"The overall hospital average risk score is **{score:.1f}**.",
                reason_items=[
                    f"Calculated across **{len(df)} total audits**.",
                    f"Contains **{fails} failed audits** and **{pendings} pending audits**.",
                    f"A total of **{opens} open escalations** are pending resolution."
                ],
                recommendation="Prioritize resolving pending critical priority audits to reduce overall hospital risk."
            )
            structured_data = {"score": score}

        elif intent == "icu_risk_score":
            score = analyzer.get_icu_risk_score()
            icu_df = df[df["ward"] == "ICU"]
            fails = len(icu_df[icu_df["status"] == "Fail"])
            opens = len(icu_df[icu_df["escalation_status"] == "Open"])
            
            response_text = format_response(
                answer=f"The average risk score for the **ICU** ward is **{score:.1f}**.",
                reason_items=[
                    f"**{fails} failed audits** out of {len(icu_df)} total ICU records.",
                    f"**{opens} open escalations** require immediate resolution."
                ],
                recommendation="Deploy senior hygiene officers to the ICU and implement daily audits."
            )
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
            
            response_text = format_response(
                answer=f"Predicted hospital risk is **{pred_data['prediction_7d']:.1f}** in 7 days and **{pred_data['prediction_30d']:.1f}** in 30 days.",
                reason_items=[
                    f"Current average hospital risk score is **{analyzer.get_hospital_risk_score():.1f}**.",
                    f"Linear regression shows a daily slope trend of **{slope:.4f}** ({trend}).",
                    f"Historical comparison: {comp_text}"
                ],
                recommendation="Initiate predictive training modules and preemptive checks in high-risk departments."
            )
            structured_data = pred_data

        elif intent == "compliance_score":
            score = analyzer.get_compliance_score()
            compliant_count = len(df[df["compliance_score"] >= 80])
            total = len(df)
            
            response_text = format_response(
                answer=f"The overall compliance score for the hospital is **{score:.1f}%**.",
                reason_items=[
                    f"Average of all audit records in the database.",
                    f"**{compliant_count} out of {total} audits** ({compliant_count/total*100:.1f}%) meet the 80% threshold."
                ],
                recommendation="Enforce standards in underperforming departments to lift the hospital compliance average."
            )
            structured_data = {"compliance_score": score}

        elif intent == "nabh_compliance":
            score = analyzer.get_nabh_compliance()
            compliant_count = len(df[df["compliance_score"] >= 80])
            total = len(df)
            
            response_text = format_response(
                answer=f"The hospital's compliance score under **NABH standards** is **{score:.1f}%**.",
                reason_items=[
                    f"NABH rate is the percentage of audits scoring 80% or above in compliance.",
                    f"Currently, **{compliant_count} out of {total} audits** meet this standard.",
                    "The standard target benchmark is 85%."
                ],
                recommendation="Retrain staff in departments with compliance scores below 85% to reach the certification benchmark."
            )
            structured_data = {"nabh_compliance": score}

        elif intent == "lowest_compliance_dept":
            dept, score = analyzer.get_lowest_compliance_dept()
            dept_df = df[df["department"] == dept]
            fails = len(dept_df[dept_df["status"] == "Fail"])
            opens = len(dept_df[dept_df["escalation_status"] == "Open"])
            
            response_text = format_response(
                answer=f"The department with the lowest compliance is **{dept}** with an average compliance score of **{score:.1f}%**.",
                reason_items=[
                    f"**{fails} failed audits** recorded in {dept}.",
                    f"**{opens} open escalations** currently pending in this department."
                ],
                recommendation=f"Schedule an immediate compliance review and retraining for the {dept} department."
            )
            structured_data = {"department": dept, "score": score}

        elif intent == "compliance_trend":
            trend_data = analyzer.get_compliance_trend()
            direction = trend_data["trend_direction"]
            slope = trend_data["slope"]
            
            response_text = format_response(
                answer=f"The hospital's compliance trend is currently **{direction}**.",
                reason_items=[
                    f"Linear regression slope of daily compliance average is **{slope:.4f}**.",
                    f"Overall compliance average stands at **{analyzer.get_compliance_score():.1f}%**."
                ],
                recommendation="Investigate and address periods of declining compliance to ensure quality standards."
            )
            structured_data = trend_data

        elif intent == "pending_audits":
            pending = analyzer.get_pending_audits()
            count = len(pending)
            crit_count = len(pending[pending["priority"] == "Critical"])
            high_count = len(pending[pending["priority"] == "High"])
            
            response_text = format_response(
                answer=f"There are currently **{count} pending audits** in the system.",
                reason_items=[
                    f"**{crit_count} Critical priority audits** awaiting completion.",
                    f"**{high_count} High priority audits** in progress.",
                    "Pending records represent audits awaiting supervisor approval."
                ],
                recommendation="Instruct assigned staff to prioritize and complete all Critical and High priority pending audits today."
            )
            structured_data = {"count": count, "pending": pending.head(10).to_dict(orient="records")}

        elif intent == "completed_audits":
            passed_df = df[df["status"] == "Pass"]
            count = len(passed_df)
            failed_count = len(df[df["status"] == "Fail"])
            
            response_text = format_response(
                answer=f"There are a total of **{count} completed (Passed) audits** in the system.",
                reason_items=[
                    f"**{count} passed audits** recorded.",
                    f"Contrastingly, there are **{failed_count} failed audits** recorded in completed checks."
                ],
                recommendation="Deploy corrective actions to resolve the failed audits and archive these passed audits."
            )
            structured_data = {"count": count}

        elif intent == "failed_audits":
            failed = analyzer.get_failed_audits()
            count = len(failed)
            opens = len(failed[failed["escalation_status"] == "Open"])
            criticals = len(failed[failed["priority"] == "Critical"])
            
            response_text = format_response(
                answer=f"There are **{count} failed audits** recorded.",
                reason_items=[
                    f"Associated with **{opens} active open escalations**.",
                    f"Contains **{criticals} Critical priority failures**."
                ],
                recommendation="Directly assign senior engineers and hygiene managers to resolve these failed checks."
            )
            structured_data = {"count": count, "failed": failed.head(10).to_dict(orient="records")}

        elif intent == "todays_audits":
            todays = analyzer.get_todays_audits()
            count = len(todays)
            date_str = analyzer.max_date.strftime("%Y-%m-%d")
            passed = len(todays[todays["status"] == "Pass"])
            pending = len(todays[todays["status"] == "Pending"])
            failed = len(todays[todays["status"] == "Fail"])
            
            response_text = format_response(
                answer=f"There are **{count} audits** recorded for the latest date ({date_str}).",
                reason_items=[
                    f"**{passed} passed audits**.",
                    f"**{pending} pending audits**.",
                    f"**{failed} failed audits**."
                ],
                recommendation="Conduct an immediate follow-up on today's failed audits."
            )
            structured_data = {"count": count, "date": date_str}

        elif intent == "weeks_audits":
            weeks = analyzer.get_weeks_audits()
            count = len(weeks)
            passed = len(weeks[weeks["status"] == "Pass"])
            pending = len(weeks[weeks["status"] == "Pending"])
            failed = len(weeks[weeks["status"] == "Fail"])
            
            response_text = format_response(
                answer=f"There are **{count} audits** recorded in the last 7 days.",
                reason_items=[
                    f"**{passed} passed audits**.",
                    f"**{pending} pending audits**.",
                    f"**{failed} failed audits**."
                ],
                recommendation="Verify that weekly feedback loops have been closed for all failures."
            )
            structured_data = {"count": count}

        elif intent == "audit_summary":
            summary = analyzer.get_audit_summary()
            
            response_text = format_response(
                answer=f"The hospital has completed **{summary['total_audits']}** total audits, with a **{summary['pass_rate']:.1f}%** pass rate.",
                reason_items=[
                    f"Passed: **{summary['passed_audits']}** | Failed: **{summary['failed_audits']}** | Pending: **{summary['pending_audits']}**.",
                    f"Average audit completion time is **{summary['avg_completion_time_mins']:.1f} minutes**."
                ],
                recommendation="Focus on optimizing the checklists for departments with low pass rates."
            )
            structured_data = summary

        elif intent == "open_escalations":
            open_esc = analyzer.get_open_escalations()
            count = len(open_esc)
            criticals = len(open_esc[open_esc["priority"] == "Critical"])
            highs = len(open_esc[open_esc["priority"] == "High"])
            
            response_text = format_response(
                answer=f"There are currently **{count} open escalations** in the system.",
                reason_items=[
                    f"**{criticals} escalations** are Critical priority.",
                    f"**{highs} escalations** are High priority.",
                    "Open status indicates a compliance breach awaiting supervisor resolve."
                ],
                recommendation="Resolve Critical escalations first to prevent safety hazards."
            )
            structured_data = {"count": count}

        elif intent == "closed_escalations":
            closed_esc = analyzer.get_closed_escalations()
            count = len(closed_esc)
            
            response_text = format_response(
                answer=f"There are **{count} closed/resolved escalations** in the logs.",
                reason_items=[
                    "Closed status indicates successful correction of compliance failures.",
                    "Represents effective responder activity."
                ],
                recommendation="Document the resolution pathways to help with future troubleshooting."
            )
            structured_data = {"count": count}

        elif intent == "most_escalations_floor":
            floor, count = analyzer.get_most_escalations_floor()
            floor_df = df[df["floor"] == floor]
            opens = len(floor_df[floor_df["escalation_status"] == "Open"])
            
            response_text = format_response(
                answer=f"**Floor {floor}** has the highest volume of escalations, with **{count}** cases.",
                reason_items=[
                    f"Contains **{opens} active open escalations**.",
                    f"Floor {floor} is a hotspot for compliance issues."
                ],
                recommendation=f"Deploy an additional supervisor to Floor {floor} to clear open issues."
            )
            structured_data = {"floor": floor, "count": count}

        elif intent == "critical_escalations":
            crit = analyzer.get_critical_escalations()
            count = len(crit)
            
            response_text = format_response(
                answer=f"There are **{count} critical escalations** currently open.",
                reason_items=[
                    "These open cases are marked as Critical priority.",
                    "Represents severe immediate compliance risks."
                ],
                recommendation="Directly assign senior managers to inspect and close these critical tickets today."
            )
            structured_data = {"count": count}

        elif intent == "escalation_summary":
            summary = analyzer.get_escalation_summary()
            open_by_p = summary["open_by_priority"]
            
            response_text = format_response(
                answer=f"Total Escalations: **{summary['total_escalations']}** (**{summary['open_escalations']}** open, **{summary['closed_escalations']}** closed).",
                reason_items=[
                    f"Critical open: **{open_by_p.get('Critical', 0) or open_by_p.get('critical', 0)}**",
                    f"High open: **{open_by_p.get('High', 0) or open_by_p.get('high', 0)}**",
                    f"Medium open: **{open_by_p.get('Medium', 0) or open_by_p.get('medium', 0)}**",
                    f"Low open: **{open_by_p.get('Low', 0) or open_by_p.get('low', 0)}**"
                ],
                recommendation="Direct resources to clear Critical and High priority escalations first."
            )
            structured_data = summary

        elif intent == "best_staff":
            staff, pass_rate, comp = analyzer.get_best_staff()
            staff_df = df[df["assigned_staff"] == staff]
            total_audits = len(staff_df)
            
            response_text = format_response(
                answer=f"The best performing staff member is **{staff}**.",
                reason_items=[
                    f"Achieved a **{pass_rate:.1f}%** audit pass rate.",
                    f"Maintained an average compliance score of **{comp:.1f}%** across {total_audits} audits."
                ],
                recommendation=f"Acknowledge {staff}'s high performance and share their best practices."
            )
            structured_data = {"staff": staff, "pass_rate": pass_rate, "compliance": comp}

        elif intent == "worst_staff":
            staff, pass_rate, comp = analyzer.get_lowest_performing_staff()
            staff_df = df[df["assigned_staff"] == staff]
            total_audits = len(staff_df)
            fails = len(staff_df[staff_df["status"] == "Fail"])
            
            response_text = format_response(
                answer=f"The lowest performing staff member is **{staff}**.",
                reason_items=[
                    f"Has an audit pass rate of only **{pass_rate:.1f}%**.",
                    f"Recorded **{fails} failed audits** out of {total_audits} total audits."
                ],
                recommendation=f"Schedule immediate coaching and refresher training for {staff}."
            )
            structured_data = {"staff": staff, "pass_rate": pass_rate, "compliance": comp}

        elif intent == "staff_failed_audits":
            staff, count = analyzer.get_staff_with_most_failed_audits()
            staff_df = df[df["assigned_staff"] == staff]
            total_audits = len(staff_df)
            
            response_text = format_response(
                answer=f"Staff member **{staff}** has the most failed audits, with **{count}** failures.",
                reason_items=[
                    f"Recorded {count} failures out of {total_audits} audits assigned.",
                    f"Represents a pass rate of **{(total_audits-count)/total_audits*100:.1f}%**."
                ],
                recommendation=f"Assign a mentor to {staff} to guide them through checklist execution."
            )
            structured_data = {"staff": staff, "count": count}

        elif intent == "staff_performance_report":
            metrics = analyzer.get_staff_metrics()
            top_3 = metrics.sort_values('pass_rate', ascending=False).head(3)
            bottom_3 = metrics.sort_values('pass_rate', ascending=True).head(3)
            
            response_text = format_response(
                answer="Staff performance report (Top vs Bottom performers).",
                reason_items=[
                    "Top 3 performers: " + ", ".join([f"{row['assigned_staff']} ({row['pass_rate']:.1f}%)" for _, row in top_3.iterrows()]),
                    "Bottom 3 performers: " + ", ".join([f"{row['assigned_staff']} ({row['pass_rate']:.1f}%)" for _, row in bottom_3.iterrows()])
                ],
                recommendation="Pair underperforming staff with top performers for hands-on mentorship."
            )
            structured_data = {"top": top_3.to_dict(orient='records'), "bottom": bottom_3.to_dict(orient='records')}

        elif intent == "staff_needs_attention":
            attention = analyzer.get_staff_needs_attention()
            
            response_text = format_response(
                answer=f"There are **{len(attention)}** staff members requiring immediate attention.",
                reason_items=[
                    f"**{row['assigned_staff']}**: Pass Rate: {row['pass_rate']:.1f}% (Fails: {row['failed_audits']})"
                    for row in attention[:4]
                ],
                recommendation="Enroll these individuals in mandatory compliance refresher courses."
            )
            structured_data = {"attention": attention}

        elif intent == "hygiene_audits":
            metrics = analyzer.get_checklist_metrics("Hygiene Audit")
            
            response_text = format_response(
                answer=f"Hygiene audits achieved a **{metrics['pass_rate']:.1f}%** pass rate.",
                reason_items=[
                    f"Total hygiene audits: **{metrics['total_audits']}** (Passed: {metrics['passed_audits']}, Failed: {metrics['failed_audits']}).",
                    f"Average compliance score is **{metrics['avg_compliance_score']:.1f}%**.",
                    f"Average risk score is **{metrics['avg_risk_score']:.1f}**."
                ],
                recommendation="Increase random cleaning inspections to maintain hygiene standards."
            )
            structured_data = metrics

        elif intent == "safety_audits":
            metrics = analyzer.get_checklist_metrics("Safety Audit")
            
            response_text = format_response(
                answer=f"Safety audits achieved a **{metrics['pass_rate']:.1f}%** pass rate.",
                reason_items=[
                    f"Total safety audits: **{metrics['total_audits']}** (Passed: {metrics['passed_audits']}, Failed: {metrics['failed_audits']}).",
                    f"Average compliance score is **{metrics['avg_compliance_score']:.1f}%**.",
                    f"Average risk score is **{metrics['avg_risk_score']:.1f}**."
                ],
                recommendation="Enforce strict safety guidelines and verify emergency exits are clear."
            )
            structured_data = metrics

        elif intent == "waste_audits":
            metrics = analyzer.get_checklist_metrics("Waste Audit")
            
            response_text = format_response(
                answer=f"Waste audits achieved a **{metrics['pass_rate']:.1f}%** pass rate.",
                reason_items=[
                    f"Total waste audits: **{metrics['total_audits']}** (Passed: {metrics['passed_audits']}, Failed: {metrics['failed_audits']}).",
                    f"Average compliance score is **{metrics['avg_compliance_score']:.1f}%**.",
                    f"Average risk score is **{metrics['avg_risk_score']:.1f}**."
                ],
                recommendation="Enforce correct waste container segregation and labeling guidelines."
            )
            structured_data = metrics

        elif intent == "fire_safety_audits":
            metrics = analyzer.get_checklist_metrics("Fire Safety Audit")
            
            response_text = format_response(
                answer=f"Fire safety audits achieved a **{metrics['pass_rate']:.1f}%** pass rate.",
                reason_items=[
                    f"Total fire safety audits: **{metrics['total_audits']}** (Passed: {metrics['passed_audits']}, Failed: {metrics['failed_audits']}).",
                    f"Average compliance score is **{metrics['avg_compliance_score']:.1f}%**.",
                    f"Average risk score is **{metrics['avg_risk_score']:.1f}**."
                ],
                recommendation="Replace expired fire extinguishers and review drill compliance."
            )
            structured_data = metrics

        elif intent == "checklist_completion":
            status_map = analyzer.get_checklist_completion_status()
            
            response_text = format_response(
                answer="Completion and performance rate by checklist type.",
                reason_items=[
                    f"**{name}**: {metrics['passed_audits']}/{metrics['total_audits']} passed ({metrics['pass_rate']:.1f}% pass rate)"
                    for name, metrics in status_map.items()
                ],
                recommendation="Modify audit checklists that show low pass rates to improve compliance."
            )
            structured_data = status_map

        elif intent == "recommendations":
            recs = analyzer.generate_recommendations()
            
            response_text = format_response(
                answer="Top recommended corrective actions for the facility.",
                reason_items=[
                    f"**[{r['target']}]**: {r['recommendation']}"
                    for r in recs[:4]
                ],
                recommendation="Implement the top three recommendations immediately to address compliance gaps."
            )
            structured_data = {"recommendations": recs}

        elif intent == "icu_performance":
            icu_df = df[df["ward"] == "ICU"]
            total = len(icu_df)
            passed = len(icu_df[icu_df["status"] == "Pass"])
            failed = len(icu_df[icu_df["status"] == "Fail"])
            pass_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0.0
            avg_risk = icu_df["risk_score"].mean()
            avg_comp = icu_df["compliance_score"].mean()
            
            response_text = format_response(
                answer=f"ICU ward performance: **{pass_rate:.1f}%** pass rate.",
                reason_items=[
                    f"Total ICU audits: {total} (Passed: {passed}, Failed: {failed}).",
                    f"Average Risk Score: {avg_risk:.1f} (Hospital Avg: {analyzer.get_hospital_risk_score():.1f}).",
                    f"Average Compliance Score: {avg_comp:.1f}% (Hospital Avg: {analyzer.get_compliance_score():.1f}%)."
                ],
                recommendation="Enforce daily hygiene and sanitization reviews in the ICU ward."
            )
            structured_data = {"total": total, "pass_rate": pass_rate, "avg_risk": avg_risk, "avg_comp": avg_comp}

        elif intent == "floor_wise_risk":
            floor_risk = df.groupby("floor")["risk_score"].mean().reset_index()
            
            response_text = format_response(
                answer="Floor-wise risk score analysis.",
                reason_items=[
                    f"**Floor {int(row['floor'])}**: average risk score of **{row['risk_score']:.1f}**"
                    for _, row in floor_risk.iterrows()
                ],
                recommendation="Establish extra supervisory audits on floors with elevated risk scores."
            )
            structured_data = floor_risk.to_dict(orient="records")

        elif intent == "critical_issues":
            crit_esc = analyzer.get_critical_escalations()
            failed_audits = analyzer.get_failed_audits()
            
            response_text = format_response(
                answer=f"Found **{len(crit_esc)} open critical escalations** and **{len(failed_audits)} failed audits**.",
                reason_items=[
                    "Critical escalations require immediate safety reviews.",
                    "Failed audits signify compliance deviations."
                ],
                recommendation="Execute emergency action plans to clear all critical priority escalations."
            )
            structured_data = {"critical_escalations": len(crit_esc), "failed_audits": len(failed_audits)}

        elif intent == "delayed_audits":
            delayed = df[df["completion_time"] > 45]
            count = len(delayed)
            
            response_text = format_response(
                answer=f"We have identified **{count} audits** that experienced significant delays (> 45 minutes).",
                reason_items=[
                    f"**{count} delayed records** found in the logs.",
                    "Long audit completion times slow down operational speed."
                ],
                recommendation="Optimize check patterns and retrain staff to complete audits in under 45 minutes."
            )
            structured_data = {"count": count}

        elif intent == "risk_trends":
            trends = analyzer.get_predictive_analytics()
            overall_risk = analyzer.get_hospital_risk_score()
            floor3_waste = analyzer.get_floor_3_waste_trend()
            ot_fire = analyzer.get_ot_fire_safety_trend()
            
            response_text = format_response(
                answer="Overview of risk trends in the hospital.",
                reason_items=[
                    f"Hospital average risk is **{overall_risk:.1f}**.",
                    f"ICU Risk: {trends['icu_risk_change']}",
                    f"Floor 3 Waste: {floor3_waste['text']}",
                    f"OT Fire Safety: {ot_fire['text']}",
                    f"Staff Risk Pattern: {trends['staff_risk_pattern']}"
                ],
                recommendation="Direct immediate compliance attention to resolving rising waste issues on Floor 3 and declining fire safety scores in the OT ward."
            )
            structured_data = {**trends, "floor3_waste": floor3_waste, "ot_fire": ot_fire}

        elif intent == "icu_hygiene_risk":
            trend = analyzer.get_icu_hygiene_risk_trend()
            
            response_text = format_response(
                answer="ICU Hygiene Risk Trend analysis.",
                reason_items=[
                    f"**Analysis**: {trend['text']}",
                    f"Slope: **{trend['slope']:.3f}** units/day."
                ],
                recommendation="Schedule mandatory cleaning inspections during night shifts in the ICU."
            )
            structured_data = trend

        elif intent == "nabh_compliance_trend":
            trend = analyzer.get_nabh_compliance_weekly_trend()
            
            response_text = format_response(
                answer="NABH Compliance Weekly Trend analysis.",
                reason_items=[
                    f"**Analysis**: {trend['text']}",
                    f"Slope: **{trend['slope']:.3f}** units/week."
                ],
                recommendation="Continue current audit processes to sustain positive compliance trends."
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
