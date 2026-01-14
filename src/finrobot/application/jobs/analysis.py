from finrobot.agents.workflow import SingleAssistant


class FinancialAnalysisJob:
    """Job to run financial analysis."""

    def __init__(self, company: str, model_id: str):
        self.company = company
        self.model_id = model_id

    def run(self):
        """Execute the analysis job."""
        print(f"Starting analysis for {self.company} with settings: {self.model_id}")

        agent_config = {
            "name": "Financial_Analyst",
            "description": f"Analyzes financial data for {self.company}",
            "profile": "You are an expert financial analyst. Analyze the stock based on provided tools.",
        }

        assistant = SingleAssistant(agent_config)
        assistant.chat(f"Analyze the stock performance of {self.company}")
