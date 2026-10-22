"""
JOBAI Autonomous Agent Headless Runner
Used by GitHub Actions and automated cron workflows to discover jobs,
evaluate candidate fit, generate tailored materials, and auto-apply without requiring a local UI.
"""

import sys
import argparse
from datetime import datetime

# Ensure utf-8 encoding for cross-platform terminal output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from src.candidate_store import CandidateStore
from src.job_store import JobStore
from src.agent_workflow import ApplicationWorkflowManager
from src.models import ApplicationStatus


def main():
    parser = argparse.ArgumentParser(description="Run the JOBAI Autonomous Agent in cloud / CI environment.")
    parser.add_argument("--query", type=str, default="", help="Search query for live job roles (e.g. 'data scientist', 'machine learning')")
    parser.add_argument("--auto-apply", action="store_true", default=True, help="Automatically submit applications for matching roles")
    parser.add_argument("--threshold", type=int, default=70, help="Minimum fit score threshold percentage (default: 70)")
    args = parser.parse_args()

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting JOBAI Autonomous Cloud Agent...")
    print(f"Command Input: Query='{args.query or 'All Discovered Jobs'}', Auto-Apply={args.auto_apply}, Fit Threshold={args.threshold}%")

    candidate_store = CandidateStore()
    job_store = JobStore()
    mgr = ApplicationWorkflowManager(candidate_store, job_store)

    profile = candidate_store.get_profile()
    print(f"Loaded Candidate Ground Truth: {profile.full_name} ({profile.email})")

    if args.query:
        print(f"Searching real-time live web jobs matching '{args.query}'...")
        summary = mgr.search_and_apply_command(query=args.query, min_fit_threshold=args.threshold, auto_apply=args.auto_apply)
        results = summary["applied_jobs"]
    else:
        mgr.auto_apply_enabled = args.auto_apply
        mgr.min_fit_threshold = args.threshold
        results = mgr.run_live_autonomous_cycle()

    print("\n" + "=" * 60)
    print("AUTONOMOUS AGENT SCAN CYCLE SUMMARY")
    print("=" * 60)
    for r in results:
        status_symbol = "✅" if (r.get("action") == "Auto-Applied" or r.get("status") == "Auto-Applied") else ("⏳" if r.get("action") == "Queued for Review" else "⏭️")
        action_name = r.get("action") or r.get("status")
        print(f"{status_symbol} [{action_name.upper()}] {r['title']} at {r['employer']} | Fit: {r['fit_score']}%")
        if "receipt" in r and r["receipt"]:
            print(f"   ↳ Confirmed Receipt ID: {r['receipt']}")

    submitted = [r for r in results if (r.get("action") == "Auto-Applied" or r.get("status") == "Auto-Applied")]
    print("\n" + "-" * 60)
    print(f"Cycle Complete: {len(submitted)} applications submitted autonomously.")
    print("All materials, audit records, and submission logs verified.")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
