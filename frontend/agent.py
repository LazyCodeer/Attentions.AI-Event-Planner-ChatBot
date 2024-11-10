# agent.py
from pathlib import Path
from typing import Optional, List
from textwrap import dedent

from phi.assistant import Assistant
from phi.tools import Toolkit
from phi.tools.serpapi_tools import SerpApiTools
from phi.tools.duckduckgo import DuckDuckGo
from phi.llm.ollama import Ollama
from phi.knowledge import AssistantKnowledge
from phi.embedder.ollama import OllamaEmbedder
from phi.storage.assistant.postgres import PgAssistantStorage
from phi.vectordb.pgvector import PgVector2
from phi.utils.log import logger

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
cwd = Path(__file__).parent.resolve()
scratch_dir = cwd.joinpath("scratch")
if not scratch_dir.exists():
    scratch_dir.mkdir(exist_ok=True, parents=True)


def get_agent(
    llm_id: str = "llama3",
    user_id: Optional[str] = None,
    run_id: Optional[str] = None,
    debug_mode: bool = False,
) -> Assistant:
    logger.info(f"-*- Creating Tour Planning Agent with {llm_id} -*-")

    # Add tools available to the Agent
    tools: List[Toolkit] = [SerpApiTools(), DuckDuckGo()]

    # Add team members (sub-agents)
    team: List[Assistant] = []

    # User Interaction Agent
    user_interaction_agent = Assistant(
        name="User Interaction Agent",
        llm=Ollama(model=llm_id),
        role="Gather user preferences and collect required details",
        description="You collect user preferences and requirements for their tour planning.",
        instructions=[
            "Ask for the following details:",
            "1. City to visit",
            "2. Date of visit",
            "3. Available timings",
            "4. Budget",
            "5. Interests",
            "6. Starting point",
            "If preferences are unclear, suggest popular options",
        ],
        show_tool_calls=False,
        process_tool_responses=True,
    )
    team.append(user_interaction_agent)

    # Weather Agent
    weather_agent = Assistant(
        name="Weather Agent",
        llm=Ollama(model=llm_id),
        role="Provide weather information",
        description="You provide weather forecasts and recommendations.",
        tools=[SerpApiTools()],
        instructions=[
            "Search for current weather conditions",
            "Provide weather-based recommendations",
            "Suggest appropriate clothing and items",
            "Format response in a clear, direct manner",
        ],
        show_tool_calls=False,
        process_tool_responses=True,
    )
    team.append(weather_agent)

    # News Agent
    news_agent = Assistant(
        name="News Agent",
        llm=Ollama(model=llm_id),
        role="Check local events and updates",
        description="You find relevant local news and events.",
        tools=[SerpApiTools()],
        instructions=[
            "Search for:",
            "- Local events and festivals",
            "- Attraction status updates",
            "- Transportation updates",
            "- Safety information",
            "Present information clearly without showing search details",
        ],
        show_tool_calls=False,
        process_tool_responses=True,
    )
    team.append(news_agent)

    # Itinerary Agent
    itinerary_agent = Assistant(
        name="Itinerary Agent",
        llm=Ollama(model=llm_id),
        role="Create optimized itineraries",
        description="You create detailed, time-optimized tour plans.",
        tools=[SerpApiTools()],
        instructions=[
            "Create itineraries with:",
            "- Optimal visit sequence",
            "- Travel times and methods",
            "- Entry fees and status",
            "- Time allocations",
            "Update plans based on weather and news",
        ],
        show_tool_calls=False,
        process_tool_responses=True,
    )
    team.append(itinerary_agent)

    # Main Tour Planning Agent
    return Assistant(
        name="Tour Planning Assistant",
        run_id=run_id,
        user_id=user_id,
        llm=Ollama(model=llm_id),
        description=dedent(
            """
            I am your Tour Planning Assistant. I create personalized one-day tour itineraries by:
            1. Collecting essential details (city, date, timings)
            2. Checking weather conditions
            3. Reviewing local events
            4. Creating optimized schedules
            5. Providing detailed recommendations
            """
        ),
        instructions=[
            "Always follow this sequence:",
            "1. If city is mentioned without date/time, ask for:",
            "- Preferred date of visit",
            "- Start time",
            "- End time",
            "2. Once all details are collected:",
            "- Check weather using Weather Agent",
            "- Check events using News Agent",
            "- Create optimized itinerary",
            "3. Format itinerary with sections:",
            "- Schedule Overview",
            "- Weather Advisory",
            "- Essential Items",
            "- Local Updates",
        ],
        tools=tools,
        team=team,
        storage=PgAssistantStorage(table_name="tour_planner_runs", db_url=db_url),
        knowledge_base=AssistantKnowledge(
            vector_db=PgVector2(
                db_url=db_url,
                collection="tour_planner_knowledge",
                embedder=OllamaEmbedder(model="nomic-embed-text", dimensions=1536),
            ),
            num_documents=3,
        ),
        show_tool_calls=False,
        process_tool_responses=True,
        search_knowledge=True,
        read_chat_history=True,
        add_chat_history_to_messages=True,
        num_history_messages=5,
        markdown=True,
        add_datetime_to_instructions=True,
        introduction=f"Welcome to Wanderlust! 🌟 I'm your personal one-day adventure planner. Ready to explore a city in 24 hours? Which destination sparks your wanderlust?",
        debug_mode=debug_mode,
    )
