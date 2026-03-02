"""
doc_intelligence.py — AI Document Intelligence (Mockup)
Text area for lease clause → mock structured extraction.
"""

import streamlit as st
import json
import time

from data import MOCK_LEASE_CLAUSE, MOCK_AI_EXTRACTION
from style import section_header, ACCENT, CARD_BG, TEXT, RED, YELLOW


def render():
    """Main render function for the Document Intelligence page."""

    section_header("AI Document Intelligence")

    st.markdown(
        "Paste a lease clause below and let **Deeply AI** extract structured data instantly.  \n"
        "_This is a live mockup demonstrating the extraction pipeline._"
    )

    # ── Text Input ──────────────────────────────
    clause_text = st.text_area(
        "📄 Lease Clause Input",
        value=MOCK_LEASE_CLAUSE,
        height=160,
        placeholder="Paste lease text here…",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        analyze_btn = st.button("🔍 Analyze with Deeply AI", type="primary", use_container_width=True)

    # ── Analysis Output ─────────────────────────
    if analyze_btn:
        if not clause_text.strip():
            st.warning("Please paste a lease clause to analyze.")
            return

        # Fake processing spinner
        with st.spinner("Deeply AI is analyzing the document…"):
            time.sleep(1.8)

        st.success("✅ Analysis complete — 3 key fields extracted.")

        # ── Structured Output ───────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        section_header("Extracted Intelligence")

        # Key fields as metric cards
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div style="background:{CARD_BG}; border-left:4px solid {ACCENT};
                        border-radius:8px; padding:18px 22px; margin:4px 0;">
                <div style="font-size:0.78rem; color:#808080; text-transform:uppercase;
                            letter-spacing:1px; margin-bottom:4px;">Expiration Date</div>
                <div style="font-size:1.5rem; font-weight:700; color:#FFFFFF;">
                    {MOCK_AI_EXTRACTION["extracted_fields"]["expiration_date"]}</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div style="background:{CARD_BG}; border-left:4px solid {ACCENT};
                        border-radius:8px; padding:18px 22px; margin:4px 0;">
                <div style="font-size:0.78rem; color:#808080; text-transform:uppercase;
                            letter-spacing:1px; margin-bottom:4px;">Index Linkage</div>
                <div style="font-size:1.1rem; font-weight:700; color:#FFFFFF;">
                    {MOCK_AI_EXTRACTION["extracted_fields"]["index_linkage"]}</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div style="background:{CARD_BG}; border-left:4px solid {ACCENT};
                        border-radius:8px; padding:18px 22px; margin:4px 0;">
                <div style="font-size:0.78rem; color:#808080; text-transform:uppercase;
                            letter-spacing:1px; margin-bottom:4px;">Renewal Option</div>
                <div style="font-size:1.1rem; font-weight:700; color:#FFFFFF;">
                    {MOCK_AI_EXTRACTION["extracted_fields"]["renewal_option"]}</div>
            </div>
            """, unsafe_allow_html=True)

        # Full JSON output
        st.markdown("<br>", unsafe_allow_html=True)
        section_header("Full AI Extraction (JSON)")

        json_str = json.dumps(MOCK_AI_EXTRACTION, indent=2, ensure_ascii=False)
        st.markdown(f"""
        <div style="background:{CARD_BG}; border:1px solid {ACCENT}; border-radius:8px;
                    padding:20px; font-family:'Courier New',monospace; font-size:0.85rem;
                    color:{ACCENT}; white-space:pre-wrap; overflow-x:auto;">
{json_str}
        </div>
        """, unsafe_allow_html=True)

        # Risk flags
        if MOCK_AI_EXTRACTION.get("risk_flags"):
            st.markdown("<br>", unsafe_allow_html=True)
            section_header("Risk Flags Detected")
            for flag in MOCK_AI_EXTRACTION["risk_flags"]:
                st.markdown(f"""
                <div style="background:rgba(255,75,75,0.10); border-left:4px solid {RED};
                            border-radius:6px; padding:12px 16px; margin:6px 0; color:{TEXT};">
                    ⚠ {flag}
                </div>
                """, unsafe_allow_html=True)
