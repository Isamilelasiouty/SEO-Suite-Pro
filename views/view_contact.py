"""
Contact & Brand View for SEO Suite Pro:
Official contact information, portfolio links, and professional background for Ismail El Asiouty.
STRICT: Zero emojis, luxury gold, black, and white design system.
"""

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
from views.components import get_logo_base64, render_footer, render_header

def render_contact_view():
    render_header(subtitle="Direct Architectural Consultation & Inquiries")
    logo_uri = get_logo_base64()
    
    st.markdown(f"""
    <div class="glass-card" style="text-align:center;padding:40px 30px;max-width:820px;margin:20px auto;">
        {'<img src="' + logo_uri + '" style="width:72px;height:72px;border-radius:14px;border:1.5px solid #D4AF37;margin-bottom:16px;object-fit:cover;" />' if logo_uri else ''}
        <div style="font-family:'Poppins',sans-serif;font-size:30px;font-weight:900;color:#D4AF37;letter-spacing:-0.01em;">
            {BRAND_OWNER}
        </div>
        <div style="font-size:14px;color:#F5F5F5;font-weight:600;margin-top:6px;">
            {BRAND_ROLE}
        </div>
        <div style="font-size:13px;color:#A0A0A0;max-width:620px;margin:12px auto 28px;line-height:1.7;">
            Specializing in enterprise technical SEO architectures, full-stack data intelligence tools, 
            Google Search Console statistical modeling, and programmatic search growth engines.
        </div>
        
        <div style="display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-bottom:32px;">
            <a href="{LINKEDIN_URL}" target="_blank" style="display:inline-block;padding:10px 22px;border:1px solid #D4AF37;border-radius:6px;background:rgba(212,175,55,0.1);color:#D4AF37;text-decoration:none;font-size:13px;font-weight:700;transition:all 0.2s ease;">
                LinkedIn Profile
            </a>
            <a href="{WHATSAPP_URL}" target="_blank" style="display:inline-block;padding:10px 22px;border:1px solid #D4AF37;border-radius:6px;background:rgba(212,175,55,0.1);color:#D4AF37;text-decoration:none;font-size:13px;font-weight:700;transition:all 0.2s ease;">
                WhatsApp: {PHONE_NUMBER}
            </a>
            <a href="{TEL_URL}" style="display:inline-block;padding:10px 22px;border:1px solid #D4AF37;border-radius:6px;background:rgba(212,175,55,0.1);color:#D4AF37;text-decoration:none;font-size:13px;font-weight:700;transition:all 0.2s ease;">
                Direct Call: {PHONE_NUMBER}
            </a>
            <a href="{PORTFOLIO_URL}" target="_blank" style="display:inline-block;padding:10px 22px;border:1px solid #D4AF37;border-radius:6px;background:#D4AF37;color:#000000;text-decoration:none;font-size:13px;font-weight:700;transition:all 0.2s ease;">
                Official Portfolio Website
            </a>
        </div>
        
        <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:16px;text-align:left;border-top:1px solid rgba(212,175,55,0.2);padding-top:24px;">
            <div style="background:#141414;padding:16px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);">
                <div style="color:#D4AF37;font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">Technical SEO Audits</div>
                <div style="color:#A0A0A0;font-size:11px;line-height:1.5;">DOM hierarchy, schema markup engineering, crawl budget preservation, and indexation defense.</div>
            </div>
            <div style="background:#141414;padding:16px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);">
                <div style="color:#D4AF37;font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">Data Science & R Analytics</div>
                <div style="color:#A0A0A0;font-size:11px;line-height:1.5;">Time-series anomaly detection, STL seasonality checks, and query cannibalization solvers.</div>
            </div>
            <div style="background:#141414;padding:16px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);">
                <div style="color:#D4AF37;font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">Custom Python Tooling</div>
                <div style="color:#A0A0A0;font-size:11px;line-height:1.5;">Scalable Streamlit platforms, secure multi-tenant architectures, and AI agent integration.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    render_footer()
