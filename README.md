# GH_workflows_analyzer
simple scripts to analyze your GH workflows


## Scripts 

### get_CI_report.py
This script will allow you to fetch information about the workflow from your repository and returns the number of workflows that have succeeded or failed.

> get_CI_report.py -token {GH_token} -owner repoOwner-repo repoName -action actionName -limit 100

```
> script started with arguments: owner: allegro, repo: hermes, action: CI, limit: 100
> for given 100 workflows, script analyzed 176 workflows attempts
> Number of success: 24, number of failed: 139, number of ignored: 13
```