import unittest

from engine.detector import analyze_container


class TestDetector(unittest.TestCase):

    def test_oom_killed(self):

        container = {
            "state": {
                "terminated": {
                    "reason": "OOMKilled",
                    "exitCode": 137,
                }
            }
        }

        incidents = analyze_container(container)

        self.assertEqual(len(incidents), 1)
        self.assertEqual(
            incidents[0]["type"],
            "MEMORY_EXHAUSTION",
        )
        self.assertEqual(
            incidents[0]["reason"],
            "OOMKilled",
        )
        self.assertEqual(
            incidents[0]["exit_code"],
            137,
        )

    def test_container_error(self):

        container = {
            "state": {
                "terminated": {
                    "reason": "Error",
                    "exitCode": 1,
                }
            }
        }

        incidents = analyze_container(container)

        self.assertEqual(len(incidents), 1)
        self.assertEqual(
            incidents[0]["type"],
            "CONTAINER_ERROR",
        )
        self.assertEqual(
            incidents[0]["reason"],
            "Error",
        )

    def test_crash_loop_backoff(self):

        container = {
            "state": {
                "waiting": {
                    "reason": "CrashLoopBackOff",
                    "message": "Back-off restarting failed container",
                }
            },
            "lastState": {
                "terminated": {
                    "reason": "Error",
                    "exitCode": 1,
                }
            },
        }

        incidents = analyze_container(container)

        self.assertEqual(len(incidents), 1)

        self.assertEqual(
            incidents[0]["type"],
            "CONTAINER_CRASH_LOOP",
        )

        self.assertEqual(
            incidents[0]["reason"],
            "CrashLoopBackOff",
        )

    def test_image_pull_backoff(self):

        container = {
            "state": {
                "waiting": {
                    "reason": "ImagePullBackOff",
                    "message": "Back-off pulling image",
                }
            }
        }

        incidents = analyze_container(container)

        self.assertEqual(len(incidents), 1)

        self.assertEqual(
            incidents[0]["type"],
            "IMAGE_PULL_FAILURE",
        )

        self.assertEqual(
            incidents[0]["reason"],
            "ImagePullBackOff",
        )

    def test_err_image_pull(self):

        container = {
            "state": {
                "waiting": {
                    "reason": "ErrImagePull",
                    "message": "Failed to pull image",
                }
            }
        }

        incidents = analyze_container(container)

        self.assertEqual(len(incidents), 1)

        self.assertEqual(
            incidents[0]["type"],
            "IMAGE_PULL_FAILURE",
        )

    def test_unknown_state(self):

        container = {
            "state": {
                "waiting": {
                    "reason": "ContainerCreating",
                }
            }
        }

        incidents = analyze_container(container)

        self.assertEqual(
            incidents,
            [],
        )


if __name__ == "__main__":
    unittest.main()
