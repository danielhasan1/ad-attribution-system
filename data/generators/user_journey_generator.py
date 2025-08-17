# user_journey_generator.py
import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker
import logging
from functools import partial

from database.connection import read_campaign_data, load_journey_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


fake = Faker()

import random

def build_journey_types(num_touchpoints,
                        p_convert=0.35,                     # chance user converts
                        mid_mix_weights={'impression': 0.7, 'view': 0.3},  # middle-step mix
                        force_first_impression=True):
    """
    Returns an ordered list like: ['impression', 'view', 'impression', 'click'].
    Ensures chronological funnel and lets you tune realism via probabilities.
    """

    # 0) Edge cases
    if num_touchpoints <= 0:
        return []

    journey = []

    # 1) First touch
    if force_first_impression:
        journey.append('impression')
        remaining = num_touchpoints - 1
    else:
        # if you *don’t* want to force it, you can sample first touch too
        first = random.choices(['impression', 'view'], weights=[0.8, 0.2])[0]
        journey.append(first)
        remaining = num_touchpoints - 1

    if remaining <= 0:
        return journey

    # 2) Decide if this user converts at all
    converts = random.random() < p_convert

    # 3) If converts, reserve 1 slot at the end for 'click'
    #    (unless there’s only 1 slot total)
    if converts and remaining >= 1:
        middle_slots = remaining - 1  # last one becomes 'click'
    else:
        middle_slots = remaining

    # 4) Fill middle slots using weighted mix (impression/view)
    mid_events = list(mid_mix_weights.keys())
    mid_weights = list(mid_mix_weights.values())

    for _ in range(max(0, middle_slots)):
        journey.append(random.choices(mid_events, weights=mid_weights)[0])

    # 5) Append conversion if applicable
    if converts and len(journey) < num_touchpoints:
        journey.append('click')

    # Safety: if somehow we’re short (e.g., p_convert=False but small num_touchpoints),
    # pad with impression/view using the same mix
    while len(journey) < num_touchpoints:
        journey.append(random.choices(mid_events, weights=mid_weights)[0])

    return journey

def generate_user_journeys(campaigns_df, num_users=10000):
    touchpoints = []
    last_time = {}
    campain_seen = {}
    for user_id in range(1, num_users + 1):
        # Number of touchpoints per user (1-8)
        num_touchpoints = random.choices([1, 2, 3, 4, 5, 6, 7, 8],
                                         weights=[30, 25, 20, 15, 5, 3, 1, 1])[0]

        user_start_time = fake.date_time_between(start_date='-30d', end_date='now')
        # journey_types = ['impression']
        # if num_touchpoints > 1:
        #     journey_types += random.choices(['view', 'impression'], k=num_touchpoints - 2)
        # if num_touchpoints > 2:
        #     journey_types.append('click')
        # print(journey_types)
        curr_user_id = f'user_{user_id:06d}'

        journeys_partial = partial(build_journey_types, num_touchpoints)

        # print(journey, num_touchpoints)
        for touch_num in range(num_touchpoints):
            campaign = campaigns_df.sample(1).iloc[0]
            if campaign['campaign_id'] not in campain_seen:
                campain_seen[campaign['campaign_id']] = True
                journey = journeys_partial(True)
            else:
                journey = journeys_partial(False)
            # Time between touchpoints (hours to days)
            time_gap = timedelta(
                hours=random.randint(1, 48),
                minutes=random.randint(0, 59)
            )

            touchpoint_time = user_start_time + (time_gap * touch_num)

            if curr_user_id in last_time:
                if touchpoint_time < last_time[curr_user_id]:
                    user_start_time = last_time[curr_user_id]
                    touchpoint_time = user_start_time + (time_gap * touch_num)
                    last_time[curr_user_id] = touchpoint_time
                else:
                    last_time[curr_user_id] = touchpoint_time
            else:
                last_time[curr_user_id] = touchpoint_time
            # Select random campaign


            touchpoint = {
                'user_id': curr_user_id,
                'timestamp': touchpoint_time,
                'platform': campaign['platform'],
                'campaign_id': campaign['campaign_id'],
                'touchpoints_type':journey[touch_num],
                'device_type': random.choice(['mobile', 'desktop', 'tablet']),
                'geo_location': fake.city()
            }
            touchpoints.append(touchpoint)
            # print(curr_user_id, touchpoint_time, journey[touch_num])

    df =  pd.DataFrame(touchpoints)
    return df


def validate_journey_data(df):
    issues = []
    null_in_impressions = df[(df['touchpoints_type'] == 'impression') & (df['touchpoints_type'].isnull())]
    if not null_in_impressions.empty:
        issues.append('touchpoints_type impression contains null values')
    return issues

if __name__ == '__main__':
    campaigns_df = read_campaign_data()
    try:

        journey_data_df = generate_user_journeys(campaigns_df)
        issues = validate_journey_data(journey_data_df)
        if issues:
            logger.info(f'Found issues: {issues}')
            raise ValueError
        journey_count = load_journey_data(journey_data_df)
        print(f"Loaded {journey_count} user journeys to database")

    except Exception as e:
        logger.error(f"Database loading failed: {e}")
        raise


