"""
WebApp Testing Crew — Phase 2b: Web Application Testing
=====================================================
Performs dedicated web application testing using gobuster and other web tools.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class WebAppTestingCrew:
    """Dedicated web application testing crew."""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self, tools: list = None):
        self._mcp_tools = tools or []

    @agent
    def web_vulnerability_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['web_vulnerability_specialist'],
            tools=self._mcp_tools,
            verbose=True,
        )

    @task
    def web_app_testing_task(self) -> Task:
        return Task(
            config=self.tasks_config['web_app_testing_task'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the web application testing crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
