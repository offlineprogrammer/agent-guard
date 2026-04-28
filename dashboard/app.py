import streamlit as st
import pandas as pd
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from db.audit import init_db, get_all_logs

init_db()
st.set_page_config(page_title="AgentGuard", page_icon="🛡", layout="wide")
st.title("🛡 AgentGuard — AI Agent Identity Governance")
st.caption("Real-time audit trail · SailPoint-style policy engine · Every agent decision logged")

logs = get_all_logs()
if logs:
    df = pd.DataFrame(logs)

    # Metrics row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Decisions",  len(df))
    c2.metric("✅ Approved",       len(df[df.decision=="APPROVED"]))
    c3.metric("🚫 Denied",         len(df[df.decision=="DENIED"]))
    c4.metric("⚠️ Escalated",     len(df[df.decision=="ESCALATE"]))

    # Color-coded audit table
    st.subheader("📋 Audit Trail")
    def color_row(val):
        colors = {"APPROVED": "background-color:#052e16;color:#86efac",
                  "DENIED":   "background-color:#450a0a;color:#fca5a5",
                  "ESCALATE": "background-color:#431407;color:#fdba74"}
        return colors.get(val, "")

    cols = ["timestamp","user_id","resource","decision","policy_rule","reason","jit_expiry"]
    styled = df[cols].style.applymap(color_row, subset=["decision"])
    st.dataframe(styled, use_container_width=True, height=380)

    # Filter
    st.subheader("🔍 Filter by Outcome")
    f = st.selectbox("Show", ["ALL","APPROVED","DENIED","ESCALATE"])
    filtered = df if f=="ALL" else df[df.decision==f]
    st.dataframe(filtered[cols], use_container_width=True)
else:
    st.info("No records yet. Run `python main.py` first to generate decisions.")

st.button("🔄 Refresh", on_click=st.rerun)