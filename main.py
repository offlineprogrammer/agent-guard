from db.audit import init_db, get_all_logs
from agents.provisioner import run_provisioner

if __name__ == "__main__":
    init_db()

    print("\n🔵 SCENARIO 1: Standard Onboarding — sarah.chen")
    print("─" * 60)
    run_provisioner(
        "Onboard sarah.chen as senior_engineer. Get her profile, "
        "determine required access for her role, and provision each "
        "resource. Current access list is empty. Risk score is 2."
    )

    print("\n🔴 SCENARIO 2: Rogue Agent — policy violation attempt")
    print("─" * 60)
    run_provisioner(
        "Provision prod_database access for john.doe. "
        "His role is engineer. Current access is []. Risk score is 7."
    )

    print("\n📋 AUDIT TRAIL — All Decisions")
    print("─" * 60)
    for log in get_all_logs():
        icon = "✅" if log["decision"] == "APPROVED" else ("⚠️" if log["decision"] == "ESCALATE" else "🚫")
        print(f"{icon} [{log['timestamp'][:19]}] {log['user_id']} → {log['resource']} | {log['decision']} | {log['policy_rule']}")

    print("\n💡 Run: streamlit run dashboard/app.py")