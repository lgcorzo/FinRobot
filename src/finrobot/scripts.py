"""Entry point for FinRobot CLI."""

import argparse
import sys
from finrobot.settings import FinRobotSettings


def main(argv: list[str] | None = None) -> int:
    """Main script for the application."""
    parser = argparse.ArgumentParser(description="FinRobot AI Agent CLI")
    parser.add_argument("--task", type=str, help="Task to execute")
    parser.add_argument("--company", type=str, help="Company symbol to analyze")

    args = parser.parse_args(argv)

    settings = FinRobotSettings()

    if args.task == "analyze" and args.company:
        print(f"Starting analysis for {args.company} with settings: {settings.openai_model}")
        from finrobot.agents.workflow import SingleAssistant

        # This is a sample usage config.
        # In a real scenario, we might load this from a registry or config file.
        agent_config = {
            "name": "Financial_Analyst",
            "description": f"Analyzes financial data for {args.company}",
            "profile": "You are an expert financial analyst. Analyze the stock based on provided tools.",
        }

        assistant = SingleAssistant(agent_config)
        assistant.chat(f"Analyze the stock performance of {args.company}")

    return 0
