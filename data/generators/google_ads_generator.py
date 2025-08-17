# google_ads_generator.py
import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker
import numpy as np
import logging

from database.connection import load_campaign_data, load_performance_data

# Assuming you have similar database connection functions
# from database.connection import load_campaign_data, load_performance_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker()

# Google Ads specific data
campaign_types = ['Search', 'Display', 'Shopping', 'Video', 'Performance Max', 'App']
# bidding_strategies = ['Manual CPC', 'Enhanced CPC', 'Target CPA', 'Target ROAS', 'Maximize Clicks',
#                       'Maximize Conversions']
campaign_objectives = ['Brand Awareness', 'Lead Generation', 'Sales Conversion', 'App Install', 'Video Views']
target_audiences = ['Men 25-34', 'Women 18-45', 'Parents', 'Tech Professionals', 'Students']
ad_statuses = ['active', 'paused', 'removed']
match_types = ['EXACT', 'PHRASE', 'BROAD', 'BROAD_MODIFIED']
device_types = ['DESKTOP', 'MOBILE', 'TABLET']
networks = ['GOOGLE_SEARCH', 'SEARCH_PARTNERS', 'CONTENT', 'YOUTUBE_SEARCH', 'YOUTUBE_WATCH']

# Industry keywords for realistic campaign names
industries = ['E-commerce', 'Healthcare', 'Technology', 'Finance', 'Education', 'Travel', 'Food', 'Fashion',
              'Real Estate', 'Automotive']
keywords_base = ['buy', 'best', 'cheap', 'discount', 'sale', 'online', 'store', 'shop', 'deal', 'price', 'review',
                 'compare']


def generate_google_campaigns(num_campaigns=20):
    """Generate realistic Google Ads campaign data"""
    campaigns = []
    for i in range(num_campaigns):
        industry = random.choice(industries)
        campaign_name = f"{random.choice(campaign_types)} - {random.choice(campaign_objectives)} - {fake.city()}"

        campaign = {
            'campaign_id': f'gads_camp_{i + 1:03d}',
            'platform': 'google_ads',
            'campaign_name': campaign_name,
            'campaign_type': random.choice(campaign_types),
            # 'bidding_strategy': random.choice(bidding_strategies),
            'daily_budget': random.uniform(1000, 50000),  # Higher budgets for Google Ads
            # 'target_cpa': random.uniform(50, 500) if random.choice([True, False]) else None,
            # 'target_roas': random.uniform(200, 800) if random.choice([True, False]) else None,
            'status': random.choice(ad_statuses),
            # 'network_settings': random.choice(networks),
            # 'location_target': fake.country(),
            'created_date': fake.date_between(start_date='-90d', end_date='today'),
            'product': f'Product_{i + 1:03d}',
        }
        campaigns.append(campaign)
    return pd.DataFrame(campaigns)


