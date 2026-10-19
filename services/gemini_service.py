"""
Google Gemini AI Integration for SEO Suite Pro:
- Zero-trust API key management (stored in session or encrypted user profile)
- Plain-language strategic SEO audits and 30-day prioritized roadmaps
- Title and Meta Description high-CTR rewriting engine
- Keyword cannibalization resolution and content differentiation briefs
- Rate limit (429) and invalid credential handling
"""

import os
from google import genai
from google.genai.errors import APIError

DEFAULT_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-1.5-flash"

def test_gemini_key(api_key: str) -> tuple[bool, str]:
    """Tests if a Gemini API key is valid by initiating a minimal request."""
    if not api_key or not api_key.strip():
        return False, "API key cannot be empty."
        
    key = api_key.strip()
    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents="Respond with the single word 'OK'."
        )
        if response and response.text:
            return True, "API Key verified successfully."
        return False, "No response received from Gemini API."
    except APIError as e:
        return False, f"Gemini API verification failed: {e.message}"
    except Exception as e:
        return False, f"Connection error during verification: {str(e)}"

def generate_seo_action_plan(api_key: str, audit_summary: dict, top_issues: list[dict]) -> str:
    """
    Generates an executive-level plain-language SEO diagnosis and 30-day prioritized action plan.
    """
    if not api_key:
        return "Gemini API key is not configured. Add your API key in Settings to activate AI strategic recommendations."
        
    prompt = f"""You are a world-class Technical SEO Director and Enterprise Organic Growth Architect.
Analyze the following website audit and Google Search Console performance data, then provide an executive summary and a prioritized 30-day technical action plan.

AUDIT SUMMARY:
{audit_summary}

TOP IDENTIFIED ISSUES:
{top_issues[:8]}

REQUIREMENTS:
1. Write in clear, professional English.
2. Structure your response into:
   - Executive Diagnosis (high-level organic health and revenue impact)
   - Priority 1: Critical Fixes (Days 1-7) - Indexation blockers, canonicals, technical errors
   - Priority 2: Quick Traffic Wins (Days 8-15) - Low CTR titles/meta, striking distance queries
   - Priority 3: Content Consolidation & Structure (Days 16-30) - Cannibalization, content depth, internal links
3. Be specific, actionable, and data-driven. Do NOT use generic advice."""

    client = genai.Client(api_key=api_key.strip())
    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=prompt
        )
        return response.text or "No content generated."
    except APIError as e:
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            return "Gemini API rate limit reached (Quota Exceeded). Please wait a moment before trying again."
        elif "API_KEY_INVALID" in str(e):
            return "Invalid Gemini API Key. Please verify your key in Settings."
        return f"Gemini API Error: {e.message}"
    except Exception as e:
        return f"Failed to generate action plan: {str(e)}"

def generate_title_meta_rewrites(api_key: str, query: str, current_title: str, current_snippet: str, target_intent: str = "Commercial") -> str:
    """
    Generates high-CTR optimized Title and Meta Description variants for underperforming search queries.
    """
    if not api_key:
        return "Gemini API key is required."
        
    prompt = f"""You are a search click-through rate (CTR) optimization specialist.
Generate 3 high-converting title tags and meta descriptions for the following search query and target page:

TARGET QUERY: {query}
CURRENT TITLE: {current_title}
CURRENT DESCRIPTION: {current_snippet}
SEARCH INTENT: {target_intent}

RULES:
- Titles: Strictly between 50 and 60 characters. Must incorporate the query naturally near the front.
- Meta Descriptions: Strictly between 130 and 155 characters. Include clear value proposition and active verb CTA.
- Format as 3 distinct options:
  Option 1: Direct & Informative
  Option 2: Value & Benefit Focused
  Option 3: High-Urgency Action

Return clean text formatted in Markdown."""

    client = genai.Client(api_key=api_key.strip())
    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=prompt
        )
        return response.text or "No suggestions generated."
    except Exception as e:
        return f"Error generating suggestions: {str(e)}"

def generate_cannibalization_brief(api_key: str, query: str, primary_url: str, secondary_urls: list[str]) -> str:
    """
    Generates a strategic content differentiation and canonicalization brief for cannibalized URLs.
    """
    if not api_key:
        return "Gemini API key is required."
        
    prompt = f"""You are a principal technical SEO consultant specializing in intent disambiguation and keyword cannibalization.
The following URLs are actively competing against each other for the identical search query in Google:

QUERY: {query}
PRIMARY URL (Highest Authority): {primary_url}
SECONDARY COMPETING URLS: {secondary_urls}

Please provide a technical remediation brief detailing:
1. Recommended Structural Action (301 Redirect vs Canonical vs Content Merge vs Intent Differentiation).
2. Exactly how the Primary URL should be strengthened.
3. How the Secondary URL(s) should be modified (which distinct long-tail keywords to target, or which duplicate sections to prune).
4. Internal link anchor text alignment instructions.

Keep the advice direct, concise, and technically authoritative."""

    client = genai.Client(api_key=api_key.strip())
    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=prompt
        )
        return response.text or "No brief generated."
    except Exception as e:
        return f"Error generating brief: {str(e)}"
