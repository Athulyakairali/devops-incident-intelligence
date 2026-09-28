import json
import os

import ollama


MODEL = "qwen2.5:7b"
OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://127.0.0.1:11434",
)


def generate_rca(report):

    incident_data = {
        "incident_id": report.get("incident_id"),
        "pod": report.get("pod"),
        "container": report.get("container"),
        "incident_type": report.get("incident_type"),
        "reason": report.get("reason"),
        "exit_code": report.get("exit_code"),
        "pod_status": report.get("pod_status"),
        "memory_limit": report.get("memory_limit"),
        "events": report.get("events", []),
        "logs": report.get("logs", ""),
    }

    prompt = f"""
You are a senior DevOps incident response engineer.

Analyze the Kubernetes incident below.

INCIDENT DATA:
{json.dumps(incident_data, indent=2)}

STRICT EVIDENCE RULES:

1. Use ONLY the information contained in INCIDENT DATA.

2. Never invent measurements, events, logs, timestamps, metrics,
   resource usage, or causes.

3. OOMKilled is confirmed because the Kubernetes container state
   explicitly reports reason OOMKilled.

4. Exit code 137 is confirmed because the incident data explicitly
   reports exit_code 137.

5. The configured memory limit is 50Mi. Treat this as configuration,
   NOT as observed memory usage.

6. The application logs report allocations up to approximately 45 MB.
   This is the LAST OBSERVED LOGGED ALLOCATION.

7. NEVER state that approximately 45 MB exceeds 50Mi.

8. NEVER convert approximately 45 MB into an exact value.

9. NEVER claim that the application definitely exceeded the configured
   memory limit unless the evidence explicitly proves this.

10. The fact that Kubernetes reported OOMKilled does NOT by itself tell
    us the exact memory usage at the moment of termination.

11. Do not claim that a memory leak exists. A memory leak may be a
    possibility, but it is NOT confirmed by the supplied evidence.

12. If the exact cause cannot be established from the evidence,
    explicitly state that under "unknowns".

13. Distinguish:
    - confirmed evidence
    - likely contributing factors
    - unknowns

14. Do not treat a hypothesis as a confirmed fact.

15. Do not recommend increasing memory as the automatic solution.

16. Recommendations should focus on investigation, monitoring,
    profiling, and reviewing memory behavior.

IMPORTANT INTERPRETATION:

The evidence supports this conclusion:

- Kubernetes terminated the container with OOMKilled.
- The container exited with code 137.
- The configured memory limit was 50Mi.
- The application logged allocations up to approximately 45 MB.
- The exact memory usage at the moment of termination is unknown.
- The evidence does not establish whether the configured 50Mi limit
  was itself insufficient.
- The evidence does not establish whether a memory leak exists.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "root_cause": "Evidence-based explanation",
    "severity": "LOW, MEDIUM, or HIGH",
    "confidence": "LOW, MEDIUM, or HIGH",

    "confirmed_evidence": [
        "Only facts directly supported by the evidence"
    ],

    "likely_contributing_factors": [
        "Reasonable but explicitly labeled inference"
    ],

    "unknowns": [
        "Things that cannot be determined from the evidence"
    ],

    "recommended_actions": [
        "Evidence-based action 1",
        "Evidence-based action 2",
        "Evidence-based action 3"
    ]
}}
"""

    client = ollama.Client(host=OLLAMA_HOST)

    response = client.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    content = response["message"]["content"].strip()

    if content.startswith("```json"):
        content = content[7:]

    if content.startswith("```"):
        content = content[3:]

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()

    try:
        return json.loads(content)

    except json.JSONDecodeError:

        return {
            "root_cause": content,
            "severity": report.get("severity", "MEDIUM"),
            "confidence": "LOW",
            "confirmed_evidence": [],
            "likely_contributing_factors": [],
            "unknowns": [
                "The LLM did not return valid structured JSON."
            ],
            "recommended_actions": [
                "Review Kubernetes events.",
                "Review application logs.",
            ],
        }
