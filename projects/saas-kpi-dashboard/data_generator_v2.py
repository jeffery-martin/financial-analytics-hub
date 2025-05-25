import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker
import uuid
import math
import os

fake = Faker()
np.random.seed(42)

class DataGenerator:
    def __init__(self, start_date="2022-01-01", end_date="2024-12-31"):
        """
        Initializes the DataGenerator with start and end dates.
        """
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")

        self.plans = {
            'Starter': {
                'base_price_monthly': 29, # Changed to base_price_monthly
                'per_seat_price': 0,
                'max_seats': 5,
                'annual_discount': 0.10,
                'base_churn_rate': 0.08,
                'features': ['basic_analytics', 'email_support']
            },
            'Professional': {
                'base_price_monthly': 49, # Changed to base_price_monthly
                'per_seat_price': 15,
                'max_seats': 50,
                'annual_discount': 0.15,
                'base_churn_rate': 0.05,
                'features': ['advanced_analytics', 'integrations', 'phone_support']
            },
            'Business': {
                'base_price_monthly': 99, # Changed to base_price_monthly
                'per_seat_price': 25,
                'max_seats': 200,
                'annual_discount': 0.20,
                'base_churn_rate': 0.03,
                'features': ['custom_dashboards', 'api_access', 'dedicated_support']
            },
            'Enterprise': {
                'base_price_monthly': 299, # Changed to base_price_monthly
                'per_seat_price': 35,
                'max_seats': 1000,
                'annual_discount': 0.25,
                'base_churn_rate': 0.015,
                'features': ['white_label', 'sso', 'custom_integrations', 'customer_success_manager']
            }
        }

        self.addons = {
            'advanced_reporting': {'price_monthly': 50, 'attachment_rate': 0.3},
            'api_premium': {'price_monthly': 100, 'attachment_rate': 0.15},
            'data_export': {'price_monthly': 25, 'attachment_rate': 0.4},
            'priority_support': {'price_monthly': 75, 'attachment_rate': 0.2},
            'custom_integrations': {'price_monthly': 200, 'attachment_rate': 0.1},
            'training_package': {'price_monthly': 500, 'attachment_rate': 0.05, 'one_time': True} # One-time add-on
        }

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

    def calculate_monthly_recurring_revenue(self, plan_name, seats, billing_frequency):
        """
        Calculates the effective monthly recurring revenue (MRR) based on the subscription plan,
        number of seats, and billing frequency, accounting for annual discounts.
        """
        plan = self.plans[plan_name]

        # Base price + per-seat pricing
        if seats <= 1:
            base_cost_monthly = plan['base_price_monthly']
        else:
            # Seats beyond the first one incur per_seat_price up to max_seats
            additional_seats = min(seats - 1, plan['max_seats'] - 1)
            base_cost_monthly = plan['base_price_monthly'] + (additional_seats * plan['per_seat_price'])

        # Apply annual discount and convert to effective monthly
        if billing_frequency == 'annual':
            # Annual plans pay (base_cost_monthly * 12) * (1 - discount)
            # So, effective monthly is (base_cost_monthly * 12 * (1 - discount)) / 12
            effective_monthly_mrr = base_cost_monthly * (1 - plan['annual_discount'])
        else: # monthly
            effective_monthly_mrr = base_cost_monthly

        return effective_monthly_mrr

    def generate_customers(self, num_customers=3000):
        """
        Generates customer data with attributes like company, acquisition date, and geography.
        Includes more realistic CAC generation.
        """
        customers = []
        customer_ids = []

        for i in range(num_customers):
            year = random.randint(self.start_date.year, self.end_date.year)
            month = random.randint(1, 12)
            try:
                last_day_of_month = (datetime(year, month + 1, 1) - timedelta(days=1)).day if month < 12 else 31
                day = random.randint(1, last_day_of_month)
                acquisition_date_potential = datetime(year, month, day)
            except ValueError:
                continue

            if not (self.start_date <= acquisition_date_potential <= self.end_date):
                continue

            seasonal_factor = self.seasonal_patterns['acquisition'][acquisition_date_potential.month]
            if random.random() > seasonal_factor / 2.0: # Reduce generation slightly outside peak seasons
                continue

            company_size_category = random.choice([
                'Startup (1-10)', 'Small (11-50)', 'Medium (51-200)',
                'Large (201-1000)', 'Enterprise (1000+)'
            ])

            size_factor = {
                'Startup (1-10)': {'seats_tendency': 1.2, 'upgrade_tendency': 0.8, 'budget': 0.7, 'cac_multiplier': 0.8},
                'Small (11-50)': {'seats_tendency': 1.5, 'upgrade_tendency': 1.0, 'budget': 1.0, 'cac_multiplier': 1.0},
                'Medium (51-200)': {'seats_tendency': 2.0, 'upgrade_tendency': 1.3, 'budget': 1.5, 'cac_multiplier': 1.5},
                'Large (201-1000)': {'seats_tendency': 3.0, 'upgrade_tendency': 1.5, 'budget': 2.0, 'cac_multiplier': 2.0},
                'Enterprise (1000+)': {'seats_tendency': 5.0, 'upgrade_tendency': 1.2, 'budget': 3.0, 'cac_multiplier': 3.0}
            }

            acquisition_channel = random.choice([
                'Organic Search', 'Paid Search', 'Social Media', 'Referral',
                'Direct', 'Content Marketing', 'Trade Show', 'Cold Outreach',
                'Partner', 'Webinar', 'Free Trial'
            ])

            # More realistic CAC generation based on channel and company size
            base_cac_channel = {
                'Organic Search': 100, 'Paid Search': 250, 'Social Media': 180, 'Referral': 50,
                'Direct': 120, 'Content Marketing': 150, 'Trade Show': 500, 'Cold Outreach': 700,
                'Partner': 300, 'Webinar': 200, 'Free Trial': 80 # Lower CAC for free trial converts
            }
            # Add some variability
            acquisition_cost = max(50, np.random.normal(base_cac_channel[acquisition_channel] * size_factor[company_size_category]['cac_multiplier'], 50))


            customer_id = str(uuid.uuid4())
            has_trial = random.random() < 0.3
            trial_start_date = None
            trial_end_date = None

            if has_trial:
                trial_duration = random.randint(7, 30)
                trial_start_offset = random.randint(1, 7)
                trial_start_date = acquisition_date_potential - timedelta(days=trial_start_offset)
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
                'acquisition_date': acquisition_date_potential,
                'acquisition_channel': acquisition_channel,
                'acquisition_cost': acquisition_cost,
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
        customers_df['referred_by_customer_id'] = np.random.choice(
            [None] + customer_ids, size=len(customers_df), p=[0.7] + [0.3 / len(customer_ids)] * len(customer_ids)
        )
        return customers_df

    def _create_initial_subscription(self, customer):
        """
        Creates the initial subscription for a customer.
        """
        if 'Startup' in customer['company_size'] or 'Small' in customer['company_size']:
            plan = np.random.choice(['Starter', 'Professional'], p=[0.6, 0.4])
        elif 'Medium' in customer['company_size']:
            plan = np.random.choice(['Professional', 'Business'], p=[0.5, 0.5])
        else:
            plan = np.random.choice(['Business', 'Enterprise'], p=[0.4, 0.6])

        base_seats = max(1, int(np.random.exponential(2) * customer['seats_tendency']))
        max_seats = self.plans[plan]['max_seats']
        seats = min(base_seats, max_seats)

        if 'Enterprise' in customer['company_size']:
            billing_frequency = np.random.choice(['monthly', 'annual'], p=[0.2, 0.8])
        else:
            billing_frequency = np.random.choice(['monthly', 'annual'], p=[0.6, 0.4])

        # Use the refined MRR calculation
        monthly_price = self.calculate_monthly_recurring_revenue(plan, seats, billing_frequency)

        start_delay = max(0, int(np.random.exponential(7)))
        start_date = customer['acquisition_date'] + timedelta(days=start_delay)

        if customer['has_trial'] and start_date < customer['trial_end_date']:
            start_date = customer['trial_end_date'] + timedelta(days=1)

        end_date, churn_reason = self._calculate_churn_date(start_date, plan, billing_frequency)

        return {
            'subscription_id': str(uuid.uuid4()),
            'customer_id': customer['customer_id'],
            'plan_name': plan,
            'billing_frequency': billing_frequency,
            'monthly_price': monthly_price, # This is now the effective MRR
            'seats': seats,
            'start_date': start_date,
            'end_date': end_date,
            'subscription_type': 'initial',
            'churn_reason': churn_reason,
            'add_ons': []
        }

    def _calculate_churn_date(self, start_date, plan, billing_frequency):
        """
        Calculates the churn date for a subscription, considering seasonality and
        ensuring active customers are handled correctly.
        Returns a tuple: (churn_date, churn_reason)
        """
        base_churn_rate = self.plans[plan]['base_churn_rate']
        current_date = start_date

        for _ in range(120):  # Simulate for up to 10 years
            month = current_date.month
            seasonal_churn_factor = self.seasonal_patterns['churn'][month]
            monthly_churn_rate = base_churn_rate * seasonal_churn_factor

            # Factor in plan type: lower churn for higher plans
            if plan in ['Business', 'Enterprise']:
                monthly_churn_rate *= 0.7 # Reduce churn rate for higher plans

            if random.random() < monthly_churn_rate:
                # Churn happens, return the end of the current month
                if current_date.month == 12:
                    churn_date = current_date.replace(year=current_date.year, month=12, day=31) # End of Dec
                else:
                    churn_date = (current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1))
                return churn_date, self._generate_churn_reason()

            # Move to the start of the next month for the next churn check
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1, day=1)

            # If current_date goes beyond the simulation end_date, customer is still active
            if current_date > self.end_date:
                return self.end_date, None # Customer is active until the end of simulation

        # If customer hasn't churned after 10 years, they are still active
        return self.end_date, None

    def _generate_expansion_events(self, initial_subscription, customer):
        """
        Generates expansion events for a subscription, such as upgrades and seat additions.
        Ensures consistent pricing with the refined monthly_price calculation.
        """
        expansion_events = []

        if initial_subscription['end_date'] is None or initial_subscription['end_date'] > self.end_date:
            subscription_end = self.end_date
        else:
            subscription_end = initial_subscription['end_date']

        current_date = initial_subscription['start_date']
        current_plan = initial_subscription['plan_name']
        current_seats = initial_subscription['seats']
        current_monthly_price = initial_subscription['monthly_price'] # Track current MRR

        while current_date < subscription_end:
            # Move forward 2-6 months
            current_date += timedelta(days=random.randint(60, 180))

            if current_date >= subscription_end:
                break

            month = current_date.month
            expansion_factor = self.seasonal_patterns['expansion'][month]
            upgrade_factor = self.seasonal_patterns['upgrades'][month]

            # Check for seat expansion
            if random.random() < 0.3 * expansion_factor * customer['seats_tendency']:
                additional_seats = random.randint(1, 5)
                new_seats = min(current_seats + additional_seats, self.plans[current_plan]['max_seats'])

                if new_seats > current_seats:
                    # Calculate new monthly price based on new seats
                    new_monthly_price = self.calculate_monthly_recurring_revenue(
                        current_plan, new_seats, initial_subscription['billing_frequency']
                    )

                    if new_monthly_price > current_monthly_price: # Only create event if price actually increased
                        expansion_event = {
                            'subscription_id': str(uuid.uuid4()),
                            'customer_id': customer['customer_id'],
                            'plan_name': current_plan,
                            'billing_frequency': initial_subscription['billing_frequency'],
                            'monthly_price': new_monthly_price,
                            'seats': new_seats,
                            'start_date': current_date,
                            'end_date': initial_subscription['end_date'],
                            'subscription_type': 'seat_expansion',
                            'churn_reason': initial_subscription['churn_reason'],
                            'add_ons': []
                        }
                        expansion_events.append(expansion_event)
                        current_seats = new_seats
                        current_monthly_price = new_monthly_price


            # Check for plan upgrade
            elif random.random() < 0.15 * upgrade_factor * customer['upgrade_tendency']:
                plans_list = list(self.plans.keys())
                current_plan_index = plans_list.index(current_plan)

                if current_plan_index < len(plans_list) - 1:  # Can upgrade
                    new_plan = plans_list[current_plan_index + 1]

                    # Adjust seats for new plan if necessary
                    new_plan_max_seats = self.plans[new_plan]['max_seats']
                    new_seats = min(current_seats, new_plan_max_seats)

                    # Calculate new monthly price for the upgraded plan
                    new_monthly_price = self.calculate_monthly_recurring_revenue(
                        new_plan, new_seats, initial_subscription['billing_frequency']
                    )

                    if new_monthly_price > current_monthly_price: # Only create event if price increased
                        upgrade_event = {
                            'subscription_id': str(uuid.uuid4()),
                            'customer_id': customer['customer_id'],
                            'plan_name': new_plan,
                            'billing_frequency': initial_subscription['billing_frequency'],
                            'monthly_price': new_monthly_price,
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
                        current_monthly_price = new_monthly_price

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
        """
        addon_subscriptions = []

        for _, subscription in subscriptions_df.iterrows():
            if subscription['subscription_type'] != 'initial':
                continue

            plan_addon_multiplier = {
                'Starter': 0.5, 'Professional': 1.0, 'Business': 1.5, 'Enterprise': 2.0
            }

            multiplier = plan_addon_multiplier[subscription['plan_name']]

            for addon_name, addon_info in self.addons.items():
                if random.random() < addon_info['attachment_rate'] * multiplier:
                    days_delay = random.randint(30, 180)
                    addon_start = subscription['start_date'] + timedelta(days=days_delay)

                    # For one-time add-ons, end_date is the start_date + small duration
                    if addon_info.get('one_time'):
                        addon_end = addon_start + timedelta(days=1)
                        addon_price = addon_info['price_monthly'] # Use price_monthly for one-time
                    else:
                        # Monthly recurring add-ons
                        if subscription['end_date']:
                            addon_end = min(addon_start + timedelta(days=365), subscription['end_date'])
                        else:
                            addon_end = None # Continues as long as main subscription
                        addon_price = addon_info['price_monthly']

                    # Ensure add-on starts before or at the main subscription end date if it has one
                    if subscription['end_date'] and addon_start > subscription['end_date']:
                        continue

                    addon_sub = {
                        'subscription_id': str(uuid.uuid4()),
                        'customer_id': subscription['customer_id'],
                        'plan_name': addon_name,
                        'billing_frequency': subscription['billing_frequency'], # Keep main sub's billing freq for consistency
                        'monthly_price': addon_price, # This is the monthly price or one-time amount
                        'seats': 1, # Add-ons are usually not per seat
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
        Ensures payments reflect the actual monthly_price (MRR) and billing frequency.
        """
        payments = []

        for _, subscription in subscriptions_df.iterrows():
            current_date = subscription['start_date']
            # If end_date is None (active customer), payments go up to self.end_date
            end_date = subscription['end_date'] if subscription['end_date'] else self.end_date

            # For one-time add-ons, only one payment at start_date
            if subscription['subscription_type'] == 'addon' and self.addons[subscription['plan_name']].get('one_time'):
                payment = {
                    'payment_id': str(uuid.uuid4()),
                    'subscription_id': subscription['subscription_id'],
                    'customer_id': subscription['customer_id'],
                    'payment_date': subscription['start_date'],
                    'amount': subscription['monthly_price'], # This is the one-time price
                    'status': 'successful',
                    'payment_method': random.choice(['Credit Card', 'ACH', 'Wire Transfer', 'PayPal']),
                    'subscription_type': subscription['subscription_type']
                }
                payments.append(payment)
                continue # Move to next subscription


            max_payments = 120 # Limit to 10 years of payments
            payment_count = 0

            while current_date <= end_date and payment_count < max_payments:
                payment_method = random.choice(['Credit Card', 'ACH', 'Wire Transfer', 'PayPal'])
                success_rate = {'Credit Card': 0.94, 'ACH': 0.96, 'Wire Transfer': 0.99, 'PayPal': 0.93}

                payment_status = np.random.choice(
                    ['successful', 'failed', 'refunded'],
                    p=[success_rate[payment_method], 1 - success_rate[payment_method] - 0.01, 0.01]
                )

                # Amount is the effective monthly_price or annual amount based on billing_frequency
                amount = subscription['monthly_price']
                if subscription['billing_frequency'] == 'annual':
                    amount = amount * 12

                payment = {
                    'payment_id': str(uuid.uuid4()),
                    'subscription_id': subscription['subscription_id'],
                    'customer_id': subscription['customer_id'],
                    'payment_date': current_date,
                    'amount': amount if payment_status == 'successful' else 0, # Only successful payments contribute to amount
                    'status': payment_status,
                    'payment_method': payment_method,
                    'subscription_type': subscription['subscription_type']
                }
                payments.append(payment)

                # Move to next billing cycle
                if subscription['billing_frequency'] == 'monthly':
                    current_date += timedelta(days=30) # Approximate month for simplicity
                else:
                    current_date += timedelta(days=365)

                payment_count += 1
        return pd.DataFrame(payments)

    def generate_usage_events(self, subscriptions_df, base_events_per_month=50):
        """
        Generates usage events for initial subscriptions, with feature-specific patterns
        and a more realistic daily distribution.
        """
        usage_events = []

        for _, subscription in subscriptions_df.iterrows():
            if subscription['subscription_type'] != 'initial':
                continue

            current_month_start = subscription['start_date'].replace(day=1)
            end_date = subscription['end_date'] if subscription['end_date'] else self.end_date

            plan_name = subscription['plan_name']
            plan_features = self.plans[plan_name]['features']
            plan_multipliers = {'Starter': 0.5, 'Professional': 1.0, 'Business': 1.8, 'Enterprise': 3.0}

            # Events scale with seats, but also with plan type
            events_per_month = int(
                base_events_per_month * plan_multipliers[plan_name] * math.log(subscription['seats'] + 1) # Log scale for seats
            )
            # Ensure a minimum number of events
            events_per_month = max(10, events_per_month)

            feature_probabilities = {
                'login': 0.9, 'dashboard_view': 0.8,
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
                'file_upload': 0.5, 'user_invite': 0.4
            }

            available_features = list(feature_probabilities.keys())
            plan_specific_probabilities = [feature_probabilities[f] for f in available_features]

            total_probability = sum(plan_specific_probabilities)
            if total_probability > 0:
                normalized_probabilities = [p / total_probability for p in plan_specific_probabilities]
            else:
                normalized_probabilities = [1.0 / len(plan_specific_probabilities)] * len(plan_specific_probabilities)

            while current_month_start <= end_date:
                # Distribute events throughout the month
                days_in_month = (current_month_start.replace(month=current_month_start.month % 12 + 1, day=1) - timedelta(days=1)).day
                daily_events_avg = events_per_month / days_in_month

                for day_of_month in range(1, days_in_month + 1):
                    num_daily_events = np.random.poisson(daily_events_avg)
                    for _ in range(num_daily_events):
                        event_date = current_month_start.replace(day=day_of_month) + timedelta(
                            hours=random.randint(0, 23),
                            minutes=random.randint(0, 59)
                        )
                        if event_date <= end_date: # Ensure event is not past subscription end
                            chosen_feature = np.random.choice(available_features, p=normalized_probabilities)
                            
                            # More realistic seats used: higher plans and more seats mean higher potential usage
                            seats_used = random.randint(1, max(1, min(subscription['seats'], int(subscription['seats'] * np.random.beta(0.8, 1.5)))))

                            usage_event = {
                                'event_id': str(uuid.uuid4()),
                                'customer_id': subscription['customer_id'],
                                'subscription_id': subscription['subscription_id'],
                                'event_date': event_date,
                                'event_type': 'feature_used',
                                'feature_used': chosen_feature,
                                'seats_used': seats_used
                            }
                            usage_events.append(usage_event)

                # Move to next month
                if current_month_start.month == 12:
                    current_month_start = current_month_start.replace(year=current_month_start.year + 1, month=1)
                else:
                    current_month_start = current_month_start.replace(month=current_month_start.month + 1)

        return pd.DataFrame(usage_events)

    def generate_support_interactions(self, customers_df):
        """
        Generates support interactions for customers, including sentiment and resolution time.
        """
        interactions = []
        start = self.start_date
        end = self.end_date

        for _, customer in customers_df.iterrows():
            # Higher budget customers might have fewer support issues or more critical ones
            num_interactions = np.random.poisson(1.5 / customer['budget_factor']) # Fewer interactions for high budget

            for _ in range(int(num_interactions)):
                interaction_date = start + timedelta(days=random.randint(0, (end - start).days))
                
                issue_category = random.choice([
                    'Billing Issue', 'Technical Problem', 'Feature Request',
                    'Onboarding Help', 'Account Management'
                ])
                
                # Higher plans/health might get faster resolution
                resolution_status = np.random.choice(['Resolved', 'Pending', 'Escalated'], p=[0.85, 0.1, 0.05])
                
                # Resolution time influenced by issue category and plan type (implicitly by customer)
                base_resolution_time = {'Billing Issue': 2, 'Technical Problem': 8, 'Feature Request': 24,
                                        'Onboarding Help': 3, 'Account Management': 4}
                
                resolution_time_hours = None
                if resolution_status == 'Resolved':
                    # Add some randomness to resolution time
                    resolution_time_hours = max(0.5, np.random.normal(base_resolution_time.get(issue_category, 5), 2))

                sentiment_score = np.random.uniform(0,1) # Will refine this calculation later, placeholder for now
                
                # Sentiment influenced by resolution status and time
                if resolution_status == 'Resolved' and resolution_time_hours < 4:
                    sentiment_rating = np.random.choice(['Positive', 'Neutral'], p=[0.7, 0.3])
                    sentiment_score = np.random.uniform(0.7, 1.0)
                elif resolution_status == 'Resolved':
                    sentiment_rating = np.random.choice(['Positive', 'Neutral', 'Negative'], p=[0.4, 0.5, 0.1])
                    sentiment_score = np.random.uniform(0.4, 0.8)
                else: # Pending or Escalated
                    sentiment_rating = np.random.choice(['Neutral', 'Negative'], p=[0.3, 0.7])
                    sentiment_score = np.random.uniform(0.0, 0.5)

                interaction = {
                    'interaction_id': str(uuid.uuid4()),
                    'customer_id': customer['customer_id'],
                    'interaction_date': interaction_date,
                    'issue_category': issue_category,
                    'resolution_status': resolution_status,
                    'resolution_time_hours': resolution_time_hours,
                    'sentiment_rating': sentiment_rating, # Store categorical sentiment
                    'sentiment_score': sentiment_score # Store numerical sentiment
                }
                interactions.append(interaction)

        return pd.DataFrame(interactions)

    def calculate_customer_health_and_churn(self, customers_df, subscriptions_df, usage_df, support_df):
        """
        Calculates Customer Health Score and determines final Churn status.
        This is a post-processing step on the generated data.
        """
        # Merge dataframes for a comprehensive view
        customer_data = customers_df.copy()
        
        # Calculate Churned status based on subscription end dates relative to simulation end
        customer_data['Churned'] = customer_data['customer_id'].apply(
            lambda cid: 1 if subscriptions_df[(subscriptions_df['customer_id'] == cid) & 
                                              (subscriptions_df['end_date'].notna()) &
                                              (subscriptions_df['end_date'] < self.end_date)].any().any()
            else 0
        )
        
        # Aggregate usage data
        daily_usage = usage_df.groupby(['customer_id', pd.Grouper(key='event_date', freq='D')]).size().reset_index(name='daily_events')
        avg_monthly_usage = daily_usage.groupby('customer_id')['daily_events'].mean().reset_index(name='avg_daily_events')
        
        # Calculate Average Sentiment Score from support interactions
        # Map sentiment ratings to numerical values for averaging
        sentiment_mapping = {'Positive': 1.0, 'Neutral': 0.5, 'Negative': 0.0}
        support_df['numerical_sentiment'] = support_df['sentiment_rating'].map(sentiment_mapping)
        avg_sentiment = support_df.groupby('customer_id')['numerical_sentiment'].mean().reset_index(name='Avg_Sentiment_Score')
        
        # Calculate a simple usage score (e.g., higher if more active days or events)
        customer_usage_summary = usage_df.groupby('customer_id').agg(
            Active_Days=('event_date', lambda x: x.dt.date.nunique()),
            Total_Usage_Events=('event_type', 'count')
        ).reset_index()
        
        # Normalize usage metrics for health score (simplified)
        max_active_days = customer_usage_summary['Active_Days'].max()
        max_total_events = customer_usage_summary['Total_Usage_Events'].max()

        customer_usage_summary['Usage_Score'] = (
            0.5 * (customer_usage_summary['Active_Days'] / max_active_days) +
            0.5 * (customer_usage_summary['Total_Usage_Events'] / max_total_events)
        )
        
        # Merge these back into customer_data
        customer_data = customer_data.merge(avg_monthly_usage, on='customer_id', how='left').fillna({'avg_daily_events': 0})
        customer_data = customer_data.merge(avg_sentiment, on='customer_id', how='left').fillna({'Avg_Sentiment_Score': 0.5}) # Default to neutral
        customer_data = customer_data.merge(customer_usage_summary, on='customer_id', how='left').fillna({
            'Active_Days': 0, 'Total_Usage_Events': 0, 'Usage_Score': 0
        })

        # Calculate Customer Health Score based on various factors
        # Combine sentiment, usage, and implicitly, churn
        customer_data['Customer_Health_Score'] = (
            0.4 * customer_data['Usage_Score'] +
            0.3 * customer_data['Avg_Sentiment_Score'] +
            0.2 * (1 - customer_data['Churned']) + # Active customers have higher health
            0.1 * (customer_data['budget_factor'] / customer_data['budget_factor'].max()) # Higher budget customers might be considered healthier
        )
        
        # Normalize health score to 0-1
        customer_data['Customer_Health_Score'] = customer_data['Customer_Health_Score'] / customer_data['Customer_Health_Score'].max()
        
        return customer_data[['customer_id', 'Churned', 'Avg_Sentiment_Score', 'Active_Days', 'Total_Usage_Events', 'Usage_Score', 'Customer_Health_Score']]


def generate_dataset():
    """
    Generates a comprehensive dataset with all enhancements and saves it to CSVs.
    """
    generator = DataGenerator()

    output_dir = '/Volumes/dip_fin_prod/gold/excel' # Adjust this path as needed for your environment
    os.makedirs(output_dir, exist_ok=True) # Ensure directory exists

    print("Generating customers...")
    customers = generator.generate_customers(2000)

    print("Generating core subscriptions...")
    subscriptions = generator.generate_subscriptions(customers)

    print("Generating add-on subscriptions...")
    addon_subscriptions = generator.generate_addon_subscriptions(subscriptions)

    all_subscriptions = pd.concat([subscriptions, addon_subscriptions], ignore_index=True)

    print("Generating payments...")
    payments = generator.generate_payment_events(all_subscriptions)

    print("Generating usage events...")
    usage = generator.generate_usage_events(subscriptions) # Only core subscriptions for usage

    print("Generating support interactions...")
    support_interactions = generator.generate_support_interactions(customers)

    # --- Post-processing to calculate final unit economics metrics ---
    # Calculate MRR for initial subscriptions directly (if not already handled correctly)
    # This is important for LTV calculations later.
    # Note: The `monthly_price` in subscriptions is already the effective MRR now.

    # Calculate LTV and CAC Payback, Customer Health Score at the customer level
    # For LTV: Sum of successful payments per customer
    customer_payments = payments[payments['status'] == 'successful'].groupby('customer_id')['amount'].sum().reset_index(name='Total_Revenue')

    # Merge total revenue back to customers
    customers_with_revenue = customers.merge(customer_payments, on='customer_id', how='left').fillna({'Total_Revenue': 0})
    
    # Calculate Monthly_Revenue as Total_Revenue / (Active_Days / 30.4) for active customers, or actual duration
    # This is an approximation; true MRR should come from subscription data.
    # For more accuracy, you'd calculate MRR from the all_subscriptions DF, summing monthly_price for active periods.
    
    # For simplicity, let's use the average monthly revenue from their initial subscription, adjusted if churned early
    # Or, sum monthly_price for each month they were active for better LTV
    
    # Let's derive LTV from total payments, and then derive monthly_revenue if needed from there.
    # The LTV and CAC Payback in the original problem statement are likely derived using these payments.

    # Calculate LTV from total payments
    customers_with_revenue['LTV'] = customers_with_revenue['Total_Revenue']

    # Merge CAC
    customers_final = customers_with_revenue.merge(customers[['customer_id', 'acquisition_cost']], on='customer_id', how='left')
    customers_final.rename(columns={'acquisition_cost': 'CAC'}, inplace=True)

    # Calculate LTV_CAC_Ratio
    customers_final['LTV_CAC_Ratio'] = customers_final['LTV'] / customers_final['CAC']
    customers_final['LTV_CAC_Ratio'] = customers_final['LTV_CAC_Ratio'].replace([np.inf, -np.inf], np.nan).fillna(0) # Handle division by zero

    # Calculate CAC_Payback_Months: CAC / Avg Monthly Revenue
    # A more robust MRR calculation:
    # First, calculate effective monthly revenue for each subscription duration
    def calculate_effective_mrr_for_duration(sub_row, end_sim_date):
        if sub_row['end_date'] is None:
            # Active until simulation end
            duration_months = (end_sim_date - sub_row['start_date']).days / 30.4
        else:
            duration_months = (sub_row['end_date'] - sub_row['start_date']).days / 30.4
        
        if duration_months <= 0: return 0
        return sub_row['monthly_price'] # monthly_price is already MRR

    # Calculate total MRR generated by each customer over their lifespan or simulation period
    customer_mrr_periods = []
    for customer_id in customers_final['customer_id'].unique():
        customer_subs = all_subscriptions[all_subscriptions['customer_id'] == customer_id].copy()
        customer_subs.sort_values(by='start_date', inplace=True)

        total_mrr_over_lifespan = 0
        current_active_mrr = 0
        current_seats = 0
        
        # Track active subscriptions for MRR calculation
        active_subscriptions_info = {} # {subscription_id: {'start_date', 'end_date', 'monthly_price'}}

        # Iterate through relevant dates (subscription changes, churn, simulation end)
        all_dates = sorted(list(set(customer_subs['start_date'].tolist() + 
                                   [date for date in customer_subs['end_date'].tolist() if date is not None] + 
                                   [generator.end_date])))
        
        last_date = None
        for current_date in all_dates:
            if current_date > generator.end_date:
                current_date = generator.end_date # Cap at simulation end

            if last_date is not None and current_date > last_date:
                # Calculate MRR for the period between last_date and current_date
                days_in_period = (current_date - last_date).days
                if days_in_period > 0 and current_active_mrr > 0:
                     total_mrr_over_lifespan += current_active_mrr * (days_in_period / 30.4) # Sum MRR for the period

            # Update active subscriptions and current_active_mrr at current_date
            # Remove ended subscriptions
            subs_to_remove = []
            for sub_id, info in active_subscriptions_info.items():
                if info['end_date'] and current_date >= info['end_date']:
                    subs_to_remove.append(sub_id)
            for sub_id in subs_to_remove:
                del active_subscriptions_info[sub_id]

            # Add new subscriptions starting on current_date
            new_subs = customer_subs[customer_subs['start_date'] == current_date]
            for _, sub_row in new_subs.iterrows():
                active_subscriptions_info[sub_row['subscription_id']] = {
                    'start_date': sub_row['start_date'],
                    'end_date': sub_row['end_date'],
                    'monthly_price': sub_row['monthly_price']
                }

            # Recalculate current_active_mrr from active subscriptions
            current_active_mrr = sum(info['monthly_price'] for info in active_subscriptions_info.values())
            
            last_date = current_date
            if current_date >= generator.end_date:
                break # Stop if we've reached the simulation end

        customer_mrr_periods.append({'customer_id': customer_id, 'Total_MRR_Over_Lifespan': total_mrr_over_lifespan})

    customer_mrr_df = pd.DataFrame(customer_mrr_periods)
    customers_final = customers_final.merge(customer_mrr_df, on='customer_id', how='left').fillna({'Total_MRR_Over_Lifespan': 0})
    
    # Use Total_MRR_Over_Lifespan as LTV if it's considered gross revenue LTV
    # Adjust LTV to be net revenue if needed, considering refunds/failed payments.
    
    # Ensure Monthly_Revenue is calculated for CAC Payback from actual paid revenue
    # Average Monthly Revenue = Total_Revenue / Actual_Active_Months
    # Need to calculate Active_Months for each customer
    customer_active_dates = all_subscriptions.groupby('customer_id').agg(
        first_active=('start_date', 'min'),
        last_active=('end_date', lambda x: x.max() if x.max() is not pd.NaT else generator.end_date)
    ).reset_index()

    customer_active_dates['actual_active_months'] = (
        (customer_active_dates['last_active'] - customer_active_dates['first_active']).dt.days / 30.4
    ).apply(lambda x: max(1, x)) # Ensure at least 1 month if active

    customers_final = customers_final.merge(customer_active_dates[['customer_id', 'actual_active_months']], on='customer_id', how='left').fillna({'actual_active_months': 1})
    customers_final['Monthly_Revenue'] = customers_final['Total_Revenue'] / customers_final['actual_active_months']
    customers_final['Monthly_Revenue'] = customers_final['Monthly_Revenue'].replace([np.inf, -np.inf], np.nan).fillna(0)


    customers_final['CAC_Payback_Months'] = customers_final['CAC'] / customers_final['Monthly_Revenue']
    customers_final['CAC_Payback_Months'] = customers_final['CAC_Payback_Months'].replace([np.inf, -np.inf], np.nan).fillna(0) # Handle division by zero

    # Calculate Customer Health Score and Churn (integrated into a new function)
    customer_health_churn_data = generator.calculate_customer_health_and_churn(
        customers_final, all_subscriptions, usage, support_interactions
    )
    customers_final = customers_final.merge(customer_health_churn_data, on='customer_id', how='left')


    # Prepare final unit_economics_by_segment.csv
    # This involves grouping the detailed customers_final data
    df_unit_economics_by_segment_final = customers_final.groupby(['industry', 'company_size', 'plan_name', 'billing_frequency']).agg(
        Avg_CAC=('CAC', 'mean'),
        Avg_LTV=('LTV', 'mean'),
        Avg_LTV_CAC=('LTV_CAC_Ratio', 'mean'),
        Avg_Payback_Months=('CAC_Payback_Months', 'mean'),
        Avg_Health_Score=('Customer_Health_Score', 'mean'),
        Customer_Count=('customer_id', 'count')
    ).reset_index()
    # Fill any NaNs that might arise from empty groups or inf values
    df_unit_economics_by_segment_final = df_unit_economics_by_segment_final.replace([np.inf, -np.inf], np.nan).fillna(0)


    print("Saving data to CSVs...")
    customers_final.to_csv(os.path.join(output_dir, 'unit_economics.csv'), index=False)
    df_unit_economics_by_segment_final.to_csv(os.path.join(output_dir, 'unit_economics_by_segment.csv'), index=False)
    all_subscriptions.to_csv(os.path.join(output_dir, 'subscriptions.csv'), index=False)
    payments.to_csv(os.path.join(output_dir, 'payments.csv'), index=False)
    usage.to_csv(os.path.join(output_dir, 'usage_events.csv'), index=False)
    support_interactions.to_csv(os.path.join(output_dir, 'support_interactions.csv'), index=False)

    print(f"\nGenerated Dataset and saved to CSVs in: {output_dir}")
    print(f"- {len(customers)} customers")
    print(f"- {len(subscriptions)} core subscriptions")
    print(f"- {len(addon_subscriptions)} add-on subscriptions")
    print(f"- {len(payments)} payment events")
    print(f"- {len(usage)} usage events")
    print(f"- {len(support_interactions)} support interactions")

    print(f"\n📊 Quick Analysis (from generated data):")
    print(f"- Average CAC: {customers_final['CAC'].mean():.2f}")
    print(f"- Average LTV: {customers_final['LTV'].mean():.2f}")
    print(f"- Average LTV/CAC Ratio: {customers_final['LTV_CAC_Ratio'].mean():.2f}")
    print(f"- Average CAC Payback Months: {customers_final['CAC_Payback_Months'].mean():.2f}")
    print(f"- Overall Churn Rate: {customers_final['Churned'].mean() * 100:.2f}%")
    print(f"- Average Customer Health Score: {customers_final['Customer_Health_Score'].mean():.2f}")
    print(f"- Average seats per subscription: {subscriptions['seats'].mean():.1f}")
    print(f"- Plan distribution (core subscriptions): {subscriptions['plan_name'].value_counts().to_dict()}")
    print(f"- Expansion events: {len(subscriptions[subscriptions['subscription_type'] != 'initial']) + len(addon_subscriptions)}")

    return customers_final, all_subscriptions, payments, usage, support_interactions, df_unit_economics_by_segment_final

# Run the generation
if __name__ == "__main__":
    customers_df, subscriptions_df, payments_df, usage_df, support_interactions_df, segments_df = generate_dataset()
