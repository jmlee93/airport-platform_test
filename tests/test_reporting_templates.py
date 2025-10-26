from reporting import TemplateEngine, generate_summary, render_sentence
from reporting.nlg_templates import SCENARIO_TEMPLATES


def test_render_capex_sentence():
    engine = TemplateEngine()
    aggregated = {"capex": {"change_pct": 5.25}}
    sentence = render_sentence(engine, "capex_change", aggregated)
    assert "CAPEX" in sentence
    assert "+5.3%" in sentence
    assert sentence.endswith(".")


def test_generate_default_summary():
    aggregated = {
        "capex": {"change_pct": -4.1},
        "irr": {"previous": 8.5, "current": 9.2, "change_pct_point": 0.7},
    }
    summary = generate_summary(aggregated)
    assert "CAPEX" in summary
    assert "-4.1%" in summary
    assert "프로젝트 IRR" in summary
    assert summary.count(".") >= 2


def test_unknown_scenario_falls_back_to_default():
    aggregated = {
        "capex": {"change_pct": 1.0},
        "irr": {"previous": 10.0, "current": 9.5, "change_pct_point": -0.5},
    }
    default_summary = generate_summary(aggregated)
    fallback_summary = generate_summary(aggregated, scenario="nonexistent")
    assert fallback_summary == default_summary


def test_cost_focus_scenario_uses_opex_template():
    aggregated = {
        "capex": {"change_pct": 2.0},
        "opex": {"change_pct": -3.4},
    }
    summary = generate_summary(aggregated, scenario="cost_focus")
    assert "CAPEX" in summary
    assert "OPEX" in summary
    assert "-3.4%" in summary
