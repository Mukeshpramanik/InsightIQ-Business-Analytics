"""
InsightIQ Business Insights Engine.
Generates deterministic, transparent rule-based analytical findings from the active dataset.
Every finding provides a concise headline, supporting metric, calculation methodology,
business interpretation, and actionable management recommendation.
"""
import pandas as pd
from typing import List, Dict, Any, Optional
from backend.database import get_db_connection
from backend.analytics.kpis import build_filter_where_clause, get_dashboard_kpis

def generate_business_insights(
    dataset_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Evaluates transparent analytical rules against active dataset transactions."""
    conn = get_db_connection()
    where_clause, params = build_filter_where_clause(
        dataset_id, start_date, end_date, region, category, segment, product
    )
    
    df = pd.read_sql_query(f"SELECT * FROM sales_data {where_clause}", conn, params=params)
    conn.close()
    
    if df.empty or len(df) < 5:
        return []
        
    insights = []
    
    # 1. Headline Growth & Margin Dynamics
    kpis = get_dashboard_kpis(dataset_id, start_date, end_date, region, category, segment, product)
    total_rev = kpis["total_revenue"]
    total_prof = kpis["total_profit"]
    margin_pct = kpis["profit_margin_pct"]
    
    if kpis["has_comparison_baseline"] and kpis["revenue_growth_pct"] is not None:
        growth = kpis["revenue_growth_pct"]
        if growth >= 5.0:
            insights.append({
                "id": "growth_positive",
                "type": "growth",
                "severity": "success",
                "headline": f"Strong Period Revenue Growth (+{growth}%)",
                "supporting_metric": f"+{growth}% Period-over-Period (${total_rev:,.2f} vs ${kpis['prev_revenue']:,.2f})",
                "calculation_basis": "Percentage variance between current period revenue and preceding baseline period of matching duration.",
                "interpretation": "Sales volume and order generation are trending positively, signaling healthy market demand and customer acquisition.",
                "recommendation": "Capitalize on sales momentum by ensuring inventory levels for high-velocity SKUs and expanding seasonal promotion campaigns."
            })
        elif growth <= -5.0:
            insights.append({
                "id": "growth_negative",
                "type": "growth",
                "severity": "warning",
                "headline": f"Revenue Contraction Detected ({growth}%)",
                "supporting_metric": f"{growth}% Period-over-Period (${total_rev:,.2f} vs ${kpis['prev_revenue']:,.2f})",
                "calculation_basis": "Percentage drop between current period revenue and preceding baseline period.",
                "interpretation": "Sales velocity has declined compared to the prior period, potentially indicating seasonal lulls or competitive pressures.",
                "recommendation": "Review churn drivers, revisit marketing attribution, and offer targeted reactivation promotions to win back sluggish accounts."
            })
            
    # Margin Health Rule
    if margin_pct < 15.0:
        insights.append({
            "id": "margin_compressed",
            "type": "risk",
            "severity": "warning",
            "headline": f"Compressed Overall Profit Margin ({margin_pct}%)",
            "supporting_metric": f"{margin_pct}% Net Margin (${total_prof:,.2f} profit on ${total_rev:,.2f} revenue)",
            "calculation_basis": "Total Profit divided by Total Revenue multiplied by 100.",
            "interpretation": "Operating margin is running below the healthy target benchmark of 20%, indicating elevated discounting or logistics overhead.",
            "recommendation": "Cap maximum promotional discount depth at 15% and audit carrier shipping surcharges to protect net profitability."
        })
    elif margin_pct >= 25.0:
        insights.append({
            "id": "margin_strong",
            "type": "opportunity",
            "severity": "success",
            "headline": f"Exceptional Profit Margin Performance ({margin_pct}%)",
            "supporting_metric": f"{margin_pct}% Net Margin (${total_prof:,.2f} profit on ${total_rev:,.2f} revenue)",
            "calculation_basis": "Total Profit divided by Total Revenue multiplied by 100.",
            "interpretation": "Strong unit economics and disciplined discounting are generating superior bottom-line returns per sales dollar.",
            "recommendation": "Reinvest a portion of high margin yields into customer acquisition and digital advertising to capture additional market share."
        })

    # 2. Product Level: High Volume / Low Margin (Margin Drag)
    prod_summary = df.groupby(["product_name", "category"]).agg(
        rev=("revenue", "sum"),
        prof=("profit", "sum"),
        qty=("quantity", "sum")
    ).reset_index()
    prod_summary["margin"] = (prod_summary["prof"] / prod_summary["rev"]) * 100.0
    prod_summary["rev_share"] = (prod_summary["rev"] / total_rev) * 100.0
    
    # Products with > 3% total revenue but < 10% margin
    drag_products = prod_summary[(prod_summary["rev_share"] >= 3.0) & (prod_summary["margin"] < 10.0)]
    if not drag_products.empty:
        worst_drag = drag_products.sort_values(by="rev_share", ascending=False).iloc[0]
        insights.append({
            "id": "product_margin_drag",
            "type": "risk",
            "severity": "warning",
            "headline": f"Profit Margin Drag on High-Volume Product: {worst_drag['product_name']}",
            "supporting_metric": f"{worst_drag['margin']:.1f}% Margin despite {worst_drag['rev_share']:.1f}% Revenue Share (${worst_drag['rev']:,.2f})",
            "calculation_basis": "Product represents >3% of total enterprise sales but delivers sub-10% net margin.",
            "interpretation": f"Although '{worst_drag['product_name']}' generates significant top-line revenue, high fulfillment costs or heavy discounting diminish its contribution to net profit.",
            "recommendation": "Renegotiate wholesale procurement pricing, scale back promotional discounts on this SKU, or bundle with higher-margin accessories."
        })

    # 3. Customer Concentration (Pareto Principle 80/20 Analysis)
    cust_rev = df.groupby("customer_id")["revenue"].sum().sort_values(ascending=False).values
    num_cust = len(cust_rev)
    if num_cust >= 10:
        top_20_count = max(1, int(num_cust * 0.20))
        top_20_rev = cust_rev[:top_20_count].sum()
        concentration_pct = round((top_20_rev / total_rev) * 100.0, 1)
        
        if concentration_pct >= 60.0:
            insights.append({
                "id": "pareto_concentration",
                "type": "concentration",
                "severity": "info",
                "headline": f"Customer Revenue Concentration: Top 20% Drive {concentration_pct}% of Sales",
                "supporting_metric": f"{top_20_count} of {num_cust} customers generate ${top_20_rev:,.2f} ({concentration_pct}%)",
                "calculation_basis": "Cumulative revenue generated by the top 20th percentile of customers by spend divided by total revenue.",
                "interpretation": "High revenue concentration indicates a valuable key-account cohort, but also introduces retention risk should key accounts defect.",
                "recommendation": "Assign dedicated account managers to top-tier accounts while running onboarding campaigns to expand the mid-tier customer base."
            })

    # 4. Regional Performance Disparity
    reg_summary = df.groupby("region").agg(
        rev=("revenue", "sum"),
        prof=("profit", "sum")
    ).reset_index()
    reg_summary["share"] = (reg_summary["rev"] / total_rev) * 100.0
    reg_summary["margin"] = (reg_summary["prof"] / reg_summary["rev"]) * 100.0
    
    if len(reg_summary) >= 3:
        top_reg = reg_summary.sort_values(by="rev", ascending=False).iloc[0]
        bottom_reg = reg_summary.sort_values(by="rev", ascending=True).iloc[0]
        
        insights.append({
            "id": "regional_dominance",
            "type": "opportunity",
            "severity": "info",
            "headline": f"Regional Sales Dominance: {top_reg['region']} Leads with {top_reg['share']:.1f}% Share",
            "supporting_metric": f"${top_reg['rev']:,.2f} Revenue with {top_reg['margin']:.1f}% Profit Margin in {top_reg['region']}",
            "calculation_basis": "Regional sales share computed as regional revenue divided by total revenue.",
            "interpretation": f"The {top_reg['region']} region serves as the primary revenue engine. Meanwhile, {bottom_reg['region']} represents an underpenetrated market ({bottom_reg['share']:.1f}% of total).",
            "recommendation": f"Adopt successful sales enablement strategies from {top_reg['region']} to stimulate growth in underperforming regions like {bottom_reg['region']}."
        })

    # 5. Discount Sensitivity Analysis
    discounted_df = df[df["discount"] > 0.15]
    if len(discounted_df) > 10:
        disc_margin = (discounted_df["profit"].sum() / max(1.0, discounted_df["revenue"].sum())) * 100.0
        standard_df = df[df["discount"] <= 0.15]
        std_margin = (standard_df["profit"].sum() / max(1.0, standard_df["revenue"].sum())) * 100.0
        
        if std_margin - disc_margin >= 10.0:
            insights.append({
                "id": "discount_cannibalization",
                "type": "risk",
                "severity": "warning",
                "headline": f"Discount Cannibalization: Deep Discounts Halve Margin ({disc_margin:.1f}% vs {std_margin:.1f}%)",
                "supporting_metric": f"{disc_margin:.1f}% Margin on >15% discounts vs {std_margin:.1f}% on standard orders",
                "calculation_basis": "Net margin comparison between orders with >15% discount vs low/zero discount transactions.",
                "interpretation": "Aggressive price cuts are eroding profitability without generating sufficient incremental volume to compensate.",
                "recommendation": "Implement strict discount approval thresholds for orders exceeding 15% discount to safeguard bottom-line margins."
            })
            
    return insights
