import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker
import uuid
import math
from google.colab import drive
import os

# Set up Faker for generating realistic data
fake = Faker()
np.random.seed(42)  # For reproducibility


class AdvancedSaaSDataGenerator:
    def __init__(self, start_date="2022-01-01", end_date="2024-12-31"):
        """
        Initializes the AdvancedSaaSDataGenerator with start and end dates.

        Args:
            start_date (str, optional): The start date for data generation. Defaults to "2022-01-01".
            end_date (str, optional): The end date for data generation. Defaults to "2024-12-31".
        """
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Define subscription plans with tier pricing
        self.plans = {
            'Starter': {
                'base_price': 29,
                'per_seat_price': 0,  # Fixed pricing
                'max_seats': 5,
                'annual_discount': 0.10,
                'base_churn_rate': 0.08,
                'features': ['basic_analytics', 'email_support']
            },
            'Professional': {
                'base_price': 49,
                'per_seat_price': 15,  # $15 per additional seat
                'max_seats': 50,
                'annual_discount': 0.15,
                'base_churn_rate': 0.05,
                'features': ['advanced_analytics', 'integrations', 'phone_support']
            },
            'Business': {
                'base_price': 99,
                'per_seat_price': 25,
                'max_seats': 200,
                'annual_discount': 0.20,
                'base_churn_rate': 0.03,
                'features': ['custom_dashboards', 'api_access', 'dedicated_support']
            },
            'Enterprise': {
                'base_price': 299,
                'per_seat_price': 35,
                'max_seats': 1000,
                'annual_discount': 0.25,
                'base_churn_rate': 0.015,
                'features': ['white_label', 'sso', 'custom_integrations', 'customer_success_manager']
            }
        }

        # Add-on products for expansion revenue
        self.addons = {
            'advanced_reporting': {'price': 50, 'attachment_rate': 0.3},
            'api_premium': {'price': 100, 'attachment_rate': 0.15},
            'data_export': {'price': 25, 'attachment_rate': 0.4},
            'priority_support': {'price': 75, 'attachment_rate': 0.2},
            'custom_integrations': {'price': 200, 'attachment_rate': 0.1},
            'training_package': {'price': 500, 'attachment_rate': 0.05, 'one_time': True}
        }

        # Seasonal patterns for different business aspects
        self.seasonal_patterns = {
            'acquisition': {
                1: 1.4, 2: 1.6, 3: 1.2, 4: 1.0, 5: 0.9, 6: 0.7,
                7: 0.6, 8: 0.8, 9: 1.5, 10: 1.6, 11: 1.3, 12: 0.8
            },
            'churn': {
                1: 1.3, 2: 1.1, 3: 1.0, 4: 0.9, 5: 0.9, 6: 1.0,
                7: 1.1, 8: 1.0, 9: 0.8, 10: 0.7, 11: 0.8, 12: 1.2
            },
            'expansion': {
                1: 0.8, 2: 0.9, 3: 1.2, 4: 1.3, 5: 1.1, 6: 1.0,
                7: 0.9, 8: 1.0, 9: 1.4, 10: 1.5, 11: 1.2, 12: 0.9
            },
            'upgrades': {
                1: 1.1, 2: 1.2, 3: 1.3, 4: 1.4, 5: 1.0, 6: 0.9,
                7: 0.8, 8: 0.9, 9: 1.2, 10: 1.3, 11: 1.1, 12: 1.0
            }
        }

    def generate_customers(self, num_customers=3000):
        """
        Generates customer data with attributes like company, acquisition date, and geography.

        Args:
            num_customers (int, optional): The number of customers to generate. Defaults to 3000.

        Returns:
            pd.DataFrame: A DataFrame containing customer data.
        """
        customers = []
        customer_ids = []  # To keep track of generated customer IDs for referrals

        for i in range(num_customers):
            # Generate acquisition date with seasonal patterns AND day randomness
            year = random.randint(self.start_date.year, self.end_date.year)
            month = random.randint(1, 12)
            # Ensure the day is valid for the month and year
            try:
                # Get the last day of the month
                last_day_of_month = (datetime(year, month + 1, 1) - timedelta(days=1)).day if month < 12 else 31
                day = random.randint(1, last_day_of_month)
                acquisition_date_potential = datetime(year, month, day)
            except ValueError:
                continue  # Skip if the generated date is invalid

            if self.start_date <= acquisition_date_potential <= self.end_date:
                acquisition_date = acquisition_date_potential
            else:
                continue  # Skip if outside the overall date range

            # Apply seasonal acquisition pattern
            month_acq = acquisition_date.month
            seasonal_factor = self.seasonal_patterns['acquisition'][month_acq]
            if random.random() > seasonal_factor / 2.0:
                continue

            # Enhanced customer attributes
            company_size_category = random.choice([
                'Startup (1-10)', 'Small (11-50)', 'Medium (51-200)',
                'Large (201-1000)', 'Enterprise (1000+)'
            ])

            size_factor = {
                'Startup (1-10)': {'seats_tendency': 1.2, 'upgrade_tendency': 0.8, 'budget': 0.7},
                'Small (11-50)': {'seats_tendency': 1.5, 'upgrade_tendency': 1.0, 'budget': 1.0},
                'Medium (51-200)': {'seats_tendency': 2.0, 'upgrade_tendency': 1.3, 'budget': 1.5},
                'Large (201-1000)': {'seats_tendency': 3.0, 'upgrade_tendency': 1.5, 'budget': 2.0},
                'Enterprise (1000+)': {'seats_tendency': 5.0, 'upgrade_tendency': 1.2, 'budget': 3.0}
            }
            customer_id = str(uuid.uuid4())
            has_trial = random.random() < 0.3  # 30% chance of having a trial
            trial_start_date = None
            trial_end_date = None

            if has_trial:
                trial_duration = random.randint(7, 30)
                # Trial starts a few days before the acquisition date
                trial_start_offset = random.randint(1, 7)
                trial_start_date = acquisition_date - timedelta(days=trial_start_offset)
                trial_end_date = trial_start_date + timedelta(days=trial_duration)

            customer = {
                'customer_id': customer_id,
                'company_name': fake.company(),
                'contact_email': fake.email(),
                'industry': random.choice([
                    'Technology', 'Healthcare', 'Finance', 'Retail',
                    'Manufacturing', 'Education', 'Marketing', 'Consulting',
                    'Real Estate', 'Media', 'Legal', 'Non-profit'
                ]),
                'company_size': company_size_category,
                'acquisition_date': acquisition_date,
                'acquisition_channel': random.choice([
                    'Organic Search', 'Paid Search', 'Social Media', 'Referral',
                    'Direct', 'Content Marketing', 'Trade Show', 'Cold Outreach',
                    'Partner', 'Webinar', 'Free Trial'  # Added 'Free Trial' as a channel
                ]),
                'acquisition_cost': np.random.lognormal(5, 0.8),
                'geography': random.choice([
                    'North America', 'Europe', 'Asia-Pacific', 'Latin America', 'Other'
                ]),
                'seats_tendency': size_factor[company_size_category]['seats_tendency'],
                'upgrade_tendency': size_factor[company_size_category]['upgrade_tendency'],
                'budget_factor': size_factor[company_size_category]['budget'],
                'has_trial': has_trial,
                'trial_start_date': trial_start_date,
                'trial_end_date': trial_end_date
            }
            customers.append(customer)
            customer_ids.append(customer_id)

        customers_df = pd.DataFrame(customers)
        # Add referral information after all customers are generated
        customers_df['referred_by_customer_id'] = np.random.choice(
            [None] + customer_ids, size=len(customers_df), p=[0.7] + [0.3 / len(customer_ids)] * len(customer_ids)
        )
        return customers_df

    def calculate_tier_pricing(self, plan_name, seats, billing_frequency):
        """
        Calculates the price based on the subscription plan, number of seats, and billing frequency.

        Args:
            plan_name (str): The name of the subscription plan.
            seats (int): The number of seats.
            billing_frequency (str): The billing frequency ('monthly' or 'annual').

        Returns:
            float: The calculated price.
        """
        plan = self.plans[plan_name]

        # Base price + per-seat pricing
        if seats <= 1:
            base_cost = plan['base_price']
        else:
            additional_seats = min(seats - 1, plan['max_seats'] - 1)
            base_cost = plan['base_price'] + (additional_seats * plan['per_seat_price'])

        # Apply annual discount
        if billing_frequency == 'annual':
            base_cost = base_cost * 12 * (1 - plan['annual_discount'])

        return base_cost

    def generate_subscriptions(self, customers_df):
        """
        Generates subscription data for each customer, including initial subscriptions and expansion events.

        Args:
            customers_df (pd.DataFrame): DataFrame containing customer data.

        Returns:
            pd.DataFrame: A DataFrame containing subscription data.
        """
        subscriptions = []

        for _, customer in customers_df.iterrows():
            # Initial subscription
            subscription = self._create_initial_subscription(customer)
            subscriptions.append(subscription)

            # Generate expansion events (upgrades, seat additions, add-ons)
            expansion_events = self._generate_expansion_events(subscription, customer)
            subscriptions.extend(expansion_events)

        return pd.DataFrame(subscriptions)

    def _create_initial_subscription(self, customer):
        """
        Creates the initial subscription for a customer.

        Args:
            customer (pd.Series): A Series containing customer data.

        Returns:
            dict: A dictionary representing the initial subscription.
        """
        # Choose initial plan based on company size and budget
        if 'Startup' in customer['company_size'] or 'Small' in customer['company_size']:
            plan = np.random.choice(['Starter', 'Professional'], p=[0.6, 0.4])
        elif 'Medium' in customer['company_size']:
            plan = np.random.choice(['Professional', 'Business'], p=[0.5, 0.5])
        else:
            plan = np.random.choice(['Business', 'Enterprise'], p=[0.4, 0.6])

        # Determine initial seat count
        base_seats = max(1, int(np.random.exponential(2) * customer['seats_tendency']))
        max_seats = self.plans[plan]['max_seats']
        seats = min(base_seats, max_seats)

        # Choose billing frequency (enterprises prefer annual)
        if 'Enterprise' in customer['company_size']:
            billing_frequency = np.random.choice(['monthly', 'annual'], p=[0.2, 0.8])
        else:
            billing_frequency = np.random.choice(['monthly', 'annual'], p=[0.6, 0.4])

        # Calculate price
        monthly_price = self.calculate_tier_pricing(plan, seats, billing_frequency)
        if billing_frequency == 'annual':
            monthly_price = monthly_price / 12

        # Generate start date (close to acquisition with some delay)
        start_delay = max(0, int(np.random.exponential(7)))  # Average 7 days delay
        start_date = customer['acquisition_date'] + timedelta(days=start_delay)

        # Subscription starts after the trial ends, if there was one
        if customer['has_trial'] and start_date < customer['trial_end_date']:
            start_date = customer['trial_end_date'] + timedelta(days=1)

        # Generate end date with seasonal churn consideration
        end_date = self._calculate_churn_date(start_date, plan, billing_frequency)

        return {
            'subscription_id': str(uuid.uuid4()),
            'customer_id': customer['customer_id'],
            'plan_name': plan,
            'billing_frequency': billing_frequency,
            'monthly_price': monthly_price,
            'seats': seats,
            'start_date': start_date,
            'end_date': end_date,
            'subscription_type': 'initial',
            'churn_reason': self._generate_churn_reason() if end_date else None,
            'add_ons': []
        }

    def _calculate_churn_date(self, start_date, plan, billing_frequency):
        """
        Calculates the churn date for a subscription, considering seasonality.

        Args:
            start_date (datetime): The start date of the subscription.
            plan (str): The name of the subscription plan.
            billing_frequency (str): The billing frequency.

        Returns:
            datetime: The calculated churn date, or None if the customer doesn't churn.
        """
        base_churn_rate = self.plans[plan]['base_churn_rate']

        # Simulate month-by-month survival
        current_date = start_date
        for _ in range(120):  # Max 10 years
            month = current_date.month
            seasonal_churn_factor = self.seasonal_patterns['churn'][month]
            monthly_churn_rate = base_churn_rate * seasonal_churn_factor

            # Check if customer churns this month
            if random.random() < monthly_churn_rate:
                return current_date

            # Move to next month, setting day to 1 to avoid invalid dates
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1, day=1) #changed this line

            #now add the random number of days back in.
            current_date = current_date + timedelta(days = random.randint(0,27))
        # 30% chance customer is still active
        return None if random.random() < 0.3 else current_date


    def _generate_expansion_events(self, initial_subscription, customer):
        """
        Generates expansion events for a subscription, such as upgrades and seat additions.

        Args:
            initial_subscription (dict): The initial subscription data.
            customer (pd.Series): The customer data.

        Returns:
            list: A list of dictionaries representing expansion events.
        """
        expansion_events = []

        if initial_subscription['end_date'] is None or initial_subscription['end_date'] > self.end_date:
            subscription_end = self.end_date
        else:
            subscription_end = initial_subscription['end_date']

        current_date = initial_subscription['start_date']
        current_plan = initial_subscription['plan_name']
        current_seats = initial_subscription['seats']

        while current_date < subscription_end:
            # Move forward 2-6 months
            current_date += timedelta(days=random.randint(60, 180))

            if current_date >= subscription_end:
                break

            month = current_date.month
            expansion_factor = self.seasonal_patterns['expansion'][month]
            upgrade_factor = self.seasonal_patterns['upgrades'][month]

            # Check for seat expansion (more likely than plan upgrades)
            if random.random() < 0.3 * expansion_factor * customer['seats_tendency']:
                additional_seats = random.randint(1, 5)
                new_seats = min(current_seats + additional_seats, self.plans[current_plan]['max_seats'])

                if new_seats > current_seats:
                    # Create seat expansion event
                    new_price = self.calculate_tier_pricing(current_plan, new_seats,
                                                          initial_subscription['billing_frequency'])
                    if initial_subscription['billing_frequency'] == 'annual':
                        new_price = new_price / 12

                    expansion_event = {
                        'subscription_id': str(uuid.uuid4()),
                        'customer_id': customer['customer_id'],
                        'plan_name': current_plan,
                        'billing_frequency': initial_subscription['billing_frequency'],
                        'monthly_price': new_price,
                        'seats': new_seats,
                        'start_date': current_date,
                        'end_date': initial_subscription['end_date'],
                        'subscription_type': 'seat_expansion',
                        'churn_reason': initial_subscription['churn_reason'],
                        'add_ons': []
                    }
                    expansion_events.append(expansion_event)
                    current_seats = new_seats

            # Check for plan upgrade
            elif random.random() < 0.15 * upgrade_factor * customer['upgrade_tendency']:
                plans_list = list(self.plans.keys())
                current_plan_index = plans_list.index(current_plan)

                if current_plan_index < len(plans_list) - 1:  # Can upgrade
                    new_plan = plans_list[current_plan_index + 1]

                    # Adjust seats for new plan if necessary
                    new_plan_max_seats = self.plans[new_plan]['max_seats']
                    new_seats = min(current_seats, new_plan_max_seats)

                    new_price = self.calculate_tier_pricing(new_plan, new_seats,
                                                          initial_subscription['billing_frequency'])
                    if initial_subscription['billing_frequency'] == 'annual':
                        new_price = new_price / 12

                    upgrade_event = {
                        'subscription_id': str(uuid.uuid4()),
                        'customer_id': customer['customer_id'],
                        'plan_name': new_plan,
                        'billing_frequency': initial_subscription['billing_frequency'],
                        'monthly_price': new_price,
                        'seats': new_seats,
                        'start_date': current_date,
                        'end_date': initial_subscription['end_date'],
                        'subscription_type': 'plan_upgrade',
                        'churn_reason': initial_subscription['churn_reason'],
                        'add_ons': []
                    }
                    expansion_events.append(upgrade_event)
                    current_plan = new_plan
                    current_seats = new_seats

        return expansion_events

    def _generate_churn_reason(self):
        """Generates a realistic churn reason."""
        reasons = [
            'Price sensitivity', 'Lack of features', 'Poor support',
            'Competitor switch', 'Budget cuts', 'No longer needed',
            'Technical issues', 'Merger/acquisition', 'Poor onboarding',
            'Low usage', 'Feature gaps', 'Better alternative found'
        ]
        return random.choice(reasons)

    def generate_addon_subscriptions(self, subscriptions_df):
        """
        Generates add-on subscriptions for existing subscriptions.

        Args:
            subscriptions_df (pd.DataFrame): DataFrame containing subscription data.

        Returns:
            pd.DataFrame: A DataFrame containing add-on subscription data.
        """
        addon_subscriptions = []

        for _, subscription in subscriptions_df.iterrows():
            if subscription['subscription_type'] != 'initial':
                continue

            # Each plan has different add-on attachment rates
            plan_addon_multiplier = {
                'Starter': 0.5, 'Professional': 1.0, 'Business': 1.5, 'Enterprise': 2.0
            }

            multiplier = plan_addon_multiplier[subscription['plan_name']]

            for addon_name, addon_info in self.addons.items():
                if random.random() < addon_info['attachment_rate'] * multiplier:
                    # Generate start date (sometime after main subscription)
                    days_delay = random.randint(30, 180)
                    addon_start = subscription['start_date'] + timedelta(days=days_delay)

                    if subscription['end_date']:
                        addon_end = min(addon_start + timedelta(days=365), subscription['end_date'])
                    else:
                        addon_end = None

                    addon_sub = {
                        'subscription_id': str(uuid.uuid4()),
                        'customer_id': subscription['customer_id'],
                        'plan_name': addon_name,
                        'billing_frequency': subscription['billing_frequency'],
                        'monthly_price': addon_info['price'] if addon_info.get('one_time') else addon_info['price'],
                        'seats': 1,
                        'start_date': addon_start,
                        'end_date': addon_end,
                        'subscription_type': 'addon',
                        'churn_reason': None,
                        'add_ons': []
                    }
                    addon_subscriptions.append(addon_sub)
        return pd.DataFrame(addon_subscriptions)

    def generate_payment_events(self, subscriptions_df):
        """
        Generates payment events for subscriptions.

        Args:
            subscriptions_df (pd.DataFrame): DataFrame containing subscription data.

        Returns:
            pd.DataFrame: A DataFrame containing payment event data.
        """
        payments = []

        for _, subscription in subscriptions_df.iterrows():
            current_date = subscription['start_date']
            end_date = subscription['end_date'] if subscription['end_date'] else self.end_date

            max_payments = 120
            payment_count = 0

            while current_date <= end_date and payment_count < max_payments:
                # Payment success rate varies by plan and payment method
                payment_method = random.choice(['Credit Card', 'ACH', 'Wire Transfer', 'PayPal'])
                success_rate = {'Credit Card': 0.94, 'ACH': 0.96, 'Wire Transfer': 0.99, 'PayPal': 0.93}

                payment_status = np.random.choice(
                    ['successful', 'failed', 'refunded'],
                    p=[success_rate[payment_method], 1 - success_rate[payment_method] - 0.01, 0.01]
                )

                amount = subscription['monthly_price']
                if subscription['billing_frequency'] == 'annual':
                    amount = amount * 12

                payment = {
                    'payment_id': str(uuid.uuid4()),
                    'subscription_id': subscription['subscription_id'],
                    'customer_id': subscription['customer_id'],
                    'payment_date': current_date,
                    'amount': amount if payment_status == 'successful' else 0,
                    'status': payment_status,
                    'payment_method': payment_method,
                    'subscription_type': subscription['subscription_type']
                }
                payments.append(payment)

                # Move to next billing cycle
                if subscription['billing_frequency'] == 'monthly':
                    current_date += timedelta(days=30)
                else:
                    current_date += timedelta(days=365)

                payment_count += 1
        return pd.DataFrame(payments)

    def generate_usage_events(self, subscriptions_df, base_events_per_month=50):
        """
        Generates usage events for subscriptions, with feature-specific patterns.

        Args:
            subscriptions_df (pd.DataFrame): DataFrame containing subscription data.
            base_events_per_month (int, optional): Base number of usage events per month. Defaults to 50.

        Returns:
            pd.DataFrame: A DataFrame containing usage event data.
        """
        usage_events = []

        for _, subscription in subscriptions_df.iterrows():
            if subscription['subscription_type'] != 'initial':
                continue

            current_month = subscription['start_date'].replace(day=1)
            end_date = subscription['end_date'] if subscription['end_date'] else self.end_date

            plan_name = subscription['plan_name']
            plan_features = self.plans[plan_name]['features']
            plan_multipliers = {'Starter': 0.5, 'Professional': 1.0, 'Business': 1.8, 'Enterprise': 3.0}
            events_per_month = int(
                base_events_per_month * plan_multipliers[plan_name] * math.sqrt(subscription['seats']))

            # Define feature usage probabilities based on the plan
            feature_probabilities = {
                'login': 0.9,
                'dashboard_view': 0.8,
                'basic_report': 0.7 if 'basic_analytics' in plan_features else 0.3,
                'advanced_analytics': 0.6 if 'advanced_analytics' in plan_features else 0.1,
                'integrations': 0.5 if 'integrations' in plan_features else 0.05,
                'phone_support': 0.2 if 'phone_support' in plan_features else 0.01,
                'custom_dashboards': 0.4 if 'custom_dashboards' in plan_features else 0.01,
                'api_access': 0.3 if 'api_access' in plan_features else 0.01,
                'white_label': 0.1 if 'white_label' in plan_features else 0.005,
                'sso': 0.15 if 'sso' in plan_features else 0.005,
                'custom_integrations': 0.2 if 'custom_integrations' in plan_features else 0.005,
                'customer_success_manager': 0.05 if 'customer_success_manager' in plan_features else 0.001,
                'report_generated': 0.6,
                'data_export': 0.4 if 'basic_analytics' in plan_features or 'advanced_analytics' in plan_features else 0.1,
                'api_call': 0.3 if 'api_access' in plan_features else 0.05,
                'file_upload': 0.5,
                'user_invite': 0.4
            }

            available_features = list(feature_probabilities.keys())
            # Ensure probabilities sum to 1 for the features *actually available* for this plan
            plan_specific_probabilities = [feature_probabilities[f] for f in available_features]

            # Normalize probabilities to sum to 1
            total_probability = sum(plan_specific_probabilities)
            if total_probability > 0:
                normalized_probabilities = [p / total_probability for p in plan_specific_probabilities]
            else:
                normalized_probabilities = [1.0 / len(plan_specific_probabilities)] * len(plan_specific_probabilities) # Ensure probabilities sum to 1

            while current_month <= end_date:
                monthly_events = np.random.poisson(events_per_month)

                for _ in range(monthly_events):
                    event_date = current_month + timedelta(
                        days=random.randint(0, 27),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )

                    chosen_feature = np.random.choice(available_features,
                                                     p=normalized_probabilities)

                    usage_event = {
                        'event_id': str(uuid.uuid4()),
                        'customer_id': subscription['customer_id'],
                        'subscription_id': subscription['subscription_id'],
                        'event_date': event_date,
                        'event_type': 'feature_used',
                        'feature_used': chosen_feature,
                        'seats_used': random.randint(1, subscription['seats'])
                    }
                    usage_events.append(usage_event)

                if current_month.month == 12:
                    current_month = current_month.replace(year=current_month.year + 1, month=1)
                else:
                    current_month = current_month.replace(month=current_month.month + 1)

        return pd.DataFrame(usage_events)

    def generate_support_interactions(self, customers_df, start_date="2022-01-01", end_date="2024-12-31"):
        """
        Generates support interactions for customers.

        Args:
            customers_df (pd.DataFrame): DataFrame containing customer data.
            start_date (str, optional): Start date for support interactions. Defaults to "2022-01-01".
            end_date (str, optional): End date for support interactions. Defaults to "2024-12-31".

        Returns:
            pd.DataFrame: A DataFrame containing support interaction data.
        """
        interactions = []
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        for customer_id in customers_df['customer_id']:
            num_interactions = np.random.poisson(1.5)  # Average 1.5 interactions per customer

            for _ in range(num_interactions):
                interaction_date = start + timedelta(days=random.randint(0, (end - start).days))
                issue_category = random.choice([
                    'Billing Issue', 'Technical Problem', 'Feature Request',
                    'Onboarding Help', 'Account Management'
                ])
                resolution_status = random.choice(['Resolved', 'Pending', 'Escalated'])
                resolution_time_hours = np.random.lognormal(1,
                                                          0.5) if resolution_status == 'Resolved' else None
                sentiment = np.random.choice(['Positive', 'Neutral', 'Negative'],
                                             p=[0.2, 0.5, 0.3])

                interaction = {
                    'interaction_id': str(uuid.uuid4()),
                    'customer_id': customer_id,
                    'interaction_date': interaction_date,
                    'issue_category': issue_category,
                    'resolution_status': resolution_status,
                    'resolution_time_hours': resolution_time_hours,
                    'sentiment': sentiment
                }
                interactions.append(interaction)

        return pd.DataFrame(interactions)


