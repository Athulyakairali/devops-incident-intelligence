from kubernetes import client

from engine.detector import get_kubernetes_client


def get_events():

    api = get_kubernetes_client()

    response = api.list_event_for_all_namespaces()

    return client.ApiClient().sanitize_for_serialization(response)


def get_pod_info(pod_name):

    api = get_kubernetes_client()

    response = api.read_namespaced_pod(
        name=pod_name,
        namespace="default",
    )

    return client.ApiClient().sanitize_for_serialization(response)


def get_pod_events(pod_name):

    pod = get_pod_info(pod_name)

    pod_uid = pod["metadata"]["uid"]

    data = get_events()

    pod_events = []

    for event in data["items"]:

        involved_object = event.get(
            "involvedObject",
            {},
        )

        event_name = involved_object.get("name")
        event_uid = involved_object.get("uid")

        if (
            event_name == pod_name
            and event_uid == pod_uid
        ):
            pod_events.append({
                "reason": event.get("reason"),
                "message": event.get("message"),
                "type": event.get("type"),
                "timestamp": (
                    event.get("lastTimestamp")
                    or event.get("eventTime")
                ),
            })

    return pod_events


if __name__ == "__main__":

    pod_name = "memory-stress"

    events = get_pod_events(pod_name)

    for event in events:
        print(
            f"{event['timestamp']} | "
            f"{event['reason']} | "
            f"{event['message']}"
        )