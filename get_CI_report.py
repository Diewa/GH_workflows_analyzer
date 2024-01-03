import argparse
import requests

# get arguments
gh_analyzer = argparse.ArgumentParser(description='analyze gh actions history')
gh_analyzer.add_argument('--token', '-token', required=True, help='Your GH token.')
gh_analyzer.add_argument('--owner', '-owner', required=True, help='The owner of repository you want to analyze.')
gh_analyzer.add_argument('--repo', '-repo', required=True, help='The name of repository you want to analyze.')
gh_analyzer.add_argument('--action', '-action', required=True, help='The name of workflow you want to analyze.')
gh_analyzer.add_argument('--limit', '-limit', required=True, help='Number of workflows you want to analyze')
gh_analyzer.add_argument('--date_oldest', '-date_oldest', required=True, help='Date range - the oldest workflow')
gh_analyzer.add_argument('--list_workflows', '-list_workflows', required=False, help='optional argument, true/false - list all included workflows')

arguments = gh_analyzer.parse_args()
token = arguments.token
owner = arguments.owner
repo = arguments.repo
action = arguments.action
date_oldest = arguments.date_oldest
list_workflows = False if arguments.list_workflows == '' else  arguments.list_workflows == 'true'
limit = 100 if arguments.limit == '' else int(arguments.limit)

print(f'script started with arguments: owner: {owner}, repo: {repo}, action: {action}, limit: {limit}', 'from date: ', date_oldest)

# global variables
git_header = headers = {'Authorization': f'Bearer {token}'}


def get_all_workflows():
    current_page = 1
    number_of_workflows_in_response = 1
    response_workflows = []
    workflows_ids = []

    # get all x or all workflows
    while len(response_workflows) <= limit and number_of_workflows_in_response > 0:
        url = f'http://api.github.com/repos/{owner}/{repo}/actions/runs?per_page=100&page={current_page}&event=push&created=>={date_oldest}'
        actions_response = requests.get(url, headers=git_header)
        workflow_runs = actions_response.json()['workflow_runs']

        number_of_workflows_in_response = len(workflow_runs)
        current_page += 1

        # filter workflows
        for workflow in workflow_runs:
            if workflow['name'] == action and workflow['id'] not in workflows_ids and workflow['head_branch'] == 'master' and len(response_workflows) < limit:
                response_workflows.append(workflow)
                # print('created_at', workflow['created_at'], 'id: ', workflow['id'], 'event: ', workflow['event'])

    return response_workflows


def get_status_for_every_attempt(workflows):
    conclusions = []
    for run in workflows:
        run_attempt = run['run_attempt']
        run_id = run['id']
        # there was more than one attempt for following workflow
        if run_attempt > 1:
            for attempt in range(1, run_attempt + 1):
                response = requests.get(
                    f'http://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/attempts/{attempt}',
                    headers=git_header)
                body = response.json()
                conclusions.append(body['conclusion'])
        else:
            conclusions.append(run['conclusion'])

    return conclusions


def print_summary(attempt_statuses):
    success_statuses = ['completed', 'success']
    failed_statuses = ['action_required', 'failure', 'stale', 'timed_out']
    ignored_statuses = ['cancelled', 'neutral', 'skipped', 'in_progress', 'queued', 'requested', 'waiting', 'pending']
    attempts_number = len(attempt_statuses)

    print(f'for given {limit} workflows, script analyzed {attempts_number} workflows attempts')

    count_status_occurrences = lambda attempt_statuses: {
        "success": sum(1 for status in attempt_statuses if status in success_statuses),
        "failed": sum(1 for status in attempt_statuses if status in failed_statuses),
        "ignored": sum(1 for status in attempt_statuses if status in ignored_statuses)
    }
    statuses = count_status_occurrences(attempt_statuses)
    print(
        f'Number of success: {statuses["success"]}, number of failed: {statuses["failed"]}, number of ignored: {statuses["ignored"]}')

def list_included_workflows(included_workflows):
    print("list of all included workflows")
    for workflow in included_workflows:
        print('workflow_id: ', workflow['id'], 'workflow_url: ', workflow['url'])

workflows = get_all_workflows()
attempt_statuses = get_status_for_every_attempt(workflows)
print_summary(attempt_statuses)

if list_workflows:
    list_included_workflows(workflows)
