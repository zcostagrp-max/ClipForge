import os
import json
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

HIGHLIGHT_PROMPT = """
You are an expert at finding viral short-form video clips from long-form transcripts.

Analyze the following timestamped transcript and identify the 5-12 best potential clips (15-60 seconds each).

Score each potential clip on:
- Hook strength (first 3 seconds must grab attention)
- Emotional intensity
- Humor / controversy / insight density
- Story completeness
- Shareability

Return ONLY a valid JSON array of objects with this exact structure:
[
  {
    "start": 124.5,
    "end": 167.2,
    "title": "Why most people stay broke",
    "virality_score": 94,
    "reason": "Strong contrarian hook + clear insight",
    "transcript": "full transcript text of the segment"
  }
]

Sort by virality_score descending. Prefer complete thoughts. Avoid mid-sentence cuts.

Transcript:
{transcript}
"""

def format_transcript(segments: list) -> str:
    lines = []
    for seg in segments:
        lines.append(f"[{seg['start']:.1f}-{seg['end']:.1f}] {seg['text']}")
    return "\n".join(lines)

def find_highlights(segments: list) -> list:
    transcript_text = format_transcript(segments)
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key and anthropic_key.startswith("sk-"):
        try:
            client = Anthropic(api_key=anthropic_key)
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": HIGHLIGHT_PROMPT.format(transcript=transcript_text)}]
            )
            content = response.content[0].text
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
        except Exception as e:
            print(f"Anthropic failed: {e}")
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key.startswith("sk-"):
        try:
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": HIGHLIGHT_PROMPT.format(transcript=transcript_text)}],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            if isinstance(data, dict) and "clips" in data:
                return data["clips"]
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"OpenAI failed: {e}")
    return heuristic_highlights(segments)

def heuristic_highlights(segments: list) -> list:
    keywords = ["why", "how", "secret", "mistake", "never", "always", "truth", "money", "success", "fail", "crazy", "insane", "believe"]
    scored = []
    for i, seg in enumerate(segments):
        text = seg["text"].lower()
        score = sum(10 for k in keywords if k in text)
        if len(seg["text"]) > 50:
            score += 5
        scored.append((score, seg))
    scored.sort(key=lambda x: x[0], reverse=True)
    clips = []
    for score, seg in scored[:8]:
        duration = seg["end"] - seg["start"]
        if 10 < duration < 90:
            clips.append({
                "start": seg["start"],
                "end": min(seg["end"], seg["start"] + 45),
                "title": seg["text"][:50] + "...",
                "virality_score": min(95, 60 + score),
                "reason": "Heuristic match on high-energy keywords",
                "transcript": seg["text"]
            })
    return clips
