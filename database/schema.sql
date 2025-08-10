-- campaigns table
CREATE TABLE campaigns (
	campaign_id VARCHAR(50) PRIMARY KEY,
	platform VARCHAR(20) NOT NULL, -- google | facebook
	campaign_name VARCHAR(100),
	campaign_type VARCHAR(50),
	daily_budget DECIMAL(10, 2),
	status VARCHAR(20),
	created_date DATE
);


--daily_performance table
CREATE TABLE daily_performance(
	id SERIAL PRIMARY KEY,
	date DATE NOT NULL,
	campaign_id VARCHAR(50) REFERENCES campaigns(campaign_id),
	impressions INTEGER,
	clicks INTEGER,
	spend DECIMAL(10, 2),
	conversion INTEGER,
	revenue DECIMAL(10, 2),
	cpc DECIMAL(8,4),
	cpm DECIMAL(8,4),
	ctr DECIMAL(8,4)
);

--user touchpoints table
CREATE TABLE user_touchpoints(
	id SERIAL PRIMARY KEY,
	user_id VARCHAR(50) NOT NULL,
	timestamp TIMESTAMP NOT NULL,
	platform VARCHAR(20) NOT NULL,
	campaign_id VARCHAR(50) REFERENCES campaigns(campaign_id),
	touchpoints_type VARCHAR(30), --'impression', 'click', 'view'
	device_type VARCHAR(20),
	geo_location VARCHAR(50)
);

--conversions table
CREATE TABLE conversions (
	id SERIAL PRIMARY KEY,
	user_id VARCHAR(50) NOT NULL,
	conversion_timestamp TIMESTAMP NOT NULL,
	revenue DECIMAL(10, 2),
	conversion_type VARCHAR(30), -- 'purchase', 'signup', 'lead'
	attributed_campaign_id VARCHAR(50),
	attribution_model VARCHAR(30) -- 'first touch', 'last touch', 'linear'
);