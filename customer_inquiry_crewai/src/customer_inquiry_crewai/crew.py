from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from customer_inquiry_crewai.tools import GetPolicyTool
from customer_inquiry_crewai.schemas import (
    IntentAnalysisOutput,
    PolicyRetrievalOutput,
    ResponseGenerationOutput,
)
# Experimental control settings for fair comparison with LangGraph
# Hard constraints:
# - same LLM model as LangGraph
# - same prompt structure
# - same policy JSON DB
# - same Python tool function
# - no memory / no reflection / no replanning / no delegation
# - no human intervention
# - max agent step = 3
# - max tool call = 1
COMMON_MODEL = "gpt-4o-mini"
COMMON_TEMPERATURE = 0
COMMON_MAX_TOKENS = 512
COMMON_MAX_AGENT_STEP = 3
COMMON_MAX_TOOL_CALL = 1
COMMON_MEMORY_ENABLED = False
COMMON_ALLOW_DELEGATION = False
COMMON_PROCESS = Process.sequential
COMMON_LLM = {
    "model": "gpt-4o-mini",
    "temperature": 0,
    "max_tokens": 512
}

@CrewBase
class CustomerInquiryCrewai():
    """CustomerInquiryCrewai crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def intent_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['intent_analyst'], # type: ignore[index]
            verbose=True,
            allow_delegation=False,
            llm=COMMON_LLM,
            max_iter=1
        )

    @agent
    def policy_retriever(self) -> Agent:
        return Agent(
            config=self.agents_config['policy_retriever'], # type: ignore[index]
            verbose=True,
            allow_delegation=False,
            llm=COMMON_LLM,
            max_iter=1,            
            tools=[GetPolicyTool()]
        )

    @agent
    def response_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['response_generator'],
            verbose=True,
            allow_delegation=False,
            llm=COMMON_LLM,
            max_iter=1
        )

    @task
    def intent_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['intent_analysis_task'],
            output_pydantic=IntentAnalysisOutput, # type: ignore[index]
        )

    @task
    def policy_retrieval_task(self) -> Task:
        return Task(
            config=self.tasks_config['policy_retrieval_task'],
            output_pydantic=PolicyRetrievalOutput,  # type: ignore[index]
        )

    @task
    def response_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['response_generation_task'],
            output_pydantic=ResponseGenerationOutput,  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CustomerInquiryCrewai crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            memory=False
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
