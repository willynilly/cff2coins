from pathlib import Path
from cff2coins import CffCoinSpan


def test_get_references_for_cff_without_references():
    input_cff_file_path: Path = Path(
        "tests", "references", "without_references", "input.cff"
    )
    cff_coin_span = CffCoinSpan.from_cff_file(cff_file_path=input_cff_file_path)
    assert cff_coin_span.references == []


def test_get_references_for_cff_with_references():
    input_cff_file_path: Path = Path(
        "tests", "references", "with_references", "input.cff"
    )
    cff_coin_span = CffCoinSpan.from_cff_file(cff_file_path=input_cff_file_path)
    assert len(cff_coin_span.references) == 2