def generate_google_performance(campaigns_df, days=30):
    """Generate realistic Google Ads performance data with industry benchmarks"""
    performance_data = []

    # Google Ads industry benchmarks by campaign type
    industry_benchmarks = {
        'search': {'ctr_range': (2.0, 5.0), 'cvr_range': (3, 8), 'cpc_range': (1.0, 5.0)},
        'display': {'ctr_range': (0.4, 1.2), 'cvr_range': (1, 3), 'cpc_range': (0.3, 2.0)},
        'shopping': {'ctr_range': (0.7, 2.5), 'cvr_range': (5, 15), 'cpc_range': (0.5, 3.0)},
        'video': {'ctr_range': (0.8, 2.0), 'cvr_range': (2, 6), 'cpc_range': (0.2, 1.5)},
        'performance_max': {'ctr_range': (1.5, 4.0), 'cvr_range': (4, 12), 'cpc_range': (0.8, 4.0)},
        'app': {'ctr_range': (1.0, 3.0), 'cvr_range': (8, 20), 'cpc_range': (0.5, 2.5)}
    }

    for _, campaign in campaigns_df.iterrows():
        # Campaign gets consistent performance characteristics
        campaign_type = campaign['campaign_type']
        benchmarks = industry_benchmarks.get(campaign_type, industry_benchmarks['search'])

        # Base performance stays consistent for this campaign
        base_ctr = np.random.uniform(*benchmarks['ctr_range'])
        base_cvr = np.random.uniform(*benchmarks['cvr_range'])
        base_cpc = np.random.uniform(*benchmarks['cpc_range'])

        for i in range(days):
            date = datetime.now().date() - timedelta(days=i)

            # Add day-of-week seasonality (Google Ads patterns)
            day_adjustment = 0.0
            if date.weekday() in [5, 6]:  # Weekend - varies by industry
                if campaign_type in ['shopping', 'display']:
                    day_adjustment = 0.1  # Shopping peaks on weekends
                else:
                    day_adjustment = -0.2  # B2B searches drop
            elif date.weekday() in [1, 2, 3]:  # Tue-Thu peak for B2B
                day_adjustment = 0.15

            # Daily variance around base performance
            daily_variance = np.random.uniform(-0.15, 0.15)
            daily_ctr = max(0.1, base_ctr + day_adjustment + daily_variance)
            daily_ctr = min(daily_ctr, 8.0)  # Google Ads can have higher CTRs than FB
            daily_cpc = base_cpc * np.random.uniform(0.85, 1.15)
            daily_cvr = base_cvr * np.random.uniform(0.6, 1.4)

            # Calculate metrics from daily budget and performance
            impressions = int(campaign['daily_budget'] / daily_cpc / (daily_ctr / 100) * np.random.uniform(0.4, 1.6))
            clicks = int(impressions * (daily_ctr / 100))
            cost = clicks * round(daily_cpc, 2)
            conversions = int(clicks * (daily_cvr / 100))

            # # Google Ads specific metrics
            # avg_position = random.uniform(1.1, 4.0)  # Average ad position
            # search_impression_share = random.uniform(15, 85)  # % of eligible impressions
            # quality_score = random.randint(3, 10)  # Quality Score 1-10

            # Revenue calculation (varies by campaign type)
            if campaign_type == 'shopping':
                avg_order_value = random.uniform(800, 3000)
            elif campaign_type == 'app':
                avg_order_value = random.uniform(50, 200)  # Lower for app installs
            else:
                avg_order_value = random.uniform(300, 2500)

            revenue = conversions * avg_order_value

            # perf = {
            #     'date': date,
            #     'campaign_id': campaign['campaign_id'],
            #     'impressions': impressions,
            #     'clicks': clicks,
            #     'cost': round(cost, 2),
            #     'conversions': conversions,
            #     'revenue': round(revenue, 2),
            #     'cpc': round(daily_cpc, 2),
            #     'cpm': round((cost / impressions) * 1000, 2) if impressions > 0 else 0,
            #     'ctr': round(daily_ctr, 2),
            #     'conversion_rate': round(daily_cvr, 2),
            #     'avg_position': round(avg_position, 1),
            #     'search_impression_share': round(search_impression_share, 2),
            #     'quality_score': quality_score,
            #     'cost_per_conversion': round(cost / conversions, 2) if conversions > 0 else 0,
            #     'roas': round(revenue / cost, 2) if cost > 0 else 0
            # }
            perf = {
                'date': date,
                'campaign_id': campaign['campaign_id'],
                'impressions': impressions,
                'clicks': clicks,
                'spend': round(cost, 2),
                'conversions': conversions,
                'revenue': round(revenue, 2),
                'cpc': round(daily_cpc, 2),
                'cpm': round((cost / impressions) * 1000, 2) if impressions > 0 else 0,
                'ctr': round(daily_ctr, 2)
            }
            performance_data.append(perf)

    return pd.DataFrame(performance_data)


def generate_keyword_data(campaigns_df, keywords_per_campaign=10):
    """Generate keyword-level data for Google Ads"""
    keyword_data = []

    for _, campaign in campaigns_df.iterrows():
        for j in range(keywords_per_campaign):
            industry = random.choice(industries).lower()
            keyword_base = random.choice(keywords_base)
            keyword_text = f"{keyword_base} {industry}"

            keyword = {
                'keyword_id': f'kw_{campaign["campaign_id"]}_{j + 1:02d}',
                'campaign_id': campaign['campaign_id'],
                'keyword': keyword_text,
                'match_type': random.choice(match_types),
                'status': random.choice(ad_statuses),
                'max_cpc': random.uniform(0.5, 20.0),
                'quality_score': random.randint(1, 10),
                'search_volume': random.randint(100, 50000),
                'competition': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'suggested_bid': random.uniform(0.3, 15.0)
            }
            keyword_data.append(keyword)

    return pd.DataFrame(keyword_data)


def validate_campaign_data(df):
    """Validate Google Ads campaign data for realistic constraints"""
    issues = []

    # Budget validation
    low_budget_df = df[df['daily_budget'] < 100]
    high_budget_df = df[df['daily_budget'] > 100000]

    # Status validation
    invalid_status = df[~df['status'].isin(ad_statuses)]

    # Campaign type validation
    invalid_type = df[~df['campaign_type'].isin(campaign_types)]

    if not low_budget_df.empty:
        issues.append(f"Low budget: {len(low_budget_df)} campaigns")
    if not high_budget_df.empty:
        issues.append(f"High budget: {len(high_budget_df)} campaigns")
    if not invalid_status.empty:
        issues.append(f"Invalid status: {len(invalid_status)} campaigns")
    if not invalid_type.empty:
        issues.append(f"Invalid campaign type: {len(invalid_type)} campaigns")

    return issues


