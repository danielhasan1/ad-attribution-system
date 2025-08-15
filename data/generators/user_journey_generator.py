# user_journey_generator.py
import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker
import logging

from database.connection import read_campaign_data, load_journey_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


fake = Faker()


def generate_user_journeys(campaigns_df, num_users=10000):
    touchpoints = []

    for user_id in range(1, num_users + 1):
        # Number of touchpoints per user (1-8)
        num_touchpoints = random.choices([1, 2, 3, 4, 5, 6, 7, 8],
                                         weights=[30, 25, 20, 15, 5, 3, 1, 1])[0]

        user_start_time = fake.date_time_between(start_date='-30d', end_date='now')

        for touch_num in range(num_touchpoints):
            # Time between touchpoints (hours to days)
            time_gap = timedelta(
                hours=random.randint(1, 48),
                minutes=random.randint(0, 59)
            )

            touchpoint_time = user_start_time + (time_gap * touch_num)

            # Select random campaign
            campaign = campaigns_df.sample(1).iloc[0]

            touchpoint = {
                'user_id': f'user_{user_id:06d}',
                'timestamp': touchpoint_time,
                'platform': campaign['platform'],
                'campaign_id': campaign['campaign_id'],
                'touchpoints_type': random.choices(
                    ['impression', 'click', 'view'],
                    weights=[60, 30, 10]
                )[0],
                'device_type': random.choice(['mobile', 'desktop', 'tablet']),
                'geo_location': fake.city()
            }
            touchpoints.append(touchpoint)

    return pd.DataFrame(touchpoints)


if __name__ == '__main__':
    campaigns_df = read_campaign_data()
    try:

        journey_count = load_journey_data(generate_user_journeys(campaigns_df))

        print(f"Loaded {journey_count} user journeys to database")

    except Exception as e:
        logger.error(f"Database loading failed: {e}")
        raise


