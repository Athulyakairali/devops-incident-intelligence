import json
import os

from kubernetes import client
from kubernetes import config


INCIDENT_REASONS = {
    "OOMKilled": "MEMORY_EXHAUSTION",
    "CrashLoopBackOff": "CONTAINER_CRASH_LOOP",
    "ImagePullBackOff": "IMAGE_PULL_FAILURE",
    "ErrImagePull": "IMAGE_PULL_FAILURE",
    "Error": "CONTAINER_ERROR",
}


def get_kubernetes_client():

    if os.getenv("KUBERNETES_IN_CLUSTER") == "true":

        configuration = client.Configuration()

        configuration.host = os.getenv(
            "KUBERNETES_API_SERVER"
        )

        configuration.ssl_ca_cert = "/certs/ca.crt"
        configuration.cert_file = "/certs/client.crt"
        configuration.key_file = "/certs/client.key"

        configuration.verify_ssl = False

        return client.CoreV1Api(
            client.ApiClient(configuration)
        )

    config.load_kube_config()

    return client.CoreV1Api()


def get_pods():

    api = get_kubernetes_client()

    response = api.list_namespaced_pod(
        namespace="default"
    )

    return client.ApiClient().sanitize_for_serialization(
        response
    )


def analyze_container(container):

    incidents = []

    current_state = container.get(
        "state",
        {},
    )

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

    last_state = container.get(
        "lastState",
        {},
    )

    previous_terminated = last_state.get(
        "terminated"
    )

    if previous_terminated:

        reason = previous_terminated.get("reason")

        if reason in INCIDENT_REASONS:

            incidents.append({
                "type": INCIDENT_REASONS[reason],
                "reason": reason,
                "exit_code": previous_terminated.get(
                    "exitCode"
                ),
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

            detected = analyze_container(
                container
            )

            for incident in detected:

                incident["pod"] = pod_name

                incident["container"] = container[
                    "name"
                ]

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
            unique_incidents.append(
                incident
            )

    return unique_incidents


def main():

    incidents = detect_incidents()

    incidents = remove_duplicates(
        incidents
    )

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
