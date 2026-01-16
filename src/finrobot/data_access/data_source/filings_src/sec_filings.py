import os
import re
import signal
import typing as T
from datetime import date
from enum import Enum

import requests
from ratelimit import limits, sleep_and_retry
from unstructured.staging.base import convert_to_isd

from finrobot.data_access.data_source.filings_src.prepline_sec_filings.sec_document import (
    REPORT_TYPES,
    VALID_FILING_TYPES,
    SECDocument,
)
from finrobot.data_access.data_source.filings_src.prepline_sec_filings.sections import (
    ALL_SECTIONS,
    SECTIONS_10K,
    SECTIONS_10Q,
    SECTIONS_S1,
    section_string_to_enum,
    validate_section_names,
)

DATE_FORMAT_TOKENS = "%Y-%m-%d"
DEFAULT_BEFORE_DATE = date.today().strftime(DATE_FORMAT_TOKENS)
DEFAULT_AFTER_DATE = date(2000, 1, 1).strftime(DATE_FORMAT_TOKENS)


class timeout:
    def __init__(self, seconds: int = 1, error_message: str = "Timeout"):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum: int, frame: T.Any) -> None:
        raise TimeoutError(self.error_message)

    def __enter__(self) -> None:
        try:
            signal.signal(signal.SIGALRM, self.handle_timeout)
            signal.alarm(self.seconds)
        except ValueError:
            pass

    def __exit__(self, type: T.Any, value: T.Any, traceback: T.Any) -> None:
        try:
            signal.alarm(0)
        except ValueError:
            pass


# pipeline-api
def get_regex_enum(section_regex: str) -> T.Any:
    """Get sections using regular expression

    Args:
        section_regex (str): regular expression for the section name

    Returns:
        CustomSECSection.CUSTOM: Custom regex section name
    """

    class CustomSECSection(Enum):
        CUSTOM = re.compile(section_regex)

        @property
        def pattern(self) -> T.Any:
            return self.value

    return CustomSECSection.CUSTOM


class SECExtractor:
    def __init__(
        self,
        ticker: str,
        sections: T.List[str] = ["_ALL"],
        filing_type: T.Optional[str] = None,
    ) -> None:
        """_summary_

        Args:
            tickers (List[str]): list of ticker
            amount (int): amount of documenteds
            filing_type (str): 10-K or 10-Q
            start_date (str, optional): start date of getting files. Defaults to DEFAULT_AFTER_DATE.
            end_date (str, optional): end date of getting files. Defaults to DEFAULT_BEFORE_DATE.
            sections (List[str], optional): sections required, check sections names. Defaults to ["_ALL"].
        """

        self.ticker = ticker
        self.sections = sections
        self.filing_type = filing_type

    def get_year(self, filing_details: str) -> T.Optional[str]:
        """Get the year for 10-K and year,month for 10-Q

        Args:
            filing_details (str): filing url

        Returns:
            str: year for 10-K and year,month for 10-Q
        """
        details = filing_details.split("/")[-1]
        if self.filing_type == "10-K":
            matches = re.findall(r"20\d{2}", details)
        elif self.filing_type == "10-Q":
            matches = re.findall(r"20\d{4}", details)

        if matches:
            return matches[-1]  # Return the first match
        else:
            return None  # In case no match is found

    def get_all_text(self, section: str, all_narratives: T.Dict[str, T.List[T.Dict[str, T.Any]]]) -> str:
        """Join all the text from a section

        Args:
            section (str): section name
            all_narratives (dict): dictionary of section names and text

        Returns:
            str: joined text
        """
        all_texts = []
        for text_dict in all_narratives[section]:
            for key, val in text_dict.items():
                if key == "text":
                    all_texts.append(val)
        return " ".join(all_texts)

    def get_section_texts_from_text(self, text: str) -> T.Dict[str, str]:
        """Get the text from filing document URL

        Args:
            text (str): filing text content

        Returns:
            Dict[str, str]: all texts of sections
        """
        all_narratives, filing_type = self.pipeline_api(text, m_section=self.sections)
        all_narrative_dict = dict.fromkeys(all_narratives.keys())

        for section in all_narratives:
            all_narrative_dict[section] = self.get_all_text(section, all_narratives)

        return T.cast(T.Dict[str, str], all_narrative_dict)

    def pipeline_api(
        self,
        text: str,
        m_section: T.List[str] = [],
        m_section_regex: T.List[str] = [],
    ) -> T.Tuple[T.Dict[str, T.Any], str]:
        """Unsturcured API to get the text

        Args:
            text (str): Text from the filing document URL
            m_section (list, optional): Section required. Defaults to [].
            m_section_regex (list, optional): Custom Section required using regex . Defaults to [].

        Raises:
            ValueError: Invalid document names
            ValueError: Invalid section names

        Returns:
                Tuple[Dict[str, Any], str]: section and correspoding texts, and filing type
        """
        validate_section_names(m_section)

        sec_document = SECDocument.from_string(text)
        if sec_document.filing_type not in VALID_FILING_TYPES:
            raise ValueError(
                f"SEC document filing type {sec_document.filing_type} is not supported, "
                f"must be one of {','.join(VALID_FILING_TYPES)}"
            )
        results = {}
        if m_section == [ALL_SECTIONS]:
            filing_type = sec_document.filing_type
            if filing_type in REPORT_TYPES:
                if filing_type.startswith("10-K"):
                    m_section = [enum.name for enum in SECTIONS_10K]
                elif filing_type.startswith("10-Q"):
                    m_section = [enum.name for enum in SECTIONS_10Q]
                else:
                    raise ValueError(f"Invalid report type: {filing_type}")

            else:
                m_section = [enum.name for enum in SECTIONS_S1]
        for section in m_section:
            results[section] = sec_document.get_section_narrative(section_string_to_enum[section])

        for i, section_regex in enumerate(m_section_regex):
            regex_num = get_regex_enum(section_regex)
            with timeout(seconds=5):
                section_elements = sec_document.get_section_narrative(regex_num)
                results[f"REGEX_{i}"] = section_elements
        return {
            section: convert_to_isd(section_narrative) for section, section_narrative in results.items()
        }, sec_document.filing_type

    @sleep_and_retry
    @limits(calls=10, period=1)
    def get_filing(self, url: str, company: str, email: str) -> str:
        """Fetches the specified filing from the SEC EDGAR Archives. Conforms to the rate
        limits specified on the SEC website.
        ref: https://www.sec.gov/os/accessing-edgar-data"""
        session = self._get_session(company, email)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = session.get(url)
        response.raise_for_status()
        return response.text

    def _get_session(self, company: T.Optional[str] = None, email: T.Optional[str] = None) -> requests.Session:
        """Creates a requests sessions with the appropriate headers set. If these headers are not
        set, SEC will reject your request.
        ref: https://www.sec.gov/os/accessing-edgar-data"""
        if company is None:
            company = os.environ.get("SEC_API_ORGANIZATION")
        if email is None:
            email = os.environ.get("SEC_API_EMAIL")
        assert company
        assert email
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": f"{company} {email}",
                "Content-Type": "text/html",
            }
        )
        return session
