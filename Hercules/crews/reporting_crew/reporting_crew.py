"""
Reporting Crew — Phase 6: Report Generation
============================================
Generates professional vulnerability assessment reports.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class ReportingCrew:
    """Reporting crew for professional vulnerability report generation."""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self, tools: list = None, ctf_mode: bool = False):
        self._mcp_tools = tools or []
        self._ctf_mode = ctf_mode

    @agent
    def report_compiler(self) -> Agent:
        return Agent(
            config=self.agents_config['report_compiler'],
            tools=self._mcp_tools,
            verbose=True,
        )

    @agent
    def executive_summary_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['executive_summary_writer'],
            tools=self._mcp_tools,
            verbose=True,
        )

    @agent
    def ctf_writeup_author(self) -> Agent:
        return Agent(
            config=self.agents_config['ctf_writeup_author'],
            tools=self._mcp_tools,
            verbose=True,
        )

    @task
    def compile_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['compile_report_task'],
        )

    @task
    def executive_summary_task(self) -> Task:
        return Task(
            config=self.tasks_config['executive_summary_task'],
            context=[self.compile_report_task()],
        )

    @task
    def ctf_writeup_task(self) -> Task:
        return Task(
            config=self.tasks_config['ctf_writeup_task'],
            context=[self.compile_report_task()],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the reporting crew."""
        # Use only agents required for the selected tasks
        active_agents = [self.report_compiler(), self.executive_summary_writer()]
        active_tasks = [self.compile_report_task(), self.executive_summary_task()]
        
        if self._ctf_mode:
            active_agents.append(self.ctf_writeup_author())
            active_tasks.append(self.ctf_writeup_task())

        return Crew(
            agents=active_agents,
            tasks=active_tasks,
            process=Process.sequential,
            verbose=True,
        )
