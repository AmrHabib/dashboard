import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import io

# إعداد صفحة Streamlit
st.set_page_config(
    page_title="لوحة تحكم المخزون",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مخصص
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        padding: 20px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        margin-bottom: 30px;
        border-right: 5px solid #2E86AB;
    }
    .kpi-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.3s;
        border-top: 4px solid #2E86AB;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: bold;
        margin: 5px 0;
        color: #2E86AB;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# دالة لتحميل البيانات
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('sample_inventory.csv')
        return df
    except:
        # بيانات تجريبية
        data = {
            'Year': [2018, 2018, 2018, 2018, 2018, 2019, 2019, 2019, 2019, 2019],
            'Description': ['Standard 3.00m', 'Standard 2.80m', 'Standard 2.50m', 'Ledger 2.50 m', 'Steel board 3.00 m',
                          'Standard 3.00m', 'Standard 2.80m', 'Standard 2.50m', 'Ledger 2.50 m', 'Steel board 3.00 m'],
            'Category': ['Scaffolding', 'Scaffolding', 'Scaffolding', 'Scaffolding', 'Scaffolding',
                        'Scaffolding', 'Scaffolding', 'Scaffolding', 'Scaffolding', 'Scaffolding'],
            'Closing': [87286, 28000, 50231, 126704, 92250, 85609, 27968, 48371, 126426, 91884],
            'Purchases': [166, 289, -864, -6462, 2288, 7829, 9711, 19086, 11791, 31363],
            'Sales': [86465, 27704, 50018, 133083, 89711, 77780, 18257, 29285, 114635, 60521],
            'Total Value': [446149.65, 138565.35, 208904.50, 315286.29, 612253.35, 440886.35, 138441.60, 205576.75, 314800.74, 611488.02],
            'Unit Price': [5.15, 4.95, 4.25, 2.49, 6.62, 5.15, 4.95, 4.25, 2.49, 6.62]
        }
        return pd.DataFrame(data)

# تحميل البيانات
df = load_data()

# عنوان الصفحة
st.markdown('<div class="main-header"><h1>📊 لوحة تحكم المخزون والمبيعات</h1><p>نسخة مبسطة للتشغيل الفوري</p></div>', unsafe_allow_html=True)

# ============== الشريط الجانبي ==============
with st.sidebar:
    st.markdown("### ⚙️ الفلاتر")
    
    # فلترة السنة
    years = sorted(df['Year'].unique())
    selected_years = st.multiselect("السنة:", years, default=years)
    
    # فلترة الفئة
    categories = sorted(df['Category'].unique())
    selected_categories = st.multiselect("الفئة:", categories, default=categories)
    
    st.markdown("---")
    st.markdown(f"**عدد السجلات:** {len(df):,}")
    st.markdown(f"**عدد الأصناف:** {len(df['Description'].unique())}")

# ============== فلترة البيانات ==============
filtered_df = df.copy()
if selected_years:
    filtered_df = filtered_df[filtered_df['Year'].isin(selected_years)]
if selected_categories:
    filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]

# ============== مؤشرات الأداء ==============
st.markdown("### 📈 مؤشرات الأداء")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_qty = filtered_df['Closing'].sum()
    st.markdown(f"""
    <div class="kpi-card">
        <div>إجمالي الكمية</div>
        <div class="kpi-value">{total_qty:,.0f}</div>
        <div style="font-size:12px;">قطعة</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_purchases = filtered_df['Purchases'].sum()
    st.markdown(f"""
    <div class="kpi-card">
        <div>إجمالي المشتريات</div>
        <div class="kpi-value">{total_purchases:,.0f}</div>
        <div style="font-size:12px;">قطعة</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    total_sales = filtered_df['Sales'].sum()
    st.markdown(f"""
    <div class="kpi-card">
        <div>إجمالي المبيعات</div>
        <div class="kpi-value">{total_sales:,.0f}</div>
        <div style="font-size:12px;">قطعة</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    total_value = filtered_df['Total Value'].sum()
    st.markdown(f"""
    <div class="kpi-card">
        <div>القيمة الإجمالية</div>
        <div class="kpi-value">${total_value:,.0f}</div>
        <div style="font-size:12px;">دولار</div>
    </div>
    """, unsafe_allow_html=True)

# ============== الرسوم البيانية ==============
st.markdown("---")
st.markdown("### 📊 الرسوم البيانية")

tab1, tab2, tab3 = st.tabs(["التوزيع حسب الفئة", "حركة المخزون", "البيانات التفصيلية"])

with tab1:
    # مخطط دائري للتوزيع
    if 'Category' in filtered_df.columns:
        category_summary = filtered_df.groupby('Category')['Closing'].sum().reset_index()
        fig = px.pie(category_summary, values='Closing', names='Category', title='توزيع المخزون حسب الفئة')
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    # مخطط شريطي للمقارنة بين السنوات
    if 'Year' in filtered_df.columns:
        yearly_summary = filtered_df.groupby('Year').agg({
            'Purchases': 'sum',
            'Sales': 'sum',
            'Closing': 'sum'
        }).reset_index()
        
        fig = go.Figure(data=[
            go.Bar(name='المشتريات', x=yearly_summary['Year'], y=yearly_summary['Purchases']),
            go.Bar(name='المبيعات', x=yearly_summary['Year'], y=yearly_summary['Sales']),
            go.Bar(name='المخزون', x=yearly_summary['Year'], y=yearly_summary['Closing'])
        ])
        fig.update_layout(title='حركة المخزون عبر السنوات', barmode='group')
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    # عرض البيانات
    st.dataframe(filtered_df, use_container_width=True, height=300)
    
    # خيارات التصدير
    col1, col2 = st.columns(2)
    with col1:
        # تصدير CSV
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تصدير CSV",
            data=csv,
            file_name="inventory_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # تصدير Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Inventory')
        excel_data = excel_buffer.getvalue()
        st.download_button(
            label="📊 تصدير Excel",
            data=excel_data,
            file_name="inventory_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ============== تذييل الصفحة ==============
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**تاريخ التشغيل:** {datetime.now().strftime('%Y-%m-%d')}")
with col2:
    st.markdown("**التطبيق جاهز للاستخدام** ✅")
with col3:
    st.markdown("**الإصدار:** 1.0.0")

st.success("تم تحميل لوحة التحكم بنجاح! استخدم الفلاتر في الشريط الجانبي.")