from cff2coins import CoinsParser
from tests.utils import run_from_html_file_test


def test_from_html_file_for_empty_html_file():
    actual_json, expected_json = run_from_html_file_test(test_name="empty_html_file")
    assert actual_json == expected_json


def test_from_html_file_for_single_non_coins_span():
    actual_json, expected_json = run_from_html_file_test(
        test_name="single_non_coins_span"
    )
    assert actual_json == expected_json


def test_from_html_file_for_html_with_single_empty_coins_span():
    actual_json, expected_json = run_from_html_file_test(
        test_name="single_empty_coins_span"
    )
    assert actual_json == expected_json


def test_from_html_file_for_html_with_multiple_empty_coins_spans():
    actual_json, expected_json = run_from_html_file_test(
        test_name="multiple_empty_coins_spans"
    )
    assert actual_json == expected_json


def test_from_html_file_for_html_with_single_non_empty_coins_span():
    actual_json, expected_json = run_from_html_file_test(
        test_name="single_non_empty_coins_span"
    )
    assert actual_json == expected_json
