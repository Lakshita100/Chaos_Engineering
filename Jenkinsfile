pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 45, unit: 'MINUTES')
    }

    environment {
        APP_URL = 'http://127.0.0.1:5000'
        CONTAINER_NAME = 'chaos-ai-container'
        IMAGE_NAME = 'chaos-ai'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'python3 -m venv .venv && .venv/bin/python -m pip install --upgrade pip && .venv/bin/pip install -r app/requirements.txt'
            }
        }

        stage('Unit Tests') {
            steps {
                sh 'mkdir -p results && .venv/bin/pytest tests/ -v --junitxml=results/unit-test-results.xml'
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'results/unit-test-results.xml'
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build --tag "$IMAGE_NAME:$BUILD_NUMBER" --tag "$IMAGE_NAME:ci" .'
            }
        }

        stage('Start Container') {
            steps {
                sh '''
                    docker rm --force "$CONTAINER_NAME" 2>/dev/null || true
                    docker run --detach --init --cap-add NET_ADMIN \
                      --publish 127.0.0.1:5000:5000 --name "$CONTAINER_NAME" \
                      "$IMAGE_NAME:ci"
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    for attempt in $(seq 1 30); do
                      if curl --fail --silent "$APP_URL/health"; then exit 0; fi
                      sleep 2
                    done
                    echo "Service failed health check"
                    docker logs "$CONTAINER_NAME" || true
                    exit 1
                '''
            }
        }

        stage('Selenium Tests') {
            steps {
                sh 'APP_URL="$APP_URL" .venv/bin/pytest selenium/ -v --junitxml=results/selenium-test-results.xml'
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'results/selenium-test-results.xml'
                }
            }
        }

        stage('Chaos Experiments') {
            steps {
                sh '.venv/bin/python chaos/run_experiments.py --requests 20 --duration 5 --workers 2 --mb 64 --delay 100 1 2 3 4'
            }
        }
    }

    post {
        always {
            sh '''
                mkdir -p results
                docker logs "$CONTAINER_NAME" > results/container_logs.txt 2>&1 || true
                docker rm --force "$CONTAINER_NAME" 2>/dev/null || true
            '''
            archiveArtifacts allowEmptyArchive: true, artifacts: 'results/**', fingerprint: true
        }
    }
}
