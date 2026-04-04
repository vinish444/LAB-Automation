import argparse
import json
import requests


def main():
    parser = argparse.ArgumentParser(description="NetAuto CLI")
    sub = parser.add_subparsers(dest="action", required=True)

    run_cmd = sub.add_parser("run", help="Submit command job")
    run_cmd.add_argument("--command", action="append", dest="commands", default=[])
    run_cmd.add_argument("--parser", default="raw")
    run_cmd.add_argument("--host", action="append", dest="hosts", default=[])
    run_cmd.add_argument("--group", action="append", dest="groups", default=[])
    run_cmd.add_argument("--api-url", default="http://127.0.0.1:8000")
    run_cmd.add_argument("--real", action="store_true", help="Use real SSH instead of mock mode")

    status_cmd = sub.add_parser("status", help="Check job status")
    status_cmd.add_argument("job_id")
    status_cmd.add_argument("--api-url", default="http://127.0.0.1:8000")

    result_cmd = sub.add_parser("result", help="Get job result")
    result_cmd.add_argument("job_id")
    result_cmd.add_argument("--api-url", default="http://127.0.0.1:8000")

    args = parser.parse_args()

    if args.action == "run":
        if not args.commands:
            parser.error("At least one --command is required for run")
        payload = {
            "commands": args.commands,
            "parser": args.parser,
            "mock": not args.real,
            "inventory": {
                "hosts": args.hosts or None,
                "groups": args.groups or None,
            },
        }
        response = requests.post(f"{args.api_url}/run", json=payload, timeout=30)
    elif args.action == "status":
        response = requests.get(f"{args.api_url}/status/{args.job_id}", timeout=30)
    else:
        response = requests.get(f"{args.api_url}/result/{args.job_id}", timeout=30)

    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    main()
