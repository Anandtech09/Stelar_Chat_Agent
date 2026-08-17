import os
from agno.agent import Agent
from agno.team import Team
from agno.team.mode import TeamMode
from agno.models.google import Gemini

from tools.design_tools import generate_palette, calculate_layout
from tools.web_tools import web_search, fetch_materials
from tools.storage_tools import (
    save_consultation,
    send_email_consultation,
    verify_email_deliverability,
    update_consultation_excel
)


def _get_model():
    """Shared model factory — single connection reused by all agents."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    model_id = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    return Gemini(id=model_id, api_key=api_key)


def build_stelar_team() -> Team:
    """
    Build the Stelar Interiors multi-agent team using Agno Team API.
    
    Team Leader (Root Concierge) coordinates and delegates to:
      - DesignAdvisor: color palettes + material recommendations
      - LayoutAgent: room geometry + furniture placement
      - ResearchAgent: web search for design inspiration images
    """
    model = _get_model()

    design_agent = Agent(
        name="DesignAdvisor",
        role="Color palette specialist and material recommender for interior design projects.",
        model=model,
        tools=[generate_palette, fetch_materials],
        instructions=[
            "You generate color palettes and recommend matching physical materials for interior design.",
            "When asked about colors, palettes, shades, tones, or materials — call the generate_palette tool with the style and room type.",
            "When asked about specific materials like wood, fabric, paint, stone — call fetch_materials.",
            "BREVITY: Keep your response to 2 short sentences max. Let the tool data speak for itself.",
        ],
    )

    layout_agent = Agent(
        name="LayoutAgent",
        role="Spatial geometry calculator for room layouts and furniture placement.",
        model=model,
        tools=[calculate_layout],
        instructions=[
            "You calculate room areas, furniture spatial footprint, and wall placements.",
            "When given room dimensions, call calculate_layout with the room_length and room_width.",
            "BREVITY: Keep your response to 2 short sentences max. Present the numbers clearly.",
        ],
    )

    research_agent = Agent(
        name="ResearchAgent",
        role="Web researcher that finds interior design inspiration images and trend articles.",
        model=model,
        tools=[web_search],
        instructions=[
            "You search the web for interior design inspiration images and trending styles.",
            "When asked for inspiration, examples, trends, or images — call web_search with a descriptive query.",
            "BREVITY: Keep your response to 2 short sentences max.",
        ],
    )

    brief_agent = Agent(
        name="BriefCoordinator",
        role="Manages consultation brief synthesis, file saving, Excel leads tracking, and email dispatch.",
        model=model,
        tools=[save_consultation, send_email_consultation, verify_email_deliverability, update_consultation_excel],
        instructions=[
            "You synthesize client interior design consultation briefs, save them to disk/Excel, and dispatch summaries via email.",
            "When asked to save, export, log to spreadsheet, or email the consultation brief — call save_consultation or update_consultation_excel or send_email_consultation.",
            "Verify email addresses using verify_email_deliverability before sending.",
            "BREVITY: Keep your response to 2 short sentences max.",
        ],
    )

    team = Team(
        name="Stelar Interiors Concierge Team",
        mode=TeamMode.coordinate,
        model=model,
        members=[design_agent, layout_agent, research_agent, brief_agent],
        instructions=[
            "You are the senior Client Gathering Concierge at Stelar Interiors.",
            "CRITICAL BREVITY RULE: Keep ALL responses to 2-3 short sentences maximum. Never write long essays or paragraphs.",
            "Ask only ONE clear, friendly question at a time.",
            "Communicate with warmth, elegance, and charm — like a premium luxury design firm concierge.",
            "Your main goal is to delight clients and persuasively guide them toward booking a complimentary In-Person Site Visit.",
            "CONTACT DETAILS GOAL: Gently gather the client's Name, Mobile/WhatsApp Number, and Location/City so our senior design team can coordinate the visit.",
            "",
            "DELEGATION RULES:",
            "- When client asks about colors, palettes, shades, materials, textures → delegate to DesignAdvisor.",
            "- When client asks about layout, floor plan, dimensions, furniture placement → delegate to LayoutAgent.",
            "- When client asks for inspiration, images, examples, trends → delegate to ResearchAgent.",
            "- When client asks to save the brief, export consultation, log to spreadsheet, or send email → delegate to BriefCoordinator.",
            "- For greetings, casual chat, visit booking, or general questions → respond directly yourself.",
            "",
            "If a visitor says 'just browsing' or 'just visiting', reply with an impressive 2-sentence offer for a no-obligation site visit.",
            "Do NOT output internal code, debug tags, JSON, or raw data. Only output friendly conversational text.",
        ],
    )
    return team
