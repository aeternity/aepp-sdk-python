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
    DOCKER_COMPOSE = "docker-compose -p ${env.BUILD_TAG} -H 127.0.0.1:2376"
    SCANNER_HOME = tool 'default-sonarqube-scanner'
  }

  stages {

    stage('Test') {
      steps {          
          withCredentials([usernamePassword(credentialsId: 'genesis-wallet',
                                          usernameVariable: 'WALLET_PUB',
                                          passwordVariable: 'WALLET_PRIV')]) {
          sh "${env.DOCKER_COMPOSE} run sdk flake8"
          sh "${env.DOCKER_COMPOSE} run sdk pytest --junitxml test-results.xml tests --cov=aeternity --cov-config .coveragerc --cov-report xml:coverage.xml -k test_hashing"
        }
      }
    }

    stage('Sonarqube Analysis') {
      agent { 
        node { 
          label 'local'
          reuseNode: 'true'
        }
      }
      steps {
        // run sonar?
        withSonarQubeEnv('default-sonarqube-server') {
          sh "${env.SCANNER_HOME}/bin/sonar-scanner -X"
        }
      }
    }


    stage('Publish') {
      when {
        buildingTag()
        beforeAgent true
      }
      steps {
        withCredentials([
          usernamePassword(credentialsId: 'pypi',
                                          usernameVariable: 'TWINE_USERNAME',
                                          passwordVariable: 'TWINE_PASSWORD'),
          string(credentialsId: 'pypi_repo_url', variable: 'TWINE_REPOSITORY_URL')]) {
            sh '''make clean && make build && make publish'''
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