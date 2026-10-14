"""
InsightIQ Reports and Export Generation Engine.
Generates compliant CSV downloads (with formula injection protection)
and high-resolution executive summary PDF reports via ReportLab.
"""
import io
import datetime
import pandas as pd
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from backend.database import get_db_connection
from backend.analytics.kpis import build_filter_where_clause, get_dashboard_kpis, get_category_breakdown, get_region_breakdown
from backend.analytics.insights import generate_business_insights
from backend.analytics.segmentation import calculate_customer_segmentation
from backend.analytics.data_cleaning import sanitize_formula_injection

def generate_filtered_sales_csv(
    dataset_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None
) -> str:
    """Exports filtered dataset records to CSV with formula injection prevention."""
    conn = get_db_connection()
    where_clause, params = build_filter_where_clause(
        dataset_id, start_date, end_date, region, category, segment, product
    )
    
    df = pd.read_sql_query(f"""
        SELECT 
            order_id, order_date, customer_id, customer_name, segment,
            region, country, city, state, category, sub_category, product_name,
            quantity, unit_price, discount, shipping_cost, revenue, cost, profit
        FROM sales_data
        {where_clause}
        ORDER BY order_date ASC
    """, conn, params=params)
    conn.close()
    
    # Sanitize string columns
    for col in df.select_dtypes(include=["object", "string"]):
        df[col] = df[col].apply(sanitize_formula_injection)
        
    return df.to_csv(index=False)

def generate_segmentation_csv(dataset_id: str) -> str:
    """Exports RFM customer segmentation report to CSV."""
    seg_data = calculate_customer_segmentation(dataset_id)
    customers = seg_data.get("customers_sample", [])
    df = pd.DataFrame(customers)
    
    for col in df.select_dtypes(include=["object", "string"]):
        df[col] = df[col].apply(sanitize_formula_injection)
        
    return df.to_csv(index=False)

def generate_insights_csv(
    dataset_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None
) -> str:
    """Exports business insights to CSV."""
    insights = generate_business_insights(dataset_id, start_date, end_date, region, category, segment, product)
    df = pd.DataFrame(insights)
    return df.to_csv(index=False)

