def calculate_severity(obligation_type: str, coverage_score: float, is_mandatory: bool) -> str:
    """
    Deterministic severity calculation logic:
    - CRITICAL = mandatory + no coverage (coverage_score == 0)
    - HIGH = mandatory + weak coverage (0 < coverage_score < 0.70)
    - MEDIUM = advisory + no coverage (coverage_score == 0)
    - LOW = advisory + weak coverage (0 < coverage_score < 0.70)
    """
    is_mandatory_flag = is_mandatory or (obligation_type.upper() in ["MANDATORY", "MUST", "SHALL"])
    
    if coverage_score == 0:
        return "CRITICAL" if is_mandatory_flag else "MEDIUM"
    elif coverage_score < 0.70:
        return "HIGH" if is_mandatory_flag else "LOW"
    else:
        return "COMPLIANT"
