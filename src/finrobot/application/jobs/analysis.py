"""Application Layer - Financial Analysis Job."""

import typing as T

from finrobot.models.agents.workflow import SingleAssistant

from .base import Job

# %% JOBS


class FinancialAnalysisJob(Job):
    """Job to perform financial analysis of a company."""

    KIND: T.Literal["analysis"] = "analysis"
    company: str
    model_id: str = "gpt-4"

    def run(self) -> T.Any:
        """Run the financial analysis job."""
        config = {
            "name": "Financial_Analyst",
            "description": f"Identify the company {self.company} and perform a financial analysis.",
        }
        llm_config = {"model": self.model_id}

        assistant = SingleAssistant(config, llm_config=llm_config)

        logger = self.logger_service.logger()
        # In a real scenario, we might want to log this in MLflow too
        logger.info(f"Starting financial analysis for {self.company} using {self.model_id}")

        message = f"Please analyze the financial performance of {self.company} over the last year."
        result = assistant.chat(message)

        logger.info(f"Financial analysis for {self.company} completed.")
        return result


__all__ = ["FinancialAnalysisJob"]
