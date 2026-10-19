"""
Google Gemini AI Assistant View for SEO Suite Pro:
- Secure in-session or encrypted profile API key storage (zero plain text storage)
- Executive 30-day SEO action plan generation
- High-CTR Title and Meta Description rewriter
- Keyword cannibalization differentiation and content briefs
- Rate limit (429) and invalid key handling
"""

import streamlit as st
from core.auth import get_current_user
from core.database import update_user_api_key
from core.security import decrypt_secret, encrypt_secret
from services.gemini_service import (
    generate_cannibalization_brief,
    generate_seo_action_plan,
    generate_title_meta_rewrites,
    test_gemini_key,
)
from views.components import render_footer, render_header, render_section_header

def render_gemini_view():
    render_header(subtitle="Google Gemini AI Strategic Assistant")
    user = get_current_user()
    
    # ── 1. API Key Configuration & Security ─────────────────────────
    render_section_header("API Key Management", "Enter your Google AI Studio Gemini API Key (Free Tier)")
    
    # Retrieve existing key from session or decrypted profile
    current_key = st.session_state.get("gemini_api_key", "")
    if not current_key and user and user.get("encrypted_api_key"):
        current_key = decrypt_secret(user["encrypted_api_key"])
        if current_key:
            st.session_state["gemini_api_key"] = current_key
            
    col_k1, col_k2 = st.columns([3, 1])
    with col_k1:
        masked_val = ("•" * 28 + current_key[-4:]) if current_key else ""
        key_input = st.text_input(
            "Gemini API Key",
            value=masked_val if current_key else "",
            type="password",
            placeholder="AIzaSy...",
            help="Get your free API key at https://aistudio.google.com/app/apikey"
        )
    with col_k2:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            save_key_btn = st.button("Save Key", type="primary", use_container_width=True)
        with col_btn2:
            clear_key_btn = st.button("Clear", use_container_width=True)
            
    if clear_key_btn:
        st.session_state.pop("gemini_api_key", None)
        if user:
            update_user_api_key(user["id"], "")
        st.success("API key cleared from session and profile.")
        st.rerun()
        
    if save_key_btn:
        if not key_input or key_input.startswith("••••"):
            st.warning("Please enter a new API key string.")
        else:
            with st.spinner("Validating API key with Google AI Studio..."):
                is_valid, msg = test_gemini_key(key_input)
                if is_valid:
                    st.session_state["gemini_api_key"] = key_input.strip()
                    if user:
                        enc = encrypt_secret(key_input.strip())
                        update_user_api_key(user["id"], enc)
                    st.success("Gemini API key validated and securely stored in encrypted profile.")
                    st.rerun()
                else:
                    st.error(msg)
                    
    active_key = st.session_state.get("gemini_api_key", "")
    if not active_key:
        st.info("AI features are optional. All technical crawling and Search Console analysis functions remain 100% active without an API key.")
        render_footer()
        return
        
    # ── 2. AI Capabilities Workspace ────────────────────────────────
    render_section_header("AI Strategy Workflows", "Generate plain-language recommendations and prioritized roadmaps")
    
    tab_plan, tab_rewriter, tab_cannibal = st.tabs([
        "Executive 30-Day Action Plan",
        "High-CTR Title & Snippet Rewriter",
        "Cannibalization Differentiation Brief"
    ])
    
    # Check active data
    gsc_data = st.session_state.get("active_gsc_analysis", {}).get("results", {})
    onpage_data = st.session_state.get("active_onpage_audit", {})
    
    with tab_plan:
        st.markdown("""
        <div style="font-size:12px;color:#A0A0A0;margin-bottom:12px;">
            Synthesize all active On-Page DOM issues and Search Console findings into a structured, executive 30-day technical SEO action plan.
        </div>
        """, unsafe_allow_html=True)
        
        if not gsc_data and not onpage_data:
            st.warning("Run an On-Page Audit or Search Console Analysis first to generate data for the action plan.")
        else:
            if st.button("Generate Executive 30-Day Plan", type="primary"):
                with st.spinner("Consulting Google Gemini AI for technical diagnosis..."):
                    summary = gsc_data.get("summary", {}) if gsc_data else {"target_url": onpage_data.get("target_url")}
                    top_issues = gsc_data.get("issues", []) if gsc_data else [{"issue": d} for d in onpage_data.get("pages", [{}])[0].get("deductions", [])]
                    plan = generate_seo_action_plan(active_key, summary, top_issues)
                    st.session_state["gemini_saved_plan"] = plan
                    
            saved_plan = st.session_state.get("gemini_saved_plan")
            if saved_plan:
                st.markdown(f"""
                <div class="glass-card" style="padding:24px;border-left:4px solid #D4AF37;">
                    {saved_plan}
                </div>
                """, unsafe_allow_html=True)
                
    with tab_rewriter:
        st.markdown("#### High-Converting Title & Meta Description Generator")
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            q_in = st.text_input("Target Query", placeholder="e.g. technical seo audit checklist")
            t_in = st.text_input("Current Title Tag", placeholder="e.g. SEO Audit Checklist - Example Site")
        with col_w2:
            m_in = st.text_area("Current Meta Description", placeholder="e.g. Read our seo audit checklist to improve your ranking.")
            intent_in = st.selectbox("Search Intent", ["Commercial / Transactional", "Informational", "Comparison / Investigative"])
            
        if st.button("Generate 3 High-CTR Options", type="primary", use_container_width=True):
            if not q_in:
                st.error("Please specify a target query.")
            else:
                with st.spinner("Generating CTR-optimized variations..."):
                    rewrites = generate_title_meta_rewrites(active_key, q_in, t_in, m_in, intent_in)
                    st.markdown(f"""
                    <div class="glass-card" style="padding:20px;border-left:3px solid #D4AF37;margin-top:16px;">
                        {rewrites}
                    </div>
                    """, unsafe_allow_html=True)
                    
    with tab_cannibal:
        st.markdown("#### Intent Disambiguation & Cannibalization Brief")
        c_query = st.text_input("Cannibalized Query", placeholder="e.g. best enterprise seo platform")
        c_prim = st.text_input("Primary Target URL", placeholder="https://example.com/platform")
        c_sec = st.text_area("Secondary Competing URLs (one per line)", placeholder="https://example.com/blog/best-seo-platforms\nhttps://example.com/pricing")
        
        if st.button("Generate Differentiation Brief", type="primary", use_container_width=True):
            if not c_query or not c_prim:
                st.error("Please provide both query and primary URL.")
            else:
                sec_list = [s.strip() for s in c_sec.splitlines() if s.strip()]
                with st.spinner("Formulating technical disambiguation protocol..."):
                    brief = generate_cannibalization_brief(active_key, c_query, c_prim, sec_list)
                    st.markdown(f"""
                    <div class="glass-card" style="padding:20px;border-left:3px solid #D4AF37;margin-top:16px;">
                        {brief}
                    </div>
                    """, unsafe_allow_html=True)
                    
    render_footer()
