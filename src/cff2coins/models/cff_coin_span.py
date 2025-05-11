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

# https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md#definitionsreferencetype
# https://web.archive.org/web/20221128181750/https://oclc-research.github.io/OpenURL-Frozen/ListSets.xml

COINS_FMT_AND_GENRE_TO_MAPPING_FROM_CFF_REF_TO_COINS = {
    ("info:ofi/fmt:kev:mtx:journal", "article"): {
        "title": "rft.atitle",
        "journal": "rft.jtitle",
        "authors": "rft.au",
        "date": "rft.date",
        "volume": "rft.volume",
        "issue": "rft.issue",
        "pages": "rft.pages",
        "doi": "rft_id",
        "url": "rft_id",
        "issn": "rft.issn",
        "publisher": "rft.pub",
        "abstract": "rft.description",
        "keywords": "rft.subject",
    },
    ("info:ofi/fmt:kev:mtx:book", "book"): {
        "title": "rft.btitle",
        "authors": "rft.au",
        "editors": "rft.aucorp",
        "publisher": "rft.pub",
        "address": "rft.place",
        "date": "rft.date",
        "edition": "rft.edition",
        "isbn": "rft.isbn",
        "url": "rft_id",
        "abstract": "rft.description",
        "keywords": "rft.subject",
    },
    ("info:ofi/fmt:kev:mtx:book", "bookitem"): {
        "title": "rft.atitle",
        "book_title": "rft.btitle",
        "authors": "rft.au",
        "editors": "rft.aucorp",
        "publisher": "rft.pub",
        "address": "rft.place",
        "date": "rft.date",
        "pages": "rft.pages",
        "isbn": "rft.isbn",
        "url": "rft_id",
        "abstract": "rft.description",
        "keywords": "rft.subject",
    },
    ("info:ofi/fmt:kev:mtx:dissertation", "dissertation"): {
        "title": "rft.title",
        "authors": "rft.au",
        "institution": "rft.inst",
        "date": "rft.date",
        "type": "rft.degree",
        "url": "rft_id",
        "abstract": "rft.description",
        "keywords": "rft.subject",
    },
    ("info:ofi/fmt:kev:mtx:data", "dataset"): {
        "title": "rft.title",
        "authors": "rft.au",
        "publisher": "rft.pub",
        "date": "rft.date",
        "doi": "rft_id",
        "url": "rft_id",
        "version": "rft.version",
        "abstract": "rft.description",
        "keywords": "rft.subject",
    },
    ("info:ofi/fmt:kev:mtx:report", "report"): {
        "title": "rft.title",
        "authors": "rft.au",
        "institution": "rft.inst",
        "date": "rft.date",
        "report_number": "rft.number",
        "url": "rft_id",
        "abstract": "rft.description",
        "keywords": "rft.subject",
    },
    ("info:ofi/fmt:kev:mtx:patent", "patent"): {
        "title": "rft.title",
        "inventors": "rft.au",
        "date": "rft.date",
        "number": "rft.number",
        "country": "rft.country",
        "url": "rft_id",
        "abstract": "rft.description",
        "keywords": "rft.subject",
    },
    ("info:ofi/fmt:kev:mtx:computerProgram", None): {
        "title": "rft.title",
        "authors": "rft.au",
        "version": "rft.version",
        "date": "rft.date",
        "publisher": "rft.pub",
        "url": "rft_id",
        "abstract": "rft.description",
        "keywords": "rft.subject",
    },
    ("info:ofi/fmt:kev:mtx:dc", None): {
        "title": "rft.title",
        "authors": "rft.creator",
        "publisher": "rft.publisher",
        "date": "rft.date",
        "type": "rft.type",
        "identifier": "rft.identifier",
        "url": "rft.identifier",
        "abstract": "rft.description",
        "keywords": "rft.subject",
    },
}


