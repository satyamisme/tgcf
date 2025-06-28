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
    st.header("🔗 Connection Manager")
    
    # Top controls
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("➕ Add New Connection", use_container_width=True):
            CONFIG.forwards.append(Forward())
            write_config(CONFIG)
            st.experimental_rerun()
    
    active_count = sum(fwd.use_this for fwd in CONFIG.forwards)
    total_count = len(CONFIG.forwards)
    with col2:
        st.caption(f"Showing {total_count} connections ({active_count} active)")
    
    if total_count == 0:
        st.info("No connections found. Click 'Add New Connection' to create one!")
        st.stop()
    
    # Connection table
    for i, fwd in enumerate(CONFIG.forwards):
        # Create expandable container for each connection
        status = "🟢" if fwd.use_this else "🟡"
        default_name = f"Connection {i+1}"
        display_name = fwd.con_name or default_name
        
        with st.expander(f"{status} {display_name}", expanded=False):
            # Compact row with main controls
            cols = st.columns([0.1, 0.25, 0.25, 0.25, 0.15])
            with cols[0]:
                fwd.use_this = st.checkbox(
                    "Active", 
                    value=fwd.use_this,
                    key=f"active_{i}",
                    label_visibility="visible"
                )
            with cols[1]:
                fwd.con_name = st.text_input(
                    "Name",
                    value=fwd.con_name,
                    key=f"name_{i}",
                    placeholder=default_name,
                    label_visibility="collapsed"
                )
            with cols[2]:
                fwd.source = st.text_input(
                    "Source",
                    value=fwd.source,
                    key=f"source_{i}",
                    label_visibility="collapsed",
                    placeholder="Enter source"
                ).strip()
            with cols[3]:
                dest_text = st.text_area(
                    "Destinations",
                    value=get_string(fwd.dest),
                    key=f"dest_{i}",
                    height=60,
                    label_visibility="collapsed",
                    placeholder="One per line"
                )
                fwd.dest = get_list(dest_text)
            with cols[4]:
                if st.button("🗑️ Delete", 
                            key=f"del_{i}", 
                            use_container_width=True,
                            type="primary"):
                    del CONFIG.forwards[i]
                    write_config(CONFIG)
                    st.experimental_rerun()
            
            # Detailed settings (hidden by default)
            with st.expander("Advanced Settings", expanded=False):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.caption("Past Mode Configuration")
                    fwd.offset = st.number_input(
                        "Offset",
                        value=fwd.offset,
                        key=f"offset_{i}",
                        step=1
                    )
                    fwd.end = st.number_input(
                        "End",
                        value=fwd.end,
                        key=f"end_{i}",
                        step=1
                    )
                with col_b:
                    st.caption("Connection Info")
                    st.text(f"Source: {fwd.source or 'Not set'}")
                    st.text(f"Destinations: {len(fwd.dest)} configured")
                    if fwd.dest:
                        st.caption("\n".join(fwd.dest))
    
    # Save button at bottom
    if st.button("💾 Save All Changes", 
                use_container_width=True, 
                type="primary",
                disabled=not CONFIG.forwards):
        write_config(CONFIG)
        st.success("All connections updated!")
        time.sleep(1)
        st.experimental_rerun()
