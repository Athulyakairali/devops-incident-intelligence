import subprocess


def get_pod_logs(pod_name):
    result = subprocess.run(
        [
            "kubectl",
            "logs",
            pod_name,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return "No application logs available."

    return result.stdout.strip()


if __name__ == "__main__":
    pod_name = "memory-stress"

    logs = get_pod_logs(pod_name)

    print("APPLICATION LOGS")
    print("-" * 60)

    if logs:
        print(logs)
    else:
        print("No logs found.")
