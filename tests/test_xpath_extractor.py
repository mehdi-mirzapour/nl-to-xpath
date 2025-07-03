from xpath_extractor import extract_xpath_pattern
from models import model

def test_extract_xpath_pattern_login_button():
    instruction = "Click on the 'Login' button."

    with open("resources/unit_tests/unit_test.html", "r", encoding="utf-8") as f:
        html = f.read()

    result = extract_xpath_pattern(instruction, html, model)

    assert isinstance(result, dict)
    assert result["action"] == "click"
    assert "Login" in result["xpath"]
    assert result["fill"] == ""
