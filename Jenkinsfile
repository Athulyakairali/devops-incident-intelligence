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
                    echo "Running Python tests..."

                    python3 --version

                    echo "Creating Jenkins virtual environment..."

                    python3 -m venv .jenkins-venv

                    . .jenkins-venv/bin/activate

                    echo "Installing Python dependencies..."

                    python -m pip install --upgrade pip

                    python -m pip install -r requirements.txt

                    echo "Compiling Python files..."

                    python -m py_compile app.py

                    python -m py_compile engine/*.py

                    echo "Running unit tests..."

                    python -m unittest discover \
                        -s tests \
                        -v
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

                    echo "Waiting for deployment rollout..."

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