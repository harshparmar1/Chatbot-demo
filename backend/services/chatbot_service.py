import os
import pandas as pd
from utils.ollama_client import OllamaClient

class ChatbotService:
    def __init__(self, analyzer, semantic_search):
        self.analyzer = analyzer
        self.semantic_search = semantic_search
        self.ollama = OllamaClient()

    def format_rows_as_context(self, df):
        """
        Formats a dataframe of audit logs into a clean, text-based format for Qwen context.
        """
        if df.empty:
            return "No matching audit logs found."
            
        context_str = ""
        # Limit columns to prevent sending too much token data
        cols_to_use = ['Created By', 'Created At', 'Location', 'Checklist Name', 'Remarks', 'Status', 'risk_score', 'compliance_score']
        
        for idx, row in df.head(10).iterrows():
            context_str += f"- Creator: {row['Created By']} | Date: {row['Created At']} | Location: {row['Location']} | Checklist: {row['Checklist Name']} | Remarks: {row['Remarks']} | Status: {row['Status']} | Predicted Risk: {row.get('risk_score', 0):.1f} | Predicted Compliance: {row.get('compliance_score', 100):.1f}\n"
            
        return context_str

    def get_response(self, user_message):
        """
        Processes query via the RAG workflow.
        """
        # 1. Classify Intent via Semantic Search
        intent, similarity = self.semantic_search.predict_intent(user_message)
        print(f"[RAG] Message: '{user_message}' -> Classified Intent: '{intent}' (Similarity: {similarity:.2f})")
        
        df = self.analyzer.df
        
        # 2. Python Data Analysis based on Intent
        python_summary = ""
        relevant_df = pd.DataFrame()
        structured_data = {}
        
        # We execute calculations first in Python
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
            return {
                "response": response_text,
                "intent": intent,
                "similarity": similarity,
                "data": {}
            }
            
        elif intent == "highest_risk_ward":
            ward, score = self.analyzer.get_highest_risk_ward()
            ward_df = df[df["ward"] == ward] if ward else pd.DataFrame()
            fails = len(ward_df[ward_df["status"] == "Fail"]) if not ward_df.empty else 0
            opens = len(ward_df[ward_df["escalation_status"] == "Open"]) if not ward_df.empty else 0
            criticals = len(ward_df[ward_df["priority"] == "Critical"]) if not ward_df.empty else 0
            
            python_summary = (
                f"Ward with highest risk is: {ward}\n"
                f"Average predicted risk score: {score:.1f}\n"
                f"Failed audits: {fails}\n"
                f"Open escalations: {opens}\n"
                f"Critical priority audits: {criticals}"
            )
            relevant_df = ward_df
            structured_data = {"ward": ward, "score": score}

        elif intent == "highest_risk_floor":
            floor, score = self.analyzer.get_highest_risk_floor()
            floor_df = df[df["floor"] == floor]
            fails = len(floor_df[floor_df["status"] == "Fail"])
            opens = len(floor_df[floor_df["escalation_status"] == "Open"])
            criticals = len(floor_df[floor_df["priority"] == "Critical"])
            
            python_summary = (
                f"Floor with highest risk is: Floor {floor}\n"
                f"Average predicted risk score: {score:.1f}\n"
                f"Failed audits: {fails}\n"
                f"Open escalations: {opens}\n"
                f"Critical priority audits: {criticals}"
            )
            relevant_df = floor_df
            structured_data = {"floor": floor, "score": score}

        elif intent == "hospital_risk_score":
            score = self.analyzer.get_hospital_risk_score()
            fails = len(df[df["status"] == "Fail"])
            pendings = len(df[df["status"] == "Pending"])
            opens = len(df[df["escalation_status"] == "Open"])
            
            python_summary = (
                f"Overall hospital average risk score: {score:.1f}\n"
                f"Total failed audits: {fails}\n"
                f"Total pending audits: {pendings}\n"
                f"Total open escalations: {opens}"
            )
            relevant_df = df[df["Status"] == "Fail"]
            structured_data = {"score": score}

        elif intent == "icu_risk_score":
            score = self.analyzer.get_icu_risk_score()
            icu_df = df[df["ward"] == "ICU"]
            fails = len(icu_df[icu_df["status"] == "Fail"])
            opens = len(icu_df[icu_df["escalation_status"] == "Open"])
            
            python_summary = (
                f"ICU Ward average risk score: {score:.1f}\n"
                f"Total failed audits in ICU: {fails}\n"
                f"Total open escalations in ICU: {opens}"
            )
            relevant_df = icu_df
            structured_data = {"score": score}

        elif intent == "predict_future_risk":
            pred_data = self.analyzer.predict_future_risk()
            slope = pred_data["slope"]
            trend = "increasing" if slope > 0 else "decreasing"
            
            python_summary = (
                f"Future risk forecast model summary:\n"
                f"Current hospital average risk: {self.analyzer.get_hospital_risk_score():.1f}\n"
                f"Risk slope daily trend coefficient: {slope:.4f} ({trend})\n"
                f"Predicted average risk in 7 days: {pred_data['prediction_7d']:.1f}\n"
                f"Predicted average risk in 30 days: {pred_data['prediction_30d']:.1f}\n"
                f"Historical comparison percent change: {pred_data['comparison_change']:.1f}%"
            )
            relevant_df = df.sort_values("date", ascending=False)
            structured_data = pred_data

        elif intent == "compliance_score":
            score = self.analyzer.get_compliance_score()
            compliant_count = len(df[df["compliance_score"] >= 80])
            
            python_summary = (
                f"Hospital average compliance score: {score:.1f}%\n"
                f"Total audits compliant (score >= 80): {compliant_count} out of {len(df)} ({compliant_count/len(df)*100:.1f}%)"
            )
            relevant_df = df[df["compliance_score"] < 80]
            structured_data = {"compliance_score": score}

        elif intent == "nabh_compliance":
            score = self.analyzer.get_nabh_compliance()
            compliant_count = len(df[df["compliance_score"] >= 80])
            
            python_summary = (
                f"Hospital NABH standards compliance rate: {score:.1f}%\n"
                f"NABH compliance benchmark: 85.0%\n"
                f"Description: NABH rate is the percentage of audits scoring 80% or above in compliance.\n"
                f"Currently meeting the standard: {compliant_count} out of {len(df)} audits."
            )
            relevant_df = df[df["compliance_score"] < 80]
            structured_data = {"nabh_compliance": score}

        elif intent == "lowest_compliance_dept":
            dept, score = self.analyzer.get_lowest_compliance_dept()
            dept_df = df[df["department"] == dept] if dept else pd.DataFrame()
            fails = len(dept_df[dept_df["status"] == "Fail"]) if not dept_df.empty else 0
            opens = len(dept_df[dept_df["escalation_status"] == "Open"]) if not dept_df.empty else 0
            
            python_summary = (
                f"Department with lowest compliance: {dept}\n"
                f"Average compliance score: {score:.1f}%\n"
                f"Failed audits: {fails}\n"
                f"Open escalations: {opens}"
            )
            relevant_df = dept_df
            structured_data = {"department": dept, "score": score}

        elif intent == "compliance_trend":
            trend_data = self.analyzer.get_compliance_trend()
            
            python_summary = (
                f"Hospital compliance trend direction: {trend_data['trend_direction']}\n"
                f"Compliance slope daily trend coefficient: {trend_data['slope']:.4f}\n"
                f"Current average compliance score: {self.analyzer.get_compliance_score():.1f}%"
            )
            relevant_df = df.sort_values("date", ascending=False)
            structured_data = trend_data

        elif intent == "pending_audits":
            pending = self.analyzer.get_pending_audits()
            crit_count = len(pending[pending["priority"] == "Critical"])
            high_count = len(pending[pending["priority"] == "High"])
            
            python_summary = (
                f"Total pending audits in system: {len(pending)}\n"
                f"Critical priority pending: {crit_count}\n"
                f"High priority pending: {high_count}"
            )
            relevant_df = pending
            structured_data = {"count": len(pending)}

        elif intent == "completed_audits":
            passed_df = df[df["status"] == "Pass"]
            failed_df = df[df["status"] == "Fail"]
            
            python_summary = (
                f"Total completed audits in system: {len(passed_df) + len(failed_df)}\n"
                f"Passed audits: {len(passed_df)}\n"
                f"Failed audits: {len(failed_df)}"
            )
            relevant_df = passed_df
            structured_data = {"count": len(passed_df)}

        elif intent == "failed_audits":
            failed = self.analyzer.get_failed_audits()
            opens = len(failed[failed["escalation_status"] == "Open"])
            criticals = len(failed[failed["priority"] == "Critical"])
            
            python_summary = (
                f"Total failed audits in system: {len(failed)}\n"
                f"Open escalations associated with failures: {opens}\n"
                f"Critical priority failures: {criticals}"
            )
            relevant_df = failed
            structured_data = {"count": len(failed)}

        elif intent == "todays_audits":
            todays = self.analyzer.get_todays_audits()
            date_str = self.analyzer.max_date.strftime("%Y-%m-%d")
            passed = len(todays[todays["status"] == "Pass"])
            pending = len(todays[todays["status"] == "Pending"])
            failed = len(todays[todays["status"] == "Fail"])
            
            python_summary = (
                f"Audits recorded on today/latest date ({date_str}): {len(todays)}\n"
                f"Passed: {passed}\n"
                f"Pending: {pending}\n"
                f"Failed: {failed}"
            )
            relevant_df = todays
            structured_data = {"count": len(todays), "date": date_str}

        elif intent == "weeks_audits":
            weeks = self.analyzer.get_weeks_audits()
            passed = len(weeks[weeks["status"] == "Pass"])
            pending = len(weeks[weeks["status"] == "Pending"])
            failed = len(weeks[weeks["status"] == "Fail"])
            
            python_summary = (
                f"Audits in the last 7 days of dataset: {len(weeks)}\n"
                f"Passed: {passed}\n"
                f"Pending: {pending}\n"
                f"Failed: {failed}"
            )
            relevant_df = weeks
            structured_data = {"count": len(weeks)}

        elif intent == "audit_summary":
            summary = self.analyzer.get_audit_summary()
            
            python_summary = (
                f"Overall Hospital Audit Summary:\n"
                f"Total Audits in CSV: {summary['total_audits']}\n"
                f"Completed: {summary['completed_audits']} (Passed: {summary['passed_audits']}, Failed: {summary['failed_audits']})\n"
                f"Pass Rate among completed audits: {summary['pass_rate']:.1f}%\n"
                f"Pending: {summary['pending_audits']}\n"
                f"Average audit completion time: {summary['avg_completion_time_mins']:.1f} minutes"
            )
            relevant_df = df[df["Status"] == "Fail"]
            structured_data = summary

        elif intent == "open_escalations":
            open_esc = self.analyzer.get_open_escalations()
            criticals = len(open_esc[open_esc["priority"] == "Critical"])
            highs = len(open_esc[open_esc["priority"] == "High"])
            
            python_summary = (
                f"Total active open escalations: {len(open_esc)}\n"
                f"Critical priority open escalations: {criticals}\n"
                f"High priority open escalations: {highs}"
            )
            relevant_df = open_esc
            structured_data = {"count": len(open_esc)}

        elif intent == "closed_escalations":
            closed_esc = self.analyzer.get_closed_escalations()
            
            python_summary = (
                f"Total closed/resolved escalations: {len(closed_esc)}"
            )
            relevant_df = closed_esc
            structured_data = {"count": len(closed_esc)}

        elif intent == "most_escalations_floor":
            floor, count = self.analyzer.get_most_escalations_floor()
            floor_df = df[df["floor"] == floor]
            opens = len(floor_df[floor_df["escalation_status"] == "Open"])
            
            python_summary = (
                f"Floor with highest volume of escalations is: Floor {floor}\n"
                f"Total escalations count: {count}\n"
                f"Active open escalations on this floor: {opens}"
            )
            relevant_df = floor_df
            structured_data = {"floor": floor, "count": count}

        elif intent == "critical_escalations":
            crit = self.analyzer.get_critical_escalations()
            
            python_summary = (
                f"Total open critical escalations: {len(crit)}"
            )
            relevant_df = crit
            structured_data = {"count": len(crit)}

        elif intent == "best_staff":
            staff, pass_rate, comp = self.analyzer.get_best_staff()
            staff_df = df[df["assigned_staff"] == staff] if staff else pd.DataFrame()
            
            python_summary = (
                f"Top performing audit creator/user: {staff}\n"
                f"Audit pass rate: {pass_rate:.1f}%\n"
                f"Average compliance score of audits: {comp:.1f}%\n"
                f"Total audits performed: {len(staff_df)}"
            )
            relevant_df = staff_df
            structured_data = {"staff": staff, "pass_rate": pass_rate, "compliance": comp}

        elif intent == "worst_staff":
            staff, pass_rate, comp = self.analyzer.get_lowest_performing_staff()
            staff_df = df[df["assigned_staff"] == staff] if staff else pd.DataFrame()
            fails = len(staff_df[staff_df["status"] == "Fail"]) if not staff_df.empty else 0
            
            python_summary = (
                f"Lowest performing audit creator/user: {staff}\n"
                f"Audit pass rate: {pass_rate:.1f}%\n"
                f"Average compliance score of audits: {comp:.1f}%\n"
                f"Total audits performed: {len(staff_df)}\n"
                f"Total failures recorded: {fails}"
            )
            relevant_df = staff_df
            structured_data = {"staff": staff, "pass_rate": pass_rate, "compliance": comp}

        elif intent == "staff_failed_audits":
            staff, count = self.analyzer.get_staff_with_most_failed_audits()
            staff_df = df[df["assigned_staff"] == staff] if staff else pd.DataFrame()
            
            python_summary = (
                f"User who created the most failed audits: {staff}\n"
                f"Total failed audits created: {count}\n"
                f"Total audits created: {len(staff_df)}"
            )
            relevant_df = staff_df[staff_df["Status"] == "Fail"]
            structured_data = {"staff": staff, "count": count}

        elif intent == "staff_needs_attention":
            attention = self.analyzer.get_staff_needs_attention()
            
            python_summary = (
                f"Users/Creators needing attention (low pass rates or multiple failures):\n"
            )
            for row in attention[:5]:
                python_summary += f"- {row['assigned_staff']}: Pass Rate {row['pass_rate']:.1f}% | Failed Audits: {row['failed_audits']}\n"
            relevant_df = df[df["Created By"].isin([r['assigned_staff'] for r in attention[:3]])]
            structured_data = {"attention": attention}

        elif intent == "recommendations":
            recs = self.analyzer.generate_recommendations()
            
            python_summary = "Calculated recommendations rule output:\n"
            for r in recs[:5]:
                python_summary += f"- [{r['target']}]: {r['recommendation']}\n"
            relevant_df = df[df["Status"] == "Fail"]
            structured_data = {"recommendations": recs}

        elif intent in ["hygiene_audits", "safety_audits", "waste_audits", "fire_safety_audits"]:
            mapping = {
                "hygiene_audits": "Hygiene Audit",
                "safety_audits": "Safety Audit",
                "waste_audits": "Waste Audit",
                "fire_safety_audits": "Fire Safety Audit"
            }
            chk_type = mapping[intent]
            metrics = self.analyzer.get_checklist_metrics(chk_type)
            
            python_summary = (
                f"Performance summary for {chk_type} Checklists:\n"
                f"Total Audits: {metrics['total_audits']}\n"
                f"Passed: {metrics['passed_audits']} | Failed: {metrics['failed_audits']} | Pending: {metrics['pending_audits']}\n"
                f"Pass Rate: {metrics['pass_rate']:.1f}%\n"
                f"Average Compliance Score: {metrics['avg_compliance_score']:.1f}%\n"
                f"Average Risk Score: {metrics['avg_risk_score']:.1f}"
            )
            relevant_df = df[df["checklist_type"] == chk_type]
            structured_data = metrics

        elif intent == "icu_performance":
            icu_df = df[df["ward"] == "ICU"]
            passed = len(icu_df[icu_df["status"] == "Pass"])
            failed = len(icu_df[icu_df["status"] == "Fail"])
            pass_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0.0
            
            python_summary = (
                f"ICU Performance Metrics:\n"
                f"Total audits: {len(icu_df)}\n"
                f"Passed: {passed} | Failed: {failed}\n"
                f"Pass Rate: {pass_rate:.1f}%\n"
                f"Average risk score: {icu_df['risk_score'].mean():.1f}\n"
                f"Average compliance score: {icu_df['compliance_score'].mean():.1f}%"
            )
            relevant_df = icu_df
            structured_data = {"total": len(icu_df), "pass_rate": pass_rate}

        elif intent == "floor_wise_risk":
            floor_risk = df.groupby("floor")["risk_score"].mean().reset_index()
            
            python_summary = "Floor-wise Risk Score analysis:\n"
            for _, row in floor_risk.iterrows():
                python_summary += f"- Floor {int(row['floor'])}: Average predicted risk is {row['risk_score']:.1f}\n"
            relevant_df = df
            structured_data = floor_risk.to_dict(orient="records")

        elif intent == "critical_issues":
            crit_esc = self.analyzer.get_critical_escalations()
            failed_audits = self.analyzer.get_failed_audits()
            
            python_summary = (
                f"Found {len(crit_esc)} open critical escalations and {len(failed_audits)} failed audits in dataset."
            )
            relevant_df = pd.concat([crit_esc, failed_audits]).drop_duplicates(subset=['audit_id'])
            structured_data = {"critical_escalations": len(crit_esc), "failed_audits": len(failed_audits)}

        elif intent == "delayed_audits":
            delayed = df[df["completion_time"] > 45]
            
            python_summary = (
                f"Identified {len(delayed)} audits that took longer than 45 minutes to complete."
            )
            relevant_df = delayed
            structured_data = {"count": len(delayed)}

        elif intent == "risk_trends":
            trends = self.analyzer.get_predictive_analytics()
            
            python_summary = (
                f"General Hospital Risk Trends Summary:\n"
                f"ICU Risk: {trends['icu_risk_change']}\n"
                f"Failure Trend: {trends['failure_trend']}\n"
                f"Escalation Trend: {trends['escalation_trend']}\n"
                f"Staff Risk Pattern: {trends['staff_risk_pattern']}"
            )
            relevant_df = df.sort_values("date", ascending=False)
            structured_data = trends

        elif intent == "icu_hygiene_risk":
            trend = self.analyzer.get_icu_hygiene_risk_trend()
            
            python_summary = (
                f"ICU Hygiene Risk trend details:\n"
                f"Trend context: {trend['text']}\n"
                f"Slope: {trend['slope']:.4f} risk units/day\n"
                f"Direction: {trend['direction']}"
            )
            relevant_df = df[(df["ward"] == "ICU") & (df["checklist_type"] == "Hygiene Audit")]
            structured_data = trend

        elif intent == "nabh_compliance_trend":
            trend = self.analyzer.get_nabh_compliance_weekly_trend()
            
            python_summary = (
                f"NABH compliance weekly trend details:\n"
                f"Trend context: {trend['text']}\n"
                f"Slope: {trend['slope']:.4f} compliance units/week\n"
                f"Direction: {trend['direction']}"
            )
            relevant_df = df
            structured_data = trend

        else: # FALLBACK / Generic Semantic Search RAG
            # First, check if the query mentions a specific location, user or checklist
            # Let's perform row semantic search to find top 5 relevant rows
            relevant_df, sim_scores = self.semantic_search.retrieve_relevant_rows(user_message, df, top_k=5)
            
            python_summary = (
                f"Matched relevant audit records based on semantic similarity to: '{user_message}'\n"
                f"Found {len(relevant_df)} matching logs."
            )
            structured_data = {}

        # If no relevant_df was retrieved or it's empty, use the whole df as context limit
        if relevant_df.empty:
            relevant_df = df
            
        # Get top matching rows context
        context_rows_str = self.format_rows_as_context(relevant_df)
        
        # 3. Create prompt for Qwen
        system_prompt = (
            "You are Reallist AI Audit Assistant, a professional local assistant that explains hospital audit logs and compliance issues. "
            "Use ONLY the calculated python stats and relevant context rows provided. "
            "Explain the results naturally in English. "
            "NEVER calculate or generate numbers; rely strictly on the calculated numbers in the prompt. "
            "Keep the explanation concise, professional, and recommend actionable improvements based on the findings."
        )
        
        user_content = (
            f"User Question: {user_message}\n\n"
            f"--- Python Calculated Data Analysis ---\n"
            f"{python_summary}\n\n"
            f"--- Relevant Context Audit Logs ---\n"
            f"{context_rows_str}\n\n"
            f"Explain these metrics, reasons, and recommend improvements."
        )
        
        # 4. Invoke Ollama Client (Qwen 2.5:7b)
        response_text = ""
        if self.ollama.is_available():
            response_text = self.ollama.generate_explanation(system_prompt, user_content)
        else:
            # Fallback if local Ollama is offline or model is missing
            formatted_summary = python_summary.replace('\n', '\n- ')
            response_text = (
                "### Answer\n"
                "I am having trouble connecting to local **Ollama** (`qwen2.5:7b`) to generate a natural language explanation. "
                "However, I have completed the local calculations on the dataset using Pandas:\n\n"
                f"{formatted_summary}\n\n"
                "**Context Logs Analyzed:**\n"
                f"{context_rows_str}\n\n"
                "*(Please start your local Ollama server to enable full natural language generation)*"
            )
            
        return {
            "response": response_text,
            "intent": intent,
            "similarity": similarity,
            "data": structured_data
        }
