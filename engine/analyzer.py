from kubernetes import client

from engine.detector import detect_incidents, get_kubernetes_client
from engine.events import get_pod_events
from engine.logs import get_pod_logs
from engine.rca import generate_rca


def get_pod_details(pod_name):

    api = get_kubernetes_client()

    response = api.read_namespaced_pod(
        name=pod_name,
        namespace="default",
    )

    return client.ApiClient().sanitize_for_serialization(
        response
    )


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

    elif incident["reason"] == "CrashLoopBackOff":

        report["severity"] = "HIGH"

    elif incident["reason"] in [
        "ImagePullBackOff",
        "ErrImagePull",
    ]:

        report["severity"] = "MEDIUM"

    else:

        report["severity"] = "MEDIUM"

    # Generate RCA using the complete incident report.
    rca = generate_rca(report)

    report.update({

    "root_cause": rca.get("root_cause"),

    "confirmed_evidence": rca.get("confirmed_evidence", []),

    "likely_contributing_factors": rca.get(

        "likely_contributing_factors",

        []

    ),

    "unknowns": rca.get("unknowns", []),

    "recommended_actions": rca.get(

        "recommended_actions",

        rca.get("recommendations", [])

    ),

    "confidence": rca.get("confidence"),

})

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
    print(f"Exit Code     : {report['exit_code']}")
    print(f"Pod Status    : {report['pod_status']}")
    print(f"Memory Limit  : {report['memory_limit']}")

    print()
    print("ROOT CAUSE ANALYSIS")
    print("-" * 70)
    print(report.get("root_cause", "Not available."))

    print()
    print("CONFIRMED EVIDENCE")
    print("-" * 70)

    for evidence in report.get(
        "confirmed_evidence",
        [],
    ):
        print(f"- {evidence}")

    print()
    print("LIKELY CONTRIBUTING FACTORS")
    print("-" * 70)

    for factor in report.get(
        "likely_contributing_factors",
        [],
    ):
        print(f"- {factor}")

    print()
    print("UNKNOWN / UNCONFIRMED")
    print("-" * 70)

    for unknown in report.get(
        "unknowns",
        [],
    ):
        print(f"- {unknown}")

    print()
    print("RECOMMENDATIONS")
    print("-" * 70)

    for recommendation in report.get(
        "recommendations",
        [],
    ):
        print(f"- {recommendation}")


def main():

    incidents = detect_incidents()

    if not incidents:
        print("No incidents detected.")
        return

    for incident in incidents:

        report = analyze_incident(incident)

        print_report(report)


if __name__ == "__main__":
    main()
