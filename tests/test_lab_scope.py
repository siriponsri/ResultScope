from services.lab_scope import classify_lab_scope


def test_allows_common_lab_question():
    decision = classify_lab_scope("Hb 10.8 g/dL, MCV 72 fL ช่วยดู CBC ให้หน่อย")
    assert decision.allowed is True


def test_blocks_general_programming_question():
    decision = classify_lab_scope("ช่วยเขียน Python ทำเว็บให้หน่อย")
    assert decision.allowed is False


def test_allows_follow_up_only_when_lab_context_exists():
    history = [{"role": "user", "content": "Ferritin 7 ng/mL ต่ำไหม"}]
    decision = classify_lab_scope("แล้วต้องกังวลไหม", history)
    assert decision.allowed is True


def test_blocks_ambiguous_follow_up_without_context():
    decision = classify_lab_scope("แล้วต้องกังวลไหม", [])
    assert decision.allowed is False


def test_accepts_uncommon_marker_like_value_pattern():
    decision = classify_lab_scope("LDH: 420 U/L (120-250)")
    assert decision.allowed is True


def test_python_version_is_not_misread_as_lab_value():
    decision = classify_lab_scope("Python 3.13 ใช้กับ FastAPI ได้ไหม")
    assert decision.allowed is False


def test_general_organ_question_is_not_lab_scope():
    decision = classify_lab_scope("ตับมีหน้าที่อะไร")
    assert decision.allowed is False
