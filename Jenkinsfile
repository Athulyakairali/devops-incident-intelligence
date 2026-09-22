pipeline {

    agent any

    environment {
        PATH = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"

        DOCKER = "/usr/local/bin/docker"
        KUBECTL = "/usr/local/bin/kubectl"
        MINIKUBE = "/opt/homebrew/bin/minikube"
        TRIVY = "/opt/homebrew/bin/trivy"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh '''
                    python3 --version

                    python3 -m py_compile app.py

                    python3 -m py_compile engine/*.py
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "Building Docker image..."

                    $DOCKER build \
                        -t incident-intelligence:ci \
                        .
                '''
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    echo "Running Trivy vulnerability scan..."

                    $TRIVY image \
                        --severity HIGH,CRITICAL \
                        --exit-code 1 \
                        incident-intelligence:ci
                '''
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    echo "Loading image into Minikube..."

                    $MINIKUBE image load \
                        incident-intelligence:ci

                    echo "Deploying to Kubernetes..."

                    $KUBECTL apply \
                        -f k8s/deployment.yaml

                    $KUBECTL apply \
                        -f k8s/service.yaml

                    $KUBECTL rollout status \
                        deployment/incident-intelligence \
                        --timeout=120s
                '''
            }
        }
    }

    post {

        success {
            echo 'CI/CD pipeline completed successfully.'
        }

        failure {
            echo 'CI/CD pipeline failed.'
        }
    }
}