CFF_REFERENCE_TYPE_TO_COINS = {
    "art": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "Image",
    },
    "article": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:journal",
        "rft_genre": "article",
        "rft_type": "Text",
    },
    "audiovisual": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "MovingImage",
    },
    "bill": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "Text",
    },
    "blog": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "Text",
    },
    "book": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:book",
        "rft_genre": "book",
        "rft_type": "Text",
    },
    "catalogue": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "Text",
    },
    "conference-paper": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:conference",
        "rft_genre": "conference",
        "rft_type": "Text",
    },
    "conference": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:conference",
        "rft_genre": "conference",
        "rft_type": "Text",
    },
    "data": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:data",
        "rft_genre": "dataset",
        "rft_type": "Dataset",
    },
    "database": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:data",
        "rft_genre": "dataset",
        "rft_type": "Dataset",
    },
    "dictionary": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:book",
        "rft_genre": "book",
        "rft_type": "Text",
    },
    "edited-work": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:book",
        "rft_genre": "book",
        "rft_type": "Text",
    },
    "encyclopedia": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:book",
        "rft_genre": "book",
        "rft_type": "Text",
    },
    "film-broadcast": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "MovingImage",
    },
    "generic": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "Text",
    },
    "government-document": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:report",
        "rft_genre": "report",
        "rft_type": "Text",
    },
    "grant": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "Text",
    },
    "hearing": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "Sound",
    },
    "historical-work": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:book",
        "rft_genre": "book",
        "rft_type": "Text",
    },
    "legal-case": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "Text",
    },
    "legal-rule": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "Text",
    },
    "magazine-article": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:journal",
        "rft_genre": "article",
        "rft_type": "Text",
    },
    "manual": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:report",
        "rft_genre": "report",
        "rft_type": "Text",
    },
    "map": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "Image",
    },
    "multimedia": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "InteractiveResource",
    },
    "music": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "Sound",
    },
    "newspaper-article": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:journal",
        "rft_genre": "article",
        "rft_type": "Text",
    },
    "pamphlet": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:book",
        "rft_genre": "book",
        "rft_type": "Text",
    },
    "patent": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:patent",
        "rft_genre": "patent",
        "rft_type": "Text",
    },
    "personal-communication": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "Text",
    },
    "proceedings": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:conference",
        "rft_genre": "conference",
        "rft_type": "Text",
    },
    "report": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:report",
        "rft_genre": "report",
        "rft_type": "Text",
    },
    "serial": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:journal",
        "rft_genre": "journal",
        "rft_type": "Text",
    },
    "slides": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "Image",
    },
    "software-code": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:computerProgram",
        "rft_genre": None,
        "rft_type": "Software",
    },
    "software-container": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:computerProgram",
        "rft_genre": None,
        "rft_type": "Software",
    },
    "software-executable": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:computerProgram",
        "rft_genre": None,
        "rft_type": "Software",
    },
    "software-virtual-machine": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:computerProgram",
        "rft_genre": None,
        "rft_type": "Software",
    },
    "software": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:computerProgram",
        "rft_genre": None,
        "rft_type": "Software",
    },
    "sound-recording": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "Sound",
    },
    "standard": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "Text",
    },
    "statute": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "Text",
    },
    "thesis": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dissertation",
        "rft_genre": "dissertation",
        "rft_type": "Text",
    },
    "unpublished": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:unpublished",
        "rft_genre": "unpublished",
        "rft_type": "Text",
    },
    "video": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "MovingImage",
    },
    "website": {
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:dc",
        "rft_genre": None,
        "rft_type": "InteractiveResource",
    },
}