def generate_executive_pdf_report(
    dataset_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None
) -> bytes:
    """
    Builds a professional executive PDF report containing certified KPIs,
    category performance, regional distribution, and key business findings.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        spaceAfter=14
    )
    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=12,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    table_text = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1e293b')
    )
    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    story = []
    
    # 1. Header Banner
    story.append(Paragraph("InsightIQ — Executive Business Intelligence Report", title_style))
    gen_time = datetime.datetime.now().strftime("%B %d, %Y at %H:%M:%S")
    filters_desc = f"Filters: Date Range [{start_date or 'All'} to {end_date or 'All'}], Region [{region or 'All'}], Category [{category or 'All'}]"
    story.append(Paragraph(f"Generated on {gen_time} | Dataset: {dataset_id}<br/>{filters_desc}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=14))
    
    # 2. Executive KPI Summary Cards
    kpis = get_dashboard_kpis(dataset_id, start_date, end_date, region, category, segment, product)
    story.append(Paragraph("1. Executive Financial Summary", h2_style))
    
    kpi_table_data = [
        [
            Paragraph("Metric", table_header),
            Paragraph("Current Period Value", table_header),
            Paragraph("Comparison Baseline", table_header),
            Paragraph("Growth / Health", table_header)
        ],
        [
            Paragraph("Total Revenue", table_text),
            Paragraph(f"${kpis['total_revenue']:,.2f}", table_text),
            Paragraph(f"${kpis['prev_revenue']:,.2f}" if kpis["has_comparison_baseline"] else "N/A", table_text),
            Paragraph(f"{kpis['revenue_growth_pct']:+.1f}%" if kpis["revenue_growth_pct"] is not None else "Baseline Active", table_text)
        ],
        [
            Paragraph("Total Net Profit", table_text),
            Paragraph(f"${kpis['total_profit']:,.2f}", table_text),
            Paragraph(f"${kpis['prev_profit']:,.2f}" if kpis["has_comparison_baseline"] else "N/A", table_text),
            Paragraph(f"{kpis['profit_growth_pct']:+.1f}%" if kpis["profit_growth_pct"] is not None else "Healthy", table_text)
        ],
        [
            Paragraph("Net Profit Margin", table_text),
            Paragraph(f"{kpis['profit_margin_pct']:.2f}%", table_text),
            Paragraph("Benchmark: >20%", table_text),
            Paragraph("Optimal" if kpis["profit_margin_pct"] >= 20.0 else "Attention Required", table_text)
        ],
        [
            Paragraph("Total Completed Orders", table_text),
            Paragraph(f"{kpis['total_orders']:,}", table_text),
            Paragraph("Unique Orders", table_text),
            Paragraph(f"AOV: ${kpis['average_order_value']:.2f}", table_text)
        ],
        [
            Paragraph("Active Customer Accounts", table_text),
            Paragraph(f"{kpis['total_customers']:,}", table_text),
            Paragraph("Unique Customer IDs", table_text),
            Paragraph("Diversified Base", table_text)
        ]
    ]
    
    t_kpis = Table(kpi_table_data, colWidths=[150, 130, 130, 130])
    t_kpis.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white]),
    ]))
    story.append(t_kpis)
    story.append(Spacer(1, 14))
    
    # 3. Category Performance Breakdown
    story.append(Paragraph("2. Product Category Performance", h2_style))
    categories = get_category_breakdown(dataset_id, start_date, end_date, region, category, segment, product)
    
    cat_table_data = [
        [
            Paragraph("Category", table_header),
            Paragraph("Revenue ($)", table_header),
            Paragraph("Profit ($)", table_header),
            Paragraph("Margin (%)", table_header),
            Paragraph("Share of Total (%)", table_header)
        ]
    ]
    for c in categories:
        cat_table_data.append([
            Paragraph(c["category"], table_text),
            Paragraph(f"${c['revenue']:,.2f}", table_text),
            Paragraph(f"${c['profit']:,.2f}", table_text),
            Paragraph(f"{c['profit_margin']:.1f}%", table_text),
            Paragraph(f"{c['share_pct']:.1f}%", table_text)
        ])
        
    t_cat = Table(cat_table_data, colWidths=[150, 100, 100, 90, 100])
    t_cat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white]),
    ]))
    story.append(t_cat)
    story.append(Spacer(1, 14))
    
    # 4. Key Business Insights & Recommendations
    story.append(Paragraph("3. Certified Analytical Findings & Strategic Actions", h2_style))
    insights = generate_business_insights(dataset_id, start_date, end_date, region, category, segment, product)
    
    for idx, item in enumerate(insights[:4], 1):
        story.append(Paragraph(f"<b>{idx}. {item['headline']}</b>", ParagraphStyle('IH', parent=body_style, fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#1e293b'))))
        story.append(Paragraph(f"• <b>Supporting Metric:</b> {item['supporting_metric']}", body_style))
        story.append(Paragraph(f"• <b>Business Interpretation:</b> {item['interpretation']}", body_style))
        story.append(Paragraph(f"• <b>Recommended Action:</b> {item['recommendation']}", body_style))
        story.append(Spacer(1, 6))
        
    # 5. Customer Segmentation Summary
    story.append(Spacer(1, 8))
    story.append(Paragraph("4. Customer Segmentation Distribution (RFM)", h2_style))
    seg_data = calculate_customer_segmentation(dataset_id)
    segments = seg_data.get("segments_summary", [])
    
    seg_table_data = [
        [
            Paragraph("Segment", table_header),
            Paragraph("Customer Count", table_header),
            Paragraph("Total Revenue ($)", table_header),
            Paragraph("Rev Share (%)", table_header),
            Paragraph("Avg Frequency", table_header)
        ]
    ]
    for s in segments[:5]:
        seg_table_data.append([
            Paragraph(s["segment_name"], table_text),
            Paragraph(f"{s['customer_count']:,} ({s['customer_percentage']}%)", table_text),
            Paragraph(f"${s['total_revenue']:,.2f}", table_text),
            Paragraph(f"{s['revenue_percentage']:.1f}%", table_text),
            Paragraph(f"{s['avg_frequency']:.1f} orders", table_text)
        ])
        
    t_seg = Table(seg_table_data, colWidths=[140, 100, 110, 90, 100])
    t_seg.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f766e')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white]),
    ]))
    story.append(t_seg)
    
    # 6. Disclaimer & Limitations
    story.append(Spacer(1, 16))
    story.append(Paragraph("<b>Analytical Limitations & Methodology:</b> Metrics computed strictly from uploaded/seeded dataset records without external extrapolation. Predictive forecasts and customer segment clusters provide statistical guidelines and should be evaluated alongside domain operational context.", ParagraphStyle('Disc', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7.5, textColor=colors.HexColor('#64748b'))))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
