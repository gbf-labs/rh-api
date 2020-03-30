pipeline {
//   agent { docker { image 'debian:stretch' } }
  agent any
  stages {
    stage('build') {
      steps {
        sh 'sudo pip3 install -r requirements.txt'
      }
    }
    stage('test') {
      steps {
        sh 'python3 test.py'
      }
    }
  }
}