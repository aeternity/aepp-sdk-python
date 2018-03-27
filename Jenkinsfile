pipeline {
  agent {
    dockerfile {
      filename 'Dockerfile.ci'
      args '-v /etc/group:/etc/group:ro -v /etc/passwd:/etc/passwd:ro -v /var/lib/jenkins:/var/lib/jenkins'
    }
  }

  stages {
    stage('Echo') {
      steps {
        sh 'echo "Hi!"'
      }
    }
  }

  // post {
  //   always {
  //     junit 'test-results.xml'
  //   }
  // }
}
