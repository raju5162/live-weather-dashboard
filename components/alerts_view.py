"""
Weather Alerts Component
Displays color-coded severe weather warnings and atmospheric safety advisories.
"""

import streamlit as st

def render_alerts_view(data: dict):
    st.markdown("### ⚠️ Active Weather Alerts & Safety Advisories")

    alerts = data.get("alerts", [])

    if not alerts:
        st.markdown(
            """
            <div class="weather-card" style="border-left: 5px solid #00E676;">
                <h4 style="margin:0; color:#00E676;">✅ No Severe Weather Alerts Active</h4>
                <p style="margin-top:6px; font-size:0.95rem; color:#CBD5E1;">Atmospheric conditions are stable around the target region. Standard daily activity may proceed.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        for alert in alerts:
            severity = alert.get("severity", "Warning")
            card_class = "alert-card-danger" if severity.lower() in ["danger", "extreme"] else "alert-card-warning"
            icon = "🚨" if severity.lower() in ["danger", "extreme"] else "⚠️"
            
            st.markdown(
                f"""
                <div class="{card_class}">
                    <h4 style="margin:0;">{icon} {alert['type']} <span style="font-size:0.85rem; font-weight:normal;">({severity.upper()})</span></h4>
                    <p style="margin-top:8px; font-size:0.95rem;">{alert['message']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