def generate_advanced_saas_dataset():
    """
    Generates a comprehensive SaaS dataset with all enhancements and saves it to Google Drive.

    Returns:
        tuple: A tuple containing the generated DataFrames (customers, all_subscriptions, payments, usage, support_interactions).
    """
    generator = AdvancedSaaSDataGenerator()

    print("Mounting Google Drive...")
    drive.mount('/content/drive')  # Mount Google Drive

    # Define the directory where you want to save the data
    output_dir = '/content/drive/My Drive/saas-kpi-dashboard'  # Changed to "saas-kpi-dashboard"
    # Create the directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Generating customers...")
    customers = generator.generate_customers(2000)

    print("Generating core subscriptions...")
    subscriptions = generator.generate_subscriptions(customers)

    print("Generating add-on subscriptions...")
    addon_subscriptions = generator.generate_addon_subscriptions(subscriptions)

    # Combine all subscriptions
    all_subscriptions = pd.concat([subscriptions, addon_subscriptions], ignore_index=True)

    print("Generating payments...")
    payments = generator.generate_payment_events(all_subscriptions)

    print("Generating usage events...")
    usage = generator.generate_usage_events(subscriptions)  # Only core subscriptions for usage

    print("Generating support interactions...")
    support_interactions = generator.generate_support_interactions(customers)

    # Save to Google Drive
    print("Saving data to Google Drive...")
    customers.to_csv(os.path.join(output_dir, 'customers_advanced.csv'), index=False)
    all_subscriptions.to_csv(os.path.join(output_dir, 'subscriptions_advanced.csv'), index=False)
    payments.to_csv(os.path.join(output_dir, 'payments_advanced.csv'), index=False)
    usage.to_csv(os.path.join(output_dir, 'usage_events_advanced.csv'), index=False)
    support_interactions.to_csv(os.path.join(output_dir, 'support_interactions.csv'), index=False)

    # Generate summary statistics
    print(f"\nGenerated Advanced SaaS Dataset and saved to Google Drive:")
    print(f"- {len(customers)} customers")
    print(f"- {len(subscriptions)} core subscriptions")
    print(f"- {len(addon_subscriptions)} add-on subscriptions")
    print(f"- {len(payments)} payment events")
    print(f"- {len(usage)} usage events")
    print(f"- {len(support_interactions)} support interactions")
    print(f"  Data saved to: {output_dir}")

    # Quick analysis
    print(f"\nQuick Analysis:")
    print(f"- Average seats per subscription: {subscriptions['seats'].mean():.1f}")
    print(f"- Plan distribution: {subscriptions['plan_name'].value_counts().to_dict()}")
    print(f"- Expansion events: {len(subscriptions[subscriptions['subscription_type'] != 'initial'])}")

    return customers, all_subscriptions, payments, usage, support_interactions


# Run the generation
if __name__ == "__main__":
    customers, subscriptions, payments, usage, support_interactions = generate_advanced_saas_dataset()