def validate_performance_data(df):
    """Validate Google Ads performance data for realistic metrics"""
    issues = []

    # CTR validation (Google Ads can have higher CTRs than Facebook)
    high_ctr_df = df[df['ctr'] > 8.0]
    low_ctr_df = df[df['ctr'] < 0.1]

    # Cost consistency check
    inconsistent_cost_df = df[abs(df['spend'] - (df['clicks'] * df['cpc'])) > 0.1]

    # Negative metrics check
    negative_metrics_df = df[(df['clicks'] < 0) | (df['spend'] < 0) | (df['impressions'] < 0)]

    # Quality Score validation
    # invalid_qs_df = df[(df['quality_score'] < 1) | (df['quality_score'] > 10)]

    # ROAS validation (should be positive when there's revenue)
    # invalid_roas_df = df[(df['revenue'] > 0) & (df['roas'] <= 0)]

    if not high_ctr_df.empty:
        issues.append(f"{len(high_ctr_df)} records with CTR > 8.0%")
    if not low_ctr_df.empty:
        issues.append(f"{len(low_ctr_df)} records with CTR < 0.1%")
    if not inconsistent_cost_df.empty:
        issues.append(f"{len(inconsistent_cost_df)} records with cost/cpc mismatch")
    if not negative_metrics_df.empty:
        issues.append(f"{len(negative_metrics_df)} records with negative metrics")
    # if not invalid_qs_df.empty:
    #     issues.append(f"{len(invalid_qs_df)} records with invalid Quality Score")
    # if not invalid_roas_df.empty:
    #     issues.append(f"{len(invalid_roas_df)} records with invalid ROAS")

    return issues


if __name__ == "__main__":
    try:
        # Generate campaign data
        logger.info("Generating Google Ads campaign data...")
        campaigns_df = generate_google_campaigns(20)

        # Generate performance data
        logger.info("Generating performance data...")
        performance_df = generate_google_performance(campaigns_df, 30)

        # Generate keyword data
        # logger.info("Generating keyword data...")
        # keywords_df = generate_keyword_data(campaigns_df, 8)

        # Validate data quality
        logger.info("Validating data quality...")
        campaign_issues = validate_campaign_data(campaigns_df)
        performance_issues = validate_performance_data(performance_df)

        if campaign_issues or performance_issues:
            logger.warning(f"Campaign issues: {campaign_issues}")
            logger.warning(f"Performance issues: {performance_issues}")
            raise ValueError

        # If there are critical issues, raise an error
        # critical_issues = [issue for issue in campaign_issues + performance_issues
        #                    if 'negative metrics' in issue or 'invalid' in issue.lower()]

        # if critical_issues:
        #     raise ValueError(f"Critical data quality issues: {critical_issues}")

        # # Print summary statistics
        # print("\n" + "=" * 50)
        # print("GOOGLE ADS DATA GENERATION SUMMARY")
        # print("=" * 50)
        # print(f"Campaigns generated: {len(campaigns_df)}")
        # print(f"Performance records: {len(performance_df)}")
        # print(f"Keywords generated: {len(keywords_df)}")
        # print(f"Date range: {performance_df['date'].min()} to {performance_df['date'].max()}")

        # Performance summary
        # total_cost = performance_df['cost'].sum()
        # total_revenue = performance_df['revenue'].sum()
        # avg_ctr = performance_df['ctr'].mean()
        # avg_cpc = performance_df['cpc'].mean()

        # print(f"\nPerformance Summary:")
        # print(f"Total Cost: ₹{total_cost:,.2f}")
        # print(f"Total Revenue: ₹{total_revenue:,.2f}")
        # print(f"Overall ROAS: {total_revenue / total_cost:.2f}" if total_cost > 0 else "ROAS: N/A")
        # print(f"Average CTR: {avg_ctr:.2f}%")
        # print(f"Average CPC: ₹{avg_cpc:.2f}")


        # Uncomment these lines if you have database connection functions
        try:
            # Load campaigns
            campaign_count = load_campaign_data(campaigns_df)
            print(f"Loaded {campaign_count} campaigns to database")

            # Load performance data
            perf_count = load_performance_data(performance_df)
            print(f"Loaded {perf_count} performance records to database")

        except Exception as e:
            logger.error(f"Database loading failed: {e}")
            raise

    except Exception as e:
        logger.error(f"Google Ads data generation pipeline failed: {e}")
        raise