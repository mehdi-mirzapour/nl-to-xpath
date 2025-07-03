import pytest
from sentence_segmentor import segment
from models import model


def test_segment_basic_instruction():
    instruction = """
    open localhost:5173 and then login with user name as `mehdi.mirzapour@gmail.com` and password  as `pass1234`
    open localhost:5173/items and click on add items.
    """

    expected_output = {
        "instructions": [
            "Open the URL 'localhost:5173'.",
            "Find the username input field and enter 'mehdi.mirzapour@gmail.com'.",
            "Find the password input field and enter 'pass1234'.",
            "Find and click on the 'Login' button.",
            "Navigate to the URL 'localhost:5173/items'.",
            "Find and click on the 'Add Items' button."
        ]
    }

    result = segment(instruction, model)

    assert isinstance(result, dict)
    assert "instructions" in result
    assert isinstance(result["instructions"], list)