import importlib.machinery
import sys
import types
import typing as T
from typing import Any, Callable, Dict, List, Optional, Union
from unittest.mock import MagicMock


class MockModule(types.ModuleType):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.__path__: List[str] = []
        if "chromadb" in name:
            self.__version__ = "0.5.0"
        elif "langchain" in name:
            self.__version__ = "0.1.0"

    def __getattr__(self, name: str) -> Any:
        if name in ("__spec__", "__path__", "__name__", "__version__", "__file__"):
            return super().__getattribute__(name)
        # Create a nested mock module or attribute on the fly
        # For simplicity, returning a MagicMock is usually enough once the module exists
        return MagicMock()


class MockLoader:
    @classmethod
    def create_module(cls, spec: importlib.machinery.ModuleSpec) -> MockModule:
        return MockModule(spec.name)

    @classmethod
    def exec_module(cls, module: types.ModuleType) -> None:
        pass


class MockFinder:
    @classmethod
    def find_spec(
        cls,
        fullname: str,
        path: Optional[List[str]],
        target: Optional[types.ModuleType] = None,
    ) -> Optional[importlib.machinery.ModuleSpec]:
        mocked_prefixes = [
            "langchain",
            "langchain_community",
            "langchain_openai",
            "langchain_chroma",
            "langchain_text_splitters",
            "chromadb",
            "unstructured",
            "backtrader",
            "pypdf",
            "marker",
            "sentence_transformers",
            "finnlp",
            "agent_framework",
        ]
        if any(fullname == p or fullname.startswith(p + ".") for p in mocked_prefixes):
            return importlib.machinery.ModuleSpec(
                fullname,
                MockLoader,
                is_package=True,  # type: ignore
            )
        return None


# Register the finder
sys.meta_path.insert(0, MockFinder)

# Also pre-populate some critical ones to avoid initial lookup issues
for p in ["langchain", "chromadb", "unstructured", "backtrader", "pypdf"]:
    if p not in sys.modules:
        sys.modules[p] = MockModule(p)

# Satisfy specific property checks
# Ensure specific attributes exist if they are imported individually
sys.modules["chromadb.api"] = MockModule("chromadb.api")
sys.modules["chromadb"].api = sys.modules["chromadb.api"]
sys.modules["chromadb.api"].ClientAPI = MagicMock()

sys.modules["backtrader.strategies"] = MockModule("backtrader.strategies")
sys.modules["backtrader"].strategies = sys.modules["backtrader.strategies"]
sys.modules["backtrader.strategies"].SMA_CrossOver = MagicMock()


class MockAnalyzer:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.strategy = MagicMock()

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def notify_order(self, order: Any) -> None:
        pass

    def get_analysis(self) -> Dict[str, Any]:
        return {}


sys.modules["backtrader"].Analyzer = MockAnalyzer


# Enhance agent_framework mocks
class ChatAgent:
    def __init__(
        self,
        name: str,
        instructions: Optional[str] = None,
        description: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self._instructions = instructions
        self.description = description
        self.tools = tools

    async def run(self, *args: Any, **kwargs: Any) -> None:
        pass


class ChatMessage:
    def __init__(self, text: str, role: str) -> None:
        self.text = text
        self.role = role


# Define Dummy classes to replace unstructured classes
class HTMLDocument:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.elements: List[Any] = []

    def _read_xml(self, content: Any) -> None:
        pass

    def doc_after_cleaners(self, *args: Any, **kwargs: Any) -> "HTMLDocument":
        return self

    @classmethod
    def from_elements(cls, elements: List[Any]) -> "HTMLDocument":
        doc = cls()
        doc.elements = elements
        return doc

    def after_element(self, element: Any) -> "HTMLDocument":
        # Return a new doc or mock
        return self

    def before_element(self, element: Any) -> "HTMLDocument":
        return self


class Element:
    def __init__(self, text: Optional[str] = None) -> None:
        self.text = text or ""

    def __str__(self) -> str:
        return self.text


class Text(Element):
    pass


class Title(Element):
    pass


class NarrativeText(Element):
    pass


class ListItem(Element):
    pass


# Setup specific unstructured mocks
mock_unstructured = MockModule("unstructured")
mock_doc_html = MockModule("unstructured.documents.html")
mock_doc_html.HTMLDocument = HTMLDocument
mock_doc_elements = MockModule("unstructured.documents.elements")
mock_doc_elements.Element = Element
mock_doc_elements.Text = Text
mock_doc_elements.Title = Title
mock_doc_elements.NarrativeText = NarrativeText
mock_doc_elements.ListItem = ListItem
mock_nlp_partition = MockModule("unstructured.nlp.partition")
mock_nlp_partition.is_possible_title = lambda x: False

sys.modules["unstructured"] = mock_unstructured
sys.modules["unstructured.documents"] = MockModule("unstructured.documents")
sys.modules["unstructured.documents.html"] = mock_doc_html
sys.modules["unstructured.documents.elements"] = mock_doc_elements
sys.modules["unstructured.nlp"] = MockModule("unstructured.nlp")
sys.modules["unstructured.nlp.partition"] = mock_nlp_partition


mock_af = sys.modules.get("agent_framework", MockModule("agent_framework"))
mock_af.ChatAgent = ChatAgent
mock_af.ChatMessage = ChatMessage
sys.modules["agent_framework"] = mock_af
