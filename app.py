from flask import Flask, jsonify

from engine.detector import detect_incidents
from engine.analyzer import analyze_incident


app = Flask(__name__)


@app.route("/")
def home():
    return "DevOps Incident Intelligence Platform"


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/incidents")
def incidents():

    detected_incidents = detect_incidents()

    reports = []

    for incident in detected_incidents:
        report = analyze_incident(incident)
        reports.append(report)

    return jsonify({
        "count": len(reports),
        "incidents": reports
    })


@app.route("/incidents/<incident_id>")
def incident_by_id(incident_id):

    detected_incidents = detect_incidents()

    for incident in detected_incidents:

        report = analyze_incident(incident)

        if report.get("incident_id") == incident_id:
            return jsonify(report)

    return jsonify({
        "error": "Incident not found",
        "incident_id": incident_id
    }), 404


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )