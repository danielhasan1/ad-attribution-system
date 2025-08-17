# facebook_ads_generator.py
import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker
import numpy as np
import logging

from database.connection import load_campaign_data, load_performance_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker()

campaign_objectives = ['Brand Awareness', 'Lead Generation', 'Sales Conversion', 'App Install', 'Video Views']
target_audiences = ['Men 25-34', 'Women 18-45', 'Parents', 'Tech Professionals', 'Students']


def generate_facebook_campaigns(num_campaigns=20):
    campaigns = []
    for i in range(num_campaigns):
        campaign_name = f"{random.choice(campaign_objectives)} - {random.choice(target_audiences)} - {fake.city()}"
        campaign = {
            'campaign_id': f'fb_camp_{i + 1:03d}',
            'platform': 'facebook',
            'product':f'Product_{i + 1:03d}',
            'campaign_name': f"FB Campaign {campaign_name}",
            'campaign_type': random.choice(['awareness', 'conversion', 'engagement']),
            'daily_budget': random.uniform(1000, 50000),
            'status': random.choice(['active', 'paused']),
            'created_date': fake.date_between(start_date='-90d', end_date='today'),
            'product': f'Product_{i + 1:03d}',
        }
        campaigns.append(campaign)
    return pd.DataFrame(campaigns)


# def generate_facebook_performance(campaigns_df, days=30):
#     performance_data = []
#
#     for _, campaign in campaigns_df.iterrows():
#         for i in range(days):
#             date = datetime.now().date() - timedelta(days=i)
#
#             # Generate realistic performance metrics
#             base_impressions = random.randint(1000, 100000)
#             ctr = random.uniform(0.5, 3.5)  # 0.5% to 3.5% CTR
#             clicks = int(base_impressions * (ctr / 100))
#
#             cpc = random.uniform(0.5, 15.0)  # ₹0.5 to ₹15 per click
#             spend = clicks * cpc
#
#             conversion_rate = random.uniform(1, 8)  # 1% to 8% conversion rate
#             conversions = int(clicks * (conversion_rate / 100))
#
#             avg_order_value = random.uniform(500, 5000)
#             revenue = conversions * avg_order_value
#
#             perf = {
#                 'date': date,
#                 'campaign_id': campaign['campaign_id'],
#                 'impressions': base_impressions,
#                 'clicks': clicks,
#                 'spend': round(spend, 2),
#                 'conversions': conversions,
#                 'revenue': round(revenue, 2),
#                 'cpc': round(cpc, 2),
#                 'cpm': round((spend / base_impressions) * 1000, 2),
#                 'ctr': round(ctr, 2)
#             }
#             performance_data.append(perf)
#
#     return pd.DataFrame(performance_data)



def generate_facebook_performance(campaigns_df, days=30):
    performance_data = []

    # Industry benchmark constraints
    # industry_benchmarks = {
    #     'awareness': {'ctr_range': (1.2, 2.8), 'cvr_range': (2, 5), 'cpc_range': (0.6, 1.2)},
    #     'conversion': {'ctr_range': (0.8, 2.2), 'cvr_range': (5, 12), 'cpc_range': (1.5, 8.5)},
    #     'engagement': {'ctr_range': (1.8, 3.5), 'cvr_range': (3, 8), 'cpc_range': (0.4, 1.8)}
    # }

    # more realistic
    industry_benchmarks = {
        'awareness': {'ctr_range': (0.8, 1.8), 'cvr_range': (2, 5), 'cpc_range': (0.6, 1.2)},
        'conversion': {'ctr_range': (0.9, 2.2), 'cvr_range': (5, 12), 'cpc_range': (1.5, 8.5)},
        'engagement': {'ctr_range': (1.2, 2.8), 'cvr_range': (3, 8), 'cpc_range': (0.4, 1.8)}
    }


    for _, campaign in campaigns_df.iterrows():
        # Campaign gets consistent performance characteristics
        campaign_type = campaign['campaign_type']
        benchmarks = industry_benchmarks[campaign_type]

        # Base performance stays consistent for this campaign
        base_ctr = np.random.uniform(*benchmarks['ctr_range'])
        base_cvr = np.random.uniform(*benchmarks['cvr_range'])
        base_cpc = np.random.uniform(*benchmarks['cpc_range'])

        for i in range(days):
            date = datetime.now().date() - timedelta(days=i)

            # Add day-of-week seasonality
            day_adjustment = 0.0
            if date.weekday() in [5, 6]:  # Weekend
                day_adjustment = -0.3
            elif date.weekday() in [1, 2, 3]:  # Tue-Thu peak
                day_adjustment = 0.2

            # Daily variance around base performance
            # daily_ctr = base_ctr * day_adjustment * np.random.uniform(0.8, 1.2)
            # more realistic ctr calc
            daily_variance = np.random.uniform(-0.2, 0.2)  # Reduced variance
            daily_ctr = max(0.1, base_ctr + day_adjustment + daily_variance) # floor at 0.1%
            # daily_ctr = min(base_ctr * day_adjustment * daily_variance, 3.0)  # Hard cap at 3%
            daily_ctr = min(daily_ctr, 3.0)  # Ceiling at 3.0%
            daily_cpc = base_cpc * np.random.uniform(0.9, 1.1)
            daily_cvr = base_cvr * np.random.uniform(0.7, 1.3)

            # Calculate everything from CTR/CPC
            impressions = int(campaign['daily_budget'] / daily_cpc / (daily_ctr / 100) * np.random.uniform(0.5, 1.5))
            clicks = int(impressions * (daily_ctr / 100))
            spend = clicks * round(daily_cpc,2)
            conversions = int(clicks * (daily_cvr / 100))

            # ADD THIS: Revenue calculation
            avg_order_value = random.uniform(500, 5000)  # ₹500 to ₹5000 per conversion
            revenue = conversions * avg_order_value

            perf = {
                'date': date,
                'campaign_id': campaign['campaign_id'],
                'impressions': impressions,
                'clicks': clicks,
                'spend': round(spend, 2),
                'conversions': conversions,
                'revenue': round(revenue, 2),  # Now this will work
                'cpc': round(daily_cpc, 2),
                'cpm': round((spend / impressions) * 1000, 2),
                'ctr': round(daily_ctr, 2)
            }
            performance_data.append(perf)

    return pd.DataFrame(performance_data)

def validate_campaign_data(df):
    issues = []
    low_budget_df = df[df['daily_budget'] < 100] # way too low
    high_budget_df = df[df['daily_budget'] > 100000] # suspicious kinda way too high
    invalid_status = df[~df['status'].isin(['active', 'paused', 'draft'])]
    if not low_budget_df.empty:
        issues.append(f"low budget: {len(low_budget_df)} campaigns")
    if not high_budget_df.empty:
        issues.append(f"high budget: {len(high_budget_df)} campaigns")
    if not invalid_status.empty:
        issues.append(f"invalid status: {len(invalid_status)} campaigns")
    return issues

def validate_performance_data(df):
    issues = []
    high_ctr_df = df[df['ctr'] > 3.5]
    inconsistent_spend_df = df[abs(df['spend'] - (df['clicks'] * df['cpc'])) > 0.01]
    negative_metrics_df = df[(df['clicks'] < 0) | (df['spend'] < 0) | (df['impressions'] < 0)]
    if not high_ctr_df.empty:
        issues.append(f"{len(high_ctr_df)} records with CTR > 3.5%")
    if not inconsistent_spend_df.empty:
        issues.append(f"{len(inconsistent_spend_df)} records with spend/cpc mismatch")
    if not negative_metrics_df.empty:
        issues.append(f"{len(negative_metrics_df)} records with negative metrics")
    return issues


if __name__ == "__main__":
    campaigns_df = generate_facebook_campaigns(20)
    performance_df = generate_facebook_performance(campaigns_df, 30)
    campaign_issues = validate_campaign_data(campaigns_df)
    performance_issues = validate_performance_data(performance_df)
    if campaign_issues or performance_issues:
        logger.warning(f"Campaign issues: {campaign_issues}")
        logger.warning(f"Performance issues: {performance_issues}")
        raise ValueError("Campaign issues and performance issues is there in data")
    try:
        # Load campaigns
        campaign_count = load_campaign_data(campaigns_df)
        print(f"Loaded {campaign_count} campaigns")

        # Load performance data
        perf_count = load_performance_data(performance_df)
        print(f"Loaded {perf_count} performance records")


    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise