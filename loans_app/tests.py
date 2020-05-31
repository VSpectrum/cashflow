from .models import Loan, PaymentPeriod
from pydantic import ValidationError
from decimal import Decimal
import pytest

class TestPaymentPeriod:
    @classmethod
    def setup_class(cls):
        cls.paymentperiod = PaymentPeriod()

    def test_monetize(self):
        sample_input = Decimal('123.1234567')
        right_answer = Decimal('123.12')

        # set all decimal fields of payment to have val of 123.1234567
        for field, val in self.paymentperiod.__dict__.items():
            if isinstance(val, Decimal):
                setattr(self.paymentperiod, field, sample_input)

        self.paymentperiod.monetize()

        # assert if monetize() changed all the decimal fields to have a max dp of 2
        for field, val in self.paymentperiod.__dict__.items():
            if isinstance(val, Decimal):
                class_variable = getattr(self.paymentperiod, field)
                assert class_variable == right_answer


class TestLoan:
    @classmethod
    def setup_class(cls):
        cls.validLoan = Loan(
            principal=Decimal('250000'), 
            interest_rate=Decimal('3.625'), 
            term_years=30
        )

    def test_loan_validation(self):
        with pytest.raises(ValidationError):
            invalidLoan = Loan(
                principal=0, 
                interest_rate=0, 
                term_years=0
            )

    def test_payment_per_period_calc(self):
        right_answer = Decimal('1140.13')
        payment_per_period = self.validLoan._payment_per_period_calc()
        payment_per_period = payment_per_period.quantize(Decimal('.01'))
        assert payment_per_period == right_answer

    def test_payment_plan(self):
        # use fixture of results to test against
        pass