pipeline {

    agent any

    environment {
        DOCKER = "/usr/local/bin/docker"
        KUBECTL = "/usr/local/bin/kubectl"
        MINIKUBE = "/opt/homebrew/bin/minikube"
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
                    $DOCKER build \
                        -t incident-intelligence:ci \
                        .
                '''
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    $MINIKUBE image load incident-intelligence:ci

                    $KUBECTL apply -f k8s/deployment.yaml
                    $KUBECTL apply -f k8s/service.yaml

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
