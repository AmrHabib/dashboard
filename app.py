import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import base64
from io import BytesIO

# إعداد صفحة Streamlit
st.set_page_config(
    page_title="لوحة تحكم المخزون والمبيعات",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تنسيق CSS مخصص
st.markdown("""
<style>
    /* التنسيق العام */
    .main-header {
        text-align: center;
        color: #2E86AB;
        padding: 20px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        margin-bottom: 30px;
        border-right: 5px solid #2E86AB;
    }
    
    /* بطاقات KPI */
    .kpi-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.3s;
        border-top: 4px solid #2E86AB;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .kpi-value {
        font-size: 28px;
        font-weight: bold;
        margin: 5px 0;
    }
    
    .kpi-label {
        font-size: 14px;
        color: #666;
        margin-bottom: 5px;
    }
    
    /* الألوان */
    .color-1 { color: #2E86AB; }   /* أزرق */
    .color-2 { color: #2ECC71; }   /* أخضر */
    .color-3 { color: #F39C12; }   /* برتقالي */
    .color-4 { color: #E74C3C; }   /* أحمر */
    .color-5 { color: #9B59B6; }   /* بنفسجي */
    .color-6 { color: #1ABC9C; }   /* فيروزي */
    
    /* تبويبات */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f1f3f4;
        border-radius: 5px 5px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    /* الجداول */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* أزرار */
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
    }
    
    /* شريط التقدم */
    .stProgress > div > div > div > div {
        background-color: #2E86AB;
    }
    
    /* نص عربي */
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# دالة لتحميل البيانات
@st.cache_data
def load_data():
    try:
        # قراءة البيانات من ملف CSV
        df = pd.read_csv('sample_inventory.csv', encoding='utf-8')
        
        # معالجة الأعمدة الأساسية
        if 'Description' in df.columns:
            df = df.rename(columns={'Description': 'الصنف'})
        if 'Category' in df.columns:
            df = df.rename(columns={'Category': 'الفئة'})
        if 'Year' in df.columns:
            df = df.rename(columns={'Year': 'السنة'})
        
        # إضافة أعمدة افتراضية إذا لم تكن موجودة
        required_columns = {
            'الرصيد الختامي': 'Closing',
            'المشتريات': 'Purchases', 
            'المبيعات': 'Sales',
            'القيمة الإجمالية': 'Total Value',
            'سعر الوحدة': 'Unit Price'
        }
        
        for arabic_col, english_col in required_columns.items():
            if arabic_col not in df.columns and english_col in df.columns:
                df[arabic_col] = df[english_col]
        
        # تحويل الأنواع الرقمية
        numeric_columns = ['الرصيد الختامي', 'المشتريات', 'المبيعات', 'القيمة الإجمالية', 'سعر الوحدة']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    except Exception as e:
        st.error(f"خطأ في تحميل البيانات: {str(e)}")
        # إنشاء بيانات تجريبية إذا فشل التحميل
        return create_sample_data()

# دالة لإنشاء بيانات تجريبية
def create_sample_data():
    data = {
        'الصنف': ['Standard 3.00m', 'Standard 2.80m', 'Standard 2.50m', 'Ledger 2.50 m', 'Steel board size 3.00 m',
                 'Aluminum Ladder 6.00m', 'Transom 2.50 m', 'Fixed coupler 1.5/1.5', 'Swivel coupler 1.5/1.5', 'Galvanized pipe 6.00M'],
        'الفئة': ['Scaffolding', 'Scaffolding', 'Scaffolding', 'Scaffolding', 'Scaffolding',
                 'Scaffolding', 'Scaffolding', 'Scaffolding', 'Scaffolding', 'Scaffolding'],
        'السنة': [2018, 2018, 2018, 2018, 2018, 2018, 2018, 2018, 2018, 2018],
        'الرصيد الختامي': [87286, 28000, 50231, 126704, 92250, 93, 3715, 34042, 23793, 15659],
        'المشتريات': [166, 289, -864, -6462, 2288, 8, 728, 10019, 4791, -46],
        'المبيعات': [86465, 27704, 50018, 133083, 89711, 92, 2987, 35994, 24409, 15705],
        'القيمة الإجمالية': [446149.65, 138565.35, 208904.50, 315286.29, 612253.35, 3675, 13596.90, 28758.13, 18250, 91605.15],
        'سعر الوحدة': [5.15, 4.95, 4.25, 2.49, 6.62, 36.75, 3.66, 0.63, 0.63, 5.85]
    }
    return pd.DataFrame(data)

# دالة لتحويل DataFrame إلى ملف Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

# العنوان الرئيسي
st.markdown('<div class="main-header"><h1>📊 لوحة تحكم المخزون والمبيعات</h1><p>لوحة تحكم تفاعلية لمديري المبيعات والمخازن</p></div>', unsafe_allow_html=True)

# تحميل البيانات
with st.spinner('جاري تحميل البيانات...'):
    df = load_data()

# ============== الشريط الجانبي ==============
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/dashboard.png", width=80)
    st.markdown("### ⚙️ إعدادات التحكم")
    
    # فلترة السنة
    if 'السنة' in df.columns:
        years = sorted(df['السنة'].unique())
        selected_years = st.multiselect(
            "📅 اختر السنة:",
            options=years,
            default=years
        )
    else:
        selected_years = []
    
    # فلترة الفئة
    if 'الفئة' in df.columns:
        categories = sorted(df['الفئة'].unique())
        selected_categories = st.multiselect(
            "🏷️ اختر الفئة:",
            options=categories,
            default=categories[:min(3, len(categories))]
        )
    else:
        selected_categories = []
    
    # فلترة الأصناف
    if 'الصنف' in df.columns:
        items = sorted(df['الصنف'].unique())
        selected_items = st.multiselect(
            "📦 اختر الأصناف:",
            options=items,
            default=items[:min(5, len(items))]
        )
    else:
        selected_items = []
    
    st.markdown("---")
    
    # أزرار التحكم
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 تحديث البيانات", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("🗑️ مسح الذاكرة", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # معلومات النظام
    st.markdown("### 📊 معلومات النظام")
    st.metric("عدد السجلات", f"{len(df):,}")
    if 'الصنف' in df.columns:
        st.metric("عدد الأصناف", len(df['الصنف'].unique()))
    if 'الفئة' in df.columns:
        st.metric("عدد الفئات", len(df['الفئة'].unique()))
    
    st.markdown("---")
    st.markdown("**👨‍💼 للمديرين:**")
    st.markdown("- مدير المبيعات")
    st.markdown("- مدير المخزن")

# ============== تطبيق الفلاتر ==============
filtered_df = df.copy()

if selected_years and 'السنة' in df.columns:
    filtered_df = filtered_df[filtered_df['السنة'].isin(selected_years)]
if selected_categories and 'الفئة' in df.columns:
    filtered_df = filtered_df[filtered_df['الفئة'].isin(selected_categories)]
if selected_items and 'الصنف' in df.columns:
    filtered_df = filtered_df[filtered_df['الصنف'].isin(selected_items)]

# ============== مؤشرات الأداء ==============
st.markdown("### 📈 مؤشرات الأداء الرئيسية")

# صف أول من KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_qty = filtered_df['الرصيد الختامي'].sum() if 'الرصيد الختامي' in filtered_df.columns else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">إجمالي الكمية</div>
        <div class="kpi-value color-1">{total_qty:,.0f}</div>
        <div style="font-size:12px;color:#666;">قطعة</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_purchases = filtered_df['المشتريات'].sum() if 'المشتريات' in filtered_df.columns else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">إجمالي المشتريات</div>
        <div class="kpi-value color-2">{total_purchases:,.0f}</div>
        <div style="font-size:12px;color:#666;">قطعة</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    total_sales = filtered_df['المبيعات'].sum() if 'المبيعات' in filtered_df.columns else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">إجمالي المبيعات</div>
        <div class="kpi-value color-3">{total_sales:,.0f}</div>
        <div style="font-size:12px;color:#666;">قطعة</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    total_value = filtered_df['القيمة الإجمالية'].sum() if 'القيمة الإجمالية' in filtered_df.columns else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">القيمة الإجمالية</div>
        <div class="kpi-value color-4">${total_value:,.0f}</div>
        <div style="font-size:12px;color:#666;">دولار</div>
    </div>
    """, unsafe_allow_html=True)

# صف ثاني من KPIs
col5, col6, col7, col8 = st.columns(4)

with col5:
    avg_price = filtered_df['سعر الوحدة'].mean() if 'سعر الوحدة' in filtered_df.columns else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">متوسط السعر</div>
        <div class="kpi-value color-5">${avg_price:,.2f}</div>
        <div style="font-size:12px;color:#666;">دولار/قطعة</div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    items_count = len(filtered_df['الصنف'].unique()) if 'الصنف' in filtered_df.columns else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">عدد الأصناف</div>
        <div class="kpi-value color-6">{items_count:,}</div>
        <div style="font-size:12px;color:#666;">صنف</div>
    </div>
    """, unsafe_allow_html=True)

with col7:
    if total_purchases > 0:
        turnover_rate = (total_sales / total_purchases * 100)
    else:
        turnover_rate = 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">معدل الدوران</div>
        <div class="kpi-value color-1">{turnover_rate:.1f}%</div>
        <div style="font-size:12px;color:#666;">نسبة المبيعات</div>
    </div>
    """, unsafe_allow_html=True)

