WEIGHTS={"flood_exposure":0.40,"heat_exposure":0.20,"water_stress":0.20,"service_criticality":0.20}
def score_service(row):
    return max(0,min(100,round(sum(float(row[k])*v for k,v in WEIGHTS.items()))))
def risk_label(score):
    if score>=80:return "Critical"
    if score>=60:return "High"
    if score>=35:return "Moderate"
    return "Low"
def action_for(row):
    score=score_service(row)
    if score>=60:
        return "Request local verification; confirm facility status, access routes and alternatives; coordinate with the responsible health or municipal authority."
    if score>=35:
        return "Review local conditions and monitor for change; verify water and access concerns with an authorised partner."
    return "Retain as baseline and reassess when new observations arrive."
