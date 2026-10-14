"""
InsightIQ Customer Segmentation Engine.
Implements deterministic RFM (Recency, Frequency, Monetary) quintile scoring
and Scikit-learn K-Means clustering with feature standardization.
Produces documented customer segments, revenue contributions, and strategic action plans.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from backend.database import get_db_connection

SEGMENT_STRATEGIES = {
    "Champions": {
        "description": "High spending, frequent buyers who purchased very recently. The backbone of enterprise revenue.",
        "strategy": "Reward with VIP status, early access to premium product releases, and personalized loyalty incentives."
    },
    "Loyal Customers": {
        "description": "Consistent purchasers with steady order frequency and healthy lifetime monetary value.",
        "strategy": "Upsell higher-tier products, offer cross-category bundles, and solicit product feedback/reviews."
    },
    "Potential Loyalists": {
        "description": "Recent buyers with promising spend who have placed 2-3 orders with potential for habitual purchase.",
        "strategy": "Engage with targeted category recommendations, automated replenishment reminders, and membership benefits."
    },
    "At-Risk Customers": {
        "description": "Previously frequent buyers with substantial historical spend who haven't ordered recently.",
        "strategy": "Execute proactive win-back re-engagement campaigns with tailored discount incentives and customer service check-ins."
    },
    "Promising & New": {
        "description": "First-time or recent shoppers with moderate purchase volume.",
        "strategy": "Onboard smoothly, introduce customer loyalty programs, and provide timely post-purchase support."
    },
    "Hibernating & Inactive": {
        "description": "Low frequency, low spend customers with no transactional activity over extended periods.",
        "strategy": "Include in low-cost automated email reactivation workflows or sunset to optimize marketing spend."
    }
}

def calculate_customer_segmentation(dataset_id: str, use_kmeans: bool = True) -> Dict[str, Any]:
    """
    Computes RFM metrics and deterministic customer segment assignment.
    """
    conn = get_db_connection()
    df = pd.read_sql_query("""
        SELECT 
            customer_id,
            COALESCE(customer_name, customer_id) as customer_name,
            order_date,
            order_id,
            revenue
        FROM sales_data
        WHERE dataset_id = ?
    """, conn, params=[dataset_id])
    conn.close()
    
    if df.empty or len(df["customer_id"].unique()) < 5:
        return {
            "method": "RFM Rule-Based",
            "total_customers_analyzed": 0,
            "reference_date": "N/A",
            "segments_summary": [],
            "customers_sample": [],
            "rules_documentation": {
                "requirements": "Requires valid customer_id, order_date, and revenue fields with at least 5 distinct customers."
            },
            "kmeans_inertia": None
        }
        
    df["order_date"] = pd.to_datetime(df["order_date"])
    ref_date = df["order_date"].max() + pd.Timedelta(days=1)
    
    # Customer-level RFM aggregation
    rfm = df.groupby(["customer_id", "customer_name"]).agg(
        recency=("order_date", lambda d: (ref_date - d.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum")
    ).reset_index()
    
    rfm["monetary"] = rfm["monetary"].round(2)
    total_customers = len(rfm)
    total_grand_revenue = float(rfm["monetary"].sum())
    
    # Deterministic Quintile Scoring (1 to 5)
    # Recency: lower days = higher score (5 is most recent)
    rfm["r_score"] = pd.qcut(rfm["recency"].rank(method="first"), q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    
    # Frequency: higher count = higher score (5 is most frequent)
    # Using rank(method="first") guarantees quantile stability even with repeated frequency counts
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    
    # Monetary: higher spend = higher score (5 is highest spend)
    rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    
    # Segment Assignment Rules
    def assign_rfm_segment(row):
        r, f, m = row["r_score"], row["f_score"], row["m_score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif f >= 3 and m >= 3:
            return "Loyal Customers"
        elif r >= 4 and f >= 2:
            return "Potential Loyalists"
        elif r <= 2 and (f >= 3 or m >= 4):
            return "At-Risk Customers"
        elif r >= 4 and f == 1:
            return "Promising & New"
        else:
            return "Hibernating & Inactive"
            
    rfm["segment"] = rfm.apply(assign_rfm_segment, axis=1)
    
    # Optional K-Means Clustering
    kmeans_inertia = None
    if use_kmeans and total_customers >= 10:
        try:
            # Log transform to normalize skewed spend & frequency distributions
            rfm_log = np.log1p(rfm[["recency", "frequency", "monetary"]])
            scaler = StandardScaler()
            rfm_scaled = scaler.fit_transform(rfm_log)
            
            k = min(4, total_customers)
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            rfm["cluster_id"] = kmeans.fit_predict(rfm_scaled)
            kmeans_inertia = round(float(kmeans.inertia_), 2)
        except Exception:
            rfm["cluster_id"] = None
    else:
        rfm["cluster_id"] = None
        
    # Segment Summaries
    segments_summary = []
    for seg_name, meta in SEGMENT_STRATEGIES.items():
        sub = rfm[rfm["segment"] == seg_name]
        cnt = len(sub)
        if cnt == 0:
            continue
        seg_rev = float(sub["monetary"].sum())
        segments_summary.append({
            "segment_name": seg_name,
            "customer_count": cnt,
            "customer_percentage": round((cnt / total_customers) * 100.0, 2),
            "total_revenue": round(seg_rev, 2),
            "revenue_percentage": round((seg_rev / max(1.0, total_grand_revenue)) * 100.0, 2),
            "avg_recency_days": round(float(sub["recency"].mean()), 1),
            "avg_frequency": round(float(sub["frequency"].mean()), 1),
            "avg_monetary": round(float(sub["monetary"].mean()), 2),
            "description": meta["description"],
            "recommended_strategy": meta["strategy"]
        })
        
    # Sort segments by total revenue contribution descending
    segments_summary.sort(key=lambda s: s["total_revenue"], reverse=True)
    
    # Sample individual customers for table inspection
    sample_customers = []
    for _, row in rfm.head(100).iterrows():
        sample_customers.append({
            "customer_id": str(row["customer_id"]),
            "customer_name": str(row["customer_name"]),
            "recency_days": int(row["recency"]),
            "frequency_orders": int(row["frequency"]),
            "monetary_spend": float(row["monetary"]),
            "r_score": int(row["r_score"]),
            "f_score": int(row["f_score"]),
            "m_score": int(row["m_score"]),
            "rfm_segment": str(row["segment"]),
            "cluster_id": int(row["cluster_id"]) if pd.notna(row["cluster_id"]) else None
        })
        
    rules_doc = {
        "Recency (R)": "Measured in days since the most recent order relative to the dataset reference date. Scored 1 (least recent) to 5 (most recent).",
        "Frequency (F)": "Total count of distinct completed orders placed by the customer. Scored 1 (lowest) to 5 (highest).",
        "Monetary (M)": "Cumulative gross revenue generated by the customer. Scored 1 (lowest spend) to 5 (highest spend).",
        "Clustering Note": "K-Means clusters are descriptive groupings computed over log-standardized RFM vectors, providing an unsupervised perspective on behavioral grouping."
    }
    
    return {
        "method": "RFM Deterministic Scoring + K-Means",
        "total_customers_analyzed": total_customers,
        "reference_date": ref_date.strftime("%Y-%m-%d"),
        "segments_summary": segments_summary,
        "customers_sample": sample_customers,
        "rules_documentation": rules_doc,
        "kmeans_inertia": kmeans_inertia
    }