with col8:
    if total_qty > 0:
        avg_inventory_value = total_value / total_qty
    else:
        avg_inventory_value = 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">متوسط قيمة القطعة</div>
        <div class="kpi-value color-2">${avg_inventory_value:,.2f}</div>
        <div style="font-size:12px;color:#666;">دولار</div>
    </div>
    """, unsafe_allow_html=True)

# ============== الرسوم البيانية ==============
st.markdown("---")
st.markdown("### 📊 التحليلات المرئية")

# إنشاء تبويبات للرسوم البيانية
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 نظرة عامة", 
    "🏷️ حسب الفئة", 
    "📦 أفضل الأصناف", 
    "📋 البيانات التفصيلية"
])

with tab1:
    # مخطط شريطي للمقارنة
    if 'الفئة' in filtered_df.columns and 'الرصيد الختامي' in filtered_df.columns:
        category_summary = filtered_df.groupby('الفئة')['الرصيد الختامي'].sum().reset_index()
        fig1 = px.bar(
            category_summary,
            x='الفئة',
            y='الرصيد الختامي',
            title='توزيع المخزون حسب الفئة',
            color='الفئة',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    # مخطط دائري للنسبة المئوية
    if len(filtered_df) > 0:
        fig2 = px.pie(
            filtered_df,
            values='الرصيد الختامي',
            names='الفئة' if 'الفئة' in filtered_df.columns else 'الصنف',
            title='النسبة المئوية للتوزيع',
            hole=0.3
        )
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    # مخططات حسب الفئة
    if 'الفئة' in filtered_df.columns:
        # مقارنة المشتريات والمبيعات حسب الفئة
        comparison_data = filtered_df.groupby('الفئة').agg({
            'المشتريات': 'sum',
            'المبيعات': 'sum'
        }).reset_index()
        
        fig3 = go.Figure(data=[
            go.Bar(name='المشتريات', x=comparison_data['الفئة'], y=comparison_data['المشتريات']),
            go.Bar(name='المبيعات', x=comparison_data['الفئة'], y=comparison_data['المبيعات'])
        ])
        fig3.update_layout(
            title='المقارنة بين المشتريات والمبيعات حسب الفئة',
            barmode='group'
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # مخطط قيمة المخزون حسب الفئة
        if 'القيمة الإجمالية' in filtered_df.columns:
            value_by_category = filtered_df.groupby('الفئة')['القيمة الإجمالية'].sum().reset_index()
            fig4 = px.treemap(
                value_by_category,
                path=['الفئة'],
                values='القيمة الإجمالية',
                title='توزيع القيمة حسب الفئة'
            )
            st.plotly_chart(fig4, use_container_width=True)

with tab3:
    # أفضل 10 أصناف
    if 'الصنف' in filtered_df.columns:
        # أفضل 10 أصناف حسب الكمية
        top_qty = filtered_df.nlargest(10, 'الرصيد الختامي')[['الصنف', 'الرصيد الختامي', 'القيمة الإجمالية']]
        
        fig5 = px.bar(
            top_qty,
            x='الصنف',
            y='الرصيد الختامي',
            title='أعلى 10 أصناف حسب الكمية',
            color='الرصيد الختامي',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig5, use_container_width=True)
        
        # أفضل 10 أصناف حسب القيمة
        top_value = filtered_df.nlargest(10, 'القيمة الإجمالية')[['الصنف', 'القيمة الإجمالية', 'الرصيد الختامي']]
        
        fig6 = px.bar(
            top_value,
            x='الصنف',
            y='القيمة الإجمالية',
            title='أعلى 10 أصناف حسب القيمة',
            color='القيمة الإجمالية',
            color_continuous_scale='Plasma'
        )
        st.plotly_chart(fig6, use_container_width=True)

with tab4:
    # عرض البيانات التفصيلية
    st.markdown("### 📋 البيانات المفصلة")
    
    # فلترة إضافية للجدول
    col1, col2 = st.columns(2)
    with col1:
        show_columns = st.multiselect(
            "اختر الأعمدة للعرض:",
            options=filtered_df.columns.tolist(),
            default=filtered_df.columns.tolist()[:8]
        )
    
    with col2:
        rows_to_show = st.slider("عدد الصفوف:", 10, 100, 20)
    
    if show_columns:
        display_df = filtered_df[show_columns].head(rows_to_show)
        
        # تنسيق الأرقام
        numeric_cols = display_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in ['القيمة الإجمالية', 'سعر الوحدة']:
                display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "")
            elif col in ['الرصيد الختامي', 'المشتريات', 'المبيعات']:
                display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
        
        # عرض الجدول
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        
        # خيارات التصدير
        st.markdown("### 📤 خيارات التصدير")
        export_col1, export_col2, export_col3 = st.columns(3)
        
        with export_col1:
            # تصدير كـ CSV
            csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تصدير كـ CSV",
                data=csv,
                file_name="مخزون_بيانات.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with export_col2:
            # تصدير كـ Excel
            excel_data = to_excel(filtered_df)
            st.download_button(
                label="📊 تصدير كـ Excel",
                data=excel_data,
                file_name="مخزون_بيانات.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with export_col3:
            if st.button("🖨️ طباعة التقرير", use_container_width=True):
                st.success("جاري إعداد التقرير للطباعة...")

# ============== التقارير الذكية ==============
st.markdown("---")
st.markdown("### 📑 التقارير الذكية")

# إنشاء أعمدة للتقارير
report_col1, report_col2, report_col3 = st.columns(3)

with report_col1:
    with st.expander("📊 تقرير المخزون الحرج", expanded=True):
        if 'الرصيد الختامي' in filtered_df.columns:
            # حساب متوسط المخزون
            avg_stock = filtered_df['الرصيد الختامي'].mean()
            critical_items = filtered_df[filtered_df['الرصيد الختامي'] < avg_stock * 0.3]
            
            if not critical_items.empty:
                st.warning(f"⚠️ {len(critical_items)} صنف ذو مخزون منخفض")
                st.dataframe(
                    critical_items[['الصنف', 'الفئة', 'الرصيد الختامي']].head(5),
                    use_container_width=True
                )
            else:
                st.success("🎉 جميع الأصناف في مستوى جيد")

with report_col2:
    with st.expander("💰 تقرير القيمة العالية", expanded=True):
        if 'القيمة الإجمالية' in filtered_df.columns:
            high_value_items = filtered_df.nlargest(5, 'القيمة الإجمالية')
            st.info(f"🏆 أعلى {len(high_value_items)} أصناف قيمة")
            for idx, row in high_value_items.iterrows():
                st.metric(
                    row['الصنف'] if 'الصنف' in row else f"صنف {idx}",
                    f"${row['القيمة الإجمالية']:,.0f}"
                )

with report_col3:
    with st.expander("📈 تقرير الأداء", expanded=True):
        # حساب بعض المؤشرات
        if len(filtered_df) > 0:
            total_items = len(filtered_df)
            unique_categories = len(filtered_df['الفئة'].unique()) if 'الفئة' in filtered_df.columns else 0
            avg_price = filtered_df['سعر الوحدة'].mean() if 'سعر الوحدة' in filtered_df.columns else 0
            
            st.metric("إجمالي الأصناف", f"{total_items:,}")
            st.metric("عدد الفئات", unique_categories)
            st.metric("متوسط السعر", f"${avg_price:,.2f}")

# ============== تذييل الصفحة ==============
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown(f"**📅 تاريخ التحديث:** {datetime.now().strftime('%Y-%m-%d')}")
    st.markdown("**🕒 الوقت:** " + datetime.now().strftime("%H:%M:%S"))

with footer_col2:
    st.markdown("**👨‍💼 الإدارة:**")
    st.markdown("- مدير المبيعات")
    st.markdown("- مدير المخزن")

with footer_col3:
    st.markdown("**📞 الدعم الفني:**")
    st.markdown("support@inventory-dashboard.com")
    st.markdown("**🌐 الإصدار:** 1.0.0")

# رسالة نجاح
st.success("✅ تم تحميل لوحة التحكم بنجاح! استخدم الفلاتر في الشريط الجانبي لتخصيص البيانات.")