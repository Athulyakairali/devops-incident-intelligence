from engine.detector import detect_incidents
from engine.events import get_pod_events
from engine.logs import get_pod_logs


def get_pod_details(pod_name):
    import json
    import subprocess

    result = subprocess.run(
        [
            "kubectl",
            "get",
            "pod",
            pod_name,
            "-o",
            "json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return json.loads(result.stdout)


def analyze_incident(incident):
    pod = incident["pod"]

    events = get_pod_events(pod)
    logs = get_pod_logs(pod)
    pod_details = get_pod_details(pod)

    container = pod_details["spec"]["containers"][0]

    memory_limit = (
        container
        .get("resources", {})
        .get("limits", {})
        .get("memory", "Not configured")
    )

    report = {
        "incident_id": "INC-001",
        "pod": pod,
        "container": incident["container"],
        "incident_type": incident["type"],
        "reason": incident["reason"],
        "exit_code": incident.get("exit_code"),
        "pod_status": pod_details["status"].get(
            "phase",
            "Unknown",
        ),
        "memory_limit": memory_limit,
        "events": events,
        "logs": logs,
    }

    if incident["reason"] == "OOMKilled":

        report["severity"] = "HIGH"

        report["root_cause"] = (
            "The container exceeded its configured "
            "memory limit and was terminated by Kubernetes."
        )

        report["recommendations"] = [
            "Review application memory consumption.",
            "Investigate potential memory leaks.",
            "Adjust the Kubernetes memory limit if justified.",
            "Review memory requests and limits.",
        ]

    elif incident["reason"] == "CrashLoopBackOff":

        report["severity"] = "HIGH"

        report["root_cause"] = (
            "The container is repeatedly crashing "
            "and Kubernetes is backing off restarts."
        )

        report["recommendations"] = [
            "Inspect application logs.",
            "Inspect the previous container state.",
            "Verify application configuration.",
            "Check environment variables and dependencies.",
        ]

    elif incident["reason"] in [
        "ImagePullBackOff",
        "ErrImagePull",
    ]:

        report["severity"] = "MEDIUM"

        report["root_cause"] = (
            "Kubernetes could not pull the configured "
            "container image."
        )

        report["recommendations"] = [
            "Verify the image name.",
            "Verify the image tag.",
            "Check registry authentication.",
            "Check registry availability.",
        ]

    else:

        report["severity"] = "MEDIUM"

        report["root_cause"] = (
            "The exact root cause could not be determined."
        )

        report["recommendations"] = [
            "Inspect Kubernetes events.",
            "Inspect application logs.",
            "Review pod configuration.",
        ]

    return report


def print_report(report):

    print()
    print("=" * 70)
    print("              DEVOPS INCIDENT INTELLIGENCE")
    print("=" * 70)

    print(f"Incident ID   : {report['incident_id']}")
    print(f"Pod           : {report['pod']}")
    print(f"Container     : {report['container']}")
    print(f"Incident Type : {report['incident_type']}")
    print(f"Severity      : {report['severity']}")
    print(f"Reason        : {report['reason']}")

    if report["exit_code"] is not None:
        print(f"Exit Code     : {report['exit_code']}")

    print(f"Pod Status    : {report['pod_status']}")
    print(f"Memory Limit  : {report['memory_limit']}")

    print()
    print("ROOT CAUSE")
    print("-" * 70)
    print(report["root_cause"])

    print()
    print("APPLICATION EVIDENCE")
    print("-" * 70)

    if report["logs"]:
        print(report["logs"])
    else:
        print("No application logs available.")

    print()
    print("INCIDENT TIMELINE")
    print("-" * 70)

    if report["events"]:

        for event in report["events"]:

            timestamp = (
                event.get("timestamp")
                or "unknown"
            )

            reason = (
                event.get("reason")
                or "unknown"
            )

            message = (
                event.get("message")
                or ""
            )

            print(
                f"{timestamp} | "
                f"{reason} | "
                f"{message}"
            )

    else:
        print("No Kubernetes events found.")

    print()
    print("RECOMMENDED ACTIONS")
    print("-" * 70)

    for number, recommendation in enumerate(
        report["recommendations"],
        start=1,
    ):

        print(
            f"{number}. {recommendation}"
        )

    print("=" * 70)


def main():

    incidents = detect_incidents()

    if not incidents:

        print("No incidents detected.")

        return

    for incident in incidents:

        report = analyze_incident(
            incident
        )

        print_report(report)


if __name__ == "__main__":
    main()