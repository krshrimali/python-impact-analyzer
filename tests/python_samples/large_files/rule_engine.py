# Large Python file with complex conditional logic
# This file simulates a rule engine with many nested conditions and complex decision trees

import datetime
import re
import json
import random
import math
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from enum import Enum, auto
from dataclasses import dataclass

# Constants
MAX_RULE_DEPTH = 10
DEFAULT_SCORE_THRESHOLD = 0.5
RULE_CACHE_SIZE = 100

# Enums for rule types
class RuleType(Enum):
    SIMPLE = auto()
    COMPOSITE = auto()
    CONDITIONAL = auto()
    SCORING = auto()
    TEMPORAL = auto()
    REGEX = auto()
    CUSTOM = auto()

class LogicalOperator(Enum):
    AND = auto()
    OR = auto()
    NOT = auto()
    XOR = auto()
    IMPLIES = auto()

class ComparisonOperator(Enum):
    EQUAL = auto()
    NOT_EQUAL = auto()
    GREATER_THAN = auto()
    LESS_THAN = auto()
    GREATER_THAN_OR_EQUAL = auto()
    LESS_THAN_OR_EQUAL = auto()
    CONTAINS = auto()
    NOT_CONTAINS = auto()
    STARTS_WITH = auto()
    ENDS_WITH = auto()
    MATCHES = auto()

class TemporalOperator(Enum):
    BEFORE = auto()
    AFTER = auto()
    DURING = auto()
    OVERLAPS = auto()
    WITHIN = auto()

