# Ship it: your team's pipeline

By the end, a change merged to `main` in **your** repo goes through tests, waits
for a teammate to approve, deploys to **your team's own URL**, and checks it is
live. Then you give it a rollback.

First you ship the working pipeline. Then you explain it, line by line, in your
own comments. Then you **break it on purpose**, four times, and read what goes red.

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

   Values for your team: [TEAMS.md](https://github.com/Greyisheep/gh-200-team-app/blob/main/TEAMS.md).

   None of these are secrets. That is the point of the keyless login: there is
   no password to store.

4. **Settings, Environments, New environment**, name it exactly `production`.
   - Tick **Required reviewers** and add a **teammate** (not yourself).
   - **Deployment branches and tags: Selected branches**, add `main`.

Your team's URL: `https://gh200-team-<n>-130785602363.europe-west1.run.app`
Open it now. You will see a placeholder until your first deploy.

---

## Stage 1: ship it (15 min)

1. Copy the whole of `reference/pipeline-final.yml` into
   `.github/workflows/pipeline.yml`, replacing what is there. Commit to `main`.
2. Open the **Actions** tab. The test job goes green, then the deploy job
   **waits**.
3. Your teammate opens the run, clicks **Review deployments**, ticks
   `production`, approves.
4. Open your team's URL. Your team, your commit, your name.

Stuck? The end-to-end explanation is
[PIPELINE-EXPLAINED.md](https://github.com/Greyisheep/gh-200-team-app/blob/main/PIPELINE-EXPLAINED.md).

---

## Stage 2: explain it, in your own comments (25 min)

In your `.github/workflows/pipeline.yml`, add a `#` comment **above every block
and every step** saying, in your own words:

- **what** it does
- **why** it is there
- **what would go wrong** without it

Cover at least these, in detail:

| Block | Questions your comment must answer |
|---|---|
| `on:` | Which events start this, and why both pull_request and push? |
| `permissions:` (top) | What can the token do, and why so little? |
| `concurrency:` (top and deploy) | What gets cancelled, what never does, and why? |
| `env: IMAGE` | Where does each part of the name come from? |
| test job `outputs:` | Why does the tag have to be published from the job? |
| each test step | What does it check, and what would make it go red? |
| `needs:` and `if:` | When does deploy run, and when is it skipped? |
| `environment:` | What two things does it do, one on GitHub and one for Google? |
| `permissions: id-token: write` | What token does it allow, and who checks it? |
| `env: TAG` | Read the chain `needs.test.outputs.tag` out loud, dot by dot |
| each deploy step | What happens, and on which machine? |

Commit it. It deploys again, with comments. A teammate approves.

---

## Stage 3: break it on purpose (30 min)

One break at a time. For each: make the edit, commit to `main`, approve if it
asks, **read the red step**, write down what it means, then **undo the edit and
commit** before the next one.

| Break | Edit in `.github/workflows/pipeline.yml` | Expect |
|---|---|---|
| 1 | In `deploy`, delete the line `id-token: write` | *did not inject $ACTIONS_ID_TOKEN_REQUEST_TOKEN* |
| 2 | In `deploy`, delete the three `environment:` lines | *rejected by the attribute condition* |
| 3 | In `test`, last step: change `$GITHUB_OUTPUT` to `$GITHUB_ENV` | *invalid tag ".../frontend:"* |
| 4 | On a **new branch**, delete the `if:` line from `deploy`, then open a pull request | *not allowed to deploy to production* |

After each one, add a comment to the line you broke saying what happened
without it.

---

## Stage 4: stretch, a rollback (20 min)

1. Copy `reference/rollback.yml` into `.github/workflows/`.
2. Make one more change and deploy it, so you have two versions.
3. **Actions, Rollback, Run workflow**, paste the **older** tag from that
   deploy's run summary (it looks like `a1b2c3d-12`). Approve it.
4. Refresh your URL. The old commit is back.

---

## Done when

- Your URL shows your team and your latest commit.
- Your pipeline file has a comment on every block, in your own words.
- You have seen all four reds, and your file is green again.
