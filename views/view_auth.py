"""
Authentication View: Sign In & Registration Portal
Strict gold, black, and white design with logo and bcrypt authentication.
Bilingual support (English & Arabic) and Light/Dark mode compatible.
"""

import streamlit as st
from core.auth import login_user
from core.config import BRAND_NAME, BRAND_OWNER
from core.database import authenticate_user, register_user
from core.i18n import get_current_lang, t
from views.components import get_logo_base64, render_footer

def render_auth_view():
    """Renders the login and registration interface."""
    lang = get_current_lang()
    is_ar = (lang == "ar")
    logo_uri = get_logo_base64()
    
    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
    
    col_l, col_center, col_r = st.columns([1, 1.8, 1])
    with col_center:
        st.markdown(f"""
        <div style="text-align:center;padding:24px 20px 16px;background:var(--bg-surface);border:1px solid var(--gold-border);border-radius:12px;margin-bottom:20px;box-shadow:var(--shadow-card);">
            {'<img src="' + logo_uri + '" style="width:64px;height:64px;border-radius:12px;border:1px solid var(--gold);margin-bottom:12px;object-fit:cover;box-shadow:0 2px 10px var(--gold-tint);" />' if logo_uri else ''}
            <div style="font-family:'Poppins','Cairo',sans-serif;font-size:24px;font-weight:800;color:var(--gold);">{BRAND_NAME}</div>
            <div style="font-size:12px;color:var(--text-muted);margin-top:4px;">{t('auth_welcome_sub')}</div>
            <div style="font-size:11px;color:var(--gold);margin-top:4px;">{t('built_by')} {BRAND_OWNER}</div>
        </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs([t("auth_signin_tab"), t("auth_register_tab")])
        
        with tab_login:
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            with st.form("login_form"):
                ident = st.text_input(t("auth_ident_label"), placeholder="user@example.com")
                password = st.text_input(t("auth_pass_label"), type="password")
                submit = st.form_submit_button(t("auth_signin_btn"), type="primary", use_container_width=True)
                
                if submit:
                    if not ident or not password:
                        msg = "يرجى إدخال اسم المستخدم/البريد وكلمة المرور." if is_ar else "Please provide both username/email and password."
                        st.error(msg)
                    else:
                        user = authenticate_user(ident, password)
                        if user:
                            login_user(user)
                            welcome_msg = f"أهلاً بك مجدداً، {user['username']}!" if is_ar else f"Welcome back, {user['username']}!"
                            st.success(welcome_msg)
                            st.rerun()
                        else:
                            err_msg = "بيانات الدخول غير صحيحة. يرجى التأكد من اسم المستخدم وكلمة المرور." if is_ar else "Invalid credentials. Please verify username and password."
                            st.error(err_msg)
                            
        with tab_register:
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            with st.form("register_form"):
                new_username = st.text_input(t("auth_username_label"), placeholder="e.g. johndoe")
                new_email = st.text_input(t("auth_email_label"), placeholder="john@example.com")
                new_password = st.text_input(t("auth_pass_label"), type="password", help="At least 6 characters" if not is_ar else "6 أحرف على الأقل")
                reg_submit = st.form_submit_button(t("auth_create_btn"), use_container_width=True)
                
                if reg_submit:
                    ok, msg = register_user(new_username, new_email, new_password)
                    if ok:
                        succ = "تم إنشاء الحساب بنجاح. يمكنك الآن تسجيل الدخول." if is_ar else "Account created successfully. You can now sign in."
                        st.success(succ)
                    else:
                        st.error(msg)
                        
    render_footer()
