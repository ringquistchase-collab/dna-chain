"""
research_art_generator.py
================
The artistic half of your question — agents generating AI images for
discussion/experimentation. Uses a real image-generation API (OpenAI's
images endpoint), not a placeholder.

WHAT THIS DELIBERATELY STAYS AWAY FROM
------------------------------------------
This generates ABSTRACT/ARTISTIC visualizations of network state
(topology, activity level, MOS trends) — never anything framed as a
biological, medical, or diagnostic image. That distinction matters a
lot given this project's history: an earlier file in this project
(flagged and set aside during this conversation) generated images
claiming to represent DNA/hormone/brain states as if they were
scientifically meaningful — they weren't, and presenting an AI image
as a "rendering" of someone's biology is actively misleading. This
generator only ever produces labeled, explicitly artistic
interpretations of NETWORK DATA (block counts, MOS scores, topic
graphs) — data this system actually has — never anything claiming to
depict a person's body, genome, or health state.

Every prompt is built from real numbers already in the system (see
_build_art_prompt) — not from anything a person told the system about
themselves.

SETUP
--------
Needs your own OpenAI API key (real, billed calls):

    pip install openai
    export OPENAI_API_KEY=sk-...

Usage
-----
    from research_art_generator import generate_network_art

    result = generate_network_art(
        mos_score=node.mos_score(),
        topic_count=len(agent.topics),
        style="abstract network diagram, geometric, blue and orange",
    )
    print(result["image_url"] or result["error"])
"""

from __future__ import annotations
import os

try:
    import openai
except ImportError:
    openai = None


DISCLAIMER = (
    "This is an AI-generated ARTISTIC interpretation of network activity data "
    "(block counts, MOS scores, and optionally other consented numeric signal "
    "statistics) — not a scientific visualization, not a biological or medical "
    "image, and not a representation of any person's body, brain, or health "
    "state, even when EEG/hormone statistics are included as an input channel. "
    "For real data, use node_view_visualizer.py's charts."
)


def _build_art_prompt(mos_score: dict, topic_count: int, style: str, extra_signal_stats: dict | None = None) -> str:
    quality = mos_score.get("quality", 0)
    connectivity = mos_score.get("connectivity", 0)
    agreement = mos_score.get("agreement", 0)

    extra_line = ""
    if extra_signal_stats:
        parts = ", ".join(f"{k}={v}" for k, v in extra_signal_stats.items())
        extra_line = (
            f" Additional abstract numeric data channels (NOT biological readings, "
            f"treat purely as numbers for the composition, same as the scores above): {parts}."
        )

    return (
        f"An abstract, non-representational digital artwork visualizing network "
        f"activity data: {topic_count} active topics, quality score {quality:.1f}/5, "
        f"connectivity {connectivity:.1f}/5, agreement {agreement:.1f}/5.{extra_line} "
        f"Style: {style}. This should look like abstract data art — "
        f"NOT biological imagery, NOT a scan, NOT anatomical in any way, "
        f"NOT a representation of a brain, body, or physiological state."
    )


def generate_network_art(
    mos_score: dict, topic_count: int,
    style: str = "abstract geometric network diagram, minimalist",
    api_key: str | None = None,
    extra_signal_stats: dict | None = None,
) -> dict:
    if openai is None:
        return {"error": "openai package not installed — run: pip install openai"}

    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        return {"error": "No API key — set OPENAI_API_KEY or pass api_key= explicitly"}

    prompt = _build_art_prompt(mos_score, topic_count, style, extra_signal_stats)

    client = openai.OpenAI(api_key=key)
    try:
        response = client.images.generate(
            model="dall-e-3", prompt=prompt, n=1, size="1024x1024",
        )
        image_url = response.data[0].url
    except Exception as e:
        return {"error": f"OpenAI image API call failed: {e}"}

    return {
        "image_url": image_url,
        "prompt_used": prompt,
        "disclaimer": DISCLAIMER,
    }


if __name__ == "__main__":
    # structural test — proves prompt-building works WITHOUT a real
    # (billed) API call. Real usage calls generate_network_art() with
    # a real key and an actual node.mos_score() result.
    fake_mos = {"quality": 4.2, "connectivity": 5.0, "agreement": 3.8, "mos": 4.3}
    prompt = _build_art_prompt(fake_mos, topic_count=5, style="abstract geometric, blue and orange")
    print("=== Prompt that would be sent to the image API ===")
    print(prompt)

    print("\n=== Testing the no-key failure path ===")
    os.environ.pop("OPENAI_API_KEY", None)
    result = generate_network_art(fake_mos, topic_count=5)
    print(result)
