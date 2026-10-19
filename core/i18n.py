"""
Internationalization (i18n) Module for SEO Suite Pro:
Comprehensive bilingual support for English ('en') and Arabic ('ar')
with RTL typography and localized technical terminology.
"""

import streamlit as st

def get_current_lang() -> str:
    """Returns current active language: 'en' or 'ar'."""
    return st.session_state.get("lang", "en")

def set_lang(lang_code: str):
    """Sets active language."""
    if lang_code in ("en", "ar"):
        st.session_state["lang"] = lang_code

TRANSLATIONS = {
    "en": {
        # Navigation
        "nav_dashboard": "Executive Dashboard",
        "nav_onpage": "On-Page Audit",
        "nav_gsc": "Search Console",
        "nav_offpage": "Off-Page Analysis",
        "nav_gemini": "Gemini AI Assistant",
        "nav_history": "Private History",
        "nav_admin": "Admin Analytics",
        "nav_contact": "Contact & Architecture",
        "nav_signout": "Sign Out",
        
        # General & Theme
        "theme_dark": "Dark Mode",
        "theme_light": "Light Mode",
        "lang_switch": "Language / اللغة",
        "theme_switch": "Theme / المظهر",
        "active_account": "Active Account",
        "role_user": "[USER]",
        "role_admin": "[ADMIN]",
        "built_by": "Built by",
        "portfolio": "Portfolio Website",
        "save_to_history": "Save to My History",
        "saved_success": "Analysis saved to your private history.",
        "export_csv": "Export CSV",
        "export_excel": "Export Excel",
        "export_pdf": "Export PDF",
        
        # Dashboard
        "dash_title": "Professional SEO Suite & Search Architecture",
        "dash_desc": "An enterprise-grade SEO diagnostic environment designed for deep technical crawling, Google Search Console statistical modeling (Python + R dual engines), keyword cannibalization attribution, and Google Gemini AI strategic recommendations.",
        "dash_welcome": "Executive Intelligence Dashboard • Welcome, {name}",
        "kpi_total_saved": "Total Saved Audits",
        "kpi_gsc_reports": "Search Console Reports",
        "kpi_onpage_crawls": "On-Page Crawls",
        "kpi_dual_engine": "System Architecture",
        "dual_engine_sub": "Python & R Dual Engines",
        "modules_header": "Analysis Modules",
        "modules_sub": "Select an operational workflow to begin",
        "mod_onpage_badge": "On-Page & Technical",
        "mod_onpage_title": "DOM & Sitemap Audit",
        "mod_onpage_desc": "Deep crawling with BeautifulSoup and lxml: title and meta length checks, heading hierarchies, schema validation, canonical tags, readability scores, and image alt text.",
        "launch_onpage": "Launch On-Page Audit",
        "mod_gsc_badge": "Search Console Intelligence",
        "mod_gsc_title": "Python + R Dual Engine",
        "mod_gsc_desc": "Ingest GSC JSON API responses or CSV/ZIP exports. Features Scikit-Learn TF-IDF clustering, algorithmic keyword cannibalization detection, and R anomaly modeling.",
        "launch_gsc": "Launch Search Console",
        "mod_offpage_badge": "Off-Page & Authority",
        "mod_offpage_title": "Anchor Text & Risk Model",
        "mod_offpage_desc": "Analyze backlink distributions, exact-match ratios, anchor text diversity, and algorithmic over-optimization penalty risk indicators.",
        "launch_offpage": "Launch Off-Page Audit",
        "recent_audits_title": "Recent Saved Analyses",
        "recent_audits_sub": "Access past private records",
        
        # Search Console
        "gsc_header": "Google Search Console Analytics & Dual Engine",
        "gsc_upload_box_title": "Upload Search Console Data",
        "gsc_upload_box_desc": "Upload your Google Search Console export file (.zip, .csv, or .json) to run deep statistical and intent analysis.",
        "gsc_upload_label": "Select GSC File (ZIP, CSV, JSON)",
        "gsc_sample_btn": "Load Enterprise Benchmark Dataset",
        "gsc_run_btn": "Run Search Console Analysis",
        "gsc_brand_label": "Brand Name (for Branded vs Non-Branded Analysis)",
        "kpi_clicks": "Total Organic Clicks",
        "kpi_impressions": "Total Impressions",
        "kpi_ctr": "Average CTR",
        "kpi_position": "Average Position",
        "kpi_queries": "Unique Queries",
        "kpi_pages": "Unique Landing Pages",
        "kpi_cannibalization": "Cannibalization Cases",
        "kpi_issues": "Flagged SEO Issues",
        "tab_issues": "10-Class Issue Classification",
        "tab_cannibalization": "Keyword Cannibalization Solver",
        "tab_clusters": "Semantic Intent Clusters (TF-IDF)",
        "tab_stats": "Statistical Analysis & Outliers (R/Python)",
        "tab_raw": "Raw Data Explorer",
        "filter_category": "Filter by Issue Category",
        
        # On-Page
        "onpage_header": "On-Page Technical Audit & DOM Intelligence",
        "onpage_target_label": "Target Website URL",
        "onpage_scope_label": "Audit Scope",
        "onpage_scope_single": "Single Page",
        "onpage_scope_sitemap": "Sitemap Crawl (Multi-Page)",
        "onpage_max_pages": "Maximum Pages to Crawl",
        "onpage_run_btn": "Execute Technical Audit",
        "kpi_health_score": "On-Page Health Score",
        "kpi_pages_scanned": "Pages Scanned",
        "kpi_missing_titles": "Missing Titles",
        "kpi_missing_h1": "Missing H1 Headings",
        "onpage_tab_overview": "Audit Overview & Health",
        "onpage_tab_dom": "Page-by-Page DOM Inspection",
        "onpage_tab_technical": "Robots & Security Headers",
        "onpage_tab_recs": "Technical Action Checklist",
        
        # Off-Page
        "offpage_header": "Off-Page Intelligence & Anchor Text Risk Model",
        "offpage_domain": "Target Domain",
        "offpage_brand": "Brand / Entity Name",
        "offpage_keyword": "Primary Target Keyword",
        "offpage_evaluate_btn": "Evaluate Backlink Profile",
        "offpage_data_source": "Data Source",
        "offpage_upload_csv": "Upload Backlink CSV",
        "offpage_sample_profile": "Load Diagnostic Sample Profile",
        "offpage_csv_label": "Upload CSV (Columns: source_url, target_url, anchor_text, is_nofollow)",
        "kpi_backlinks": "Total Backlinks",
        "kpi_referring_domains": "Referring Domains",
        "kpi_risk_score": "Over-Optimization Risk",
        "kpi_dofollow": "Dofollow Ratio",
        "offpage_tab_dist": "Anchor Text Distribution",
        "offpage_tab_risk": "Risk Assessment & Mitigation",
        "offpage_tab_raw": "Backlinks Table",
        
        # Gemini AI
        "ai_header": "Google Gemini AI Strategic Assistant",
        "ai_key_label": "Gemini API Key (Google AI Studio Free Tier)",
        "ai_key_placeholder": "AIzaSy...",
        "ai_save_key": "Save Key",
        "ai_clear_key": "Clear",
        "ai_generate_plan": "Generate Executive 30-Day Plan",
        "ai_generate_rewrites": "Generate 3 High-CTR Options",
        "ai_generate_brief": "Generate Differentiation Brief",
        "ai_tab_plan": "Executive 30-Day Action Plan",
        "ai_tab_rewriter": "High-CTR Title & Snippet Rewriter",
        "ai_tab_cannibal": "Cannibalization Differentiation Brief",
        "ai_no_key_notice": "AI features are optional. All technical crawling and Search Console analysis functions remain 100% active without an API key.",
        "ai_saved_success": "Gemini API key validated and securely stored in encrypted profile.",
        
        # History
        "history_header": "Private User History & Saved Audits",
        "history_empty": "You do not have any saved audits yet. Run an On-Page crawl or Search Console analysis and click 'Save to My History'.",
        "delete_record": "Delete This Record",
        "history_select": "Select Saved Audit",
        "history_vault": "Saved Analysis Vault",
        
        # Contact
        "contact_header": "Direct Architectural Consultation & Inquiries",
        "contact_linkedin": "LinkedIn Profile",
        "contact_whatsapp": "WhatsApp Direct",
        "contact_call": "Direct Call",
        "contact_portfolio": "Official Portfolio Website",
        "contact_spec_title": "Ismail El Asiouty",
        "contact_spec_role": "Senior Full-Stack Engineer & Technical SEO Architect",
        "contact_spec_desc": "Specializing in enterprise technical SEO architectures, full-stack data intelligence tools, Google Search Console statistical modeling, and programmatic search growth engines.",
        
        # Auth
        "auth_welcome_title": "SEO Suite Pro",
        "auth_welcome_sub": "Enterprise Technical SEO & Organic Intelligence Platform",
        "auth_signin_tab": "Sign In",
        "auth_register_tab": "Create Account",
        "auth_ident_label": "Username or Email",
        "auth_pass_label": "Password",
        "auth_signin_btn": "Sign In to SEO Suite Pro",
        "auth_username_label": "Desired Username",
        "auth_email_label": "Email Address",
        "auth_create_btn": "Create Private Account",
        
        # Admin
        "admin_header": "Administrative Platform Intelligence & Usage Metrics",
        "admin_privacy": "Privacy Enforced: The Admin panel reports platform throughput, computational events, and capacity metrics only. No user audit payloads or target URLs are accessible.",
        "admin_kpi_users": "Total Registered Users",
        "admin_kpi_analyses": "Total Analyses Executed",
        "admin_kpi_events": "Events (Past 7 Days)",
        "admin_kpi_security": "Security State",
    },
    
    "ar": {
        # Navigation
        "nav_dashboard": "لوحة التحكم الرئيسية",
        "nav_onpage": "فحص السيو الداخلي On-Page",
        "nav_gsc": "تحليل سيرش كونسول GSC",
        "nav_offpage": "تحليل الروابط Off-Page",
        "nav_gemini": "مساعد الذكاء الاصطناعي Gemini",
        "nav_history": "سجل التحليلات الخاص",
        "nav_admin": "إحصائيات المنصة (Admin)",
        "nav_contact": "تواصل مع المعماري",
        "nav_signout": "تسجيل الخروج",
        
        # General & Theme
        "theme_dark": "الوضع الليلي (Dark)",
        "theme_light": "الوضع الفاتح (Light)",
        "lang_switch": "اللغة / Language",
        "theme_switch": "المظهر / Theme",
        "active_account": "الحساب النشط",
        "role_user": "[مستخدم]",
        "role_admin": "[مدير]",
        "built_by": "تم البناء بواسطة",
        "portfolio": "موقع البورتفوليو",
        "save_to_history": "حفظ في سجلي الخاص",
        "saved_success": "تم حفظ التحليل بنجاح في سجلك الخاص.",
        "export_csv": "تصدير CSV",
        "export_excel": "تصدير Excel",
        "export_pdf": "تصدير PDF",
        
        # Dashboard
        "dash_title": "منصة التحليل والذكاء الاصطناعي للسيو المتقدم",
        "dash_desc": "بيئة احترافية متكاملة للزحف الفني، والتحليل الإحصائي لبيانات جوجل سيرش كونسول باستخدام محركي Python و R معاً، وفك تعارض الكلمات المفتاحية (Cannibalization)، وتوليد خطط استراتيجية باستخدام Google Gemini.",
        "dash_welcome": "لوحة التحكم الاستراتيجية • مرحباً، {name}",
        "kpi_total_saved": "إجمالي التحليلات المحفوظة",
        "kpi_gsc_reports": "تقارير سيرش كونسول",
        "kpi_onpage_crawls": "عمليات فحص الصفحات",
        "kpi_dual_engine": "معمارية النظام",
        "dual_engine_sub": "محركان إحصائيان Python & R",
        "modules_header": "وحدات الفحص والتحليل",
        "modules_sub": "اختر مسار العمل لبدء التحليل الفني",
        "mod_onpage_badge": "السيو الداخلي والفني",
        "mod_onpage_title": "فحص الـ DOM وخريطة الموقع",
        "mod_onpage_desc": "زحف فني عميق: فحص العناوين والميتا، تسلسل العناوين، التحقق من السكيما، الروابط الكنسية، وسهولة القراءة، ونصوص الصور البديلة.",
        "launch_onpage": "بدء فحص السيو الداخلي",
        "mod_gsc_badge": "ذكاء جوجل سيرش كونسول",
        "mod_gsc_title": "محرك تحليلي مزدوج Python + R",
        "mod_gsc_desc": "استيراد ملفات ZIP أو CSV أو JSON. تصنيف النوايا باستخدام TF-IDF، كشف تعارض الكلمات المفتاحية، ونمذجة الشواذ إحصائياً بلغة R.",
        "launch_gsc": "بدء تحليل سيرش كونسول",
        "mod_offpage_badge": "الروابط الخارجية والمصداقية",
        "mod_offpage_title": "توزيع الروابط ومؤشر المخاطر",
        "mod_offpage_desc": "تحليل توزيع الأنكور تكست، ونسبة الكلمات المتطابقة تماماً، وتنوع الروابط، ونموذج قياس خطر عقوبات جوجل للروابط.",
        "launch_offpage": "بدء تحليل الروابط الخلفية",
        "recent_audits_title": "التحليلات المحفوظة مؤخراً",
        "recent_audits_sub": "الوصول السريع للسجلات الخاصة السابقة",
        
        # Search Console
        "gsc_header": "تحليل جوجل سيرش كونسول والمحرك الإحصائي المزدوج",
        "gsc_upload_box_title": "رفع وتغذية ملف سيرش كونسول",
        "gsc_upload_box_desc": "اسحب وأفلت الملف المُصدّر من Google Search Console (.zip مضغوط، .csv، أو .json) لبدء التحليل الفوري وتصنيف المشاكل.",
        "gsc_upload_label": "اختر ملف سيرش كونسول (ZIP أو CSV أو JSON)",
        "gsc_sample_btn": "تحميل عينة قياسية جاهزة",
        "gsc_run_btn": "بدء تحليل بيانات السيرش كونسول",
        "gsc_brand_label": "اسم العلامة التجارية (لقياس نسبة البراند)",
        "kpi_clicks": "إجمالي النقرات العضوية",
        "kpi_impressions": "إجمالي الظهور",
        "kpi_ctr": "متوسط النقر للظهور CTR",
        "kpi_position": "متوسط الترتيب في جوجل",
        "kpi_queries": "الكلمات المفتاحية الفريدة",
        "kpi_pages": "صفحات الهبوط المأرشفة",
        "kpi_cannibalization": "حالات أكل الكلمات (Cannibalization)",
        "kpi_issues": "المشاكل الفنية المكتشفة",
        "tab_issues": "تصنيف المشاكل الفنية (10 فئات)",
        "tab_cannibalization": "معالج أكل الكلمات المفتاحية",
        "tab_clusters": "تجميع النوايا البحثية (TF-IDF)",
        "tab_stats": "التحليل الإحصائي والشواذ (R/Python)",
        "tab_raw": "استعراض البيانات المرفوعة",
        "filter_category": "تصفية حسب نوع المشكلة",
        
        # On-Page
        "onpage_header": "فحص السيو الداخلي ومعمارية الـ DOM",
        "onpage_target_label": "رابط الموقع المستهدف",
        "onpage_scope_label": "نطاق الفحص",
        "onpage_scope_single": "صفحة واحدة فقط",
        "onpage_scope_sitemap": "زحف خريطة الموقع (متعدد الصفحات)",
        "onpage_max_pages": "أقصى عدد للصفحات للزحف",
        "onpage_run_btn": "تنفيذ الفحص الفني والداخلي",
        "kpi_health_score": "درجة صحة السيو الداخلي",
        "kpi_pages_scanned": "الصفحات التي تم فحصها",
        "kpi_missing_titles": "صفحات بدون Title",
        "kpi_missing_h1": "صفحات بدون عنوان H1",
        "onpage_tab_overview": "ملخص الفحص ودرجة الصحة",
        "onpage_tab_dom": "فحص الـ DOM صفحة بصفحة",
        "onpage_tab_technical": "ملف Robots وترويسات الأمان",
        "onpage_tab_recs": "قائمة التوصيات الفنية",
        
        # Off-Page
        "offpage_header": "تحليل الروابط الخلفية ومؤشر خطر العقوبات",
        "offpage_domain": "الدومين المستهدف",
        "offpage_brand": "اسم البراند / الكيان",
        "offpage_keyword": "الكلمة المفتاحية المستهدفة",
        "offpage_evaluate_btn": "تقييم ملف الروابط الخلفية",
        "offpage_data_source": "مصدر البيانات",
        "offpage_upload_csv": "رفع ملف CSV للروابط",
        "offpage_sample_profile": "تحميل عينة تشخيصية جاهزة",
        "offpage_csv_label": "رفع ملف CSV (الأعمدة: source_url, target_url, anchor_text, is_nofollow)",
        "kpi_backlinks": "إجمالي الروابط الخلفية",
        "kpi_referring_domains": "الدومينات المحيلة",
        "kpi_risk_score": "مؤشر خطر الإفراط (Over-Optimization)",
        "kpi_dofollow": "نسبة روابط Dofollow",
        "offpage_tab_dist": "توزيع الأنكور تكست",
        "offpage_tab_risk": "تقييم المخاطر والإجراءات",
        "offpage_tab_raw": "جدول الروابط التفصيلي",
        
        # Gemini AI
        "ai_header": "مساعد الذكاء الاصطناعي Google Gemini",
        "ai_key_label": "مفتاح Gemini API (Google AI Studio المجاني)",
        "ai_key_placeholder": "AIzaSy...",
        "ai_save_key": "حفظ المفتاح",
        "ai_clear_key": "مسح",
        "ai_generate_plan": "توليد خطة عمل استراتيجية لـ 30 يوماً",
        "ai_generate_rewrites": "توليد 3 خيارات عناوين ووصف جذابة للـ CTR",
        "ai_generate_brief": "توليد بريف فك التنازع بين الروابط",
        "ai_tab_plan": "خطة عمل استراتيجية لـ 30 يوماً",
        "ai_tab_rewriter": "إعادة صياغة العناوين لرفع الـ CTR",
        "ai_tab_cannibal": "بريف فك التنازع بين الصفحات",
        "ai_no_key_notice": "ميزات الذكاء الاصطناعي اختيارية. جميع ميزات الفحص التقني وتحليل سيرش كونسول تعمل بكفاءة 100% بدون مفتاح.",
        "ai_saved_success": "تم التحقق من مفتاح Gemini وحفظه مشفراً بنجاح في ملفك الشخصي.",
        
        # History
        "history_header": "سجل التحليلات الخاص بالمعماري",
        "history_empty": "لا توجد تحليلات محفوظة بعد. قم بإجراء فحص داخلي أو تحليل سيرش كونسول ثم اضغط 'حفظ في سجلي الخاص'.",
        "delete_record": "حذف هذا السجل",
        "history_select": "اختر التحليل المطلوب استعراضه",
        "history_vault": "خزينة السجلات والتحليلات الخاصة",
        
        # Contact
        "contact_header": "التواصل المباشر والاستشارات المعمارية",
        "contact_linkedin": "الملف الشخصي على LinkedIn",
        "contact_whatsapp": "محادثة فورية WhatsApp",
        "contact_call": "اتصال هاتفي مباشر",
        "contact_portfolio": "موقع البورتفوليو الرسمي",
        "contact_spec_title": "إسماعيل الأسيوطي",
        "contact_spec_role": "مهندس برمجيات أول ومعماري سيو تقني",
        "contact_spec_desc": "متخصص في بناء معماريات السيو الفني للمؤسسات، وبناء منصات ذكاء البيانات العضوية، والتحليل الإحصائي لبيانات Google Search Console، ومحركات النمو البرمجي للبحث.",
        
        # Auth
        "auth_welcome_title": "SEO Suite Pro",
        "auth_welcome_sub": "منصة التحليل الفني والذكاء الاصطناعي المتقدم للسيو",
        "auth_signin_tab": "تسجيل الدخول",
        "auth_register_tab": "إنشاء حساب جديد",
        "auth_ident_label": "اسم المستخدم أو البريد الإلكتروني",
        "auth_pass_label": "كلمة المرور",
        "auth_signin_btn": "دخول إلى SEO Suite Pro",
        "auth_username_label": "اسم المستخدم المطلوب",
        "auth_email_label": "البريد الإلكتروني",
        "auth_create_btn": "إنشاء حساب خاص جديد",
        
        # Admin
        "admin_header": "إحصائيات المنصة ومؤشرات الاستخدام (Admin)",
        "admin_privacy": "الخصوصية الصارمة: لوحة المدير تعرض فقط معدلات الاستخدام، والأحداث البرمجية، وسعة الخادم دون أي اطلاع على بيانات المستخدمين أو روابط مواقعهم الخاصة.",
        "admin_kpi_users": "إجمالي المستخدمين المسجلين",
        "admin_kpi_analyses": "إجمالي التحليلات المنفذة",
        "admin_kpi_events": "الأحداث (خلال آخر 7 أيام)",
        "admin_kpi_security": "حالة الأمان والحماية",
    }
}

def t(key: str, default: str = "") -> str:
    """Retrieves translation for the given key in active language."""
    lang = get_current_lang()
    table = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return table.get(key, default or key)
