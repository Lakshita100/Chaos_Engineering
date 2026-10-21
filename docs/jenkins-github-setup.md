# Jenkins Freestyle and GitHub

## Jenkins job

Use the Windows Freestyle job `ResilAI-Build-Test`. There is no Groovy
`Jenkinsfile` or Pipeline job. Its Windows batch steps install/check Python
dependencies, run unit and Selenium tests, check the Flask health endpoint, run
chaos experiments 1–4, and copy reports into the Jenkins workspace for
archiving. The repository template is `jenkins-freestyle-job.xml`.

The active job currently runs the local checkout at
`D:\UserData\Desktop\ResilAI` and uses that checkout's `.venv`. Its Jenkins SCM
setting is `None`, so it does not clone, poll, or receive a GitHub webhook. To
test a commit, update the local checkout first, then select **Build Now**.

## GitHub Actions

The `.github/workflows/ci.yml` workflow is a separate GitHub check. It runs on
pushes and pull requests to `main`; it does not require Jenkins or a Jenkinsfile.

## Docker service

From the project directory:

```powershell
docker compose up --build --detach
docker compose ps
Invoke-RestMethod http://127.0.0.1:5000/health
```

The Freestyle job uses the existing service on port 5000. Compose restarts the
container after an unexpected exit and binds the API to loopback.
