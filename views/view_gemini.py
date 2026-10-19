"""
Google Gemini AI Assistant View for SEO Suite Pro:
- Secure in-session or encrypted profile API key storage (zero plain text storage)
- Executive 30-day SEO action plan generation
- High-CTR Title and Meta Description rewriter
- Keyword cannibalization differentiation and content briefs
- Rate limit (429) and invalid key handling
- Bilingual English & Arabic with dynamic theme variables
"""

import streamlit as st
from core.auth import get_current_user
from core.database import update_user_api_key
from core.i18n import get_current_lang, t
from core.security import decrypt_secret, encrypt_secret
from services.gemini_service import (
    generate_cannibalization_brief,
    generate_seo_action_plan,
    generate_title_meta_rewrites,
    test_gemini_key,
)
from views.components import (
    get_gemini_logo_svg,
    render_footer,
    render_header,
    render_section_header,
)

def render_gemini_view():
    lang = get_current_lang()
    is_ar = (lang == "ar")
    
    render_header(subtitle=t("ai_header"))
    user = get_current_user()
    
    # ── 1. API Key Configuration & Security ─────────────────────────
    render_section_header("API Key Management" if not is_ar else "إدارة مفتاح الذكاء الاصطناعي", t("ai_key_label"))
    
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
            t("ai_key_label"),
            value=masked_val if current_key else "",
            type="password",
            placeholder=t("ai_key_placeholder"),
            help="Get your free API key at https://aistudio.google.com/app/apikey"
        )
    with col_k2:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            save_key_btn = st.button(t("ai_save_key"), type="primary", use_container_width=True)
        with col_btn2:
            clear_key_btn = st.button(t("ai_clear_key"), use_container_width=True)
            
    if clear_key_btn:
        st.session_state.pop("gemini_api_key", None)
        if user:
            update_user_api_key(user["id"], "")
        msg = "تم حذف مفتاح API من الجلسة والملف الشخصي." if is_ar else "API key cleared from session and profile."
        st.success(msg)
        st.rerun()
        
    if save_key_btn:
        if not key_input or key_input.startswith("••••"):
            warn = "يرجى كتابة أو لصق مفتاح API صحيح." if is_ar else "Please enter a new API key string."
            st.warning(warn)
        else:
            with st.spinner("Validating API key with Google AI Studio..."):
                is_valid, msg = test_gemini_key(key_input)
                if is_valid:
                    st.session_state["gemini_api_key"] = key_input.strip()
                    if user:
                        enc = encrypt_secret(key_input.strip())
                        update_user_api_key(user["id"], enc)
                    st.success(t("ai_saved_success"))
                    st.rerun()
                else:
                    st.error(msg)
                    
    active_key = st.session_state.get("gemini_api_key", "")
    if not active_key:
        st.info(t("ai_no_key_notice"))
        render_footer()
        return
        
    # ── 2. AI Capabilities Workspace ────────────────────────────────
    gem_svg = get_gemini_logo_svg(22)
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin:20px 0 10px;">
        {gem_svg}
        <span style="font-family:'Poppins','Cairo',sans-serif;font-size:16px;font-weight:700;color:var(--gold);">
            {'Google Gemini 2.5 Flash / Pro Intelligence Workspace' if not is_ar else 'مساحة العمل الاستراتيجية بنموذج Google Gemini'}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    tab_plan, tab_rewriter, tab_cannibal = st.tabs([
        t("ai_tab_plan"),
        t("ai_tab_rewriter"),
        t("ai_tab_cannibal")
    ])
    
    # Check active data
    gsc_data = st.session_state.get("active_gsc_analysis", {}).get("results", {})
    onpage_data = st.session_state.get("active_onpage_audit", {})
    
    with tab_plan:
        st.markdown(f"""
        <div style="font-size:12px;color:var(--text-muted);margin-bottom:12px;">
            {t('ai_plan_desc')}
        </div>
        """, unsafe_allow_html=True)
        
        if not gsc_data and not onpage_data:
            warn = "قم بإجراء فحص داخلي أو تحليل سيرش كونسول أولاً لتغذية خطة العمل بالبيانات." if is_ar else "Run an On-Page Audit or Search Console Analysis first to generate data for the action plan."
            st.warning(warn)
        else:
            if st.button(t("ai_generate_plan"), type="primary"):
                with st.spinner("Consulting Google Gemini AI for technical diagnosis..."):
                    summary = gsc_data.get("summary", {}) if gsc_data else {"target_url": onpage_data.get("target_url")}
                    top_issues = gsc_data.get("issues", []) if gsc_data else [{"issue": d} for d in onpage_data.get("pages", [{}])[0].get("deductions", [])]
                    plan = generate_seo_action_plan(active_key, summary, top_issues)
                    st.session_state["gemini_saved_plan"] = plan
                    
            saved_plan = st.session_state.get("gemini_saved_plan")
            if saved_plan:
                st.markdown(f"""
                <div class="glass-card" style="padding:24px;border-left:4px solid var(--gold);">
                    {saved_plan}
                </div>
                """, unsafe_allow_html=True)
                
    with tab_rewriter:
        st.markdown("#### High-Converting Title & Meta Description Generator" if not is_ar else "#### مولد عناوين وميتا ديسكريبشن جاذبة للزيارات")
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            q_in = st.text_input("Target Query" if not is_ar else "الكلمة المفتاحية المستهدفة", placeholder="e.g. technical seo audit checklist")
            t_in = st.text_input("Current Title Tag" if not is_ar else "عنوان الصفحة الحالي", placeholder="e.g. SEO Audit Checklist - Example Site")
        with col_w2:
            m_in = st.text_area("Current Meta Description" if not is_ar else "الوصف الحالي للصفحة", placeholder="e.g. Read our seo audit checklist to improve your ranking.")
            intent_options = ["Commercial / Transactional", "Informational", "Comparison / Investigative"] if not is_ar else ["تجاري / شراء مباشر", "معلوماتي وإرشادي", "مقارنة وبحث تجاري"]
            intent_in = st.selectbox("Search Intent" if not is_ar else "نية البحث", intent_options)
            
        if st.button(t("ai_generate_rewrites"), type="primary", use_container_width=True):
            if not q_in:
                st.error("Please specify a target query." if not is_ar else "يرجى تحديد الكلمة المفتاحية.")
            else:
                with st.spinner("Generating CTR-optimized variations..."):
                    rewrites = generate_title_meta_rewrites(active_key, q_in, t_in, m_in, intent_in)
                    st.markdown(f"""
                    <div class="glass-card" style="padding:20px;border-left:3px solid var(--gold);margin-top:16px;">
                        {rewrites}
                    </div>
                    """, unsafe_allow_html=True)
                    
    with tab_cannibal:
        st.markdown("#### Intent Disambiguation & Cannibalization Brief" if not is_ar else "#### بريف فك التنازع بين صفحات الموقع")
        c_query = st.text_input("Cannibalized Query" if not is_ar else "الكلمة المفتاحية المتنازع عليها", placeholder="e.g. best enterprise seo platform")
        c_prim = st.text_input("Primary Target URL" if not is_ar else "الرابط الأساسي المستهدف بالترتيب", placeholder="https://example.com/platform")
        c_sec = st.text_area("Secondary Competing URLs (one per line)" if not is_ar else "الروابط المنافسة الثانوية (رابط بكل سطر)", placeholder="https://example.com/blog/best-seo-platforms\nhttps://example.com/pricing")
        
        if st.button(t("ai_generate_brief"), type="primary", use_container_width=True):
            if not c_query or not c_prim:
                st.error("Please provide both query and primary URL." if not is_ar else "يرجى توفير الكلمة المفتاحية والرابط الأساسي.")
            else:
                sec_list = [s.strip() for s in c_sec.splitlines() if s.strip()]
                with st.spinner("Formulating technical disambiguation protocol..."):
                    brief = generate_cannibalization_brief(active_key, c_query, c_prim, sec_list)
                    st.markdown(f"""
                    <div class="glass-card" style="padding:20px;border-left:3px solid var(--gold);margin-top:16px;">
                        {brief}
                    </div>
                    """, unsafe_allow_html=True)
                    
    render_footer()
