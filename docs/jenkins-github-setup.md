# Jenkins and GitHub setup

## GitHub CI

The workflow in `.github/workflows/ci.yml` runs automatically for pushes and
pull requests targeting `main`. It checks the Python tests, builds the Docker
image, starts the API, runs the Selenium tests, and stores test output and
container logs as workflow artifacts.

## Jenkins prerequisites

Use a Linux Jenkins controller with a Linux build agent that has:

- Python 3.11 and `python3-venv`
- Docker Engine and permission for the Jenkins agent account to run Docker
- Google Chrome or Chromium
- The Jenkins Pipeline, Git, and JUnit plugins

The agent must be able to publish port 5000 on its own host, since the pipeline
tests `http://127.0.0.1:5000`. Do not run concurrent builds of this project on
the same agent; the pipeline disables concurrent builds because it uses a fixed
container name and port.

## Connect Jenkins to GitHub

1. Push this project to `https://github.com/Lakshita100/Chaos_Engineering` and
   ensure the default branch is `main`.
2. In Jenkins, choose **New Item**, create a **Multibranch Pipeline**, and add a
   **GitHub** branch source for `Lakshita100/Chaos_Engineering`.
3. For a public repository, use the HTTPS clone URL without credentials. For a
   private repository, add a Jenkins credential with read-only repository
   access and select it as the branch-source credential.
4. Set the script path to `Jenkinsfile`, save, then select **Scan Multibranch
   Pipeline Now**. Jenkins discovers the pipeline from the repository.

For automatic push notifications, configure the GitHub webhook only after
Jenkins has a stable HTTPS URL reachable from GitHub. Use
`https://<your-jenkins-host>/github-webhook/` and the **Pushes** event. For a
Jenkins instance that is only reachable on a local network, use the Multibranch
Pipeline periodic scan instead of exposing Jenkins publicly.

## Start the app with Docker Compose

From the project directory:

```powershell
docker compose up --build --detach
docker compose ps
Invoke-RestMethod http://127.0.0.1:5000/health
```

Stop it with:

```powershell
docker compose down
```

The Compose service restarts after an unexpected container exit. The API port
is bound to loopback so it is available on this machine without being exposed
to the network.
