import argparse
from core import RunEverytimeAutoLike

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Main Entry Point")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command to run")\
    
    # Everytime
    everytime_parser = subparsers.add_parser("everytime", help="Run Everytime auto-like")
    everytime_parser.add_argument("--headless", action="store_true", help="Run in headless mode")

    # 실행
    args = parser.parse_args()

    if args.command == "everytime":
        RunEverytimeAutoLike(headless=args.headless)
    else:
        parser.print_help()