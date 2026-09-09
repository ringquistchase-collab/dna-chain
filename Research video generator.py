"""
research_video_generator.py
================
Real video generation via Runway ML's API, same role and same
boundaries as research_art_generator.py — the video half of your
original image+video question.

REAL API DETAILS (verified against Runway's own docs before writing
this, same as every other integration in this project)
----------------------------------------------------------------------
  Base URL:  https://api.dev.runwayml.com/v1
  Endpoint:  POST /image_to_video (text-to-video mode: omit promptImage)
  Auth:      Authorization: Bearer <RUNWAYML_API_SECRET>
  Version:   X-Runway-Version: 2024-11-06   (required header)
  Async:     submit a task, get a task id back, poll
             GET /tasks/{id} until status is SUCCEEDED or FAILED

WHAT THIS DELIBERATELY STAYS AWAY FROM
------------------------------------------
Same rule as research_art_generator.py: this only ever generates
ABSTRACT visualizations of real NETWORK ACTIVITY DATA (block counts,
MOS scores, topic counts) — never anything framed as biological,
medical, or diagnostic footage. See research_art_generator.py's
docstring for the full reasoning; it applies identically here.

SETUP
--------
Needs your own Runway API key (real, billed calls — video generation
costs meaningfully more per call than image generation):

    pip install requests   (this file uses requests for the polling
                             loop's readability; everything else in
                             this project uses urllib to avoid the
                             dependency, but a multi-minute poll loop
                             is genuinely cleaner with requests)
    export RUNWAYML_API_SECRET=key_...

Usage
-----
    from research_video_generator import generate_network_video

    result = generate_network_video(
        mos_score=node.mos_score(),
        topic_count=len(agent.topics),
        style="abstract geometric network animation, blue and orange",
    )
    print(result.get("video_url") or result.get("error"))
"""

from __future__ import annotations
import os
import time

try:
    import requests
except ImportError:
    requests = None


API_BASE = "https://api.dev.runwayml.com/v1"
API_VERSION = "2024-11-06"

DISCLAIMER = (
    "This is an AI-generated ARTISTIC video interpretation of network activity "
    "data (block counts, MOS scores) — not a scientific visualization, not a "
    "biological or medical video, and not a representation of any person's "
    "body or health state. For real data, use node_view_visualizer.py's charts."
)


def _build_video_prompt(mos_score: dict, topic_count: int, style: str, extra_signal_stats: dict | None = None) -> str:
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
        f"An abstract, non-representational animated visualization of network "
        f"activity data: {topic_count} active topics, quality score {quality:.1f}/5, "
        f"connectivity {connectivity:.1f}/5, agreement {agreement:.1f}/5.{extra_line} "
        f"Style: {style}. This should look like abstract data art in motion — "
        f"NOT biological imagery, NOT medical footage, NOT anatomical in any way, "
        f"NOT a representation of a brain, body, or physiological state."
    )


def generate_network_video(
    mos_score: dict, topic_count: int,
    style: str = "abstract geometric network animation, minimalist, slow camera drift",
    api_key: str | None = None,
    model: str = "gen4.5",
    ratio: str = "1280:720",
    duration: int = 5,
    max_wait_seconds: int = 300,
    poll_interval_seconds: int = 5,
    extra_signal_stats: dict | None = None,
) -> dict:
    if requests is None:
        return {"error": "requests package not installed — run: pip install requests"}

    key = api_key or os.environ.get("RUNWAYML_API_SECRET")
    if not key:
        return {"error": "No API key — set RUNWAYML_API_SECRET or pass api_key= explicitly"}

    prompt = _build_video_prompt(mos_score, topic_count, style, extra_signal_stats)
    headers = {
        "Authorization": f"Bearer {key}",
        "X-Runway-Version": API_VERSION,
        "Content-Type": "application/json",
    }

    try:
        submit = requests.post(
            f"{API_BASE}/image_to_video",
            headers=headers,
            json={"model": model, "promptText": prompt, "ratio": ratio, "duration": duration},
            timeout=30,
        )
        submit.raise_for_status()
        task_id = submit.json().get("id")
        if not task_id:
            return {"error": f"No task id in Runway response: {submit.json()}"}
    except Exception as e:
        return {"error": f"Runway task submission failed: {e}"}

    elapsed = 0
    while elapsed < max_wait_seconds:
        try:
            poll = requests.get(f"{API_BASE}/tasks/{task_id}", headers=headers, timeout=30)
            poll.raise_for_status()
            status_data = poll.json()
            status = status_data.get("status")
        except Exception as e:
            return {"error": f"Runway task polling failed: {e}", "task_id": task_id}

        if status == "SUCCEEDED":
            output = status_data.get("output", [])
            return {
                "video_url": output[0] if output else None,
                "task_id": task_id,
                "prompt_used": prompt,
                "disclaimer": DISCLAIMER,
            }
        if status in ("FAILED", "CANCELLED"):
            return {"error": f"Runway task ended with status {status}", "task_id": task_id, "details": status_data}

        time.sleep(poll_interval_seconds)
        elapsed += poll_interval_seconds

    return {"error": f"Timed out after {max_wait_seconds}s waiting for video", "task_id": task_id}


if __name__ == "__main__":
    # structural test — proves prompt-building works WITHOUT a real
    # (billed, multi-minute) API call. Real usage calls
    # generate_network_video() with a real key and an actual mos_score().
    fake_mos = {"quality": 4.2, "connectivity": 5.0, "agreement": 3.8, "mos": 4.3}
    prompt = _build_video_prompt(fake_mos, topic_count=5, style="abstract geometric, blue and orange, slow drift")
    print("=== Prompt that would be sent to Runway ===")
    print(prompt)

    print("\n=== Testing the no-key failure path ===")
    os.environ.pop("RUNWAYML_API_SECRET", None)
    result = generate_network_video(fake_mos, topic_count=5)
    print(result)
