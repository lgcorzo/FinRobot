import asyncio
import os
import typing as T
from abc import ABC, abstractmethod

# agent_framework imports
from agent_framework import ChatAgent, ChatMessage
from agent_framework.openai import OpenAIChatClient

from finrobot.tools import get_toolkits

from ..agent_library import library
from ..prompts import leader_system_message, role_system_message
from ..utils import instruction_message, instruction_trigger, order_message, order_trigger


class FinRobot(ChatAgent):
    def __init__(
        self,
        agent_config: T.Union[str, T.Dict[str, T.Any]],
        system_message: T.Optional[str] = None,  # overwrites previous config
        toolkits: T.List[T.Union[T.Callable[..., T.Any], T.Dict[str, T.Any], T.Any]] = [],  # overwrites previous config
        llm_config: T.Dict[str, T.Any] = {},
        **kwargs: T.Any,
    ) -> None:
        orig_name = ""
        if isinstance(agent_config, str):
            orig_name = agent_config
            name = orig_name.replace("_Shadow", "")
            assert name in library, f"FinRobot {name} not found in agent library."
            agent_config = library[name]

        agent_config = self._preprocess_config(agent_config)

        assert agent_config, "agent_config is required."
        assert agent_config.get("name", ""), "name needs to be in config."

        name = orig_name if orig_name else agent_config["name"]
        default_system_message = agent_config.get("profile", None)
        default_toolkits = agent_config.get("toolkits", [])

        system_message = system_message or default_system_message
        self.toolkits_config = toolkits or default_toolkits

        name = name.replace(" ", "_").strip()

        # Prepare tools
        tools = get_toolkits(self.toolkits_config)

        # Prepare Chat Client
        # Using default env vars or passed llm_config
        # Assuming llm_config has 'config_list' or similar from autogen, but OpenAIChatClient needs simpler config
        # We will try to extract simple keys or use env vars

        model = llm_config.get("model", os.getenv("OPENAI_MODEL", "gpt-4"))
        api_key = llm_config.get("api_key", os.getenv("OPENAI_API_KEY"))
        base_url = llm_config.get("base_url", os.getenv("OPENAI_API_BASE"))

        client = OpenAIChatClient(model_id=model, api_key=api_key, base_url=base_url)

        super().__init__(
            chat_client=client,
            name=name,
            instructions=system_message,
            description=agent_config["description"],
            tools=tools,
            **kwargs,
        )

    def _preprocess_config(self, config: T.Dict[str, T.Any]) -> T.Dict[str, T.Any]:
        role_prompt, leader_prompt, responsibilities = "", "", ""

        if "responsibilities" in config:
            title = config["title"] if "title" in config else config.get("name", "")
            if "name" not in config:
                config["name"] = config["title"]
            responsibilities = config["responsibilities"]
            responsibilities = (
                "\n".join([f" - {r}" for r in responsibilities])
                if isinstance(responsibilities, list)
                else responsibilities
            )
            role_prompt = role_system_message.format(
                title=title,
                responsibilities=responsibilities,
            )

        name = config.get("name", "")
        description = f"Name: {name}\nResponsibility:\n{responsibilities}" if responsibilities else f"Name: {name}"
        config["description"] = description.strip()

        if "group_desc" in config:
            group_desc = config["group_desc"]
            leader_prompt = leader_system_message.format(group_desc=group_desc)

        config["profile"] = (
            (role_prompt + "\n\n").strip() + (leader_prompt + "\n\n").strip() + config.get("profile", "")
        ).strip()

        return config

    def register_proxy(self, proxy: T.Any) -> None:
        # In agent_framework, we don't register proxy explicitly for tools usually.
        # But if needed, we might handle it here. For now, pass.
        pass


class SingleAssistantBase(ABC):
    def __init__(
        self,
        agent_config: T.Union[str, T.Dict[str, T.Any]],
        llm_config: T.Dict[str, T.Any] = {},
    ) -> None:
        self.assistant = FinRobot(
            agent_config=agent_config,
            llm_config=llm_config,
        )

    @abstractmethod
    def chat(self, message: str, **kwargs: T.Any) -> T.Any:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass


class SingleAssistant(SingleAssistantBase):
    def __init__(
        self,
        agent_config: T.Union[str, T.Dict[str, T.Any]],
        llm_config: T.Dict[str, T.Any] = {},
        **kwargs: T.Any,
    ) -> None:
        super().__init__(agent_config, llm_config=llm_config)
        # No UserProxyAgent in this style, assuming simple chat loop or direct interaction

    def chat(self, message: str, use_cache: bool = False, **kwargs: T.Any) -> T.Any:
        # We need to run async implementation synchronously if called from sync code
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # If already running (e.g. in notebook), we might need task
            # But for simplicity assuming standard script usage
            response = self._run_chat_sync(message)
        else:
            response = loop.run_until_complete(self._chat_async(message))
        return response

    async def _chat_async(self, message: str) -> T.Any:
        # Create a user message
        user_msg = ChatMessage(text=message, role="user")
        # Run the agent
        # ChatAgent.run(messages)
        await self.assistant.run(user_msg)
        # Accessing last message? ChatAgent usually updates its state/memory.
        # We might want to print the output.

    def _run_chat_sync(self, message: str) -> T.Any:
        return asyncio.run(self._chat_async(message))

    def reset(self) -> None:
        # agent_framework agents might not have reset?
        pass


class SingleAssistantRAG(SingleAssistant):
    # RAG implementation needs update to use agent_framework RAG capabilities or custom tools
    # For now, placeholder or adapting logic
    def __init__(
        self,
        agent_config: T.Union[str, T.Dict[str, T.Any]],
        retrieve_config: T.Dict[str, T.Any] = {},
        rag_description: str = "",
        **kwargs: T.Any,
    ) -> None:
        super().__init__(
            agent_config,
            **kwargs,
        )
        # Implementation of RAG logic with agent_framework is TBD
        # (needs VectorStore support etc provided by the framework)


# MultiAssistant classes omitted or stubbed due to complexity of migration without full docs.
class MultiAssistantBase(ABC):
    pass
