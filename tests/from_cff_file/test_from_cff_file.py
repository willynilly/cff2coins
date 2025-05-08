from tests.utils import load_exception_value_string, run_from_cff_file_test
import pytest


def test_from_cff_file_for_empty_cff_file():
    with pytest.raises(ValueError) as e:
        run_from_cff_file_test("empty_cff_file")
    assert str(e.value) == load_exception_value_string(
        test_group="from_cff_file", test_name="empty_cff_file"
    )


def test_from_cff_file_for_cff_file_without_references():
    actual_json, expected_json = run_from_cff_file_test("cff_file_without_references")
    assert actual_json == expected_json


def test_from_cff_file_for_cff_file_with_cff_file_with_references():
    actual_json, expected_json = run_from_cff_file_test("cff_file_with_references")
    assert actual_json == expected_json
