from services.intent_router import route_intent


def test_business_faq_is_routed_without_lab_value():
    decision = route_intent("What are the lab opening hours?")
    assert decision.allowed is True
    assert decision.kind == "business"
    assert decision.reason == "business_faq"


def test_concern_followup_requires_lab_history():
    history = [{"role": "user", "content": "Ferritin 7 ng/mL"}]

    with_context = route_intent("Should I be concerned?", history)
    without_context = route_intent("Should I be concerned?")

    assert with_context.allowed is True
    assert with_context.kind == "lab"
    assert with_context.reason == "lab_follow_up"
    assert without_context.allowed is False


def test_unrelated_and_unsafe_queries_do_not_enter_provider_path():
    unrelated = route_intent("Help me write Python")
    unsafe = route_intent("My Hb is low; should I change my dose?")

    assert unrelated.kind == "unrelated"
    assert unrelated.allowed is False
    assert unsafe.kind == "unsafe"
    assert unsafe.allowed is False


def test_business_plus_lab_is_explicitly_mixed():
    decision = route_intent("What does my Hb result mean, and what is the lab price?")
    assert decision.kind == "mixed"
    assert decision.allowed is True
