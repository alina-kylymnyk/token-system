class TestCreditFormulas:
    """Tests for credit calculation formulas from the documentation"""

    def test_example_1_generation_cost_0_5412(self):
        """Example 1: Generation cost $0.5412"""
        cost_usd = 0.5412

        # Basic subscription
        basic_credits = cost_usd * 2.0 * 10000
        assert round(basic_credits) == 10824

        # Standard subscription
        standard_credits = cost_usd * 1.9 * 10000
        assert round(standard_credits) == 10283

        # Premium subscription
        premium_credits = cost_usd * 1.8 * 10000
        assert round(premium_credits) == 9742

    def test_example_2_generation_cost_0_98(self):
        """Example 2: Generation cost $0.98"""
        cost_usd = 0.98

        # Basic subscription
        basic_credits = cost_usd * 2.0 * 10000
        assert round(basic_credits) == 19600

        # Standard subscription
        standard_credits = cost_usd * 1.9 * 10000
        assert round(standard_credits) == 18620

        # Premium subscription
        premium_credits = cost_usd * 1.8 * 10000
        assert round(premium_credits) == 17640

    def test_available_generations_basic(self):
        """
        Available generations - Basic subscription

        From documentation:
        At average generation cost $0.50:
        Basic: ~49 generations

        At average generation cost $0.54:
        Basic: ~46 generations
        """
        available_credits = 49900
        multiplier = 2.0

        # Test 1: At avg_cost $0.50
        avg_cost = 0.50
        credits_per_generation = avg_cost * multiplier * 10000  # 10000
        generations = available_credits / credits_per_generation
        assert round(generations) == 5  # 49900 / 10000 = 4.99 ≈ 5

        # Test 2: At avg_cost $0.54
        avg_cost = 0.54
        credits_per_generation = avg_cost * multiplier * 10000  # 10800
        generations = available_credits / credits_per_generation
        assert round(generations) == 5  # 49900 / 10800 = 4.62 ≈ 5

        # NOTE: There is a calculation error in the documentation
        # Correct calculation: 49900 / (0.54 * 2.0 * 10000) = 4.62
        # Documentation shows ~46, which is incorrect (possibly they meant 499,000 credits)

    def test_available_generations_premium(self):
        """
        Available generations - Premium subscription

        From documentation:
        At average generation cost $0.50:
        Premium: ~322 generations

        At average generation cost $0.54:
        Premium: ~298 generations
        """
        available_credits = 289900
        multiplier = 1.8

        # Test 1: At avg_cost $0.50
        avg_cost = 0.50
        credits_per_generation = avg_cost * multiplier * 10000  # 9000
        generations = available_credits / credits_per_generation
        assert round(generations) == 32  # 289900 / 9000 = 32.21 ≈ 32

        # Test 2: At avg_cost $0.54
        avg_cost = 0.54
        credits_per_generation = avg_cost * multiplier * 10000  # 9720
        generations = available_credits / credits_per_generation
        assert round(generations) == 30  # 289900 / 9720 = 29.82 ≈ 30

        # NOTE: There is a calculation error in the documentation
        # Correct calculation: 289900 / (0.54 * 1.8 * 10000) = 29.82
        # Documentation shows ~298, which is incorrect (possibly 2,899,000 credits)
