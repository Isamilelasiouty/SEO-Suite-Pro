"""
Contact & Brand View for SEO Suite Pro:
Official contact information, portfolio links, and professional background for Ismail El Asiouty.
STRICT: Zero emojis, luxury gold, black, and white design system.
Bilingual support (English & Arabic) and Light/Dark mode compatible.
"""

import textwrap
import streamlit as st
from core.config import (
    BRAND_OWNER,
    BRAND_ROLE,
    LINKEDIN_URL,
    PHONE_NUMBER,
    PORTFOLIO_URL,
    TEL_URL,
    WHATSAPP_URL,
)
from core.i18n import get_current_lang, t
from views.components import get_logo_base64, render_footer, render_header

def render_contact_view():
    lang = get_current_lang()
    is_ar = (lang == "ar")
    
    render_header(subtitle=t("contact_header"))
    logo_uri = get_logo_base64()
    
    name_display = t("contact_spec_title") if is_ar else BRAND_OWNER
    role_display = t("contact_spec_role") if is_ar else BRAND_ROLE
    desc_display = t("contact_spec_desc")
    logo_img_tag = f'<img src="{logo_uri}" style="width:76px;height:76px;border-radius:14px;border:1.5px solid var(--gold);margin-bottom:16px;object-fit:cover;box-shadow:0 4px 16px var(--gold-tint);" />' if logo_uri else ''
    
    card_html = textwrap.dedent(f"""
    <div class="glass-card" style="text-align:center;padding:40px 30px;max-width:840px;margin:20px auto;">
        {logo_img_tag}
        <div style="font-family:'Poppins','Cairo',sans-serif;font-size:30px;font-weight:900;color:var(--gold);letter-spacing:-0.01em;">
            {name_display}
        </div>
        <div style="font-size:14px;color:var(--text-soft);font-weight:600;margin-top:6px;">
            {role_display}
        </div>
        <div style="font-size:13px;color:var(--text-muted);max-width:640px;margin:12px auto 28px;line-height:1.7;">
            {desc_display}
        </div>
        
        <div style="display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-bottom:32px;">
            <a href="{LINKEDIN_URL}" target="_blank" style="display:inline-block;padding:10px 22px;border:1px solid var(--gold);border-radius:8px;background:rgba(212,175,55,0.1);color:var(--gold);text-decoration:none;font-size:13px;font-weight:700;transition:all 0.2s ease;">
                {t('contact_linkedin')}
            </a>
            <a href="{WHATSAPP_URL}" target="_blank" style="display:inline-block;padding:10px 22px;border:1px solid var(--gold);border-radius:8px;background:rgba(212,175,55,0.1);color:var(--gold);text-decoration:none;font-size:13px;font-weight:700;transition:all 0.2s ease;">
                {t('contact_whatsapp')}: {PHONE_NUMBER}
            </a>
            <a href="{TEL_URL}" style="display:inline-block;padding:10px 22px;border:1px solid var(--gold);border-radius:8px;background:rgba(212,175,55,0.1);color:var(--gold);text-decoration:none;font-size:13px;font-weight:700;transition:all 0.2s ease;">
                {t('contact_call')}: {PHONE_NUMBER}
            </a>
            <a href="{PORTFOLIO_URL}" target="_blank" style="display:inline-block;padding:10px 22px;border:1px solid var(--gold);border-radius:8px;background:var(--gold);color:#000000;text-decoration:none;font-size:13px;font-weight:700;transition:all 0.2s ease;">
                {t('contact_portfolio')}
            </a>
        </div>
        
        <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:16px;text-align:{'right' if is_ar else 'left'};border-top:1px solid var(--gold-border);padding-top:24px;">
            <div style="background:var(--bg-elevated);padding:18px;border-radius:10px;border:1px solid var(--gold-border);">
                <div style="color:var(--gold);font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">
                    {'Technical SEO Audits' if not is_ar else 'معماريات السيو التقني'}
                </div>
                <div style="color:var(--text-muted);font-size:11px;line-height:1.6;">
                    {'DOM hierarchy, schema markup engineering, crawl budget preservation, and indexation defense.' if not is_ar else 'هندسة الـ DOM، وبناء السكيما المنظمة، وحماية ميزانية الزحف، والتحكم الصارم في الفهرسة.'}
                </div>
            </div>
            <div style="background:var(--bg-elevated);padding:18px;border-radius:10px;border:1px solid var(--gold-border);">
                <div style="color:var(--gold);font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">
                    {'Data Science & R Analytics' if not is_ar else 'علم البيانات والتحليل بلغة R'}
                </div>
                <div style="color:var(--text-muted);font-size:11px;line-height:1.6;">
                    {'Time-series anomaly detection, STL seasonality checks, and query cannibalization solvers.' if not is_ar else 'كشف الشواذ الإحصائية في السيرش كونسول، ونمذجة الموسمية، وفك تداخل الكلمات المفتاحية.'}
                </div>
            </div>
            <div style="background:var(--bg-elevated);padding:18px;border-radius:10px;border:1px solid var(--gold-border);">
                <div style="color:var(--gold);font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">
                    {'Custom Python Tooling' if not is_ar else 'أدوات برمجية متقدمة بـ Python'}
                </div>
                <div style="color:var(--text-muted);font-size:11px;line-height:1.6;">
                    {'Scalable Streamlit platforms, secure multi-tenant architectures, and AI agent integration.' if not is_ar else 'تطوير منصات Streamlit احترافية، وعزل قواعد بيانات المستخدمين، وربط عملاء الذكاء الاصطناعي.'}
                </div>
            </div>
        </div>
    </div>
    """).strip()
    st.markdown(card_html, unsafe_allow_html=True)
    
    render_footer()
