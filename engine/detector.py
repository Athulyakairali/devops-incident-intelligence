import json
import subprocess


INCIDENT_REASONS = {
    "OOMKilled": "MEMORY_EXHAUSTION",
    "CrashLoopBackOff": "CONTAINER_CRASH_LOOP",
    "ImagePullBackOff": "IMAGE_PULL_FAILURE",
    "ErrImagePull": "IMAGE_PULL_FAILURE",
    "Error": "CONTAINER_ERROR",
}


def get_pods():
    result = subprocess.run(
        ["kubectl", "get", "pods", "-o", "json"],
        capture_output=True,
        text=True,
        check=True,
    )

    return json.loads(result.stdout)


def analyze_container(container):
    incidents = []

    # Current container state
    current_state = container.get("state", {})

    terminated = current_state.get("terminated")

    if terminated:
        reason = terminated.get("reason")

        if reason in INCIDENT_REASONS:
            incidents.append({
                "type": INCIDENT_REASONS[reason],
                "reason": reason,
                "exit_code": terminated.get("exitCode"),
            })

    # Previous container state
    last_state = container.get("lastState", {})

    previous_terminated = last_state.get("terminated")

    if previous_terminated:
        reason = previous_terminated.get("reason")

        if reason in INCIDENT_REASONS:
            incidents.append({
                "type": INCIDENT_REASONS[reason],
                "reason": reason,
                "exit_code": previous_terminated.get("exitCode"),
            })

    # Waiting state, e.g. CrashLoopBackOff
    waiting = current_state.get("waiting")

    if waiting:
        reason = waiting.get("reason")

        if reason in INCIDENT_REASONS:
            incidents.append({
                "type": INCIDENT_REASONS[reason],
                "reason": reason,
                "message": waiting.get("message"),
            })

    return incidents


def detect_incidents():
    data = get_pods()

    incidents = []

    for pod in data["items"]:
        pod_name = pod["metadata"]["name"]

        container_statuses = pod["status"].get(
            "containerStatuses",
            [],
        )

        for container in container_statuses:

            detected = analyze_container(container)

            for incident in detected:
                incident["pod"] = pod_name
                incident["container"] = container["name"]

                incidents.append(incident)

    return incidents


def main():
    incidents = detect_incidents()

    if not incidents:
        print("No incidents detected.")
        return

    print("INCIDENTS DETECTED")

    for incident in incidents:
        print(json.dumps(incident, indent=2))


if __name__ == "__main__":
    main()
