def calculate_severity(is_mandatory: bool, coverage_level: str) -> str:
    """
    Deterministically computes severity of a compliance gap.
    
    Rules:
    - CRITICAL: Mandatory directive with ZERO coverage ('none')
    - HIGH: Mandatory directive with WEAK or PARTIAL coverage ('weak' or 'partial')
    - MEDIUM: Advisory directive with ZERO coverage ('none')
    - LOW: Advisory directive with WEAK or PARTIAL coverage ('weak' or 'partial')
    
    If coverage is 'full', returns 'NONE' (conforming, no gap).
    """
    cov = coverage_level.lower().strip()
    
    if cov == "full":
        return "NONE"
        
    if is_mandatory:
        if cov == "none":
            return "CRITICAL"
        else:
            return "HIGH"
    else:
        if cov == "none":
            return "MEDIUM"
        else:
            return "LOW"
