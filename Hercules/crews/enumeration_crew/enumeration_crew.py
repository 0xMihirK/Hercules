"""
Enumeration Crew — Phase 2: Deep Enumeration
=============================================
Performs deep service and web application enumeration.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class EnumerationCrew:
    """Enumeration crew for deep service and web app discovery."""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self, tools: list = None):
        self._mcp_tools = tools or []

    @agent
    def service_enumerator(self) -> Agent:
        return Agent(
            config=self.agents_config['service_enumerator'],
            tools=self._mcp_tools,
            verbose=True,
        )

    @agent
    def web_app_enumerator(self) -> Agent:
        return Agent(
            config=self.agents_config['web_app_enumerator'],
            tools=self._mcp_tools,
            verbose=True,
        )

    @task
    def service_enumeration_task(self) -> Task:
        return Task(
            config=self.tasks_config['service_enumeration_task'],
        )

    @task
    def web_enumeration_task(self) -> Task:
        return Task(
            config=self.tasks_config['web_enumeration_task'],
            context=[self.service_enumeration_task()],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the enumeration crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
