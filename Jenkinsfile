
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                bat 'python --version'
            }
        }

        stage('Run Usage Aggregation') {
            steps {
                bat 'python usage_aggregation.py sample_readings.csv'
            }
        }

        stage('Test Dataset') {
            steps {
                bat 'python usage_aggregation.py test_sample_readings.csv'
            }
        }
    }
}
