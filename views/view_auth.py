"""
Authentication View: Sign In & Registration Portal
Strict gold, black, and white design with logo and bcrypt authentication.
"""

import streamlit as st
from core.database import authenticate_user, register_user
from core.auth import login_user
from views.components import get_logo_base64, render_footer

def render_auth_view():
    """Renders the login and registration interface."""
    logo_uri = get_logo_base64()
    
    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
    
    col_l, col_center, col_r = st.columns([1, 1.8, 1])
    with col_center:
        st.markdown(f"""
        <div style="text-align:center;padding:24px 20px 16px;background:#141414;border:1px solid rgba(212,175,55,0.3);border-radius:12px;margin-bottom:20px;">
            {'<img src="' + logo_uri + '" style="width:64px;height:64px;border-radius:12px;border:1px solid #D4AF37;margin-bottom:12px;object-fit:cover;" />' if logo_uri else ''}
            <div style="font-family:'Poppins',sans-serif;font-size:24px;font-weight:800;color:#D4AF37;">SEO Suite Pro</div>
            <div style="font-size:12px;color:#A0A0A0;margin-top:4px;">Enterprise Technical SEO & Organic Intelligence Platform</div>
            <div style="font-size:11px;color:#D4AF37;margin-top:2px;">Built by Ismail El Asiouty</div>
        </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])
        
        with tab_login:
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            with st.form("login_form"):
                ident = st.text_input("Username or Email", placeholder="user@example.com")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In to SEO Suite Pro", type="primary", use_container_width=True)
                
                if submit:
                    if not ident or not password:
                        st.error("Please provide both username/email and password.")
                    else:
                        user = authenticate_user(ident, password)
                        if user:
                            login_user(user)
                            st.success(f"Welcome back, {user['username']}!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Please verify username and password.")
                            
        with tab_register:
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            with st.form("register_form"):
                new_username = st.text_input("Desired Username", placeholder="e.g. johndoe")
                new_email = st.text_input("Email Address", placeholder="john@example.com")
                new_password = st.text_input("Password", type="password", help="At least 6 characters")
                reg_submit = st.form_submit_button("Create Private Account", use_container_width=True)
                
                if reg_submit:
                    ok, msg = register_user(new_username, new_email, new_password)
                    if ok:
                        st.success("Account created successfully. You can now sign in.")
                    else:
                        st.error(msg)
                        
    render_footer()
