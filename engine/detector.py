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

    current_state = container.get("state", {})

    # ---------------------------------------------------------

    # Current waiting state

    # ---------------------------------------------------------

    waiting = current_state.get("waiting")

    if waiting:

        reason = waiting.get("reason")

        if reason in INCIDENT_REASONS:

            incidents.append({

                "type": INCIDENT_REASONS[reason],

                "reason": reason,

                "message": waiting.get("message"),

            })

            # CrashLoopBackOff is the current incident.

            # Do not also report the previous Error state.

            return incidents

    # ---------------------------------------------------------

    # Current terminated state

    # ---------------------------------------------------------

    terminated = current_state.get("terminated")

    if terminated:

        reason = terminated.get("reason")

        if reason in INCIDENT_REASONS:

            incidents.append({

                "type": INCIDENT_REASONS[reason],

                "reason": reason,

                "exit_code": terminated.get("exitCode"),

            })

            return incidents

    # ---------------------------------------------------------

    # Previous terminated state

    # ---------------------------------------------------------

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

    return incidents
    # ---------------------------------------------------------
    # Previous terminated state
    # ---------------------------------------------------------

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


def remove_duplicates(incidents):
    unique_incidents = []

    seen = set()

    for incident in incidents:

        key = (
            incident.get("pod"),
            incident.get("container"),
            incident.get("type"),
            incident.get("reason"),
        )

        if key not in seen:

            seen.add(key)

            unique_incidents.append(incident)

    return unique_incidents


def main():

    incidents = detect_incidents()

    incidents = remove_duplicates(incidents)

    if not incidents:
        print("No incidents detected.")
        return

    print("INCIDENTS DETECTED")

    for incident in incidents:

        print(
            json.dumps(
                incident,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()