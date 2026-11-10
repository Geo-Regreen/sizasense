from engine.risk import score_service,risk_label
def test_score_bounds():
    row={k:100 for k in ["flood_exposure","heat_exposure","water_stress","service_criticality"]}
    assert score_service(row)==100
def test_bands():
    assert risk_label(10)=="Low"
    assert risk_label(40)=="Moderate"
    assert risk_label(60)=="High"
    assert risk_label(85)=="Critical"
