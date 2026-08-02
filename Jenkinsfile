pipeline {
    agent any

    environment {
        DOCKER_IMAGE_NAME = 'live-weather-dashboard'
        DOCKER_TAG        = "${BUILD_NUMBER}"
        REGISTRY_USER     = 'your-dockerhub-username'
    }

    stages {
        stage('Checkout Source') {
            steps {
                checkout scm
            }
        }

        stage('Static Code Analysis & Linting') {
            steps {
                sh 'python -m py_compile app.py config.py services/*.py components/*.py'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${REGISTRY_USER}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG} -t ${REGISTRY_USER}/${DOCKER_IMAGE_NAME}:latest ."
            }
        }

        stage('Push to Docker Registry') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                    sh "docker push ${REGISTRY_USER}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"
                    sh "docker push ${REGISTRY_USER}/${DOCKER_IMAGE_NAME}:latest"
                }
            }
        }

        stage('Deploy to Kubernetes Cluster') {
            steps {
                sh "kubectl apply -f k8s/deployment.yaml"
                sh "kubectl apply -f k8s/service.yaml"
                sh "kubectl rollout restart deployment/weather-dashboard-deployment"
            }
        }
    }

    post {
        always {
            sh 'docker logout'
        }
        success {
            echo 'Jenkins Pipeline successfully built, pushed, and deployed the Weather Dashboard to Kubernetes!'
        }
        failure {
            echo 'Jenkins Pipeline execution failed.'
        }
    }
}
