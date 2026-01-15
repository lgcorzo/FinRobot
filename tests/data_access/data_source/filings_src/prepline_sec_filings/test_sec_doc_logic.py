from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document import (
    SECDocument,
    SECSection,
    cluster_num_to_indices,
    get_narrative_texts,
    to_sklearn_format,
)
from unstructured.documents.elements import ListItem, NarrativeText, Text, Title


# Helper to avoid MagicMock in regex
def mock_clean(text, **kwargs):
    t = str(text).strip()
    if kwargs.get("lowercase"):
        t = t.lower()
    return t


@pytest.fixture(autouse=True)
def patch_clean():
    with patch(
        "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.clean_sec_text",
        side_effect=mock_clean,
    ) as m:
        yield m


def test_sec_doc_misc_logic():
    doc = SECDocument.from_elements([])
    doc.filing_type = "10-K"
    with patch("unstructured.documents.html.HTMLDocument.doc_after_cleaners") as mock_base:
        mock_base.return_value = MagicMock()
        new_doc = doc.doc_after_cleaners()
        assert new_doc.filing_type == "10-K"

    assert doc._is_last_section_in_report(SECSection.FORM_SUMMARY, MagicMock()) is True
    assert doc._is_last_section_in_report(SECSection.EXHIBITS, MagicMock()) is True
    doc.filing_type = "10-Q"
    assert doc._is_last_section_in_report(SECSection.EXHIBITS, MagicMock()) is True

    doc_mock = MagicMock()
    doc_mock.elements = [NarrativeText("A"), Title("B"), NarrativeText("C")]
    assert len(get_narrative_texts(doc_mock, up_to_next_title=True)) == 1
    assert len(get_narrative_texts(doc_mock, up_to_next_title=False)) == 2

    elem_idxs = np.array([10.0, 30.0])
    res = np.array([0, 0])
    assert cluster_num_to_indices(0, elem_idxs, res) == [10, 30]

    with patch(
        "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.is_possible_title",
        side_effect=[True, False],
    ):
        elements = [Title(text="T"), NarrativeText(text="N")]
        fmt = to_sklearn_format(elements)
        assert fmt.shape == (1, 1)


def test_get_toc_sections_search():
    doc = SECDocument.from_elements([])
    doc.filing_type = "10-K"
    toc_mock = MagicMock()
    e1 = Title(text="Item 1")
    e2 = Title(text="Item 1A")
    toc_mock.elements = [e1, e2]

    with patch(
        "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.is_section_elem",
        side_effect=[True, False, True],
    ):
        toc_mock.after_element.return_value = MagicMock(elements=[e2])
        start, end = doc._get_toc_sections(SECSection.BUSINESS, toc_mock)
        assert start == e1
        assert end == e2


def test_is_section_elem_patterns():
    from finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document import is_section_elem

    elem = Title(text="Item 1. Business")
    assert is_section_elem(SECSection.BUSINESS, elem, "10-K") is True

    elem = Title(text="SUMMARY")
    assert is_section_elem(SECSection.PROSPECTUS_SUMMARY, elem, "S-1") is True


def test_s1_titles():
    from finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document import (
        is_item_title,
        is_risk_title,
    )

    assert is_risk_title("Risk Factors", "S-1") is True
    assert is_item_title("PROSPECTUS", "S-1") is True


def test_match_functions():
    from finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document import (
        match_10k_toc_title_to_section,
        match_s1_toc_title_to_section,
    )

    assert match_s1_toc_title_to_section("P", "P") is True
    assert match_10k_toc_title_to_section("item 1. business", "item 1") is True
    assert match_10k_toc_title_to_section("risk factors", "risk factors") is True
    assert match_10k_toc_title_to_section("unknown", "other") is False


def test_get_risk_narrative():
    doc = SECDocument.from_elements([])
    with patch.object(doc, "get_section_narrative") as mock_get:
        doc.get_risk_narrative()
        mock_get.assert_called_with(SECSection.RISK_FACTORS)


def test_get_element_by_title():
    from finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document import get_element_by_title

    e1 = Title(text="Item 1")
    res = get_element_by_title(iter([e1]), "Item 1", "10-K")
    assert res == e1

    res = get_element_by_title(iter([e1]), "Item 1", "S-1")
    assert res == e1