# Data classes for rule definitions
@dataclass
class RuleContext:
    """Context for rule evaluation."""
    facts: Dict[str, Any]
    timestamp: datetime.datetime = None
    trace: List[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now()
        if self.trace is None:
            self.trace = []
    
    def add_trace(self, message: str) -> None:
        """Add a trace message to the context."""
        self.trace.append(f"[{datetime.datetime.now().isoformat()}] {message}")
    
    def get_fact(self, fact_name: str, default: Any = None) -> Any:
        """Get a fact from the context."""
        return self.facts.get(fact_name, default)
    
    def set_fact(self, fact_name: str, value: Any) -> None:
        """Set a fact in the context."""
        self.facts[fact_name] = value

@dataclass
class RuleResult:
    """Result of a rule evaluation."""
    success: bool
    score: float = 0.0
    message: str = ""
    actions: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []
    
    def add_action(self, action_type: str, **kwargs) -> None:
        """Add an action to the result."""
        self.actions.append({"type": action_type, **kwargs})
    
    def merge(self, other: 'RuleResult', operator: LogicalOperator) -> 'RuleResult':
        """Merge this result with another result using the specified operator."""
        if operator == LogicalOperator.AND:
            success = self.success and other.success
            score = min(self.score, other.score)
        elif operator == LogicalOperator.OR:
            success = self.success or other.success
            score = max(self.score, other.score)
        elif operator == LogicalOperator.NOT:
            success = not other.success
            score = 1.0 - other.score
        elif operator == LogicalOperator.XOR:
            success = (self.success and not other.success) or (not self.success and other.success)
            score = abs(self.score - other.score)
        elif operator == LogicalOperator.IMPLIES:
            success = (not self.success) or other.success
            score = 1.0 if success else 0.0
        else:
            raise ValueError(f"Unsupported operator: {operator}")
        
        # Combine actions
        actions = self.actions.copy()
        for action in other.actions:
            if action not in actions:
                actions.append(action)
        
        # Combine messages
        message = f"{self.message} {operator.name} {other.message}" if self.message and other.message else self.message or other.message
        
        return RuleResult(success=success, score=score, message=message, actions=actions)

# Base Rule class
class Rule:
    """Base class for all rules."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.rule_type = RuleType.SIMPLE
        self._cache = {}
    
    def evaluate(self, context: RuleContext) -> RuleResult:
        """Evaluate the rule against the given context."""
        # Check cache first
        cache_key = self._get_cache_key(context)
        if cache_key in self._cache:
            context.add_trace(f"Rule '{self.name}' cache hit")
            return self._cache[cache_key]
        
        context.add_trace(f"Evaluating rule '{self.name}'")
        result = self._evaluate(context)
        
        # Update cache
        self._update_cache(cache_key, result)
        
        return result
    
    def _evaluate(self, context: RuleContext) -> RuleResult:
        """Internal evaluation method to be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement _evaluate")
    
    def _get_cache_key(self, context: RuleContext) -> str:
        """Generate a cache key for the given context."""
        # Simple implementation - in a real system, this would be more sophisticated
        facts_str = json.dumps(context.facts, sort_keys=True)
        return f"{self.name}:{hash(facts_str)}"
    
    def _update_cache(self, key: str, result: RuleResult) -> None:
        """Update the rule cache."""
        self._cache[key] = result
        
        # Limit cache size
        if len(self._cache) > RULE_CACHE_SIZE:
            # Remove a random key to keep cache size in check
            remove_key = random.choice(list(self._cache.keys()))
            del self._cache[remove_key]
    
    def __str__(self) -> str:
        return f"{self.rule_type.name} Rule: {self.name}"

# Simple rules
class SimpleRule(Rule):
    """A simple rule that evaluates a single condition."""
    
    def __init__(self, name: str, fact_name: str, operator: ComparisonOperator, 
                 expected_value: Any, description: str = ""):
        super().__init__(name, description)
        self.rule_type = RuleType.SIMPLE
        self.fact_name = fact_name
        self.operator = operator
        self.expected_value = expected_value
    
    def _evaluate(self, context: RuleContext) -> RuleResult:
        actual_value = context.get_fact(self.fact_name)
        
        if actual_value is None:
            return RuleResult(
                success=False,
                message=f"Fact '{self.fact_name}' not found in context"
            )
        
        success = self._compare_values(actual_value, self.expected_value)
        
        message = f"Fact '{self.fact_name}' {self.operator.name} '{self.expected_value}': {'SUCCESS' if success else 'FAILURE'}"
        context.add_trace(message)
        
        return RuleResult(success=success, message=message)
    
    def _compare_values(self, actual: Any, expected: Any) -> bool:
        """Compare values using the specified operator."""
        if self.operator == ComparisonOperator.EQUAL:
            return actual == expected
        elif self.operator == ComparisonOperator.NOT_EQUAL:
            return actual != expected
        elif self.operator == ComparisonOperator.GREATER_THAN:
            return actual > expected
        elif self.operator == ComparisonOperator.LESS_THAN:
            return actual < expected
        elif self.operator == ComparisonOperator.GREATER_THAN_OR_EQUAL:
            return actual >= expected
        elif self.operator == ComparisonOperator.LESS_THAN_OR_EQUAL:
            return actual <= expected
        elif self.operator == ComparisonOperator.CONTAINS:
            return expected in actual
        elif self.operator == ComparisonOperator.NOT_CONTAINS:
            return expected not in actual
        elif self.operator == ComparisonOperator.STARTS_WITH:
            return actual.startswith(expected)
        elif self.operator == ComparisonOperator.ENDS_WITH:
            return actual.endswith(expected)
        elif self.operator == ComparisonOperator.MATCHES:
            return bool(re.match(expected, actual))
        else:
            raise ValueError(f"Unsupported operator: {self.operator}")

# Composite rules
class CompositeRule(Rule):
    """A rule that combines multiple other rules using a logical operator."""
    
    def __init__(self, name: str, rules: List[Rule], operator: LogicalOperator, description: str = ""):
        super().__init__(name, description)
        self.rule_type = RuleType.COMPOSITE
        self.rules = rules
        self.operator = operator
    
    def _evaluate(self, context: RuleContext) -> RuleResult:
        if not self.rules:
            return RuleResult(success=False, message="No rules to evaluate")
        
        # Evaluate the first rule
        result = self.rules[0].evaluate(context)
        
        # Short-circuit evaluation for AND and OR
        if self.operator == LogicalOperator.AND and not result.success:
            context.add_trace(f"Short-circuit AND evaluation for '{self.name}'")
            return result
        
        if self.operator == LogicalOperator.OR and result.success:
            context.add_trace(f"Short-circuit OR evaluation for '{self.name}'")
            return result
        
        # Evaluate remaining rules and combine results
        for rule in self.rules[1:]:
            next_result = rule.evaluate(context)
            result = result.merge(next_result, self.operator)
            
            # Short-circuit if possible
            if self.operator == LogicalOperator.AND and not result.success:
                context.add_trace(f"Short-circuit AND evaluation for '{self.name}'")
                break
            
            if self.operator == LogicalOperator.OR and result.success:
                context.add_trace(f"Short-circuit OR evaluation for '{self.name}'")
                break
        
        context.add_trace(f"Composite rule '{self.name}' result: {result.success}")
        return result

# Conditional rules
class ConditionalRule(Rule):
    """A rule that evaluates different rules based on a condition."""
    
    def __init__(self, name: str, condition: Rule, then_rule: Rule, else_rule: Optional[Rule] = None, description: str = ""):
        super().__init__(name, description)
        self.rule_type = RuleType.CONDITIONAL
        self.condition = condition
        self.then_rule = then_rule
        self.else_rule = else_rule
    
    def _evaluate(self, context: RuleContext) -> RuleResult:
        # Evaluate the condition
        condition_result = self.condition.evaluate(context)
        
        if condition_result.success:
            context.add_trace(f"Condition '{self.condition.name}' succeeded, evaluating THEN rule")
            result = self.then_rule.evaluate(context)
        elif self.else_rule:
            context.add_trace(f"Condition '{self.condition.name}' failed, evaluating ELSE rule")
            result = self.else_rule.evaluate(context)
        else:
            context.add_trace(f"Condition '{self.condition.name}' failed, no ELSE rule")
            result = RuleResult(success=False, message="Condition failed and no ELSE rule provided")
        
        return result

# Scoring rules
class ScoringRule(Rule):
    """A rule that assigns a score based on multiple criteria."""
    
    def __init__(self, name: str, scoring_rules: List[Tuple[Rule, float]], threshold: float = DEFAULT_SCORE_THRESHOLD, description: str = ""):
        super().__init__(name, description)
        self.rule_type = RuleType.SCORING
        self.scoring_rules = scoring_rules  # List of (rule, weight) tuples
        self.threshold = threshold
    
    def _evaluate(self, context: RuleContext) -> RuleResult:
        total_weight = sum(weight for _, weight in self.scoring_rules)
        weighted_score = 0.0
        
        rule_results = []
        for rule, weight in self.scoring_rules:
            rule_result = rule.evaluate(context)
            normalized_weight = weight / total_weight if total_weight > 0 else 0
            rule_score = rule_result.score if hasattr(rule_result, 'score') else (1.0 if rule_result.success else 0.0)
            weighted_score += rule_score * normalized_weight
            rule_results.append((rule, rule_result, normalized_weight))
        
        success = weighted_score >= self.threshold
        
        # Build detailed message
        message_parts = [f"Scoring rule '{self.name}' result: {weighted_score:.2f} (threshold: {self.threshold:.2f})"]
        for rule, result, weight in rule_results:
            rule_score = result.score if hasattr(result, 'score') else (1.0 if result.success else 0.0)
            message_parts.append(f"  - {rule.name}: {rule_score:.2f} * {weight:.2f} = {rule_score * weight:.2f}")
        
        message = "\n".join(message_parts)
        context.add_trace(message)
        
        return RuleResult(success=success, score=weighted_score, message=message)

# Temporal rules
class TemporalRule(Rule):
    """A rule that evaluates conditions based on time."""
    
    def __init__(self, name: str, fact_name: str, operator: TemporalOperator, 
                 reference_time: Union[datetime.datetime, str], window: Optional[datetime.timedelta] = None, description: str = ""):
        super().__init__(name, description)
        self.rule_type = RuleType.TEMPORAL
        self.fact_name = fact_name
        self.operator = operator
        
        # Handle string reference time
        if isinstance(reference_time, str):
            self.reference_time = datetime.datetime.fromisoformat(reference_time)
        else:
            self.reference_time = reference_time
        
        self.window = window
    
    def _evaluate(self, context: RuleContext) -> RuleResult:
        fact_time = context.get_fact(self.fact_name)
        
        if fact_time is None:
            return RuleResult(
                success=False,
                message=f"Temporal fact '{self.fact_name}' not found in context"
            )
        
        # Convert string to datetime if needed
        if isinstance(fact_time, str):
            try:
                fact_time = datetime.datetime.fromisoformat(fact_time)
            except ValueError:
                return RuleResult(
                    success=False,
                    message=f"Could not parse temporal fact '{self.fact_name}' as datetime: {fact_time}"
                )
        
        success = self._compare_times(fact_time)
        
        message = f"Temporal fact '{self.fact_name}' {self.operator.name} reference time: {'SUCCESS' if success else 'FAILURE'}"
        context.add_trace(message)
        
        return RuleResult(success=success, message=message)
    
    def _compare_times(self, fact_time: datetime.datetime) -> bool:
        """Compare times using the specified operator."""
        if self.operator == TemporalOperator.BEFORE:
            return fact_time < self.reference_time
        elif self.operator == TemporalOperator.AFTER:
            return fact_time > self.reference_time
        elif self.operator == TemporalOperator.DURING:
            if not self.window:
                raise ValueError("Window required for DURING operator")
            start_time = self.reference_time
            end_time = self.reference_time + self.window
            return start_time <= fact_time <= end_time
        elif self.operator == TemporalOperator.OVERLAPS:
            if not self.window:
                raise ValueError("Window required for OVERLAPS operator")
            fact_start = fact_time
            fact_end = fact_time + self.window
            ref_start = self.reference_time
            ref_end = self.reference_time + self.window
            return (fact_start <= ref_end) and (ref_start <= fact_end)
        elif self.operator == TemporalOperator.WITHIN:
            if not self.window:
                raise ValueError("Window required for WITHIN operator")
            delta = abs(fact_time - self.reference_time)
            return delta <= self.window
        else:
            raise ValueError(f"Unsupported temporal operator: {self.operator}")

# Regex rules
class RegexRule(Rule):
    """A rule that evaluates a regular expression against a fact."""
    
    def __init__(self, name: str, fact_name: str, pattern: str, description: str = ""):
        super().__init__(name, description)
        self.rule_type = RuleType.REGEX
        self.fact_name = fact_name
        self.pattern = pattern
        self.regex = re.compile(pattern)
    
    def _evaluate(self, context: RuleContext) -> RuleResult:
        fact_value = context.get_fact(self.fact_name)
        
        if fact_value is None:
            return RuleResult(
                success=False,
                message=f"Fact '{self.fact_name}' not found in context"
            )
        
        if not isinstance(fact_value, str):
            return RuleResult(
                success=False,
                message=f"Fact '{self.fact_name}' is not a string: {type(fact_value)}"
            )
        
        match = self.regex.search(fact_value)
        success = bool(match)
        
        message = f"Regex match for '{self.fact_name}' against pattern '{self.pattern}': {'SUCCESS' if success else 'FAILURE'}"
        context.add_trace(message)
        
        result = RuleResult(success=success, message=message)
        
        # Add captured groups as actions if there's a match
        if success and match.groups():
            result.add_action("regex_capture", groups=match.groups(), groupdict=match.groupdict())
        
        return result

# Custom rules
class CustomRule(Rule):
    """A rule that uses a custom function for evaluation."""
    
    def __init__(self, name: str, evaluation_function: Callable[[RuleContext], RuleResult], description: str = ""):
        super().__init__(name, description)
        self.rule_type = RuleType.CUSTOM
        self.evaluation_function = evaluation_function
    
    def _evaluate(self, context: RuleContext) -> RuleResult:
        context.add_trace(f"Evaluating custom rule '{self.name}'")
        return self.evaluation_function(context)

# Rule Engine
class RuleEngine:
    """Engine for evaluating rules against facts."""
    
    def __init__(self):
        self.rules: Dict[str, Rule] = {}
        self.rule_sets: Dict[str, List[str]] = {}
    
    def add_rule(self, rule: Rule) -> None:
        """Add a rule to the engine."""
        self.rules[rule.name] = rule
    
    def remove_rule(self, rule_name: str) -> None:
        """Remove a rule from the engine."""
        if rule_name in self.rules:
            del self.rules[rule_name]
            
            # Remove from any rule sets
            for rule_set_name, rule_names in self.rule_sets.items():
                if rule_name in rule_names:
                    self.rule_sets[rule_set_name].remove(rule_name)
    
    def create_rule_set(self, name: str, rule_names: List[str]) -> None:
        """Create a named set of rules."""
        # Validate that all rules exist
        for rule_name in rule_names:
            if rule_name not in self.rules:
                raise ValueError(f"Rule '{rule_name}' does not exist")
        
        self.rule_sets[name] = rule_names.copy()
    
    def evaluate_rule(self, rule_name: str, facts: Dict[str, Any]) -> RuleResult:
        """Evaluate a single rule against the given facts."""
        if rule_name not in self.rules:
            return RuleResult(success=False, message=f"Rule '{rule_name}' not found")
        
        context = RuleContext(facts=facts)
        return self.rules[rule_name].evaluate(context)
    
    def evaluate_rule_set(self, rule_set_name: str, facts: Dict[str, Any], operator: LogicalOperator = LogicalOperator.AND) -> RuleResult:
        """Evaluate a set of rules against the given facts."""
        if rule_set_name not in self.rule_sets:
            return RuleResult(success=False, message=f"Rule set '{rule_set_name}' not found")
        
        rule_names = self.rule_sets[rule_set_name]
        if not rule_names:
            return RuleResult(success=False, message=f"Rule set '{rule_set_name}' is empty")
        
        context = RuleContext(facts=facts)
        
        # Evaluate the first rule
        first_rule_name = rule_names[0]
        result = self.rules[first_rule_name].evaluate(context)
        
        # Short-circuit evaluation if possible
        if operator == LogicalOperator.AND and not result.success:
            return result
        
        if operator == LogicalOperator.OR and result.success:
            return result
        
        # Evaluate remaining rules
        for rule_name in rule_names[1:]:
            rule_result = self.rules[rule_name].evaluate(context)
            result = result.merge(rule_result, operator)
            
            # Short-circuit if possible
            if operator == LogicalOperator.AND and not result.success:
                break
            
            if operator == LogicalOperator.OR and result.success:
                break
        
        return result
    
    def evaluate_all_rules(self, facts: Dict[str, Any]) -> Dict[str, RuleResult]:
        """Evaluate all rules against the given facts."""
        results = {}
        context = RuleContext(facts=facts)
        
        for rule_name, rule in self.rules.items():
            results[rule_name] = rule.evaluate(context)
        
        return results

# Example usage and complex rule construction
def create_customer_eligibility_rules() -> RuleEngine:
    """Create a set of rules for determining customer eligibility for various products."""
    engine = RuleEngine()
    
    # Basic customer validation rules
    age_rule = SimpleRule(
        name="minimum_age",
        fact_name="customer.age",
        operator=ComparisonOperator.GREATER_THAN_OR_EQUAL,
        expected_value=18,
        description="Customer must be at least 18 years old"
    )
    
    income_rule = SimpleRule(
        name="minimum_income",
        fact_name="customer.annual_income",
        operator=ComparisonOperator.GREATER_THAN_OR_EQUAL,
        expected_value=20000,
        description="Customer must have annual income of at least $20,000"
    )
    
    credit_score_rule = SimpleRule(
        name="minimum_credit_score",
        fact_name="customer.credit_score",
        operator=ComparisonOperator.GREATER_THAN_OR_EQUAL,
        expected_value=600,
        description="Customer must have a credit score of at least 600"
    )
    
    # Address validation
    address_regex = RegexRule(
        name="valid_address_format",
        fact_name="customer.address",
        pattern=r"^\d+\s+[A-Za-z\s]+,\s+[A-Za-z\s]+,\s+[A-Z]{2}\s+\d{5}$",
        description="Address must be in the format: 123 Main St, City, ST 12345"
    )
    
    email_regex = RegexRule(
        name="valid_email",
        fact_name="customer.email",
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Email must be in a valid format"
    )
    
    # Temporal rules
    account_age_rule = TemporalRule(
        name="minimum_account_age",
        fact_name="customer.account_created_date",
        operator=TemporalOperator.BEFORE,
        reference_time=datetime.datetime.now() - datetime.timedelta(days=90),
        description="Account must be at least 90 days old"
    )
    
    recent_login_rule = TemporalRule(
        name="recent_login",
        fact_name="customer.last_login_date",
        operator=TemporalOperator.WITHIN,
        reference_time=datetime.datetime.now(),
        window=datetime.timedelta(days=30),
        description="Customer must have logged in within the last 30 days"
    )
    
    # Composite rules
    basic_eligibility = CompositeRule(
        name="basic_eligibility",
        rules=[age_rule, income_rule, credit_score_rule],
        operator=LogicalOperator.AND,
        description="Basic eligibility criteria for all products"
    )
    
    contact_validation = CompositeRule(
        name="contact_validation",
        rules=[address_regex, email_regex],
        operator=LogicalOperator.AND,
        description="Validation of customer contact information"
    )
    
    activity_check = CompositeRule(
        name="activity_check",
        rules=[account_age_rule, recent_login_rule],
        operator=LogicalOperator.AND,
        description="Check for customer account activity"
    )
    
    # Credit card eligibility scoring
    credit_card_score = ScoringRule(
        name="credit_card_eligibility_score",
        scoring_rules=[
            (credit_score_rule, 0.5),
            (income_rule, 0.3),
            (activity_check, 0.2)
        ],
        threshold=0.7,
        description="Scoring rule for credit card eligibility"
    )
    
    # Loan eligibility with conditional logic
    high_income_rule = SimpleRule(
        name="high_income",
        fact_name="customer.annual_income",
        operator=ComparisonOperator.GREATER_THAN_OR_EQUAL,
        expected_value=100000,
        description="Customer has high income (>= $100,000)"
    )
    
    excellent_credit_rule = SimpleRule(
        name="excellent_credit",
        fact_name="customer.credit_score",
        operator=ComparisonOperator.GREATER_THAN_OR_EQUAL,
        expected_value=750,
        description="Customer has excellent credit (>= 750)"
    )
    
    premium_customer = CompositeRule(
        name="premium_customer",
        rules=[high_income_rule, excellent_credit_rule],
        operator=LogicalOperator.AND,
        description="Customer qualifies as a premium customer"
    )
    
    standard_loan_eligibility = CompositeRule(
        name="standard_loan_eligibility",
        rules=[basic_eligibility, contact_validation],
        operator=LogicalOperator.AND,
        description="Standard loan eligibility criteria"
    )
    
    premium_loan_eligibility = SimpleRule(
        name="premium_loan_eligibility",
        fact_name="customer.premium_member",
        operator=ComparisonOperator.EQUAL,
        expected_value=True,
        description="Premium member loan eligibility"
    )
    
    loan_eligibility = ConditionalRule(
        name="loan_eligibility",
        condition=premium_customer,
        then_rule=premium_loan_eligibility,
        else_rule=standard_loan_eligibility,
        description="Determine loan eligibility based on customer status"
    )
    
    # Custom rule for fraud detection
    def evaluate_fraud_risk(context: RuleContext) -> RuleResult:
        # Complex fraud detection logic
        risk_score = 0.0
        risk_factors = []
        
        # Check for suspicious IP address
        ip_address = context.get_fact("customer.ip_address")
        suspicious_ips = ["192.168.0.1", "10.0.0.1"]  # Example list
        if ip_address in suspicious_ips:
            risk_score += 0.4
            risk_factors.append("Suspicious IP address")
        
        # Check for multiple failed login attempts
        login_attempts = context.get_fact("customer.failed_login_attempts", 0)
        if login_attempts > 3:
            risk_score += 0.3
            risk_factors.append(f"Multiple failed login attempts ({login_attempts})")
        
        # Check for rapid account changes
        last_update = context.get_fact("customer.last_account_update")
        if last_update:
            try:
                update_time = datetime.datetime.fromisoformat(last_update)
                if (datetime.datetime.now() - update_time).total_seconds() < 3600:  # Less than 1 hour
                    risk_score += 0.2
                    risk_factors.append("Recent account update")
            except ValueError:
                pass
        
        # Check for unusual transaction amount
        transaction_amount = context.get_fact("transaction.amount", 0)
        average_amount = context.get_fact("customer.average_transaction_amount", 0)
        if average_amount > 0 and transaction_amount > average_amount * 3:
            risk_score += 0.3
            risk_factors.append(f"Unusual transaction amount (${transaction_amount} vs avg ${average_amount})")
        
        # Determine result
        success = risk_score < 0.5
        message = f"Fraud risk assessment: {risk_score:.2f}"
        if risk_factors:
            message += f"\nRisk factors: {', '.join(risk_factors)}"
        
        result = RuleResult(success=success, score=risk_score, message=message)
        
        # Add actions based on risk level
        if risk_score >= 0.7:
            result.add_action("block_transaction", reason="High fraud risk")
        elif risk_score >= 0.5:
            result.add_action("flag_for_review", reason="Medium fraud risk")
        else:
            result.add_action("allow_transaction", reason="Low fraud risk")
        
        return result
    
    fraud_detection_rule = CustomRule(
        name="fraud_detection",
        evaluation_function=evaluate_fraud_risk,
        description="Custom rule for fraud detection"
    )
    
    # Add all rules to the engine
    for rule in [
        age_rule, income_rule, credit_score_rule, address_regex, email_regex,
        account_age_rule, recent_login_rule, basic_eligibility, contact_validation,
        activity_check, credit_card_score, high_income_rule, excellent_credit_rule,
        premium_customer, standard_loan_eligibility, premium_loan_eligibility,
        loan_eligibility, fraud_detection_rule
    ]:
        engine.add_rule(rule)
    
    # Create rule sets
    engine.create_rule_set("customer_validation", [
        "minimum_age", "valid_email", "valid_address_format"
    ])
    
    engine.create_rule_set("credit_card_application", [
        "basic_eligibility", "credit_card_eligibility_score", "fraud_detection"
    ])
    
    engine.create_rule_set("loan_application", [
        "loan_eligibility", "fraud_detection"
    ])
    
    return engine

def process_customer_application(engine: RuleEngine, customer_data: Dict[str, Any], product_type: str) -> Dict[str, Any]:
    """Process a customer application for a specific product."""
    # Prepare facts
    facts = {"customer": customer_data}
    
    # Add transaction data if available
    if "transaction" in customer_data:
        facts["transaction"] = customer_data["transaction"]
    
    # Determine which rule set to evaluate
    if product_type == "credit_card":
        rule_set = "credit_card_application"
    elif product_type == "loan":
        rule_set = "loan_application"
    else:
        return {
            "success": False,
            "message": f"Unknown product type: {product_type}",
            "actions": []
        }
    
    # Evaluate the rule set
    result = engine.evaluate_rule_set(rule_set, facts)
    
    # Prepare response
    response = {
        "success": result.success,
        "message": result.message,
        "actions": result.actions,
        "score": result.score
    }
    
    return response

def main():
    # Create the rule engine with predefined rules
    engine = create_customer_eligibility_rules()
    
    # Example customer data
    good_customer = {
        "name": "John Doe",
        "age": 35,
        "annual_income": 75000,
        "credit_score": 720,
        "address": "123 Main St, Anytown, CA 12345",
        "email": "john.doe@example.com",
        "account_created_date": (datetime.datetime.now() - datetime.timedelta(days=180)).isoformat(),
        "last_login_date": (datetime.datetime.now() - datetime.timedelta(days=5)).isoformat(),
        "failed_login_attempts": 0,
        "premium_member": False,
        "average_transaction_amount": 500,
        "transaction": {
            "amount": 600,
            "date": datetime.datetime.now().isoformat(),
            "type": "purchase"
        }
    }
    
    risky_customer = {
        "name": "Jane Smith",
        "age": 22,
        "annual_income": 30000,
        "credit_score": 620,
        "address": "456 Oak St, Somewhere, NY 54321",
        "email": "jane.smith@example.com",
        "account_created_date": (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat(),
        "last_login_date": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(),
        "failed_login_attempts": 4,
        "premium_member": False,
        "average_transaction_amount": 200,
        "transaction": {
            "amount": 2000,
            "date": datetime.datetime.now().isoformat(),
            "type": "withdrawal"
        }
    }
    
    premium_customer = {
        "name": "Robert Johnson",
        "age": 45,
        "annual_income": 150000,
        "credit_score": 800,
        "address": "789 Pine St, Elsewhere, TX 67890",
        "email": "robert.johnson@example.com",
        "account_created_date": (datetime.datetime.now() - datetime.timedelta(days=365)).isoformat(),
        "last_login_date": (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(),
        "failed_login_attempts": 0,
        "premium_member": True,
        "average_transaction_amount": 1500,
        "transaction": {
            "amount": 3000,
            "date": datetime.datetime.now().isoformat(),
            "type": "transfer"
        }
    }
    
    # Process applications
    print("=== Good Customer Credit Card Application ===")
    result = process_customer_application(engine, good_customer, "credit_card")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print(f"Score: {result.get('score', 'N/A')}")
    print("Actions:")
    for action in result.get('actions', []):
        print(f"  - {action['type']}: {action.get('reason', '')}")
    
    print("\n=== Risky Customer Credit Card Application ===")
    result = process_customer_application(engine, risky_customer, "credit_card")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print(f"Score: {result.get('score', 'N/A')}")
    print("Actions:")
    for action in result.get('actions', []):
        print(f"  - {action['type']}: {action.get('reason', '')}")
    
    print("\n=== Premium Customer Loan Application ===")
    result = process_customer_application(engine, premium_customer, "loan")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print(f"Score: {result.get('score', 'N/A')}")
    print("Actions:")
    for action in result.get('actions', []):
        print(f"  - {action['type']}: {action.get('reason', '')}")

if __name__ == "__main__":
    main()