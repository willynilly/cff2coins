from tests.utils import run_to_html_string_test


def test_to_html_file_for_cff_coin_span_without_references():
    actual_html, expected_html = run_to_html_string_test(
        test_name="cff_coin_span_without_references"
    )
    assert actual_html == expected_html


def test_to_html_file_for_cff_coin_span_with_references():
    actual_html, expected_html = run_to_html_string_test(
        test_name="cff_coin_span_with_references"
    )
    assert actual_html == expected_html
