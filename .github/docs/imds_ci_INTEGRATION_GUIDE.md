# IMDS CI Integration Guide

## Overview

This guide explains how to integrate IMDS diagnostic tools into your CI/CD pipelines for automated testing, monitoring, and alerting.

## Supported CI/CD Platforms

- **GitHub Actions** (Primary support)
- **Azure DevOps**
- **GitLab CI**
- **Jenkins**
- **CircleCI**
- **Travis CI**

## GitHub Actions Integration

### Quick Start

Add the IMDS check to your workflow:

```yaml
name: CI Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run IMDS Diagnostic
        uses: ./.github/actions/imds-check
        with:
          verbose: true
          fail-on-inaccessible: false  # Don't fail on GitHub-hosted runners
```

### Preflight Checks

Automatically run IMDS diagnostics on pull requests:

```yaml
name: IMDS Preflight
on:
  pull_request:
    branches: [main, develop]

jobs:
  imds-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check IMDS Accessibility
        id: imds
        uses: ./.github/actions/imds-check
        with:
          timeout: 10
          output-artifact: true
        continue-on-error: true
      
      - name: Comment on PR
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const accessible = '${{ steps.imds.outputs.imds-accessible }}';
            const comment = accessible === 'true' 
              ? '✅ IMDS is accessible on this runner'
              : '⚠️  IMDS is not accessible (expected on GitHub-hosted runners)';
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### Self-Hosted Runners

For self-hosted runners on Azure VMs:

```yaml
name: Azure Runner Check
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  check-imds:
    runs-on: [self-hosted, azure]
    steps:
      - uses: actions/checkout@v4
      
      - name: IMDS Health Check
        uses: ./.github/actions/imds-check
        with:
          verbose: true
          fail-on-inaccessible: true  # Fail if IMDS is down
          output-artifact: true
      
      - name: Upload Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: imds-health-${{ github.run_number }}
          path: imds_results.json
          retention-days: 90
      
      - name: Notify on Failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "⚠️ IMDS check failed on self-hosted runner",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*IMDS Health Check Failed*\n\nRunner: ${{ runner.name }}\nWorkflow: ${{ github.workflow }}\nRun: ${{ github.run_id }}"
                  }
                }
              ]
            }
```

### Matrix Testing

Test across multiple runner types:

```yaml
name: IMDS Matrix Test
on: workflow_dispatch

jobs:
  test-runners:
    runs-on: ${{ matrix.runner }}
    strategy:
      matrix:
        runner:
          - ubuntu-latest
          - ubuntu-22.04
          - [self-hosted, azure, linux]
          - [self-hosted, azure, windows]
      fail-fast: false
    
    steps:
      - uses: actions/checkout@v4
      
      - name: IMDS Check
        uses: ./.github/actions/imds-check
        continue-on-error: true
      
      - name: Record Result
        run: |
          echo "Runner: ${{ matrix.runner }}" >> results.txt
          echo "IMDS Accessible: ${{ steps.imds.outputs.imds-accessible }}" >> results.txt
          echo "---" >> results.txt
      
      - name: Upload Matrix Results
        uses: actions/upload-artifact@v4
        with:
          name: runner-${{ strategy.job-index }}
          path: results.txt
```

## Azure DevOps Integration

### Pipeline YAML

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
- checkout: self

- bash: |
    chmod +x .github/scripts/imds_diagnostic.sh
    ./.github/scripts/imds_diagnostic.sh --output $(Build.ArtifactStagingDirectory)/imds_results.json
  displayName: 'Run IMDS Diagnostic'
  continueOnError: true

- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: '$(Build.ArtifactStagingDirectory)/imds_results.json'
    artifactName: 'imds-diagnostic'
  displayName: 'Publish IMDS Results'

- bash: |
    accessible=$(jq -r '.imds_accessible' $(Build.ArtifactStagingDirectory)/imds_results.json)
    if [ "$accessible" = "true" ]; then
      echo "##vso[task.complete result=Succeeded;]IMDS is accessible"
    else
      echo "##vso[task.logissue type=warning]IMDS is not accessible"
    fi
  displayName: 'Check IMDS Status'
```

### Self-Hosted Azure DevOps Agents

```yaml
pool:
  name: 'Azure-Pool'
  demands:
    - azure-vm
    - imds-required

steps:
- bash: |
    ./.github/scripts/imds_diagnostic.sh --verbose --output results.json
    
    if [ $? -ne 0 ]; then
      echo "##vso[task.logissue type=error]IMDS check failed"
      exit 1
    fi
  displayName: 'IMDS Health Check'
  
- task: PublishPipelineArtifact@1
  inputs:
    targetPath: 'results.json'
    artifactName: 'imds-results'
```

## GitLab CI Integration

```yaml
# .gitlab-ci.yml
stages:
  - test
  - deploy

imds_check:
  stage: test
  image: ubuntu:latest
  before_script:
    - apt-get update && apt-get install -y curl jq iputils-ping
  script:
    - chmod +x .github/scripts/imds_diagnostic.sh
    - ./.github/scripts/imds_diagnostic.sh --output imds_results.json || true
    - |
      accessible=$(jq -r '.imds_accessible' imds_results.json)
      if [ "$accessible" = "true" ]; then
        echo "✅ IMDS is accessible"
      else
        echo "⚠️  IMDS is not accessible"
      fi
  artifacts:
    paths:
      - imds_results.json
    expire_in: 30 days
    reports:
      junit: imds_results.json
  allow_failure: true
  tags:
    - azure-runner  # Only on Azure-hosted runners

deploy:
  stage: deploy
  dependencies:
    - imds_check
  script:
    - echo "Deploying to Azure..."
  only:
    - main
```

