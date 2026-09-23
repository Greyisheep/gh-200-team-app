# The pipeline, end to end, on one page

File: `.github/workflows/pipeline.yml` (same as `reference/pipeline-final.yml`).

## The shape

```
pull request ──► test ──► (deploy skipped)
push to main ──► test ──► deploy ──► waits for a teammate ──► live, and checked
```

## Top of the file: rules for the whole workflow

| Lines | What it says | Why |
|---|---|---|
| `on:` | Run on pull requests to main, pushes to main, and the Run button | PRs get tested before merge; main gets tested and deployed |
| `permissions: contents: read` | Every job's token can only read the code | Least privilege. A job must ask for more itself |
| `concurrency:` | A newer PR push cancels the old run; runs on main never cancel | Nobody waits for a run of code you already replaced |
| `env: IMAGE` | The image name, built from your variables | One place to change it. It reads `vars.GCP_REGION`, `vars.GCP_PROJECT`, `vars.AR_REPO` |

## Job 1: `test` (every PR and every push)

A brand new Linux machine. Nothing leaves GitHub.

1. **checkout**: copy your code onto the machine.
2. **Stamp the page**: `scripts/stamp.py` writes your team, commit and name into `app/index.html`, from environment variables.
3. **Build the image**: `docker build`, the same Dockerfile production uses.
4. **Run it and check it answers**: start the container, `curl` it, look for "Shipped by a pipeline". Red if the page is broken.
5. **Pick the version tag**: `tag=<commit>-<run number>`, like `912e105-12`, written to `$GITHUB_OUTPUT`.

`outputs: tag:` publishes that tag from the job, so the next job can read it. Without it, the value dies with this machine.

## Job 2: `deploy` (only a push to main)

| Line | What it does |
|---|---|
| `needs: test` | Waits for test to pass. Red test, no deploy |
| `if: push and main` | Pull requests never deploy. On a PR this job shows as skipped |
| `environment: production` | Pauses for a teammate to click **Review deployments**, only allows `main`, and is what Google checks before trusting the job |
| `concurrency: deploy-production` | One deploy at a time, never cancelled halfway |
| `permissions: id-token: write` | Lets this job ask GitHub for a login token for Google |
| `env: TAG` from `needs.test.outputs.tag` | Reads the tag the test job published |

Then the steps, on another brand new machine:

1. **checkout** and **Stamp the page**, now with `DEPLOY_ENV: production` and your `BANNER`.
2. **Log in to Google Cloud, keyless**: GitHub gives the job a signed token saying *this repo, production environment*. Google checks it against the list of class repos and hands back access for about an hour, to **your team's service only**. No password is stored anywhere.
3. **setup-gcloud**: installs the Google Cloud command line tool.
4. **Build and push the image**: tagged with `$TAG`, pushed to your team's image repo.
5. **Deploy**: Cloud Run starts the new image and moves traffic to it.
6. **Check it is live**: `curl` the live URL and check it shows this commit. Red if not. The run summary shows the URL and the tag.

## Where each value comes from

| You see | It comes from |
|---|---|
| `${{ vars.X }}` | Settings, Secrets and variables, Actions, **Variables** |
| `${{ github.sha }}`, `github.actor` | The commit and person that started the run |
| `${{ steps.version.outputs.tag }}` | Step `id: version` in the same job |
| `${{ needs.test.outputs.tag }}` | Job `test`'s `outputs:` |
| `$TAG`, `$IMAGE` | Environment variables, read by the shell |

## The four lines that matter most

| Remove it | And you get |
|---|---|
| `id-token: write` | *did not inject $ACTIONS_ID_TOKEN_REQUEST_TOKEN* |
| `environment: production` | *The given credential is rejected by the attribute condition* |
| `$GITHUB_OUTPUT` (use `$GITHUB_ENV`) | *invalid tag ".../frontend:"* |
| the `if:` on deploy | On a PR: *not allowed to deploy to production* |
