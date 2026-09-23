"""Write build facts into the page.

Values arrive as environment variables, never pasted into a shell command, so
nothing a person typed (a branch name, a banner) can become part of a script.
"""
import datetime
import html
import os

PAGE = "app/index.html"
values = {
    "__TEAM__": os.environ.get("TEAM") or "Your team",
    "__SHA__": os.environ.get("SHA", "local")[:7],
    "__ACTOR__": os.environ.get("ACTOR", "someone"),
    "__ENV__": os.environ.get("DEPLOY_ENV", "local"),
    "__BANNER__": os.environ.get("BANNER") or "Deployed by GitHub Actions",
    "__TIME__": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
}
text = open(PAGE, encoding="utf-8").read()
for key, value in values.items():
    text = text.replace(key, html.escape(value))
open(PAGE, "w", encoding="utf-8").write(text)
print("stamped:", {k: v for k, v in values.items() if k != "__BANNER__"})
