from src.domain.onboarding_rules import build_onboarding_steps, next_step


def make(**overrides):
    values = dict(
        has_period=True,
        subject_count=2,
        class_meeting_count=1,
        topic_count=0,
        session_count=0,
        completed_session_count=0,
    )
    values.update(overrides)
    return build_onboarding_steps(**values)


def test_next_step_is_first_pending_in_order():
    steps = make()
    assert [step.done for step in steps] == [True, True, True, False, False, False]
    assert next_step(steps).key == "topic"


def test_new_user_starts_with_period_and_finished_user_has_no_next_step():
    assert next_step(make(has_period=False, subject_count=0, class_meeting_count=0)).key == "period"
    done = make(topic_count=3, session_count=4, completed_session_count=1)
    assert next_step(done) is None
