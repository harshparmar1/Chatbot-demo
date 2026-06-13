import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression

class HospitalAuditAnalyzer:
    def __init__(self, csv_path="hospital_audit_500.csv"):
        self.csv_path = csv_path
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV file not found at {self.csv_path}")
        
        self.df = pd.read_csv(self.csv_path)
        # Parse date column
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        # Determine the "current" reference date (max date in the dataset)
        if not self.df.empty:
            self.max_date = self.df['date'].max()
        else:
            self.max_date = pd.to_datetime(datetime.now().strftime("%Y-%m-%d"))

    def reload(self):
        self.load_data()

    # 1. Risk Analysis
    def get_highest_risk_ward(self):
        ward_risk = self.df.groupby('ward')['risk_score'].mean().reset_index()
        if ward_risk.empty:
            return None, 0
        idx = ward_risk['risk_score'].idxmax()
        highest = ward_risk.loc[idx]
        return highest['ward'], float(highest['risk_score'])

    def get_highest_risk_floor(self):
        floor_risk = self.df.groupby('floor')['risk_score'].mean().reset_index()
        if floor_risk.empty:
            return None, 0
        idx = floor_risk['risk_score'].idxmax()
        highest = floor_risk.loc[idx]
        return int(highest['floor']), float(highest['risk_score'])

    def get_hospital_risk_score(self):
        if self.df.empty:
            return 0.0
        return float(self.df['risk_score'].mean())

    def get_icu_risk_score(self):
        icu_df = self.df[self.df['ward'] == 'ICU']
        if icu_df.empty:
            return 0.0
        return float(icu_df['risk_score'].mean())

    def predict_future_risk(self):
        # We group by date and train a Linear Regression model
        daily_risk = self.df.groupby('date')['risk_score'].mean().reset_index()
        if len(daily_risk) < 2:
            return {"slope": 0.0, "prediction_7d": float(self.get_hospital_risk_score()), "prediction_30d": float(self.get_hospital_risk_score())}
        
        # Sort by date
        daily_risk = daily_risk.sort_values('date')
        
        # Convert date to days index starting at 0
        min_date = daily_risk['date'].min()
        daily_risk['day_index'] = (daily_risk['date'] - min_date).dt.days
        
        X = daily_risk[['day_index']].values
        y = daily_risk['risk_score'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        slope = float(model.coef_[0])
        last_day = daily_risk['day_index'].max()
        
        pred_7d = float(model.predict([[last_day + 7]])[0])
        pred_30d = float(model.predict([[last_day + 30]])[0])
        
        # Clamp predictions
        pred_7d = max(0.0, min(100.0, pred_7d))
        pred_30d = max(0.0, min(100.0, pred_30d))
        
        # Historical comparison: last 30 days vs previous 30 days
        last_30_days_df = self.df[self.df['date'] >= (self.max_date - timedelta(days=30))]
        prev_30_days_df = self.df[(self.df['date'] < (self.max_date - timedelta(days=30))) & (self.df['date'] >= (self.max_date - timedelta(days=60)))]
        
        comp_change = 0.0
        if not last_30_days_df.empty and not prev_30_days_df.empty:
            l30_mean = last_30_days_df['risk_score'].mean()
            p30_mean = prev_30_days_df['risk_score'].mean()
            if p30_mean > 0:
                comp_change = ((l30_mean - p30_mean) / p30_mean) * 100
                
        return {
            "slope": slope,
            "prediction_7d": pred_7d,
            "prediction_30d": pred_30d,
            "comparison_change": comp_change
        }

    # 2. Compliance Analysis
    def get_compliance_score(self):
        if self.df.empty:
            return 0.0
        return float(self.df['compliance_score'].mean())

    def get_nabh_compliance(self):
        # NABH score: percentage of audits meeting compliance threshold (>= 80 compliance score)
        if self.df.empty:
            return 0.0
        compliant_count = len(self.df[self.df['compliance_score'] >= 80])
        return float((compliant_count / len(self.df)) * 100)

    def get_lowest_compliance_dept(self):
        dept_compliance = self.df.groupby('department')['compliance_score'].mean().reset_index()
        if dept_compliance.empty:
            return None, 0
        idx = dept_compliance['compliance_score'].idxmin()
        lowest = dept_compliance.loc[idx]
        return lowest['department'], float(lowest['compliance_score'])

    def get_compliance_trend(self):
        # We group by date and train a Linear Regression model
        daily_comp = self.df.groupby('date')['compliance_score'].mean().reset_index()
        if len(daily_comp) < 2:
            return {"slope": 0.0, "trend_direction": "stable"}
            
        daily_comp = daily_comp.sort_values('date')
        min_date = daily_comp['date'].min()
        daily_comp['day_index'] = (daily_comp['date'] - min_date).dt.days
        
        X = daily_comp[['day_index']].values
        y = daily_comp['compliance_score'].values
        
        model = LinearRegression()
        model.fit(X, y)
        slope = float(model.coef_[0])
        
        if slope > 0.05:
            trend_direction = "improving"
        elif slope < -0.05:
            trend_direction = "declining"
        else:
            trend_direction = "stable"
            
        return {
            "slope": slope,
            "trend_direction": trend_direction
        }

    # 3. Audit Analysis
    def get_pending_audits(self):
        return self.df[self.df['status'].str.lower() == 'pending']

    def get_completed_audits(self):
        return self.df[self.df['status'].str.lower().isin(['pass', 'fail'])]

    def get_failed_audits(self):
        return self.df[self.df['status'].str.lower() == 'fail']

    def get_todays_audits(self):
        # Simulated "today" is the max date in the CSV
        return self.df[self.df['date'] == self.max_date]

    def get_weeks_audits(self):
        # Simulated "this week" is the last 7 days of the dataset
        start_week = self.max_date - timedelta(days=6)
        return self.df[(self.df['date'] >= start_week) & (self.df['date'] <= self.max_date)]

    def get_audit_summary(self):
        total = len(self.df)
        pending = len(self.get_pending_audits())
        failed = len(self.get_failed_audits())
        passed = len(self.df[self.df['status'].str.lower() == 'pass'])
        
        avg_completion = float(self.df['completion_time'].mean()) if total > 0 else 0.0
        pass_rate = float((passed / (passed + failed)) * 100) if (passed + failed) > 0 else 0.0
        
        return {
            "total_audits": total,
            "pending_audits": pending,
            "failed_audits": failed,
            "completed_audits": passed + failed,
            "passed_audits": passed,
            "pass_rate": pass_rate,
            "avg_completion_time_mins": avg_completion
        }

    # 4. Escalation Analysis
    def get_open_escalations(self):
        return self.df[self.df['escalation_status'].str.lower() == 'open']

    def get_closed_escalations(self):
        return self.df[self.df['escalation_status'].str.lower() == 'closed']

    def get_most_escalations_floor(self):
        open_esc = self.get_open_escalations()
        if open_esc.empty:
            # Fallback to total escalations if no open ones
            open_esc = self.df[self.df['escalation_status'].str.lower().isin(['open', 'closed'])]
            if open_esc.empty:
                return None, 0
        floor_esc = open_esc.groupby('floor').size().reset_index(name='count')
        idx = floor_esc['count'].idxmax()
        highest = floor_esc.loc[idx]
        return int(highest['floor']), int(highest['count'])

    def get_critical_escalations(self):
        return self.df[(self.df['escalation_status'].str.lower() == 'open') & (self.df['priority'].str.lower() == 'critical')]

    def get_escalation_summary(self):
        open_esc = len(self.get_open_escalations())
        closed_esc = len(self.get_closed_escalations())
        total = open_esc + closed_esc
        
        open_by_priority = self.get_open_escalations().groupby('priority').size().to_dict()
        # Ensure standard keys are present
        for p in ['Low', 'Medium', 'High', 'Critical']:
            if p not in open_by_priority and p.lower() not in open_by_priority:
                open_by_priority[p] = 0
                
        return {
            "total_escalations": total,
            "open_escalations": open_esc,
            "closed_escalations": closed_esc,
            "open_by_priority": open_by_priority
        }

    # 5. Staff Performance Analysis
    def get_staff_metrics(self):
        # Calculate stats per staff
        staff_groups = self.df.groupby('assigned_staff')
        staff_report = []
        
        for name, group in staff_groups:
            total_assigned = len(group)
            passed = len(group[group['status'].str.lower() == 'pass'])
            failed = len(group[group['status'].str.lower() == 'fail'])
            pending = len(group[group['status'].str.lower() == 'pending'])
            
            pass_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0.0
            avg_comp = float(group['completion_time'].mean())
            avg_compliance = float(group['compliance_score'].mean())
            avg_risk = float(group['risk_score'].mean())
            
            staff_report.append({
                "assigned_staff": name,
                "total_audits": total_assigned,
                "passed_audits": passed,
                "failed_audits": failed,
                "pending_audits": pending,
                "pass_rate": pass_rate,
                "avg_completion_time": avg_comp,
                "avg_compliance_score": avg_compliance,
                "avg_risk_score": avg_risk
            })
            
        return pd.DataFrame(staff_report)

    def get_best_staff(self):
        metrics = self.get_staff_metrics()
        if metrics.empty:
            return None, 0
        # Filter for staff with at least 5 audits to avoid sample size bias, fallback if none
        filtered = metrics[metrics['total_audits'] >= 5]
        if filtered.empty:
            filtered = metrics
        # Best: highest pass_rate, then highest average compliance
        best = filtered.sort_values(by=['pass_rate', 'avg_compliance_score'], ascending=False).iloc[0]
        return best['assigned_staff'], float(best['pass_rate']), float(best['avg_compliance_score'])

    def get_lowest_performing_staff(self):
        metrics = self.get_staff_metrics()
        if metrics.empty:
            return None, 0
        filtered = metrics[metrics['total_audits'] >= 5]
        if filtered.empty:
            filtered = metrics
        # Worst: lowest pass_rate, then lowest average compliance
        worst = filtered.sort_values(by=['pass_rate', 'avg_compliance_score'], ascending=True).iloc[0]
        return worst['assigned_staff'], float(worst['pass_rate']), float(worst['avg_compliance_score'])

    def get_staff_with_most_failed_audits(self):
        metrics = self.get_staff_metrics()
        if metrics.empty:
            return None, 0
        most_failed = metrics.sort_values(by='failed_audits', ascending=False).iloc[0]
        return most_failed['assigned_staff'], int(most_failed['failed_audits'])

    def get_staff_needs_attention(self):
        # Returns staff with pass rate < 60% or with open escalations on their failed audits
        metrics = self.get_staff_metrics()
        if metrics.empty:
            return []
        
        # Staff needing attention: low pass rate or high failed count
        attention_staff = metrics[(metrics['pass_rate'] < 60) | (metrics['failed_audits'] >= 3)]
        attention_staff = attention_staff.sort_values(by='pass_rate', ascending=True)
        return attention_staff.to_dict(orient='records')

    # 6. Checklist Insights
    def get_checklist_metrics(self, checklist_type):
        subset = self.df[self.df['checklist_type'].str.lower() == checklist_type.lower()]
        if subset.empty:
            return {"count": 0, "pass_rate": 0.0, "avg_compliance": 0.0, "avg_risk": 0.0}
            
        total = len(subset)
        passed = len(subset[subset['status'].str.lower() == 'pass'])
        failed = len(subset[subset['status'].str.lower() == 'fail'])
        pending = len(subset[subset['status'].str.lower() == 'pending'])
        
        pass_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0.0
        avg_comp = float(subset['compliance_score'].mean())
        avg_risk = float(subset['risk_score'].mean())
        
        return {
            "checklist_type": checklist_type,
            "total_audits": total,
            "passed_audits": passed,
            "failed_audits": failed,
            "pending_audits": pending,
            "pass_rate": pass_rate,
            "avg_compliance_score": avg_comp,
            "avg_risk_score": avg_risk
        }

    def get_checklist_completion_status(self):
        # Group status by checklist type
        checklists = self.df['checklist_type'].unique()
        results = {}
        for c in checklists:
            results[c] = self.get_checklist_metrics(c)
        return results

    # 7. Predictive Analytics & Trends
    def get_predictive_analytics(self):
        # ICU Risk Change calculation (similar to example)
        icu_df = self.df[self.df['ward'] == 'ICU'].sort_values('date')
        icu_change_text = "ICU risk has remained stable compared to previous audits."
        if len(icu_df) >= 10:
            midpoint = len(icu_df) // 2
            prev_half = icu_df.iloc[:midpoint]
            recent_half = icu_df.iloc[midpoint:]
            prev_risk = prev_half['risk_score'].mean()
            recent_risk = recent_half['risk_score'].mean()
            
            if prev_risk > 0:
                diff_percent = ((recent_risk - prev_risk) / prev_risk) * 100
                direction = "increased" if diff_percent > 0 else "decreased"
                icu_change_text = f"ICU risk has {direction} by {abs(diff_percent):.1f}% compared to previous audits."
        
        # Scikit-learn Linear Regression on overall failure rate over time
        # Group failures by month
        self.df['month_year'] = self.df['date'].dt.to_period('M')
        monthly_status = self.df.groupby(['month_year', 'status']).size().unstack(fill_value=0)
        
        failure_trend_text = "Failure rates are holding steady across standard checkpoints."
        if not monthly_status.empty and 'Fail' in monthly_status.columns:
            monthly_status['total'] = monthly_status.sum(axis=1)
            monthly_status['fail_rate'] = (monthly_status['Fail'] / monthly_status['total']) * 100
            
            monthly_status = monthly_status.reset_index()
            monthly_status['month_idx'] = range(len(monthly_status))
            
            if len(monthly_status) >= 2:
                X = monthly_status[['month_idx']].values
                y = monthly_status['fail_rate'].values
                
                model = LinearRegression()
                model.fit(X, y)
                slope = model.coef_[0]
                
                if slope > 0.5:
                    failure_trend_text = f"Failure rates show an upward trend, rising by average {slope:.2f}% percentage points monthly."
                elif slope < -0.5:
                    failure_trend_text = f"Failure rates are declining, dropping by average {abs(slope):.2f}% percentage points monthly."
        
        # Escalation trend (using regression)
        escalation_trend_text = "Escalation volume shows no major monthly deviations."
        monthly_esc = self.df[self.df['escalation_status'].str.lower() == 'open'].groupby('month_year').size().reset_index(name='open_count')
        if len(monthly_esc) >= 2:
            monthly_esc['month_idx'] = range(len(monthly_esc))
            X = monthly_esc[['month_idx']].values
            y = monthly_esc['open_count'].values
            
            model = LinearRegression()
            model.fit(X, y)
            slope = model.coef_[0]
            
            if slope > 0.3:
                escalation_trend_text = f"Open escalations are trending upward, increasing by roughly {slope:.1f} cases per month."
            elif slope < -0.3:
                escalation_trend_text = f"Open escalations are trending downward, resolving at a rate of {abs(slope):.1f} cases per month."
        
        # Staff risk patterns
        staff_metrics = self.get_staff_metrics()
        staff_risk_text = "No anomalous risk concentrations detected among assigned personnel."
        if not staff_metrics.empty:
            high_risk_staff = staff_metrics.sort_values(by='avg_risk_score', ascending=False)
            top_risk = high_risk_staff.iloc[0]
            if top_risk['avg_risk_score'] > 70:
                staff_risk_text = f"Staff member {top_risk['assigned_staff']} has the highest risk concentration with an average risk score of {top_risk['avg_risk_score']:.1f} across {top_risk['total_audits']} audits."
                
        return {
            "icu_risk_change": icu_change_text,
            "failure_trend": failure_trend_text,
            "escalation_trend": escalation_trend_text,
            "staff_risk_pattern": staff_risk_text
        }

    # 8. Recommendation Engine
    def generate_recommendations(self):
        recs = []
        
        # ICU Risk Rule
        icu_risk = self.get_icu_risk_score()
        if icu_risk > 65:
            recs.append({
                "type": "risk",
                "target": "ICU",
                "recommendation": "Increase ICU cleaning frequency and implement twice-daily hygiene sweeps to bring the risk score down (Current ICU Risk: {:.1f}).".format(icu_risk)
            })
            
        # Ward Risk Rule
        hw_name, hw_score = self.get_highest_risk_ward()
        if hw_score > 60:
            recs.append({
                "type": "risk",
                "target": hw_name,
                "recommendation": "Conduct targeted risk-reduction interventions in the {} ward immediately (Current Risk: {:.1f}).".format(hw_name, hw_score)
            })
            
        # Floor Risk Rule
        hf_num, hf_score = self.get_highest_risk_floor()
        if hf_score > 60:
            recs.append({
                "type": "risk",
                "target": f"Floor {hf_num}",
                "recommendation": "Establish additional safety checks and supervisory audits on Floor {} due to elevated risk levels (Current Risk: {:.1f}).".format(hf_num, hf_score)
            })

        # Escalation Rule
        open_esc = len(self.get_open_escalations())
        if open_esc > 50:
            he_floor, he_count = self.get_most_escalations_floor()
            recs.append({
                "type": "escalation",
                "target": "Supervisors",
                "recommendation": "Assign additional compliance supervisors to Floor {} (which has the most escalations: {}) to accelerate pending issue resolutions.".format(he_floor, he_count)
            })

        # Compliance Rule
        compliance = self.get_compliance_score()
        if compliance < 85:
            lowest_dept, lowest_score = self.get_lowest_compliance_dept()
            recs.append({
                "type": "compliance",
                "target": lowest_dept,
                "recommendation": "Schedule an immediate compliance review and retraining for the {} department, which currently has the lowest compliance score ({:.1f}%).".format(lowest_dept, lowest_score)
            })
        else:
            recs.append({
                "type": "compliance",
                "target": "General",
                "recommendation": "Compliance scores are healthy ({:.1f}%). Continue current audit protocols and schedule standard monthly refresher courses.".format(compliance)
            })
            
        # Staff performance rule
        worst_staff_name, worst_pass_rate, worst_compliance = self.get_lowest_performing_staff()
        if worst_pass_rate < 70:
            recs.append({
                "type": "performance",
                "target": worst_staff_name,
                "recommendation": "Conduct a performance review for staff member {} (Pass Rate: {:.1f}%, Avg Compliance: {:.1f}%) and assign a mentor for quality control.".format(worst_staff_name, worst_pass_rate, worst_compliance)
            })

        return recs
        
    # Main dashboard statistics getter
    def get_dashboard_data(self):
        hw_name, hw_score = self.get_highest_risk_ward()
        hf_num, hf_score = self.get_highest_risk_floor()
        best_staff_name, best_staff_pass, best_staff_comp = self.get_best_staff()
        summary = self.get_audit_summary()
        esc_summary = self.get_escalation_summary()
        critical_count = len(self.get_critical_escalations())
        
        # Monthly compliance & risk trends (for charts)
        self.df['month_year_str'] = self.df['date'].dt.strftime('%b %Y')
        # Sort by date properly for grouping
        monthly_data = self.df.groupby(['month_year_str', self.df['date'].dt.to_period('M')]).agg({
            'compliance_score': 'mean',
            'risk_score': 'mean',
            'audit_id': 'count'
        }).reset_index().sort_values('date')
        
        charts_monthly = []
        for _, row in monthly_data.iterrows():
            charts_monthly.append({
                "month": row['month_year_str'],
                "compliance": round(float(row['compliance_score']), 1),
                "risk": round(float(row['risk_score']), 1),
                "audits": int(row['audit_id'])
            })
            
        # Floor-wise stats
        floor_data = self.df.groupby('floor').agg({
            'risk_score': 'mean',
            'compliance_score': 'mean',
            'audit_id': 'count'
        }).reset_index()
        charts_floor = []
        for _, row in floor_data.iterrows():
            charts_floor.append({
                "floor": f"Floor {int(row['floor'])}",
                "risk": round(float(row['risk_score']), 1),
                "compliance": round(float(row['compliance_score']), 1),
                "audits": int(row['audit_id'])
            })
            
        # Checklist types performance
        checklist_data = self.get_checklist_completion_status()
        charts_checklist = []
        for name, data in checklist_data.items():
            charts_checklist.append({
                "name": name,
                "total": data['total_audits'],
                "passed": data['passed_audits'],
                "failed": data['failed_audits'],
                "pending": data['pending_audits'],
                "compliance": round(data['avg_compliance_score'], 1)
            })

        # Staff performance top list
        staff_data = self.get_staff_metrics().sort_values(by='pass_rate', ascending=False).head(5)
        staff_list = []
        for _, row in staff_data.iterrows():
            staff_list.append({
                "staff": row['assigned_staff'],
                "audits": int(row['total_audits']),
                "pass_rate": round(float(row['pass_rate']), 1),
                "compliance": round(float(row['avg_compliance_score']), 1)
            })
            
        return {
            "overall_risk_score": round(self.get_hospital_risk_score(), 1),
            "compliance_score": round(self.get_compliance_score(), 1),
            "nabh_compliance": round(self.get_nabh_compliance(), 1),
            "pending_audits": summary['pending_audits'],
            "failed_audits": summary['failed_audits'],
            "completed_audits": summary['completed_audits'],
            "total_audits": summary['total_audits'],
            "open_escalations": esc_summary['open_escalations'],
            "closed_escalations": esc_summary['closed_escalations'],
            "critical_issues": critical_count,
            "best_staff": best_staff_name,
            "high_risk_ward": hw_name,
            "high_risk_ward_score": round(hw_score, 1),
            "high_risk_floor": hf_num,
            "high_risk_floor_score": round(hf_score, 1),
            "charts": {
                "monthly": charts_monthly,
                "floor": charts_floor,
                "checklist": charts_checklist
            },
            "top_staff": staff_list,
            "recommendations": self.generate_recommendations()[:3] # Show top 3 in dashboard
        }

    def get_icu_hygiene_risk_trend(self):
        # Filter for ICU and Hygiene Audit
        icu_hygiene = self.df[(self.df['ward'] == 'ICU') & (self.df['checklist_type'] == 'Hygiene Audit')].sort_values('date')
        if icu_hygiene.empty:
            return {"slope": 0.0, "text": "No ICU hygiene audits found."}
            
        # Group by week/date to get averages over time
        icu_hygiene = icu_hygiene.copy()
        icu_hygiene['day_idx'] = (icu_hygiene['date'] - icu_hygiene['date'].min()).dt.days
        if len(icu_hygiene) < 2:
            return {"slope": 0.0, "text": f"Only one ICU hygiene audit found (Risk Score: {icu_hygiene.iloc[0]['risk_score']})."}
            
        X = icu_hygiene[['day_idx']].values
        y = icu_hygiene['risk_score'].values
        
        model = LinearRegression()
        model.fit(X, y)
        slope = float(model.coef_[0])
        
        # Determine if it's increasing or decreasing
        direction = "increasing" if slope > 0 else "decreasing"
        
        # Calculate percentage change over the last month
        recent_audits = icu_hygiene.tail(5)
        earlier_audits = icu_hygiene.head(max(1, len(icu_hygiene)-5))
        recent_mean = recent_audits['risk_score'].mean()
        earlier_mean = earlier_audits['risk_score'].mean()
        change_pct = ((recent_mean - earlier_mean) / earlier_mean) * 100 if earlier_mean > 0 else 0.0
        
        color = "red" if slope > 0 else "green"
        text = f"**ICU hygiene risk** is currently **{direction}** by **{abs(change_pct):.1f}%** compared to previous periods (average risk slope: **{slope:.3f}/day**)."
        
        return {
            "slope": slope,
            "direction": direction,
            "change_pct": change_pct,
            "color": color,
            "text": text
        }
        
    def get_nabh_compliance_weekly_trend(self):
        if self.df.empty:
            return {"slope": 0.0, "text": "No data available."}
            
        self.df['week_start'] = self.df['date'].dt.to_period('W').dt.start_time
        weekly = self.df.groupby('week_start')['compliance_score'].mean().reset_index().sort_values('week_start')
        
        if len(weekly) < 2:
            return {"slope": 0.0, "text": "Insufficient weekly data."}
            
        weekly['week_idx'] = range(len(weekly))
        X = weekly[['week_idx']].values
        y = weekly['compliance_score'].values
        
        model = LinearRegression()
        model.fit(X, y)
        slope = float(model.coef_[0])
        
        direction = "improving" if slope > 0 else "declining"
        
        # Get last week vs the one before
        recent_comp = weekly.iloc[-1]['compliance_score']
        prev_comp = weekly.iloc[-2]['compliance_score'] if len(weekly) >= 2 else recent_comp
        diff = recent_comp - prev_comp
        
        text = f"**NABH compliance score** is showing a **steady {direction}** (slope of **{slope:.3f}** units per week, currently averaging **{recent_comp:.1f}%** this week, which is a change of **{diff:+.1f}%**)."
        
        return {
            "slope": slope,
            "direction": direction,
            "current_week_avg": recent_comp,
            "diff": diff,
            "text": text
        }
