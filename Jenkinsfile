pipeline {
  agent {
    dockerfile {
      filename 'Dockerfile.ci'
      args '-v /etc/group:/etc/group:ro ' +
           '-v /etc/passwd:/etc/passwd:ro ' +
           '-v /var/lib/jenkins:/var/lib/jenkins ' +
           '-v /usr/bin/docker:/usr/bin/docker:ro ' +
           '--network=host'
    }
  }

  stages {
    // stage('Build') {
    //   steps {
    //     sh 'ln -sf /node_modules ./'
    //     sh 'yarn build'
    //   }
    // }

    stage('Test') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'genesis-wallet',
                                          usernameVariable: 'WALLET_PUB',
                                          passwordVariable: 'WALLET_PRIV')]) {
          sh "docker-compose -p ${env.BUILD_TAG} -H localhost:2376 run sdk pytest --junitxml test-results.xml aeternity/tests"
          // sh 'docker-compose -H localhost:2376 run sdk yarn test-jenkins'
        }
      }
    }
  }

  post {
    always {
      junit '/app/test-results.xml'
      ah 'rm -rf .pytest_cache aeternity/__pycache__ aeternity/tests/__pycache__'
      sh 'docker-compose -H localhost:2376 down -v ||:'
    }
  }
}