# Ship it: your team's pipeline

By the end, a change merged to `main` in **your** repo goes through tests, waits
for a teammate to approve, deploys to **your team's own URL**, and checks it is
live. Then you give it a rollback.

Some of what you add below **fails on purpose**. When a run goes red, read the
error, write down what you think it means, and wait. We fix each one together.

---

## Stage 0: set up (10 min)

1. On this repo, click **Use this template, Create a new repository**.
   Owner: one person in your team. Make it **Public**. Name: `gh-200-team-<n>`.
2. Post the full name (for example `ada/gh-200-team-2`) in the class chat.
   Your instructor connects it to your team's cloud service.
3. In **your** repo: **Settings, Secrets and variables, Actions, Variables tab,
   New repository variable**. Add all seven. Your instructor gives you the values.

   | Name | Example |
   |---|---|
   | `TEAM` | `Team 2` |
   | `SERVICE` | `gh200-team-2` |
   | `AR_REPO` | `gh200-team-2` |
   | `DEPLOYER_SA` | `gh200-team-2@deepstack-492609.iam.gserviceaccount.com` |
   | `WIF_PROVIDER` | `projects/130785602363/locations/global/workloadIdentityPools/gh200-github/providers/gh200-teams` |
   | `GCP_PROJECT` | `deepstack-492609` |
   | `GCP_REGION` | `europe-west1` |

   Optional: add `BANNER` with any sentence, and it appears on your live page.

   None of these are secrets. That is the point of the keyless login: there is
   no password to store.

4. **Settings, Environments, New environment**, name it exactly `production`.
   - Tick **Required reviewers** and add a **teammate** (not yourself).
   - **Deployment branches and tags: Selected branches**, add `main`.

Your team's URL: `https://gh200-team-<n>-130785602363.europe-west1.run.app`
Open it now. You will see a placeholder until your first deploy.

---

## Stage 1: CI (5 min)

`.github/workflows/pipeline.yml` already builds the page into an image and
checks it renders, on every pull request and every push to `main`.

Edit `app/index.html` in the browser, change a word, commit to `main`. Watch it
go green in the **Actions** tab.

---

## Stage 2: the first deploy attempt (30 min, three red runs)

This is how most people write their first deploy job. Add it, exactly as it is.

**a)** At the end of the `test` job, add one step:

```yaml
      - name: Pick the version tag
        run: echo "TAG=${GITHUB_SHA::7}-${GITHUB_RUN_NUMBER}" >> "$GITHUB_ENV"
```

**b)** Under `jobs:`, after the whole `test` job, add the `deploy` job:

```yaml
  deploy:
    name: Deploy to Cloud Run
    needs: test
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false

      - name: Stamp the page
        env:
          TEAM: ${{ vars.TEAM }}
          SHA: ${{ github.sha }}
          ACTOR: ${{ github.actor }}
          DEPLOY_ENV: production
          BANNER: ${{ vars.BANNER }}
        run: python3 scripts/stamp.py

      - name: Log in to Google Cloud, keyless
        uses: google-github-actions/auth@7c6bc770dae815cd3e89ee6cdf493a5fab2cc093 # v3
        with:
          workload_identity_provider: ${{ vars.WIF_PROVIDER }}
          service_account: ${{ vars.DEPLOYER_SA }}

      - uses: google-github-actions/setup-gcloud@aa5489c8933f4cc7a4f7d45035b3b1440c9c10db # v3.0.1

      - name: Build and push the image
        run: |
          gcloud auth configure-docker "${{ vars.GCP_REGION }}-docker.pkg.dev" --quiet
          docker build -t "$IMAGE:$TAG" app
          docker push "$IMAGE:$TAG"

      - name: Deploy
        id: deploy
        uses: google-github-actions/deploy-cloudrun@2028e2d7d30a78c6910e0632e48dd561b064884d # v3
        with:
          service: ${{ vars.SERVICE }}
          region: ${{ vars.GCP_REGION }}
          image: ${{ env.IMAGE }}:${{ env.TAG }}

      - name: Check it is live
        env:
          URL: ${{ steps.deploy.outputs.url }}
        run: |
          curl -fs "$URL" | grep -q "${GITHUB_SHA:0:7}" \
            || { echo "::error::The live page is not showing this commit"; exit 1; }
          echo "### Live at $URL, tag $TAG" >> "$GITHUB_STEP_SUMMARY"
```

Commit to `main`. It goes red. **Read the red step, then wait.** After each fix
from the class, commit again. Expect three different reds before a green.

---

## Stage 3: a pull request (10 min, one red run)

Make a branch, change a word on the page, open a pull request to `main`.
Look at what the `deploy` job does. Red again. **Wait.**

---

## Stage 4: prove it (10 min)

Merge the pull request. A teammate approves the deploy (**Review deployments**
on the run). Open your team's URL: your commit, your name, your team.

---

## Stage 5: stretch, a rollback (20 min)

1. Copy `reference/rollback.yml` into `.github/workflows/`.
2. Make one more change and deploy it, so you have two versions.
3. **Actions, Rollback, Run workflow**, paste the **older** tag from that
   deploy's run summary (it looks like `a1b2c3d-12`). Approve it.
4. Refresh your URL. The old commit is back.

---

## Stuck?

`reference/pipeline-final.yml` is the finished pipeline. Try for five minutes
before you open it, then compare line by line.
