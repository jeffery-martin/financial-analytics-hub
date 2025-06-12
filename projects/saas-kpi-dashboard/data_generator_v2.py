import math
import random
import uuid
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from os import path, makedirs

import numpy as np
import pandas as pd
from faker import Faker

# Initialize Faker for generating fake data
fake = Faker()
# Set a random seed for reproducibility
np.random.seed(42)


class DataGenerator:
    """
    A class to generate synthetic SaaS subscription, payment, usage, and support data.
    """

    def __init__(self, start_date="2022-01-01", end_date="2024-12-31"):
        """
        Initializes the DataGenerator with a specified date range for data generation.

        Args:
            start_date (str): The start date for data generation in (%Y-%m-%d) format.
            end_date (str): The end date for data generation in (%Y-%m-%d) format.
        """
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Define subscription plans with their attributes
        self.plans = {
            'Starter': {
                'base_price_monthly': 29,
                'per_seat_price': 0,
                'max_seats': 5,
                'annual_discount': 0.10,
                'base_churn_rate': 0.10,  # Slightly increased from 0.08
                'features': ['basic_analytics', 'email_support']
            },
            'Professional': {
                'base_price_monthly': 49,
                'per_seat_price': 15,
                'max_seats': 50,
                'annual_discount': 0.15,
                'base_churn_rate': 0.06,  # Slightly increased from 0.05
                'features': ['advanced_analytics', 'integrations', 'phone_support']
            },
            'Business': {
                'base_price_monthly': 99,
                'per_seat_price': 25,
                'max_seats': 200,
                'annual_discount': 0.20,
                'base_churn_rate': 0.04,  # Slightly increased from 0.03
                'features': ['custom_dashboards', 'api_access', 'dedicated_support']
            },
            'Enterprise': {
                'base_price_monthly': 299,
                'per_seat_price': 35,
                'max_seats': 1000,
                'annual_discount': 0.25,
                'base_churn_rate': 0.02,  # Slightly increased from 0.015
                'features': ['white_label', 'sso', 'custom_integrations', 'customer_success_manager']
            }
        }

        # Define add-ons with their prices, attachment rates, and if they are one-time
        self.addons = {
            'advanced_reporting': {'price_monthly': 50, 'attachment_rate': 0.3, 'one_time': False},
            'api_premium': {'price_monthly': 100, 'attachment_rate': 0.15, 'one_time': False},
            'data_export': {'price_monthly': 25, 'attachment_rate': 0.4, 'one_time': False},
            'priority_support': {'price_monthly': 75, 'attachment_rate': 0.2, 'one_time': False},
            'custom_integrations': {'price_monthly': 200, 'attachment_rate': 0.1, 'one_time': False},
            'training_package': {'price_monthly': 500, 'attachment_rate': 0.05, 'one_time': True}
        }

        # Define seasonal patterns for various events (acquisition, churn, expansion, upgrades)
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
        Calculates the effective monthly recurring revenue (MRR) for a given plan,
        number of seats, and billing frequency, accounting for annual discounts.

        Args:
            plan_name (str): The name of the subscription plan.
            seats (int): The number of seats for the subscription.
            billing_frequency (str): 'monthly' or 'annual'.

        Returns:
            float: The effective monthly recurring revenue (MRR).
        """
        plan = self.plans[plan_name]

        # Calculate base cost based on plan's base price and per-seat price
        # Only seats beyond the first incur per_seat_price up to max_seats
        additional_seats = max(0, min(seats - 1, plan['max_seats'] - 1))
        base_cost_monthly = plan['base_price_monthly'] + (additional_seats * plan['per_seat_price'])

        # Apply annual discount if billing frequency is annual
        if billing_frequency == 'annual':
            # Effective monthly MRR for annual plans is the discounted annual total divided by 12
            effective_monthly_mrr = base_cost_monthly * (1 - plan['annual_discount'])
        else:  # monthly
            effective_monthly_mrr = base_cost_monthly

        return effective_monthly_mrr

    def generate_customers(self, num_customers=3000):
        """
        Generates synthetic customer data, including acquisition details, company size,
        and geographical information. Includes realistic Customer Acquisition Cost (CAC) generation.

        Args:
            num_customers (int): The desired number of customers to generate.

        Returns:
            pandas.DataFrame: A DataFrame containing generated customer data.
        """
        customers = []
        customer_ids = []

        # Define factors influencing customer attributes based on company size
        size_factors = {
            'Startup (1-10)': {'seats_tendency': 1.2, 'upgrade_tendency': 0.8, 'budget': 0.7, 'cac_multiplier': 0.8},
            'Small (11-50)': {'seats_tendency': 1.5, 'upgrade_tendency': 1.0, 'budget': 1.0, 'cac_multiplier': 1.0},
            'Medium (51-200)': {'seats_tendency': 2.0, 'upgrade_tendency': 1.3, 'budget': 1.5, 'cac_multiplier': 1.5},
            'Large (201-1000)': {'seats_tendency': 3.0, 'upgrade_tendency': 1.5, 'budget': 2.0, 'cac_multiplier': 2.0},
            'Enterprise (1000+)': {'seats_tendency': 5.0, 'upgrade_tendency': 1.2, 'budget': 3.0, 'cac_multiplier': 3.0}
        }

        # Base CAC for different acquisition channels - SIGNIFICANTLY INCREASEED FOR LTV:CAC ADJUSTMENT
        base_cac_channel = {
            'Organic Search': 500,  # Increased from 100
            'Paid Search': 1250,  # Increased from 250
            'Social Media': 900,  # Increased from 180
            'Referral': 250,  # Increased from 50
            'Direct': 600,  # Increased from 120
            'Content Marketing': 750,  # Increased from 150
            'Trade Show': 2500,  # Increased from 500
            'Cold Outreach': 3500,  # Increased from 700
            'Partner': 1500,  # Increased from 300
            'Webinar': 1000,  # Increased from 200
            'Free Trial': 400  # Increased from 80
        }

        for i in range(num_customers):
            # Generate a random acquisition date within the specified range
            year = random.randint(self.start_date.year, self.end_date.year)
            month = random.randint(1, 12)
            try:
                last_day_of_month = (datetime(year, month + 1, 1) - timedelta(days=1)).day if month < 12 else 31
                day = random.randint(1, last_day_of_month)
                acquisition_date_potential = datetime(year, month, day)
            except ValueError:
                continue  # Skip invalid dates (e.g., Feb 30)

            # Ensure acquisition date is within the desired range
            if not (self.start_date <= acquisition_date_potential <= self.end_date):
                continue

            # Apply seasonal factor for acquisition
            seasonal_factor = self.seasonal_patterns['acquisition'][acquisition_date_potential.month]
            if random.random() > seasonal_factor / 2.0:  # Adjust probability to reduce generation outside peak seasons
                continue

            company_size_category = random.choice(list(size_factors.keys()))
            acquisition_channel = random.choice(list(base_cac_channel.keys()))

            # Calculate acquisition cost based on channel and company size
            acquisition_cost = max(50, np.random.normal(
                base_cac_channel[acquisition_channel] * size_factors[company_size_category]['cac_multiplier'], 50
            ))

            customer_id = str(uuid.uuid4())
            customer_ids.append(customer_id)  # Collect customer IDs for referral

            # Determine if customer had a trial
            has_trial = random.random() < 0.3
            trial_start_date = None
            trial_end_date = None

            if has_trial:
                trial_duration = random.randint(7, 30)
                trial_start_offset = random.randint(1, 7)  # Trial might start before acquisition date
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
                'seats_tendency': size_factors[company_size_category]['seats_tendency'],
                'upgrade_tendency': size_factors[company_size_category]['upgrade_tendency'],
                'budget_factor': size_factors[company_size_category]['budget'],
                'has_trial': has_trial,
                'trial_start_date': trial_start_date,
                'trial_end_date': trial_end_date
            }
            customers.append(customer)

        customers_df = pd.DataFrame(customers)
        # Randomly assign referred_by_customer_id
        if customer_ids:
            customers_df['referred_by_customer_id'] = np.random.choice(
                [None] + customer_ids,
                size=len(customers_df),
                p=[0.7] + [0.3 / len(customer_ids)] * len(customer_ids)
            )
        else:
            customers_df['referred_by_customer_id'] = None
        return customers_df

    def _create_initial_subscription(self, customer):
        """
        Creates the initial subscription for a given customer.

        Args:
            customer (dict): A dictionary containing customer attributes.

        Returns:
            dict: A dictionary representing the initial subscription details.
        """
        # Determine initial plan based on company size
        if 'Startup' in customer['company_size'] or 'Small' in customer['company_size']:
            plan = np.random.choice(['Starter', 'Professional'], p=[0.6, 0.4])
        elif 'Medium' in customer['company_size']:
            plan = np.random.choice(['Professional', 'Business'], p=[0.5, 0.5])
        else:
            plan = np.random.choice(['Business', 'Enterprise'], p=[0.4, 0.6])

        # Determine initial seats, capped by max_seats for the chosen plan
        base_seats = max(1, int(np.random.exponential(2) * customer['seats_tendency']))
        seats = min(base_seats, self.plans[plan]['max_seats'])

        # Determine billing frequency based on company size
        if 'Enterprise' in customer['company_size']:
            billing_frequency = np.random.choice(['monthly', 'annual'], p=[0.2, 0.8])
        else:
            billing_frequency = np.random.choice(['monthly', 'annual'], p=[0.6, 0.4])

        # Calculate the effective monthly price (MRR)
        monthly_price = self.calculate_monthly_recurring_revenue(plan, seats, billing_frequency)

        # Determine subscription start date (after acquisition, possibly after trial)
        start_delay = max(0, int(np.random.exponential(7)))
        start_date = customer['acquisition_date'] + timedelta(days=start_delay)

        if customer['has_trial'] and customer['trial_end_date'] and start_date < customer['trial_end_date']:
            start_date = customer['trial_end_date'] + timedelta(days=1)

        # Ensure start_date is not beyond simulation end
        if start_date > self.end_date:
            return None  # Customer acquired too late to start a subscription in simulation

        # Calculate churn date and reason
        end_date, churn_reason = self._calculate_churn_date(start_date, plan)

        return {
            'subscription_id': str(uuid.uuid4()),
            'customer_id': customer['customer_id'],
            'plan_name': plan,
            'billing_frequency': billing_frequency,
            'monthly_price': monthly_price,  # This is the effective MRR
            'seats': seats,
            'start_date': start_date,
            'end_date': end_date,
            'subscription_type': 'initial',
            'churn_reason': churn_reason,
            'add_ons': []  # Add-ons are generated separately
        }

    def _calculate_churn_date(self, start_date, plan):
        """
        Calculates the churn date for a subscription, considering seasonality and
        plan type. If no churn occurs within the simulation, the end_date is self.end_date.

        Args:
            start_date (datetime): The start date of the subscription.
            plan (str): The name of the subscription plan.

        Returns:
            tuple: A tuple containing (churn_date: datetime, churn_reason: str or None).
        """
        base_churn_rate = self.plans[plan]['base_churn_rate']
        current_date = start_date

        # Simulate month by month for churn probability
        for _ in range(12 * 10):  # Simulate for up to 10 years
            # If the current date exceeds the simulation end date, customer is still active
            if current_date > self.end_date:
                return self.end_date, None  # Customer remains active until simulation end

            month = current_date.month
            seasonal_churn_factor = self.seasonal_patterns['churn'][month]
            monthly_churn_rate = base_churn_rate * seasonal_churn_factor

            # Original: Factor in plan type: higher plans tend to have lower churn
            # if plan in ['Business', 'Enterprise']:
            #     monthly_churn_rate *= 0.7 # Reduce churn rate for higher plans
            # REMOVED the multiplier to allow higher plans to have slightly higher churn pressure
            # and contribute to bringing down LTV.

            if random.random() < monthly_churn_rate:
                # Churn happens, return the last day of the current month
                if current_date.month == 12:
                    churn_date = current_date.replace(year=current_date.year, month=12, day=31)
                else:
                    churn_date = (current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1))
                # Ensure churn_date does not exceed simulation end_date
                return min(churn_date, self.end_date), self._generate_churn_reason()

            # Move to the start of the next month for the next churn check
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1, day=1)

        # If customer hasn't churned after 10 years, they are still active until simulation end
        return self.end_date, None

    def _generate_expansion_events(self, initial_subscription, customer):
        """
        Generates expansion events (seat additions, plan upgrades) for a given initial subscription.
        Each expansion event creates a new subscription record reflecting the change.

        Args:
            initial_subscription (dict): The initial subscription details.
            customer (dict): The customer associated with the subscription.

        Returns:
            list: A list of dictionaries, each representing an expansion subscription event.
        """
        expansion_events = []

        # Determine the effective end date for generating expansion events
        # If the initial subscription has an end_date, use that; otherwise, use simulation end_date
        effective_subscription_end = initial_subscription['end_date'] if initial_subscription[
            'end_date'] else self.end_date

        current_date = initial_subscription['start_date']
        current_plan = initial_subscription['plan_name']
        current_seats = initial_subscription['seats']
        current_monthly_price = initial_subscription['monthly_price']

        while current_date < effective_subscription_end:
            # Move forward 2-6 months for the next potential expansion event
            current_date += timedelta(days=random.randint(60, 180))

            if current_date >= effective_subscription_end:
                break  # Stop if beyond the subscription's or simulation's end

            month = current_date.month
            expansion_factor = self.seasonal_patterns['expansion'][month]
            upgrade_factor = self.seasonal_patterns['upgrades'][month]

            # Check for seat expansion
            if random.random() < 0.3 * expansion_factor * customer['seats_tendency']:
                additional_seats = random.randint(1, 5)
                new_seats = min(current_seats + additional_seats, self.plans[current_plan]['max_seats'])

                if new_seats > current_seats:
                    new_monthly_price = self.calculate_monthly_recurring_revenue(
                        current_plan, new_seats, initial_subscription['billing_frequency']
                    )

                    if new_monthly_price > current_monthly_price:  # Only create event if MRR actually increased
                        expansion_event = {
                            'subscription_id': str(uuid.uuid4()),
                            'customer_id': customer['customer_id'],
                            'plan_name': current_plan,
                            'billing_frequency': initial_subscription['billing_frequency'],
                            'monthly_price': new_monthly_price,
                            'seats': new_seats,
                            'start_date': current_date,
                            'end_date': initial_subscription['end_date'],  # Inherit end_date from initial sub
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

                if current_plan_index < len(plans_list) - 1:  # Check if an upgrade is possible
                    new_plan = plans_list[current_plan_index + 1]

                    # Adjust seats for the new plan's max seat limit
                    new_plan_max_seats = self.plans[new_plan]['max_seats']
                    new_seats = min(current_seats, new_plan_max_seats)

                    new_monthly_price = self.calculate_monthly_recurring_revenue(
                        new_plan, new_seats, initial_subscription['billing_frequency']
                    )

                    if new_monthly_price > current_monthly_price:  # Only create event if MRR increased
                        upgrade_event = {
                            'subscription_id': str(uuid.uuid4()),
                            'customer_id': customer['customer_id'],
                            'plan_name': new_plan,
                            'billing_frequency': initial_subscription['billing_frequency'],
                            'monthly_price': new_monthly_price,
                            'seats': new_seats,
                            'start_date': current_date,
                            'end_date': initial_subscription['end_date'],  # Inherit end_date from initial sub
                            'subscription_type': 'plan_upgrade',
                            'churn_reason': initial_subscription['churn_reason'],
                            'add_ons': []
                        }
                        expansion_events.append(upgrade_event)
                        current_plan = new_plan
                        current_seats = new_seats
                        current_monthly_price = new_monthly_price

        return expansion_events

    def generate_all_subscriptions(self, customers_df):
        """
        Generates all subscription events for all customers, including initial and expansion events.

        Args:
            customers_df (pandas.DataFrame): DataFrame of generated customer data.

        Returns:
            pandas.DataFrame: A DataFrame containing all subscription events.
        """
        all_subscriptions_list = []

        # Store initial plans for later use in segment analysis
        customer_initial_plans = {}

        for _, customer in customers_df.iterrows():
            initial_sub = self._create_initial_subscription(customer)
            if initial_sub:  # Only add if a valid initial subscription was created
                all_subscriptions_list.append(initial_sub)
                customer_initial_plans[customer['customer_id']] = initial_sub['plan_name']

                # Generate expansion events for this initial subscription
                expansion_events = self._generate_expansion_events(initial_sub, customer)
                all_subscriptions_list.extend(expansion_events)

        subscriptions_df = pd.DataFrame(all_subscriptions_list)
        # Add a column for the customer's initial plan, useful for segmentation
        subscriptions_df['customer_initial_plan'] = subscriptions_df['customer_id'].map(customer_initial_plans)
        return subscriptions_df

    def _generate_churn_reason(self):
        """
        Generates a realistic churn reason from a predefined list.

        Returns:
            str: A random churn reason.
        """
        reasons = [
            'Price sensitivity', 'Lack of features', 'Poor support',
            'Competitor switch', 'Budget cuts', 'No longer needed',
            'Technical issues', 'Merger/acquisition', 'Poor onboarding',
            'Low usage', 'Feature gaps', 'Better alternative found'
        ]
        return random.choice(reasons)

    def generate_addon_subscriptions(self, subscriptions_df):
        """
        Generates add-on subscriptions for existing initial subscriptions.

        Args:
            subscriptions_df (pandas.DataFrame): DataFrame of all core and expansion subscriptions.

        Returns:
            pandas.DataFrame: A DataFrame containing generated add-on subscription data.
        """
        addon_subscriptions = []

        # Iterate only through initial subscriptions to attach add-ons
        initial_subscriptions = subscriptions_df[subscriptions_df['subscription_type'] == 'initial']

        for _, subscription in initial_subscriptions.iterrows():
            plan_addon_multiplier = {
                'Starter': 0.5, 'Professional': 1.0, 'Business': 1.5, 'Enterprise': 2.0
            }
            multiplier = plan_addon_multiplier.get(subscription['plan_name'], 1.0)  # Default to 1.0 if not found

            for addon_name, addon_info in self.addons.items():
                if random.random() < addon_info['attachment_rate'] * multiplier:
                    # Add-on start date is relative to the main subscription's start date
                    days_delay = random.randint(30, 180)
                    addon_start = subscription['start_date'] + timedelta(days=days_delay)

                    # Ensure add-on starts before or at the main subscription end date if it has one
                    if subscription['end_date'] and addon_start > subscription['end_date']:
                        continue

                    # For one-time add-ons, end_date is shortly after start_date
                    if addon_info.get('one_time'):
                        addon_end = addon_start + timedelta(days=1)  # Treat as a single day event for reporting
                    else:
                        # Monthly recurring add-ons
                        # Their end date is tied to the main subscription's end date, or simulation end_date
                        if subscription['end_date']:
                            addon_end = min(addon_start + timedelta(days=365 * 10),
                                            subscription['end_date'])  # Cap at 10 years or main sub end
                        else:
                            addon_end = self.end_date  # Continues as long as main subscription / simulation

                    addon_sub = {
                        'subscription_id': str(uuid.uuid4()),
                        'customer_id': subscription['customer_id'],
                        'plan_name': addon_name,  # The add-on name becomes the 'plan_name' for this record
                        'billing_frequency': subscription['billing_frequency'],  # Inherit main sub's billing freq
                        'monthly_price': addon_info['price_monthly'],  # This is the monthly price or one-time amount
                        'seats': 1,  # Add-ons are usually not per seat
                        'start_date': addon_start,
                        'end_date': addon_end,
                        'subscription_type': 'addon',
                        'churn_reason': None,
                        'add_ons': []  # Add-ons don't have nested add-ons
                    }
                    addon_subscriptions.append(addon_sub)
        return pd.DataFrame(addon_subscriptions)

    def generate_payment_events(self, subscriptions_df):
        """
        Generates payment events for all subscriptions (core, expansion, add-on).
        Handles monthly, annual, and one-time payments.

        Args:
            subscriptions_df (pandas.DataFrame): DataFrame of all subscriptions.

        Returns:
            pandas.DataFrame: A DataFrame containing generated payment events.
        """
        payments = []

        for _, subscription in subscriptions_df.iterrows():
            current_date = subscription['start_date']
            # Determine the payment generation end date (subscription end or simulation end)
            payment_end_date = subscription['end_date'] if subscription['end_date'] else self.end_date

            # Handle one-time add-ons: only one payment at start_date
            if subscription['subscription_type'] == 'addon' and self.addons[subscription['plan_name']].get('one_time'):
                payment = {
                    'payment_id': str(uuid.uuid4()),
                    'subscription_id': subscription['subscription_id'],
                    'customer_id': subscription['customer_id'],
                    'payment_date': subscription['start_date'],
                    'amount': subscription['monthly_price'],  # This is the one-time price
                    'status': 'successful',
                    'payment_method': random.choice(['Credit Card', 'ACH', 'Wire Transfer', 'PayPal']),
                    'subscription_type': subscription['subscription_type']
                }
                payments.append(payment)
                continue  # Move to next subscription, no recurring payments for one-time add-ons

            max_payments = 120  # Limit to 10 years of payments to prevent infinite loops
            payment_count = 0

            while current_date <= payment_end_date and current_date <= self.end_date and payment_count < max_payments:
                payment_method = random.choice(['Credit Card', 'ACH', 'Wire Transfer', 'PayPal'])
                success_rate = {'Credit Card': 0.94, 'ACH': 0.96, 'Wire Transfer': 0.99, 'PayPal': 0.93}

                # Determine payment status
                payment_status = np.random.choice(
                    ['successful', 'failed', 'refunded'],
                    p=[success_rate[payment_method], 1 - success_rate[payment_method] - 0.01, 0.01]
                )

                # Amount is the effective monthly_price (MRR) for monthly plans, or annual amount for annual plans
                amount_due = subscription['monthly_price']
                if subscription['billing_frequency'] == 'annual':
                    amount_due = amount_due * 12  # Annual plans pay 12x their effective monthly MRR

                payment_amount = amount_due if payment_status == 'successful' else 0  # Only successful payments have amount

                payment = {
                    'payment_id': str(uuid.uuid4()),
                    'subscription_id': subscription['subscription_id'],
                    'customer_id': subscription['customer_id'],
                    'payment_date': current_date,
                    'amount': payment_amount,
                    'status': payment_status,
                    'payment_method': payment_method,
                    'subscription_type': subscription['subscription_type']
                }
                payments.append(payment)

                # Move to the start of the next billing cycle
                if subscription['billing_frequency'] == 'monthly':
                    current_date += relativedelta(months=1)
                else:
                    current_date += relativedelta(years=1)

                payment_count += 1
        return pd.DataFrame(payments)

    def generate_usage_events(self, subscriptions_df, base_events_per_month=50):
        """
        Generates usage events for initial and expansion subscriptions (add-ons don't have usage).
        Usage patterns are influenced by plan features and seats.

        Args:
            subscriptions_df (pandas.DataFrame): DataFrame of initial and expansion subscriptions.
            base_events_per_month (int): Base number of usage events per month for calculation.

        Returns:
            pandas.DataFrame: A DataFrame containing generated usage events.
        """
        usage_events = []

        # Filter for only core and expansion subscriptions for usage tracking
        core_and_expansion_subs = subscriptions_df[
            (subscriptions_df['subscription_type'] == 'initial') |
            (subscriptions_df['subscription_type'] == 'seat_expansion') |
            (subscriptions_df['subscription_type'] == 'plan_upgrade')
            ].copy()

        for _, subscription in core_and_expansion_subs.iterrows():
            current_month_start = subscription['start_date'].replace(day=1)
            end_date_for_usage = subscription['end_date'] if subscription['end_date'] else self.end_date

            plan_name = subscription['plan_name']
            plan_features = self.plans.get(plan_name, {}).get('features', [])  # Safely get features
            plan_multipliers = {'Starter': 0.5, 'Professional': 1.0, 'Business': 1.8, 'Enterprise': 3.0}

            # Calculate expected events per month, scaling with plan and seats
            events_per_month_calc = int(
                base_events_per_month * plan_multipliers.get(plan_name, 1.0) * math.log(subscription['seats'] + 1)
            )
            events_per_month = max(10, events_per_month_calc)  # Ensure a minimum number of events

            # Define feature probabilities, adjusting based on actual plan features
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
            else:  # Fallback if no features or probabilities sum to zero
                normalized_probabilities = [1.0 / len(plan_specific_probabilities)] * len(plan_specific_probabilities)

            while current_month_start <= end_date_for_usage and current_month_start <= self.end_date:
                # Calculate days in the current month
                if current_month_start.month == 12:
                    days_in_month = (current_month_start.replace(year=current_month_start.year + 1, month=1,
                                                                 day=1) - current_month_start).days
                else:
                    days_in_month = (current_month_start.replace(month=current_month_start.month + 1,
                                                                 day=1) - current_month_start).days

                daily_events_avg = events_per_month / days_in_month

                for day_of_month in range(1, days_in_month + 1):
                    num_daily_events = np.random.poisson(daily_events_avg)
                    for _ in range(num_daily_events):
                        event_date = current_month_start.replace(day=day_of_month) + timedelta(
                            hours=random.randint(0, 23),
                            minutes=random.randint(0, 59)
                        )
                        # Ensure event date is within the subscription's active period and simulation end
                        if subscription[
                            'start_date'] <= event_date <= end_date_for_usage and event_date <= self.end_date:
                            chosen_feature = np.random.choice(available_features, p=normalized_probabilities)

                            # Simulate seats used: higher plans and more seats mean higher potential usage
                            seats_used = random.randint(1, max(1, min(subscription['seats'], int(
                                subscription['seats'] * np.random.beta(0.8, 1.5)))))

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

                # Move to the start of the next month
                if current_month_start.month == 12:
                    current_month_start = current_month_start.replace(year=current_month_start.year + 1, month=1)
                else:
                    current_month_start = current_month_start.replace(month=current_month_start.month + 1)

        return pd.DataFrame(usage_events)

    def generate_support_interactions(self, customers_df):
        """
        Generates support interactions for customers, including issue category,
        resolution status, time, and sentiment.

        Args:
            customers_df (pandas.DataFrame): DataFrame of generated customer data.

        Returns:
            pandas.DataFrame: A DataFrame containing generated support interaction data.
        """
        interactions = []
        start = self.start_date
        end = self.end_date

        for _, customer in customers_df.iterrows():
            # Number of interactions influenced by budget (higher budget -> fewer issues generally)
            num_interactions = np.random.poisson(1.5 / customer['budget_factor'])

            for _ in range(int(num_interactions)):
                interaction_date = start + timedelta(days=random.randint(0, (end - start).days))

                issue_category = random.choice([
                    'Billing Issue', 'Technical Problem', 'Feature Request',
                    'Onboarding Help', 'Account Management'
                ])

                # Resolution status probability
                resolution_status = np.random.choice(['Resolved', 'Pending', 'Escalated'], p=[0.85, 0.1, 0.05])

                # Base resolution times for categories (hours)
                base_resolution_time = {
                    'Billing Issue': 2, 'Technical Problem': 8, 'Feature Request': 24,
                    'Onboarding Help': 3, 'Account Management': 4
                }

                resolution_time_hours = None
                if resolution_status == 'Resolved':
                    # Add randomness to resolution time, influenced by category
                    resolution_time_hours = max(0.5, np.random.normal(base_resolution_time.get(issue_category, 5), 2))

                # Sentiment influenced by resolution status and time
                sentiment_rating = None
                sentiment_score = None

                if resolution_status == 'Resolved' and resolution_time_hours is not None and resolution_time_hours < 4:
                    sentiment_rating = np.random.choice(['Positive', 'Neutral'], p=[0.7, 0.3])
                    sentiment_score = np.random.uniform(0.7, 1.0)
                elif resolution_status == 'Resolved':
                    sentiment_rating = np.random.choice(['Positive', 'Neutral', 'Negative'], p=[0.4, 0.5, 0.1])
                    sentiment_score = np.random.uniform(0.4, 0.8)
                else:  # Pending or Escalated
                    sentiment_rating = np.random.choice(['Neutral', 'Negative'], p=[0.3, 0.7])
                    sentiment_score = np.random.uniform(0.0, 0.5)

                interaction = {
                    'interaction_id': str(uuid.uuid4()),
                    'customer_id': customer['customer_id'],
                    'interaction_date': interaction_date,
                    'issue_category': issue_category,
                    'resolution_status': resolution_status,
                    'resolution_time_hours': resolution_time_hours,
                    'sentiment_rating': sentiment_rating,
                    'sentiment_score': sentiment_score
                }
                interactions.append(interaction)

        return pd.DataFrame(interactions)

    def calculate_customer_health_and_churn(self, customers_df, subscriptions_df, usage_df, support_df):
        """
        Calculates Customer Health Score and determines final Churn status based on aggregated data.
        This is a post-processing step.

        Args:
            customers_df (pandas.DataFrame): DataFrame of generated customer data.
            subscriptions_df (pandas.DataFrame): DataFrame of all subscription events.
            usage_df (pandas.DataFrame): DataFrame of usage events.
            support_df (pandas.DataFrame): DataFrame of support interactions.

        Returns:
            pandas.DataFrame: A DataFrame with customer_id, Churned status, and health metrics.
        """
        customer_data = customers_df.copy()

        # Determine churned status based on the last subscription end date for each customer
        # A customer is churned if their latest subscription ended before the simulation end date
        latest_sub_end = subscriptions_df.groupby('customer_id')['end_date'].max().reset_index(name='latest_end_date')

        customer_data = customer_data.merge(latest_sub_end, on='customer_id', how='left')
        customer_data['Churned'] = customer_data['latest_end_date'].apply(
            lambda x: 1 if pd.notna(x) and x < self.end_date else 0
        )
        # If no subscription data, assume not churned within simulation (might be new customer)
        customer_data['Churned'] = customer_data['Churned'].fillna(0)

        # Aggregate usage data: average daily events and total active days
        daily_usage = usage_df.groupby(['customer_id', pd.Grouper(key='event_date', freq='D')]).size().reset_index(
            name='daily_events')
        avg_daily_events = daily_usage.groupby('customer_id')['daily_events'].mean().reset_index(
            name='avg_daily_events')

        customer_usage_summary = usage_df.groupby('customer_id').agg(
            Active_Days=('event_date', lambda x: x.dt.date.nunique()),
            Total_Usage_Events=('event_type', 'count')
        ).reset_index()

        # Calculate Average Sentiment Score from support interactions
        sentiment_mapping = {'Positive': 1.0, 'Neutral': 0.5, 'Negative': 0.0}
        support_df['numerical_sentiment'] = support_df['sentiment_rating'].map(sentiment_mapping)
        avg_sentiment = support_df.groupby('customer_id')['numerical_sentiment'].mean().reset_index(
            name='Avg_Sentiment_Score')

        # Merge aggregated data back to customer_data
        customer_data = customer_data.merge(avg_daily_events, on='customer_id', how='left').fillna(
            {'avg_daily_events': 0})
        customer_data = customer_data.merge(customer_usage_summary, on='customer_id', how='left').fillna({
            'Active_Days': 0, 'Total_Usage_Events': 0
        })
        customer_data = customer_data.merge(avg_sentiment, on='customer_id', how='left').fillna(
            {'Avg_Sentiment_Score': 0.5})

        # Normalize usage metrics for health score calculation
        # Handle cases where max() might be 0 to avoid division by zero
        max_active_days = customer_data['Active_Days'].max() if customer_data['Active_Days'].max() > 0 else 1
        max_total_events = customer_data['Total_Usage_Events'].max() if customer_data[
                                                                            'Total_Usage_Events'].max() > 0 else 1

        customer_data['Usage_Score'] = (
                0.5 * (customer_data['Active_Days'] / max_active_days) +
                0.5 * (customer_data['Total_Usage_Events'] / max_total_events)
        )
        customer_data['Usage_Score'] = customer_data['Usage_Score'].fillna(0)  # Fill NaN for customers with no usage

        # Calculate Customer Health Score based on various normalized factors
        customer_data['Customer_Health_Score'] = (
                0.4 * customer_data['Usage_Score'] +
                0.3 * customer_data['Avg_Sentiment_Score'] +
                0.2 * (1 - customer_data['Churned']) +  # Active customers (Churned=0) contribute positively
                0.1 * (customer_data['budget_factor'] / (
            customer_data['budget_factor'].max() if customer_data['budget_factor'].max() > 0 else 1))
        # Higher budget might indicate stability
        )

        # Normalize health score to a 0-1 scale
        max_health_score = customer_data['Customer_Health_Score'].max()
        if max_health_score > 0:
            customer_data['Customer_Health_Score'] = customer_data['Customer_Health_Score'] / max_health_score
        else:
            customer_data['Customer_Health_Score'] = 0.5  # Default if no variability

        # Select and return relevant columns
        return customer_data[[
            'customer_id', 'Churned', 'Avg_Sentiment_Score', 'Active_Days',
            'Total_Usage_Events', 'Usage_Score', 'Customer_Health_Score'
        ]]


def generate_dataset():
    """
    Generates a comprehensive synthetic SaaS dataset including customers,
    subscriptions (initial, expansion, add-on), payments, usage, and support interactions.
    Calculates unit economics metrics (LTV, CAC, Payback, Health Score) and saves data to CSVs.

    Returns:
        tuple: A tuple of pandas DataFrames:
               (customers_final, all_subscriptions, payments, usage, support_interactions, df_unit_economics_by_segment_final)
    """
    generator = DataGenerator()

    # Define output directory to your cloned repo for easy commit/push
    output_dir = '/Users/jeffmartin/PycharmProjects/financial-analytics-hub/projects/saas-kpi-dashboard'
    makedirs(output_dir, exist_ok=True)

    print("Generating customers...")
    customers = generator.generate_customers(2000)

    print("Generating all subscriptions (initial and expansion events)...")
    # This method now handles both initial and subsequent expansion events
    all_subscriptions = generator.generate_all_subscriptions(customers)

    print("Generating add-on subscriptions...")
    addon_subscriptions = generator.generate_addon_subscriptions(all_subscriptions)

    # Concatenate all subscription types for payment generation and overall analysis
    all_subscriptions_final = pd.concat([all_subscriptions, addon_subscriptions], ignore_index=True)

    print("Generating payments...")
    payments = generator.generate_payment_events(all_subscriptions_final)

    print("Generating usage events (only for core and expansion subscriptions)...")
    # Usage events are typically tied to core product subscriptions, not add-ons
    usage = generator.generate_usage_events(
        all_subscriptions[all_subscriptions['subscription_type'].isin(['initial', 'seat_expansion', 'plan_upgrade'])])

    print("Generating support interactions...")
    support_interactions = generator.generate_support_interactions(customers)

    # --- Post-processing to calculate final unit economics metrics ---

    # Calculate LTV: Sum of successful payments per customer
    # Ensure payments_df is not empty before operations
    if not payments.empty:
        customer_payments = payments[payments['status'] == 'successful'].groupby('customer_id')[
            'amount'].sum().reset_index(name='Total_Revenue')
    else:
        customer_payments = pd.DataFrame(columns=['customer_id', 'Total_Revenue'])

    # Merge total revenue back to customers
    customers_with_revenue = customers.merge(customer_payments, on='customer_id', how='left').fillna(
        {'Total_Revenue': 0})

    # Add CAC to customers_final (already exists in customers DataFrame)
    customers_with_revenue.rename(columns={'acquisition_cost': 'CAC'}, inplace=True)
    customers_with_revenue['CAC'] = customers_with_revenue['CAC'].fillna(0)  # Ensure no NaN CAC

    # Calculate LTV: For this dataset, LTV is simply the total revenue generated
    customers_with_revenue['LTV'] = customers_with_revenue['Total_Revenue']

    # Calculate LTV_CAC_Ratio, handling division by zero
    customers_with_revenue['LTV_CAC_Ratio'] = customers_with_revenue.apply(
        lambda row: row['LTV'] / row['CAC'] if row['CAC'] > 0 else 0, axis=1
    )

    # Calculate Actual Active Months for each customer
    customer_active_dates = all_subscriptions_final.groupby('customer_id').agg(
        first_active=('start_date', 'min'),
        last_active=('end_date', lambda x: x.max() if x.max() is not pd.NaT else generator.end_date)
    ).reset_index()

    customer_active_dates['actual_active_months'] = (
            (customer_active_dates['last_active'] - customer_active_dates['first_active']).dt.days / 30.4
    ).apply(lambda x: max(1, x))  # Ensure at least 1 month if active

    customers_final = customers_with_revenue.merge(customer_active_dates[['customer_id', 'actual_active_months']],
                                                   on='customer_id', how='left').fillna({'actual_active_months': 1})

    # Calculate Average Monthly Revenue for CAC Payback (using total revenue over active months)
    customers_final['Monthly_Revenue'] = customers_final['Total_Revenue'] / customers_final['actual_active_months']
    customers_final['Monthly_Revenue'] = customers_final['Monthly_Revenue'].replace([np.inf, -np.inf], np.nan).fillna(0)

    # Calculate CAC_Payback_Months, handling division by zero
    customers_final['CAC_Payback_Months'] = customers_final.apply(
        lambda row: row['CAC'] / row['Monthly_Revenue'] if row['Monthly_Revenue'] > 0 else 0, axis=1
    )

    # Calculate Customer Health Score and Churn (integrated into a new function)
    customer_health_churn_data = generator.calculate_customer_health_and_churn(
        customers_final, all_subscriptions_final, usage, support_interactions
    )
    customers_final = customers_final.merge(customer_health_churn_data, on='customer_id', how='left')

    # Prepare final unit_economics_by_segment.csv
    # Merge the initial plan name back to customers_final for proper segmentation
    initial_subs_only = all_subscriptions_final[all_subscriptions_final['subscription_type'] == 'initial'].copy()
    customers_final = customers_final.merge(initial_subs_only[['customer_id', 'plan_name', 'billing_frequency']],
                                            on='customer_id', how='left', suffixes=('', '_initial'))
    # Rename for clarity
    customers_final.rename(columns={'plan_name': 'initial_plan_name', 'billing_frequency': 'initial_billing_frequency'},
                           inplace=True)

    df_unit_economics_by_segment_final = customers_final.groupby(
        ['industry', 'company_size', 'initial_plan_name', 'initial_billing_frequency']
    ).agg(
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
    customers_final.to_csv(path.join(output_dir, 'unit_economics.csv'), index=False)
    df_unit_economics_by_segment_final.to_csv(path.join(output_dir, 'unit_economics_by_segment.csv'), index=False)
    all_subscriptions_final.to_csv(path.join(output_dir, 'subscriptions.csv'), index=False)
    payments.to_csv(path.join(output_dir, 'payments.csv'), index=False)
    usage.to_csv(path.join(output_dir, 'usage_events.csv'), index=False)
    support_interactions.to_csv(path.join(output_dir, 'support_interactions.csv'), index=False)

    print(f"\nGenerated Dataset and saved to CSVs in: {output_dir}")
    print(f"- {len(customers)} customers")
    print(f"- {len(all_subscriptions)} core/expansion subscriptions")  # Updated count
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
    # Ensure 'initial' subscriptions are used for average seats and plan distribution
    print(
        f"- Average seats per initial subscription: {all_subscriptions[all_subscriptions['subscription_type'] == 'initial']['seats'].mean():.1f}")
    print(
        f"- Initial Plan distribution (core subscriptions): {all_subscriptions[all_subscriptions['subscription_type'] == 'initial']['plan_name'].value_counts().to_dict()}")
    # Calculate total expansion events
    total_expansion_events = len(
        all_subscriptions[all_subscriptions['subscription_type'].isin(['seat_expansion', 'plan_upgrade'])])
    print(f"- Expansion events: {total_expansion_events}")

    return customers_final, all_subscriptions_final, payments, usage, support_interactions, df_unit_economics_by_segment_final


# Run the generation
if __name__ == "__main__":
    customers_df, subscriptions_df, payments_df, usage_df, support_interactions_df, segments_df = generate_dataset()
