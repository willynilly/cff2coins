from __future__ import annotations

# from typing import overload, Optional, Union
from pathlib import Path
from coins_parser import CoinsParser, CoinSpanList, CoinSpan, CoinSpanTerm
import yaml

from importlib.metadata import version, PackageNotFoundError


try:
    __version__ = version(__package__ or "cff2coins")
except PackageNotFoundError:
    __version__ = "unknown"
DEFAULT_REFERRER_ID = f"github.willynilly:cff2coins-{__version__}"

DEFAULT_HTML_ENCODING = "UTF-8"
REQUIRED_CFF_FIELDS: list[str] = ["cff-version", "message", "title", "authors"]
SUPPORTED_CFF_VERSIONS = ["1.2.0"]


class CffCoinSpan:

    def __init__(self):
        self.coin_span: CoinSpan = []
        self.references: CffCoinSpanList = []

    @classmethod
    def _create_identifiers_coin_span(cls, cff: dict) -> CoinSpan:
        identifiers_coin_span = []

        # some CFF files have 'doi' field
        if "doi" in cff:
            value = cff["doi"]
            if not value.startswith("doi:"):
                value = "doi:" + value
            identifiers_coin_span.append(("rft.identifier", f"{value}"))

        # some CFF files have an identifiers section
        # that contains one or more doi, url, swf, or other identifiers
        if "identifiers" in cff:
            for identifier in cff["identifiers"]:
                value = identifier["value"]
                if value is not None:
                    value = str(value).strip()
                    if value is not "" and identifier["type"] in [
                        "doi",
                        "url",
                        "swf",
                        "other",
                    ]:
                        if identifier["type"] == "doi":
                            if not value.startswith("doi:"):
                                value = "doi:" + value
                            # resolved_url = f"http://doi.org/{value}"
                        elif identifier["type"] == "url":
                            pass
                            # resolved_url = value
                        elif identifier["type"] == "swf":
                            if not value.startswith("swf:"):
                                value = "swf:" + value
                            # resolved_url = f"https://archive.softwareheritage.org/{value}"
                        elif identifier["type"] == "other":
                            pass
                            # resolved_url = value
                        identifiers_coin_span.append(("rft.identifier", f"{value}"))
        return identifiers_coin_span

    @classmethod
    def _create_authors_coin_span(
        cls, cff: dict, is_cff_reference: bool = False
    ) -> CoinSpan:
        if "authors" not in cff:
            cff["authors"] = []

        coins_author_metadata = []
        for author in cff["authors"]:

            if "name" in author:
                author_full_name: str = author["name"]
            else:
                author_full_name: str = " ".join(
                    [author["given-names"], author["family-names"]]
                )
            coins_author_metadata.append(
                ("rft.au", author_full_name),
            )
        return coins_author_metadata

    @classmethod
    def _create_publisher_coin_span(
        cls, cff: dict, publisher: str | None = None, is_cff_reference: bool = False
    ) -> CoinSpan:
        publisher_coin_span: CoinSpan = []
        if publisher is not None and publisher != "":
            publisher_coin_span = [("rft.publisher", publisher)]
        else:
            if is_cff_reference and "publisher" in cff:
                publisher_coin_span = [("rft.publisher", cff["publisher"])]
        return publisher_coin_span

    @classmethod
    def _create_language_coin_span(
        cls, cff: dict, language: str | None = None, is_cff_reference: bool = False
    ) -> CoinSpan:
        language_coin_span: CoinSpan = []
        if language is not None and language != "":
            language_coin_span = [("rft.language", language)]
        else:
            if is_cff_reference and "language" in cff:
                language_coin_span = [("rft.language", cff["language"])]
        return language_coin_span

    @classmethod
    def _create_coin_span(
        cls,
        cff: dict,
        is_cff_reference: bool = False,
        publisher: str | None = None,
        language: str | None = None,
        referrer_id: str | None = None,
    ) -> CoinSpan:
        if referrer_id is None:
            referrer_id = DEFAULT_REFERRER_ID
        else:
            if len(referrer_id.split(":")) != 2:
                raise ValueError(
                    f"Invalid referrer id: it must have this form '<authority>:<id>'"
                )

        coin_span: CoinSpan = []

        publisher_coin_span: CoinSpan = cls._create_publisher_coin_span(
            cff=cff, publisher=publisher, is_cff_reference=is_cff_reference
        )
        language_coin_span: CoinSpan = cls._create_language_coin_span(
            cff=cff, language=language, is_cff_reference=is_cff_reference
        )
        authors_coin_span: CoinSpan = cls._create_authors_coin_span(cff=cff)
        identifiers_coin_span: CoinSpan = cls._create_identifiers_coin_span(cff=cff)

        coin_span: CoinSpan = [
            ("url_ver", "Z39.88-2004"),
            ("ctx_ver", "Z39.88-2004"),
            ("rfr_id", f"info:sid/{referrer_id}"),
        ]
        mtx_common_coin_span: CoinSpan = []
        mtx_common_coin_span += [("rft.title", f"{cff['title']}")]
        if "date-released" in cff:
            mtx_common_coin_span += [("rft.date", f"{cff['date-released']}")]
        if "abstract" in cff:
            mtx_common_coin_span += [("rft.description", f"{cff['abstract']}")]
        if "version" in cff:
            mtx_common_coin_span += [("rft.version", f"{cff['version']}")]
        if "license" in cff:
            mtx_common_coin_span += [("rft.rights", f"{cff['license']}")]
        mtx_common_coin_span += (
            language_coin_span
            + publisher_coin_span
            + identifiers_coin_span
            + authors_coin_span
        )

        if "type" not in cff or cff["type"] == "software":
            mtx_computer_program_coin_span = [
                ("rft_val_fmt", "info:ofi/fmt:kev:mtx:computerProgram"),
            ] + mtx_common_coin_span
            mtx_dc_coin_span = [
                ("rft_val_fmt", "info:ofi/fmt:kev:mtx:dc"),
                ("rft.type", "computerProgram"),
            ]

            coin_span += mtx_computer_program_coin_span + mtx_dc_coin_span
        elif cff["type"] == "dataset":
            mtx_data_coin_span = [
                ("rft_val_fmt", "info:ofi/fmt:kev:mtx:data")
            ] + mtx_common_coin_span

            mtx_dc_coin_span = [
                ("rft_val_fmt", "info:ofi/fmt:kev:mtx:dc"),
                ("rft.type", "Dataset"),
            ]

            coin_span += mtx_data_coin_span + mtx_dc_coin_span
        else:
            raise ValueError(
                "Invalid CFF dict: 'type' must be 'software' or 'dataset'."
            )
        return coin_span

    @classmethod
    def validate_cff(cls, cff: dict) -> None:
        missing_cff_fields = [
            required_cff_field
            for required_cff_field in REQUIRED_CFF_FIELDS
            if required_cff_field not in cff
        ]
        if len(missing_cff_fields):
            raise ValueError(
                "Invalid CFF: CFF dictionary is missing the following required fields: "
                + ", ".join(missing_cff_fields)
            )
        if cff["cff-version"] not in SUPPORTED_CFF_VERSIONS:
            raise ValueError(
                "Invalid CFF: CFF dictionary must specify a cff-version with one of the following: "
                + ", ".join(SUPPORTED_CFF_VERSIONS)
            )

    @classmethod
    def from_cff_dict(
        cls,
        cff: dict,
        publisher: str | None = None,
        language: str | None = None,
        referrer_id: str | None = None,
    ) -> CffCoinSpan:

        cls.validate_cff(cff=cff)

        # construct CoinSpan
        coin_span = cls._create_coin_span(
            cff=cff,
            is_cff_reference=False,
            publisher=publisher,
            language=language,
            referrer_id=referrer_id,
        )

        # construct CffCoinSpan references
        references: CffCoinSpanList = []
        if "references" in cff:
            for cff_reference in cff["references"]:
                cff_reference["cff-version"] = cff["cff-version"]
                reference_coin_span: CoinSpan = cls._create_coin_span(
                    cff=cff_reference,
                    is_cff_reference=True,
                    referrer_id=referrer_id,
                )
                reference = CffCoinSpan.from_coin_span(coin_span=reference_coin_span)
                references.append(reference)

        cff_coin_span = cls()
        cff_coin_span.coin_span = coin_span
        cff_coin_span.references = references
        return cff_coin_span

    @classmethod
    def from_cff_file(
        cls,
        cff_file_path: Path | None = None,
        publisher: str | None = None,
        language: str | None = None,
        referrer_id: str | None = None,
    ) -> CffCoinSpan:
        if cff_file_path is None:
            cff_file_path = Path("CITATION.cff")

        cff: dict = {}
        with open(cff_file_path, "r") as file:
            cff = yaml.safe_load(file) or {}

        return cls.from_cff_dict(
            cff=cff, publisher=publisher, language=language, referrer_id=referrer_id
        )

    @classmethod
    def from_cff_string(
        cls,
        cff_string: str,
        publisher: str | None = None,
        language: str | None = None,
        referrer_id: str | None = None,
    ) -> CffCoinSpan:
        # construct coins data
        cff: dict = yaml.safe_load(cff_string) or {}
        return cls.from_cff_dict(
            cff=cff,
            publisher=publisher,
            language=language,
            referrer_id=referrer_id,
        )

    @classmethod
    def from_html_file(
        cls,
        html_file_path: Path,
        encoding: str | None = None,
        beautiful_soup_parser: str | None = None,
    ) -> list[CffCoinSpan]:
        if encoding is None:
            encoding = DEFAULT_HTML_ENCODING

        html_string: str = html_file_path.read_text(encoding=encoding)
        return cls.from_html_string(
            html_string=html_string, beautiful_soup_parser=beautiful_soup_parser
        )

    @classmethod
    def from_html_string(
        cls, html_string: str, beautiful_soup_parser: str | None = None
    ) -> list[CffCoinSpan]:
        cff_coin_span_list: list[CffCoinSpan] = []
        if beautiful_soup_parser is None:
            beautiful_soup_parser = "html.parser"

        # construct coins data
        coin_spans: CoinSpanList = CoinsParser.parse(
            html=html_string, beautiful_soup_parser=beautiful_soup_parser
        )

        for coin_span in coin_spans:
            is_valid_coin_span, exception = cls.is_valid_coin_span_for_cff(coin_span)
            if is_valid_coin_span:
                cff_coin_span = cls()
                cff_coin_span.coin_span = coin_span
                cff_coin_span_list.append(cff_coin_span)

        return cff_coin_span_list

    @classmethod
    def is_valid_coin_span_term_for_cff(
        cls, coin_span_term: CoinSpanTerm
    ) -> tuple[bool, list[Exception]]:
        exceptions: list[Exception] = []
        if (
            isinstance(coin_span_term, tuple)
            and len(coin_span_term) == 2
            and isinstance(coin_span_term[0], str)
            and isinstance(coin_span_term[1], str)
        ):
            exceptions.append(
                Exception(
                    "Invalid CoinSpanTerm: coin span term must have the type tuple[str, str]."
                )
            )
            return False, exceptions
        else:
            return True, []

    @classmethod
    def is_valid_coin_span_for_cff(
        cls, coin_span: CoinSpan
    ) -> tuple[bool, Exception | None]:

        if not (
            isinstance(coin_span, list)
            and len(coin_span) > 0
            and all(
                [
                    cls.is_valid_coin_span_term_for_cff(coin_span_term=coin_span_term)
                    for coin_span_term in coin_span
                ]
            )
        ):
            exception = Exception(
                "Invalid CoinSpan for CFF: coin span must have the type list[CoinSpanTerm] and have at least one CoinSpanTerm"
            )
            return False, exception

        is_computer_program_mtx: bool = any(
            k == "rft_val_fmt" and v == "info:ofi/fmt:kev:mtx:computerProgram"
            for (k, v) in coin_span
        )
        is_computer_progam_dc: bool = any(
            k == "rft_val_fmt" and v == "info:ofi/fmt:kev:mtx:dc"
            for (k, v) in coin_span
        ) and any(k == "rft.type" and v == "computerProgram" for (k, v) in coin_span)
        is_dataset_mtx: bool = any(
            k == "rft_val_fmt" and v == "info:ofi/fmt:kev:mtx:data"
            for (k, v) in coin_span
        )
        is_dataset_dc: bool = any(
            k == "rft_val_fmt" and v == "info:ofi/fmt:kev:mtx:dc"
            for (k, v) in coin_span
        ) and any(k == "rft.type" and v == "DataSet" for (k, v) in coin_span)

        # if is_computer_program_mtx and not is_computer_progam_dc:
        #     coin_span += [("rft_val_fmt", "info:ofi/fmt:kev:mtx:dc"),
        #         ("rft.type", "computerProgram")]

        # if is_dataset_mtx and not is_dataset_dc:
        #     coin_span += [("rft_val_fmt", "info:ofi/fmt:kev:mtx:dc"),
        #         ("rft.type", "Dataset")]

        if not (
            is_computer_program_mtx
            or is_computer_progam_dc
            or is_dataset_mtx
            or is_dataset_dc
        ):
            exception = Exception(
                "Invalid COinS for CFF: must contain metadata for either a computer program or a dataset."
            )
            return False, exception

        return True, None

    @classmethod
    def from_coin_span(cls, coin_span: CoinSpan) -> CffCoinSpan:
        # construct coins metadata
        is_valid_coin_span, exception = cls.is_valid_coin_span_for_cff(
            coin_span=coin_span
        )
        if is_valid_coin_span:
            cff_coin_span = cls()
            cff_coin_span.coin_span = coin_span
            return cff_coin_span
        elif exception is not None:
            raise exception
        else:
            raise Exception("Invalid CoinSpan")

    def to_html_file(self, html_file_path: Path, with_references: bool = False):
        with open(html_file_path, "w") as f:
            f.write(self.to_html_string(with_references=with_references))

    def to_html_string(self, with_references: bool = False) -> str:
        coin_spans: CoinSpanList = [self.coin_span]
        if with_references:
            coin_spans += [reference.coin_span for reference in self.references]
        return CoinsParser.html(coin_spans=coin_spans)

    def to_cff_string(self) -> str:
        raise NotImplementedError

    def to_cff_reference_string(self) -> str:
        raise NotImplementedError


CffCoinSpanList = list[CffCoinSpan]