class CffCoinSpan:

    def __init__(self):
        self.coin_span: CoinSpan = []
        self.preferred_citation: CffCoinSpan | None = None
        self.references: CffCoinSpanList = []

    @classmethod
    def _create_identifiers_coin_span(
        cls,
        cff: dict,
        is_cff_reference: bool = False,
        is_cff_preferred_citation: bool = False,
    ) -> CoinSpan:
        identifiers_coin_span = []

        # some CFF files have 'doi' field
        if "doi" in cff:
            pid = str(cff["doi"])
            pid = pid.removeprefix("info:doi/")
            pid = pid.removeprefix("doi:")
            resolved_pid = f"https://doi.org/{pid}"
            identifiers_coin_span.append(("rft_id", resolved_pid))

        # some CFF files have an identifiers section
        # that contains one or more doi, url, swh, or other identifiers
        if "identifiers" in cff:
            for identifier in cff["identifiers"]:
                pid = identifier["value"]
                if pid is not None:
                    pid = str(pid).strip()
                    if pid is not "" and identifier["type"] in [
                        "doi",
                        "url",
                        "swh",
                        "other",
                    ]:
                        if identifier["type"] == "doi":
                            pid = pid.removeprefix("info:doi/")
                            pid = pid.removeprefix("doi:")
                            resolved_pid = f"https://doi.org/{pid}"
                        elif identifier["type"] == "url":
                            resolved_pid = pid
                        elif identifier["type"] == "swh":
                            resolved_pid = f"https://archive.softwareheritage.org/{pid}"
                        elif identifier["type"] == "other":
                            resolved_pid = None

                        # if the pid is not explicitly typed as a DOI, SHWID, or a URL
                        # use rft.identifier
                        if resolved_pid is not None:
                            identifiers_coin_span.append(("rft_id", f"{resolved_pid}"))
                        else:
                            identifiers_coin_span.append(("rft.identifier", f"{pid}"))
        return identifiers_coin_span

    @classmethod
    def _create_authors_coin_span(
        cls,
        cff: dict,
        is_cff_reference: bool = False,
        is_cff_preferred_citation: bool = False,
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
        cls,
        cff: dict,
        publisher: str | None = None,
        is_cff_reference: bool = False,
        is_cff_preferred_citation: bool = False,
    ) -> CoinSpan:
        publisher_coin_span: CoinSpan = []
        if publisher is not None and publisher != "":
            publisher_coin_span = [("rft.publisher", publisher)]
        else:
            if (is_cff_reference or is_cff_preferred_citation) and "publisher" in cff:
                publisher_coin_span = [("rft.publisher", cff["publisher"])]
        return publisher_coin_span

    @classmethod
    def _create_language_coin_span(
        cls,
        cff: dict,
        language: str | None = None,
        is_cff_reference: bool = False,
        is_cff_preferred_citation: bool = False,
    ) -> CoinSpan:
        language_coin_span: CoinSpan = []
        if language is not None and language != "":
            language_coin_span = [("rft.language", language)]
        else:
            if (is_cff_reference or is_cff_preferred_citation) and "language" in cff:
                language_coin_span = [("rft.language", cff["language"])]
        return language_coin_span

    @classmethod
    def _create_coin_span(
        cls,
        cff: dict,
        is_cff_reference: bool = False,
        is_cff_preferred_citation: bool = False,
        publisher: str | None = None,
        language: str | None = None,
        referrer_id: str | None = None,
    ) -> CoinSpan:
        if cff is None:
            raise ValueError(
                f"Invalid cff: it cannot be None. It must be a dictionary."
            )

        if referrer_id is None:
            referrer_id = DEFAULT_REFERRER_ID
        else:
            if len(referrer_id.split(":")) != 2:
                raise ValueError(
                    f"Invalid referrer id: it must have this form '<authority>:<id>'"
                )

        coin_span: CoinSpan = []

        publisher_coin_span: CoinSpan = cls._create_publisher_coin_span(
            cff=cff,
            publisher=publisher,
            is_cff_reference=is_cff_reference,
            is_cff_preferred_citation=is_cff_preferred_citation,
        )
        language_coin_span: CoinSpan = cls._create_language_coin_span(
            cff=cff,
            language=language,
            is_cff_reference=is_cff_reference,
            is_cff_preferred_citation=is_cff_preferred_citation,
        )
        authors_coin_span: CoinSpan = cls._create_authors_coin_span(
            cff=cff,
            is_cff_reference=is_cff_reference,
            is_cff_preferred_citation=is_cff_preferred_citation,
        )
        identifiers_coin_span: CoinSpan = cls._create_identifiers_coin_span(
            cff=cff,
            is_cff_reference=is_cff_reference,
            is_cff_preferred_citation=is_cff_preferred_citation,
        )

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

        if (
            "type" not in cff and not is_cff_reference and not is_cff_preferred_citation
        ) or cff["type"] == "software":
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
            if not is_cff_reference and not is_cff_preferred_citation:
                raise ValueError(
                    "Invalid CFF dict: 'type' must be 'software' or 'dataset'."
                )
            else:
                # create COinS metadata for
                # all references and preferred citations
                # that are not software or datasets

                if "type" in cff["type"]:
                    cff_type = cff["type"]
                else:
                    cff_type = "generic"
                if cff_type in CFF_REFERENCE_TYPE_TO_COINS:
                    rft_val_fmt = CFF_REFERENCE_TYPE_TO_COINS[cff["type"]][
                        "rft_val_fmt"
                    ]
                    coin_span += [("rft_val_fmt", rft_val_fmt)]

                    rft_genre = CFF_REFERENCE_TYPE_TO_COINS[cff["type"]]["rft_val_fmt"]
                    if rft_genre is not None:
                        coin_span += [("rft.genre", rft_genre)]
                    if rft_val_fmt != "info:ofi/fmt:kev:mtx:dc":
                        coin_span += [("rft_val_fmt", "info:ofi/fmt:kev:mtx:dc")]
                    rft_type = CFF_REFERENCE_TYPE_TO_COINS[cff["type"]]["rft_type"]
                    coin_span += [("rft.type", rft_type)]
                else:
                    raise ValueError(f"Invalid CFF Reference Type: {cff_type}")

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

        # construct main CoinSpan
        coin_span = cls._create_coin_span(
            cff=cff,
            is_cff_reference=False,
            is_cff_preferred_citation=False,
            publisher=publisher,
            language=language,
            referrer_id=referrer_id,
        )

        # construct preferred citation CoinSpan
        preferred_citation_coin_span: CoinSpan | None = None
        if "preferred_citation" in cff:
            cff_preferred_citation = cff["preferred_citation"]
            if cff_preferred_citation is not None:
                preferred_citation_coin_span = cls._create_coin_span(
                    cff=cff_preferred_citation,
                    is_cff_reference=False,
                    is_cff_preferred_citation=True,
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
                    is_cff_preferred_citation=True,
                    referrer_id=referrer_id,
                )
                reference = CffCoinSpan.from_coin_span(
                    coin_span=reference_coin_span,
                    is_reference=True,
                    is_preferred_citation=False,
                )
                references.append(reference)

        cff_coin_span = cls()
        cff_coin_span.coin_span = coin_span
        if preferred_citation_coin_span:
            preferred_citation = cls()
            preferred_citation.coin_span = preferred_citation_coin_span
            cff_coin_span.preferred_citation = preferred_citation
        else:
            cff_coin_span.preferred_citation = None
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
            # assume that all coin spans could be references since references have the most inclusive type (i.e., they allow for more than software or dataset)
            is_valid_coin_span, exception = cls.is_valid_coin_span_for_cff(
                coin_span=coin_span, is_reference=True, is_preferred_citation=False
            )
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
    def is_software_coin(cls, coin_span: CoinSpan):
        is_computer_program_mtx: bool = any(
            k == "rft_val_fmt" and v == "info:ofi/fmt:kev:mtx:computerProgram"
            for (k, v) in coin_span
        )
        is_computer_program_dc: bool = any(
            k == "rft_val_fmt" and v == "info:ofi/fmt:kev:mtx:dc"
            for (k, v) in coin_span
        ) and any(k == "rft.type" and v == "computerProgram" for (k, v) in coin_span)
        return is_computer_program_mtx or is_computer_program_dc

    @classmethod
    def is_dataset_coin(cls, coin_span: CoinSpan):
        is_dataset_mtx: bool = any(
            k == "rft_val_fmt" and v == "info:ofi/fmt:kev:mtx:data"
            for (k, v) in coin_span
        )
        is_dataset_dc: bool = any(
            k == "rft_val_fmt" and v == "info:ofi/fmt:kev:mtx:dc"
            for (k, v) in coin_span
        ) and any(k == "rft.type" and v == "DataSet" for (k, v) in coin_span)

        return is_dataset_mtx or is_dataset_dc

    @classmethod
    def is_valid_coin_span_for_cff(
        cls, coin_span: CoinSpan, is_reference: bool, is_preferred_citation: bool
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

        if not (is_reference or is_preferred_citation) and not (
            cls.is_software_coin(coin_span=coin_span)
            or cls.is_dataset_coin(coin_span=coin_span)
        ):
            exception = Exception(
                "Invalid COinS for CFF: must contain metadata for either a computer program or a dataset."
            )
            return False, exception

        return True, None

    @classmethod
    def from_coin_span(
        cls, coin_span: CoinSpan, is_reference: bool, is_preferred_citation: bool
    ) -> CffCoinSpan:
        # construct coins metadata
        is_valid_coin_span, exception = cls.is_valid_coin_span_for_cff(
            coin_span=coin_span,
            is_reference=is_reference,
            is_preferred_citation=is_preferred_citation,
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
