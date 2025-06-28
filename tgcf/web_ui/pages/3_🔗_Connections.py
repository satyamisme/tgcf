import time
import streamlit as st
from tgcf.config import CONFIG, Forward, read_config, write_config
from tgcf.web_ui.password import check_password
from tgcf.web_ui.utils import get_list, get_string, hide_st, switch_theme

CONFIG = read_config()

st.set_page_config(
    page_title="Connections",
    page_icon="🔗",
)
hide_st(st)
switch_theme(st, CONFIG)

if check_password(st):
    st.header("Manage Connections")
    add_new = st.button("➕ Add new connection")
    if add_new:
        CONFIG.forwards.append(Forward())
        write_config(CONFIG)
        st.experimental_rerun()

    num = len(CONFIG.forwards)

    if num == 0:
        st.info("No connections found. Click 'Add new connection' to create one!")
    else:
        # Status summary header
        active_count = sum(fwd.use_this for fwd in CONFIG.forwards)
        st.subheader(f"Connections: {active_count} active / {num} total")

        for i, forward in enumerate(CONFIG.forwards):
            # Connection header with status
            status = "🟢" if forward.use_this else "🟡"
            default_name = f"Connection {i+1}"
            con_name = forward.con_name or default_name
            expander = st.expander(f"{status} {con_name}", expanded=True)
            
            with expander:
                cols = st.columns([0.4, 0.3, 0.3])
                with cols[0]:
                    forward.con_name = st.text_input(
                        "Connection name",
                        value=forward.con_name,
                        key=f"name_{i}",
                        placeholder=default_name
                    )
                with cols[1]:
                    forward.use_this = st.checkbox(
                        "Active",
                        value=forward.use_this,
                        key=f"active_{i}"
                    )
                with cols[2]:
                    st.write("")  # Spacer
                    if st.button("🗑️ Delete", key=f"del_{i}", use_container_width=True):
                        del CONFIG.forwards[i]
                        write_config(CONFIG)
                        st.experimental_rerun()

                # Source and Destination
                st.subheader("Routing")
                c1, c2 = st.columns(2)
                with c1:
                    forward.source = st.text_input(
                        "Source",
                        value=forward.source,
                        key=f"source_{i}",
                        help="Only one source allowed per connection"
                    ).strip()
                with c2:
                    dests = st.text_area(
                        "Destinations",
                        value=get_string(forward.dest),
                        key=f"dest_{i}",
                        height=100,
                        help="One destination per line"
                    )
                    forward.dest = get_list(dests)

                # Past Mode Settings
                st.subheader("Past Mode Settings")
                c1, c2 = st.columns(2)
                with c1:
                    forward.offset = st.number_input(
                        "Offset",
                        value=forward.offset,
                        key=f"offset_{i}",
                        step=1
                    )
                with c2:
                    forward.end = st.number_input(
                        "End",
                        value=forward.end,
                        key=f"end_{i}",
                        step=1
                    )
                
                st.divider()

        # Save button at bottom
        if st.button("💾 Save All Changes", use_container_width=True, type="primary"):
            write_config(CONFIG)
            st.success("All connections updated!")
            time.sleep(1)
            st.experimental_rerun()
