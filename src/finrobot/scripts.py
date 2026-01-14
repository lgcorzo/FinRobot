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
        from finrobot.jobs.analysis import FinancialAnalysisJob

        job = FinancialAnalysisJob(args.company, settings.openai_model)
        job.run()

    return 0
