"""
Recon Crew — Phase 1: Reconnaissance
=====================================
Performs network scanning and OSINT gathering on the target.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class ReconCrew:
    """Reconnaissance crew for network scanning and OSINT gathering."""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self, tools: list = None):
        self._mcp_tools = tools or []

    @agent
    def network_recon_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['network_recon_specialist'],
            tools=self._mcp_tools,
            verbose=True,
        )

    @agent
    def osint_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['osint_analyst'],
            tools=self._mcp_tools,
            verbose=True,
        )

    @task
    def network_scan_task(self) -> Task:
        return Task(
            config=self.tasks_config['network_scan_task'],
        )

    @task
    def osint_gathering_task(self) -> Task:
        return Task(
            config=self.tasks_config['osint_gathering_task'],
            context=[self.network_scan_task()],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the reconnaissance crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
