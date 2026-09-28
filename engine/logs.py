from kubernetes import client

from engine.detector import get_kubernetes_client


def get_pod_logs(pod_name):

    api = get_kubernetes_client()

    try:
        logs = api.read_namespaced_pod_log(
            name=pod_name,
            namespace="default",
        )

        if isinstance(logs, bytes):
            logs = logs.decode("utf-8")

        if logs.startswith("b'") and logs.endswith("'"):
            logs = logs[2:-1]
            logs = logs.replace("\\n", "\n")

        return logs.strip()

    except Exception:
        return "No application logs available."

if __name__ == "__main__":

    pod_name = "memory-stress"

    logs = get_pod_logs(pod_name)

    print("APPLICATION LOGS")
    print("-" * 60)

    if logs:
        print(logs)
    else:
        print("No logs found.")