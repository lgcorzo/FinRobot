import importlib
import sys
from unittest.mock import MagicMock, patch

import pytest


# Helpers
def mock_clean_sec_text(text, lowercase=False) -> None:
    t = str(text).strip()
    if lowercase:
        t = t.lower()
    return t


# Import module under test
# Since conftest mocks unstructured, we can just import.
from unstructured.documents.elements import ListItem, NarrativeText, Text, Title
from unstructured.documents.html import HTMLDocument

import finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document as sec_doc_module
from finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document import SECDocument, SECSection


class TestSECDocument:
    def setup_method(self) -> None:
        self.clean_patcher = patch(
            "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.clean_sec_text",
            side_effect=mock_clean_sec_text,
        )
        self.mock_clean = self.clean_patcher.start()

    def teardown_method(self) -> None:
        self.clean_patcher.stop()

    def test_init(self) -> None:
        doc = SECDocument()
        assert isinstance(doc, HTMLDocument)

    def test_raise_invalid_filing_type(self) -> None:
        doc = SECDocument()
        doc.filing_type = "INVALID"

        with pytest.raises(ValueError, match="Filing type was INVALID"):
            doc.get_table_of_contents()

        doc.filing_type = None
        with pytest.raises(ValueError, match="Filing type is empty"):
            doc.get_table_of_contents()

    def test_filter_toc_10k(self) -> None:
        SECDocument = sec_doc_module.SECDocument
        doc = SECDocument()
        doc.filing_type = "10-K"
        e1 = Text("Intro")
        e2 = Text("Form 10-K")
        e3 = Text("Part I")  # Index 2 (Start)
        e4 = Text("Item 1")  # Index 3
        e5 = Text("Spacer")  # Index 4 (End - 1 -> 3)
        e6 = Text("Part I")  # Index 5 (End logic triggers here)
        e7 = Text("More")

        # Code logic: end = i - 1.
        # If match at 5 ("Part I"). end = 4.
        # Slice [2:4] -> [e3, e4].
        # Length 2. "Part I", "Item 1".

        elements = [e1, e2, e3, e4, e5, e6, e7]

        res = doc._filter_table_of_contents(elements)
        assert len(res) == 2
        assert res[0].text == "Part I"
        assert res[1].text == "Item 1"

    def test_filter_toc_s1(self) -> None:
        SECDocument = sec_doc_module.SECDocument
        doc = SECDocument()
        doc.filing_type = "S-1"
        e1 = Text("Intro")
        e2 = Text("Prospectus Summary")  # Index 1 (Start)
        e3 = Text("Risk Factors")  # Index 2
        e4 = Text("Spacer")  # Index 3
        e5 = Text("Prospectus Summary")  # Index 4 (End logic)
        e6 = Text("Content")

        # Code logic: end = indices[1] - 1.
        # indices[1] = 4. end = 3.
        # Slice [1:3] -> [e2, e3].

        elements = [e1, e2, e3, e4, e5, e6]

        res = doc._filter_table_of_contents(elements)
        assert len(res) == 2
        assert res[0].text == "Prospectus Summary"
        assert res[1].text == "Risk Factors"

    def test_is_risk_title(self) -> None:
        assert sec_doc_module.is_risk_title("Item 1A. Risk Factors", "10-K")
        assert sec_doc_module.is_risk_title("Risk Factors", "S-1")
        assert not sec_doc_module.is_risk_title("Summary", "10-K")

    def test_is_toc_title(self) -> None:
        assert sec_doc_module.is_toc_title("Table of Contents")
        assert sec_doc_module.is_toc_title("INDEX")
        assert not sec_doc_module.is_toc_title("Intro")

    def test_get_section_narrative_no_toc(self) -> None:
        SECDocument = sec_doc_module.SECDocument
        doc = SECDocument()
        doc.filing_type = "10-K"

        t1 = Title("Item 1A. Risk Factors")
        n1 = NarrativeText("Risk content")
        t2 = Title("Item 2. Properties")

        doc.elements = [t1, n1, t2]

        with patch(
            "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.is_possible_title"
        ) as mock_possible:
            mock_possible.side_effect = lambda t: "Item" in t

            res = doc.get_section_narrative_no_toc(sec_doc_module.SECSection.RISK_FACTORS)
            assert len(res) == 1
            assert res[0] == n1

    def test_read_xml(self) -> None:
        SECDocument = sec_doc_module.SECDocument
        doc = SECDocument()
        doc.document_tree = MagicMock()
        type_elem = MagicMock()
        type_elem.text = "10-K"
        doc.document_tree.find.return_value = type_elem

        # _read_xml triggers super()._read_xml which we dummied.
        doc._read_xml("content")

        assert doc.filing_type == "10-K"

    def test_is_item_title(self) -> None:
        assert sec_doc_module.is_item_title("Item 1. Business", "10-K")
        assert not sec_doc_module.is_item_title("Business", "10-K")
        assert sec_doc_module.is_item_title("PROSPECTUS", "S-1")

    def test_get_table_of_contents_success(self) -> None:
        # Mock dependencies for clustering logic
        with patch(
            "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.to_sklearn_format"
        ) as mock_sklearn:
            # Return dummy locations
            import numpy as np

            mock_sklearn.return_value = np.array([[1.0], [2.0], [3.0]], dtype=np.float32)

            with patch(
                "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.DBSCAN"
            ) as mock_dbscan:
                mock_clustering = MagicMock()
                # All in cluster 0
                mock_clustering.fit_predict.return_value = np.array([0, 0, 0])
                mock_dbscan.return_value = mock_clustering

                with patch(
                    "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.cluster_num_to_indices"
                ) as mock_indices:
                    mock_indices.return_value = [0, 1, 2]  # All elements correspond to cluster 0

                    SECDocument = sec_doc_module.SECDocument
                    doc = SECDocument()
                    doc.filing_type = "10-K"
                    # Create elements: Title(Risk), Title(Table of Contents), Title(Risk)
                    # To satisfy is_risk_title AND is_toc_title in the cluster
                    e1 = Title("Item 1A. Risk Factors")  # Risk
                    e2 = Title("Table of Contents")  # TOC
                    e3 = Title("Part I")
                    e4 = Text("Item 1")
                    e5 = Text("Part I")  # End marker

                    doc.elements = [e1, e2, e3, e4, e5]

                    # We need _filter_table_of_contents to work.
                    # logic: cluster elements are filtered.
                    # with [e1, e2, e3, e4, e5], filtered might need adjustments.
                    # Re-use previous filter logic test case elements?

                    # Let's just mock _filter_table_of_contents to return known result
                    with patch.object(SECDocument, "_filter_table_of_contents", return_value=[e3, e4]) as mock_filter:
                        toc = doc.get_table_of_contents()
                        assert isinstance(toc, HTMLDocument)
                        assert toc.elements == [e3, e4]
                        mock_filter.assert_called()

    def test_get_section_narrative_with_toc(self) -> None:
        SECDocument = sec_doc_module.SECDocument
        doc = SECDocument()
        doc.filing_type = "10-K"

        # Setup TOC structure
        toc_element = Title("Item 1. Business")
        next_toc_element = Title("Item 1A. Risk Factors")

        # Mock get_table_of_contents to return a TOC doc
        dummy_toc = HTMLDocument()
        dummy_toc.pages = [1]  # Make it truthy for "if not toc.pages:" check?
        # HTMLDocument attributes in dummy are minimal.
        # Check source: "if not toc.pages:" -> get_section_narrative_no_toc
        # So we need toc.pages to be Truthy.
        dummy_toc.pages = ["page1"]
        dummy_toc.elements = [toc_element, next_toc_element]

        # Mock _get_toc_sections
        with patch.object(SECDocument, "get_table_of_contents", return_value=dummy_toc):
            with patch.object(SECDocument, "_get_toc_sections", return_value=(toc_element, next_toc_element)):
                # Mock doc methods needed
                # doc.after_element -> doc_after_section_toc
                # get_element_by_title -> section_start
                # doc.after_element(section_start) -> doc_after_heading
                # get_element_by_title -> section_end

                # This is complex to mock purely by methods because they return Docs.
                # Assuming our Dummy HTMLDocument returns `self` for after_element/before_element
                # We need `get_element_by_title` to return something.

                e_start = Title("Item 1. Business")
                e_end = Title("Item 1A. Risk Factors")
                e_content = NarrativeText("Business Content")

                doc.elements = [e_start, e_content, e_end]

                with patch(
                    "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.get_element_by_title"
                ) as mock_get_elem:
                    mock_get_elem.side_effect = [e_start, e_end]

                    with patch(
                        "finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document.get_narrative_texts"
                    ) as mock_get_text:
                        mock_get_text.return_value = [e_content]

                        # Call
                        res = doc.get_section_narrative(sec_doc_module.SECSection.BUSINESS)

                        assert res == [e_content]
