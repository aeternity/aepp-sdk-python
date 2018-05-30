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

  environment {
    DOCKER_COMPOSE = "docker-compose -p ${env.BUILD_TAG} -H localhost:2376"
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
          sh "${env.DOCKER_COMPOSE} run sdk pytest --junitxml test-results.xml aeternity/tests"
        }
      }
    }
  }

  post {
    always {
      junit 'test-results.xml'
      sh "${env.DOCKER_COMPOSE} run sdk git clean -fdx"
      sh "${env.DOCKER_COMPOSE} down -v ||:"
    }
  }
}