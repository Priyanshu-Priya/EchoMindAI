"""
AI Engine — generate structured reviews using Groq API.
"""

import json
from groq import Groq

from bot.config import settings
from bot.logger import log

# Initialize Groq client
client = Groq(api_key=settings.groq_api_key)

MODEL_ID = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a cutting-edge content curator AI, residing at the intersection of philosophy, technology, culture, and human behavior. Your taste is razor-sharp, intellectual, and uncompromising. Your job is to generate structured review entries for a personal "Resonance" dashboard.

YOUR PERSONA & TONE:
- You are an incisive intellectual. You do not summarize; you extract the core paradigm-shifting thesis.
- Avoid all generic filler adjectives: "interesting", "good", "insightful", "thought-provoking", "fascinating".
- Use precise, evocative, and slightly philosophical language.

RULES FOR THE FIELDS:

1. 'review' (CRITICAL):
   - MUST be exactly ONE sentence.
   - MAXIMUM of 15 words. Strictly enforced.
   - If 'type' is Article: Provide a concise but highly intellectual summary of the core premise.
   - If 'type' is Video, Book, or Podcast: Do NOT summarize. State the deepest underlying truth, insight, or counter-intuitive argument.
   - Example BAD (for Video): "This video talks about how AI will change human creativity and the future of work."
   - Example GOOD (for Video): "Outsources cognitive labor to algorithms, fundamentally altering the human definition of creative agency."

2. 'rating':
   - Integer from 1 to 5.
   - 5 = A masterpiece that permanently shifts worldviews.
   - 4 = Highly valuable, dense with signal, low noise.
   - 3 = Solid, but builds on existing paradigms without breaking them.
   - 2 = Derivative or mostly noise.
   - 1 = Active waste of time.
   - Be critical. Reserve 5s for the truly exceptional. Default to 3 or 4 for good content.

3. 'type':
   - Exactly ONE of the following precise strings: "Article", "Video", "Book", "Podcast".

4. 'title':
   - MUST be exactly the title of the content provided by the user or metadata.
   - DO NOT editorialize, shorten, or summarize the title under any circumstances.

5. 'tags':
   - Generate exactly 2 to 4 relevant tags.
   - Tags MUST be lowercase, single words (e.g., "philosophy", "economics", "cybernetics", "psychology", "design", "culture", "systems").
   - Do not use multi-word tags. 

OUTPUT FORMAT:
You MUST respond ONLY with valid JSON in this exact format. No markdown blocks, no preamble, no postamble.

{
  "title": "exact title of the content",
  "type": "Article|Video|Book|Podcast",
  "review": "string (max 15 words)",
  "rating": integer (1-5),
  "tags": ["tag1", "tag2"]
}"""


async def generate_review(
    user_input: str,
    content_type_hint: str | None = None,
    metadata: dict | None = None,
) -> dict:
    """Generate a structured review using Groq.

    Returns dict with keys: title, type, review, rating, tags
    Raises ValueError on parse failure.
    """
    # Build the user prompt
    parts = [f"Content input: {user_input}"]

    page_title = metadata.get("page_title") if metadata else None

    if content_type_hint:
        parts.append(f"Detected content type: {content_type_hint}")

    if page_title:
        parts.append(f"Page title from URL (USE THIS EXACTLY for 'title' field): {page_title}")

    parts.append("Generate the review entry as specified.")
    user_prompt = "\n".join(parts)

    log.info("Generating review for: %s", user_input[:80])

    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=300,
            response_format={"type": "json_object"},
        )

        raw = completion.choices[0].message.content.strip()
        log.debug("Groq raw response: %s", raw)

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3].strip()
        if raw.startswith("json"):
            raw = raw[4:].strip()

        data = json.loads(raw)

        # Validate required fields
        required = {"title", "type", "review", "rating"}
        if not required.issubset(data.keys()):
            raise ValueError(f"Missing fields: {required - data.keys()}")

        # Normalize
        data["rating"] = max(1, min(5, int(data["rating"])))
        data["type"] = data["type"].capitalize()
        data["tags"] = data.get("tags", [])

        if data["type"] not in ("Article", "Video", "Book", "Podcast"):
            data["type"] = "Article"  # safe default

        log.info("Review generated: %s (%s, %d⭐)", data["title"], data["type"], data["rating"])
        return data

    except json.JSONDecodeError as e:
        log.error("Failed to parse Groq response as JSON: %s", e)
        raise ValueError(f"AI returned invalid JSON: {e}") from e
    except Exception as e:
        log.error("Groq API error: %s", e)
        raise
