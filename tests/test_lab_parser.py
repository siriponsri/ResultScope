from services.lab_parser import build_symbolic_context, extract_lab_values


def test_parser_flags_against_supplied_range_only():
    values = extract_lab_values("Hb 10.8 g/dL (12-16), MCV 72 fL (80-100), Ferritin 7 ng/mL (15-150)")
    assert [v.marker.lower() for v in values] == ["hb", "mcv", "ferritin"]
    assert [v.flag for v in values] == ["low", "low", "low"]


def test_parser_keeps_no_range_as_unknown():
    values = extract_lab_values("HbA1c 6.1%")
    assert len(values) == 1
    assert values[0].flag == "unknown"


def test_symbolic_context_does_not_invent_range():
    values = extract_lab_values("LDL 162 mg/dL")
    context = build_symbolic_context(values)
    assert "no supplied reference range" in context
    assert "deterministic flag=unknown" in context
