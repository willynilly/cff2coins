from typing import Optional
from cff2coins import CffCoinSpan, CoinSpan, CoinSpanList
from pathlib import Path
import json
import tempfile

from cff2coins.models.cff_coin_span import CffCoinSpanList
from cff2coins.models.cff_coin_span_json_decoder import CffCoinSpanJsonDecoder
from cff2coins.models.cff_coin_span_json_encoder import CffCoinSpanJsonEncoder


def load_html_string(test_group: str, test_name: str, file_name: str) -> str:
    return Path("tests", test_group, test_name, file_name).read_text(encoding="UTF-8")


def load_json_string(test_group: str, test_name: str, file_name: str) -> str:
    return json.dumps(
        json.loads(
            Path("tests", test_group, test_name, file_name).read_text(encoding="UTF-8")
        ),
        ensure_ascii=False,
    )


def load_exception_value_string(test_group: str, test_name: str) -> Optional[str]:
    exception_path: Path = Path("tests", test_group, test_name, "exception.json")
    if exception_path.exists():
        exception_value: str = load_json_string(
            test_group=test_group, test_name=test_name, file_name="exception.json"
        ).strip('"')
        return exception_value
    else:
        return None


def run_from_cff_file_test(test_name: str) -> tuple[str, str]:
    test_group: str = "from_cff_file"
    input_cff_file_path: Path = Path("tests", test_group, test_name, "input.cff")

    cff_coin_span: CffCoinSpan = CffCoinSpan.from_cff_file(
        cff_file_path=input_cff_file_path
    )
    actual_json = json.dumps(
        cff_coin_span, cls=CffCoinSpanJsonEncoder, ensure_ascii=False
    )

    expected_json: str = load_json_string(
        test_group=test_group, test_name=test_name, file_name="expected.json"
    )
    return actual_json, expected_json


def run_from_html_file_test(test_name: str) -> tuple[str, str]:
    test_group: str = "from_html_file"
    input_html_file_path: Path = Path("tests", test_group, test_name, "input.html")

    cff_coin_spans: CffCoinSpanList = CffCoinSpan.from_html_file(
        html_file_path=input_html_file_path
    )
    actual_json = json.dumps(
        cff_coin_spans, cls=CffCoinSpanJsonEncoder, ensure_ascii=False
    )
    expected_json: str = load_json_string(
        test_group=test_group, test_name=test_name, file_name="expected.json"
    )
    return actual_json, expected_json


def run_from_html_string_test(test_name: str) -> tuple[str, str]:
    test_group: str = "from_html_string"
    input_html: str = load_html_string(
        test_group=test_group, test_name=test_name, file_name="input.html"
    )

    cff_coin_spans: list[CffCoinSpan] = CffCoinSpan.from_html_string(input_html)
    actual_json = json.dumps(
        cff_coin_spans, cls=CffCoinSpanJsonEncoder, ensure_ascii=False
    )
    expected_json: str = load_json_string(
        test_group=test_group, test_name=test_name, file_name="expected.json"
    )
    return actual_json, expected_json


def run_to_html_file_test(test_name: str, **kwargs) -> tuple[str, str]:
    test_group: str = "to_html_file"
    input_json: str = load_json_string(
        test_group=test_group, test_name=test_name, file_name="input.json"
    )
    cff_coin_span: CffCoinSpan = json.loads(input_json, cls=CffCoinSpanJsonDecoder)
    actual_html: str = ""
    with_references: bool = False
    if "with_references" in kwargs:
        with_references = kwargs["with_references"]
    with tempfile.NamedTemporaryFile() as temp_file:
        cff_coin_span.to_html_file(
            html_file_path=Path(temp_file.name),
            with_references=with_references,
        )
        actual_html = load_html_string(
            test_group=test_group, test_name=test_name, file_name=temp_file.name
        )

    expected_html: str = load_html_string(
        test_group=test_group, test_name=test_name, file_name="expected.html"
    )
    return actual_html, expected_html


def run_to_html_string_test(test_name: str) -> tuple[str, str]:
    test_group: str = "to_html_string"
    input_json: str = load_json_string(
        test_group=test_group, test_name=test_name, file_name="input.json"
    )
    cff_coin_span: CffCoinSpan = json.loads(input_json, cls=CffCoinSpanJsonDecoder)
    actual_html: str = cff_coin_span.to_html_string()

    expected_html: str = load_html_string(
        test_group=test_group, test_name=test_name, file_name="expected.html"
    )
    return actual_html, expected_html