## Jenkins Integration

### Declarative Pipeline

```groovy
pipeline {
    agent {
        label 'azure-vm'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('IMDS Diagnostic') {
            steps {
                sh '''
                    chmod +x .github/scripts/imds_diagnostic.sh
                    ./.github/scripts/imds_diagnostic.sh --output imds_results.json
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'imds_results.json', fingerprint: true
                }
            }
        }
        
        stage('Validate IMDS') {
            steps {
                script {
                    def results = readJSON file: 'imds_results.json'
                    if (results.imds_accessible == 'true') {
                        echo "✅ IMDS is accessible"
                    } else {
                        error "❌ IMDS is not accessible"
                    }
                }
            }
        }
    }
    
    post {
        failure {
            emailext (
                subject: "IMDS Check Failed: ${env.JOB_NAME}",
                body: "IMDS diagnostic failed. Check attached results.",
                attachLog: true,
                recipientProviders: [developers(), requestor()]
            )
        }
    }
}
```

### Scripted Pipeline

```groovy
node('azure-vm') {
    stage('IMDS Check') {
        checkout scm
        
        sh '''
            chmod +x .github/scripts/imds_diagnostic.sh
            ./.github/scripts/imds_diagnostic.sh --output imds_results.json --verbose
        '''
        
        def results = readJSON file: 'imds_results.json'
        
        if (results.imds_accessible == 'false') {
            currentBuild.result = 'UNSTABLE'
            error("IMDS is not accessible: ${results.error_reason}")
        }
        
        archiveArtifacts 'imds_results.json'
    }
}
```

## CircleCI Integration

```yaml
# .circleci/config.yml
version: 2.1

executors:
  azure-vm:
    machine:
      image: ubuntu-2004:current
    resource_class: self-hosted/azure-runner

jobs:
  imds-check:
    executor: azure-vm
    steps:
      - checkout
      
      - run:
          name: Install Dependencies
          command: |
            sudo apt-get update
            sudo apt-get install -y curl jq iputils-ping
      
      - run:
          name: Run IMDS Diagnostic
          command: |
            chmod +x .github/scripts/imds_diagnostic.sh
            ./.github/scripts/imds_diagnostic.sh --output imds_results.json
      
      - run:
          name: Check Results
          command: |
            accessible=$(jq -r '.imds_accessible' imds_results.json)
            if [ "$accessible" = "true" ]; then
              echo "IMDS is accessible"
            else
              echo "IMDS is not accessible"
              exit 1
            fi
      
      - store_artifacts:
          path: imds_results.json
          destination: diagnostic-results

workflows:
  version: 2
  test-and-deploy:
    jobs:
      - imds-check
```

## Docker Integration

### Dockerfile for Testing

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    curl \
    jq \
    iputils-ping \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

COPY .github/scripts/imds_diagnostic.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/imds_diagnostic.sh

ENTRYPOINT ["imds_diagnostic.sh"]
CMD ["--verbose", "--output", "/results/imds.json"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  imds-check:
    build: .
    volumes:
      - ./results:/results
    environment:
      - IMDS_TIMEOUT=10
      - IMDS_VERBOSE=true
    network_mode: host  # Required for IMDS access
```

## Best Practices

### 1. Conditional Execution

Only run on Azure VMs:

```yaml
- name: Check if Azure VM
  id: check-azure
  run: |
    if sudo dmidecode -s system-manufacturer | grep -qi microsoft; then
      echo "is-azure=true" >> $GITHUB_OUTPUT
    else
      echo "is-azure=false" >> $GITHUB_OUTPUT
    fi

- name: IMDS Check
  if: steps.check-azure.outputs.is-azure == 'true'
  uses: ./.github/actions/imds-check
```

### 2. Artifact Retention

Store results for troubleshooting:

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: imds-diagnostic-${{ github.run_number }}
    path: imds_results.json
    retention-days: 90
```

### 3. Notifications

Alert on failures:

```yaml
- name: Notify Slack
  if: failure()
  env:
    SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
  run: |
    curl -X POST $SLACK_WEBHOOK -H 'Content-Type: application/json' -d '{
      "text": "IMDS check failed",
      "attachments": [{
        "color": "danger",
        "fields": [{
          "title": "Workflow",
          "value": "${{ github.workflow }}",
          "short": true
        }]
      }]
    }'
```

### 4. Caching Results

Cache results to reduce API calls:

```yaml
- name: Cache IMDS Results
  uses: actions/cache@v3
  with:
    path: imds_results.json
    key: imds-${{ runner.os }}-${{ github.run_id }}
    restore-keys: |
      imds-${{ runner.os }}-
```

## Troubleshooting

### GitHub Actions Issues

**Problem**: Action fails to find script
```yaml
# Solution: Ensure checkout happens first
- uses: actions/checkout@v4
- uses: ./.github/actions/imds-check
```

**Problem**: Permission denied
```yaml
# Solution: Make script executable
- run: chmod +x .github/scripts/imds_diagnostic.sh
```

### Azure DevOps Issues

**Problem**: jq not found
```yaml
# Solution: Install dependencies
- bash: sudo apt-get install -y jq curl
```

## Related Documentation

- [IMDS Diagnostic Runbook](imds_diagnostic_RUNBOOK.md)
- [Configuration Guide](imds_config_GUIDE.md)
- [Action README](../actions/imds-check/README.md)

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15  
**Maintainer:** IMDS Diagnostic Team
