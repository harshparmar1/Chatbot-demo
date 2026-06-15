import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from nlp_engine import NLPIntentClassifier, INTENTS
    from data_analyzer import HospitalAuditAnalyzer
    print("[OK] Backend imports successful!")
except Exception as e:
    print(f"[FAIL] Failed to import backend components: {e}")
    sys.exit(1)

def test_nlp():
    print("\n--- Testing NLP Intent Classifier ---")
    nlp = NLPIntentClassifier()
    
    test_cases = [
        ("Which ward has highest risk?", "highest_risk_ward"),
        ("Pending audits", "pending_audits"),
        ("Show failed audits", "failed_audits"),
        ("Show open escalations", "open_escalations"),
        ("Show compliance score", "compliance_score"),
        ("Best performing staff?", "best_staff"),
        ("Show floor-wise risk", "floor_wise_risk"),
        ("Show audit summary", "audit_summary"),
        ("Predict future risk.", "predict_future_risk"),
        ("Show recommendations.", "recommendations"),
        ("Show critical issues.", "critical_issues")
    ]
    
    success = True
    for query, expected_intent in test_cases:
        intent, similarity = nlp.predict(query)
        if intent == expected_intent:
            print(f"  [OK] '{query}' -> '{intent}' (Confidence: {similarity:.2f})")
        else:
            print(f"  [FAIL] '{query}' -> Expected '{expected_intent}', got '{intent}' (Confidence: {similarity:.2f})")
            success = False
            
    if success:
        print("[OK] NLP Intent matching verified successfully!")
    else:
        print("[FAIL] NLP Intent matching failed some tests.")
    return success

def test_analyzer():
    print("\n--- Testing Data Analyzer ---")
    try:
        analyzer = HospitalAuditAnalyzer("hospital_audit_500.csv")
    except Exception as e:
        print(f"[FAIL] Failed to load CSV data: {e}")
        return False
        
    try:
        # Check basic properties
        print(f"  Total logs parsed: {len(analyzer.df)}")
        print(f"  Max log date: {analyzer.max_date.strftime('%Y-%m-%d')}")
        
        # Test calculations
        hr_ward, hr_ward_score = analyzer.get_highest_risk_ward()
        print(f"  Highest Risk Ward: {hr_ward} (Score: {hr_ward_score:.2f})")
        assert hr_ward is not None and 20 <= hr_ward_score <= 95
        
        hr_floor, hr_floor_score = analyzer.get_highest_risk_floor()
        print(f"  Highest Risk Floor: Floor {hr_floor} (Score: {hr_floor_score:.2f})")
        assert 1 <= hr_floor <= 5 and 20 <= hr_floor_score <= 95
        
        avg_risk = analyzer.get_hospital_risk_score()
        print(f"  Hospital Avg Risk: {avg_risk:.2f}")
        assert 20 <= avg_risk <= 95
        
        avg_comp = analyzer.get_compliance_score()
        print(f"  Hospital Avg Compliance: {avg_comp:.2f}%")
        assert 60 <= avg_comp <= 100
        
        nabh = analyzer.get_nabh_compliance()
        print(f"  NABH Compliance Rate: {nabh:.2f}%")
        assert 0 <= nabh <= 100
        
        best_s, best_s_pr, best_s_comp = analyzer.get_best_staff()
        print(f"  Best Staff: {best_s} (Pass Rate: {best_s_pr:.1f}%, Compliance: {best_s_comp:.1f}%)")
        assert best_s is not None
        
        recs = analyzer.generate_recommendations()
        print(f"  Recommendations generated: {len(recs)}")
        assert len(recs) > 0
        
        pred = analyzer.predict_future_risk()
        print(f"  7-Day Risk Forecast: {pred['prediction_7d']:.2f}")
        print(f"  30-Day Risk Forecast: {pred['prediction_30d']:.2f}")
        
        print("[OK] CSV analysis mathematical validation successful!")
        return True
    except AssertionError as ae:
        print(f"[FAIL] Calculation validation failed: Out of bounds values detected.")
        return False
    except Exception as e:
        print(f"[FAIL] Calculation validation failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    nlp_ok = test_nlp()
    analyzer_ok = test_analyzer()
    if nlp_ok and analyzer_ok:
        print("\n=== ALL BACKEND CHECKS PASSED SUCCESSFULLY ===")
        sys.exit(0)
    else:
        print("\n=== SOME BACKEND CHECKS FAILED ===")
        sys.exit(1)