# NEW TESTS FOR FINAL COVERAGE PUSH
def test_sec_document_final_gaps():
    # Line 93: _filter_table_of_contents fallback []
    doc = SECDocument.from_elements([])
    doc.filing_type = "UNKNOWN"
    assert doc._filter_table_of_contents([]) == []

    # Line 101: get_table_of_contents empty title_locs
    doc = SECDocument.from_elements([])
    doc.filing_type = "10-K"
    toc = doc.get_table_of_contents()
    assert len(toc.elements) == 0

    # Line 118: get_table_of_contents fallback to elements
    doc = SECDocument.from_elements([Title(text="T")])
    doc.filing_type = "10-K"
    with patch(
        "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.to_sklearn_format",
        return_value=np.array([[0.0]]),
    ), patch(
        "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.DBSCAN.fit_predict",
        return_value=np.array([0]),
    ):
        # No risk or toc title in cluster elements, triggers line 118
        toc = doc.get_table_of_contents()
        assert len(toc.elements) == 0

    # Line 136: in_section = False when title found but no elements
    doc = SECDocument.from_elements([Title(text="Item 1. Business"), Title(text="Item 1A")])
    doc.filing_type = "10-K"
    res = doc.get_section_narrative_no_toc(SECSection.BUSINESS)
    assert len(res) == 0  # Line 136 triggered and then line 143 returned []

    # Line 152: _get_toc_sections None
    doc = SECDocument.from_elements([])
    doc.filing_type = "10-K"
    assert doc._get_toc_sections(SECSection.BUSINESS, doc) == (None, None)

    # Line 161: _get_toc_sections (section_toc, None)
    doc = SECDocument.from_elements([Title(text="Item 1. Business")])
    doc.filing_type = "10-K"
    with patch(
        "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.is_section_elem",
        return_value=True,
    ):
        res = doc._get_toc_sections(SECSection.BUSINESS, doc)
        assert res[0].text == "Item 1. Business"
        assert res[1] is None

    # Line 172, 179, 191, 200, 211
    doc = SECDocument.from_elements([Title(text="Item 1. Business")])
    doc.filing_type = "10-K"
    # Line 172: not toc.pages -> calls no_toc
    with patch.object(doc, "get_table_of_contents") as mock_toc_call:
        mock_toc = MagicMock()
        mock_toc.pages = []
        mock_toc_call.return_value = mock_toc
        doc.get_section_narrative(SECSection.BUSINESS)

    # Line 179: section_toc is None
    with patch.object(doc, "get_table_of_contents") as mock_toc_call:
        mock_toc = MagicMock()
        mock_toc.pages = [1]
        mock_toc_call.return_value = mock_toc
        with patch.object(doc, "_get_toc_sections", return_value=(None, None)):
            assert doc.get_section_narrative(SECSection.BUSINESS) == []

    # Line 191: section_start_element is None
    with patch.object(doc, "get_table_of_contents") as mock_toc_call, patch.object(
        doc, "_get_toc_sections", return_value=(MagicMock(), MagicMock())
    ), patch.object(doc, "after_element", return_value=MagicMock(elements=[])), patch(
        "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.get_element_by_title",
        return_value=None,
    ):
        mock_toc = MagicMock()
        mock_toc.pages = [1]
        mock_toc_call.return_value = mock_toc
        assert doc.get_section_narrative(SECSection.BUSINESS) == []

    # Line 200: _is_last_section_in_report or next_section_toc is None
    with patch.object(doc, "get_table_of_contents") as mock_toc_call, patch.object(
        doc, "_get_toc_sections", return_value=(MagicMock(), None)
    ), patch.object(doc, "after_element", return_value=MagicMock(elements=[])), patch(
        "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.get_element_by_title",
        return_value=MagicMock(),
    ), patch(
        "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.get_narrative_texts",
        return_value=["OK"],
    ):
        mock_toc = MagicMock()
        mock_toc.pages = [1]
        mock_toc_call.return_value = mock_toc
        assert doc.get_section_narrative(SECSection.BUSINESS) == ["OK"]

    # Line 211: section_end_element is None
    with patch.object(doc, "get_table_of_contents") as mock_toc_call, patch.object(
        doc, "_get_toc_sections", return_value=(MagicMock(), MagicMock())
    ), patch.object(doc, "after_element", return_value=MagicMock(elements=[])), patch(
        "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.get_element_by_title",
        side_effect=[MagicMock(), None],
    ), patch(
        "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.get_narrative_texts",
        return_value=["OK_END"],
    ):
        mock_toc = MagicMock()
        mock_toc.pages = [1]
        mock_toc_call.return_value = mock_toc
        assert doc.get_section_narrative(SECSection.BUSINESS) == ["OK_END"]

    # Line 292, 301
    from finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document import (
        is_item_title,
        is_risk_title,
    )

    assert is_item_title("T", "UNKNOWN") is False
    assert is_risk_title("T", "UNKNOWN") is False
