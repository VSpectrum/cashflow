from pydantic import BaseModel, Field, ValidationError, validator
from decimal import Decimal
from typing import List  


## MODELS
class PaymentPeriod(BaseModel):
    '''
    Eventually is auto-serialized to represent JSON-blob in the Loan.payment_plan list
    '''
    month: int = 1
    starting_balance: Decimal = Field(Decimal(0), alias='starting-balance')  # alias maps field name to desired format when obj is serialized
    fixed_payment: Decimal = Field(Decimal(0), alias='fixed-payment')
    interest_payment: Decimal = Field(Decimal(0), alias='interest-payment')
    principal_payment: Decimal = Field(Decimal(0), alias='principal-payment')
    ending_balance: Decimal = Field(Decimal(0), alias='ending-balance')
    total_interest: Decimal = Field(Decimal(0), alias='total-interest')

    def monetize(self):
        '''
        When a PaymentPeriod object's calculations are finalized, this function is applied to
        set the precision of the decimal values to represent a typical monetary amount
        (rounding to nearest cent)
        '''
        for field, val in self.__dict__.items():
            if isinstance(val, Decimal):
                setattr(self, field, val.quantize(Decimal('.01')))  # rounding to nearest cent
        return self
                

class Loan(BaseModel):
    '''
    This is instantiated with Principal, interest_rate and term_years.
    Using these inputs, a payment_plan can generated
    '''
    principal: Decimal  # Decimal to avoid rounding errors. Principal aka loan amount
    interest_rate: Decimal  # percent input describing rate @ yearly interval
    term_years: int  # years loan is expected to be paid over
        
    ### VALIDATION
    @validator('principal')
    def valid_principal(cls, _principal):
        if _principal > 0:
            return _principal
        raise ValueError('principal must be greater than 0')

    @validator('interest_rate')
    def valid_interest_rate(cls, _interest_rate):
        if _interest_rate > 0:
            return _interest_rate
        raise ValueError('interest_rate percentage must be greater than 0')
            
    @validator('term_years')
    def valid_term_years(cls, _term_years):
        if 0 < _term_years <= 30:
            return _term_years
        raise ValueError('term_years must be between 1 and 30 years')
    
    ### BUSINESS LOGIC
    def _payment_per_period_calc(self) -> Decimal:
        '''
        This func solves for fixed payment per period (month) using the following formula:
               r (1 + r) ^ n
        A = P ---------------
              (1 + r) ^ n - 1
        '''
        # formula as described with abbreviations for visual similarity of provided/original formula
        P = self.principal
        r = self.interest_rate / 100 / 12  # interest rate per period as decimal instead of %
        n = self.term_years * 12  # number of payments in months

        # below may be verbose but allows for easier visual debugging of formula
        numerator = P * r * (1 + r)**n
        denominator = (1 + r)**n - 1  # if r or n is 0, we will get division by 0
        return  numerator / denominator
        
    async def payment_plan(self) -> List[PaymentPeriod]:
        '''
        Using the 3 variables that instantiated this object, along with the fixed payment per period
        calculated shortly after instantiation, we build a list of what monthly payments will look like
        and the breakdown of the different payments
        '''
        fixed_payment_per_period = self._payment_per_period_calc()
        period_list = [PaymentPeriod() for _ in range(self.term_years * 12)]  # init all blobs for period into a list
        interest_per_month = self.interest_rate / 100 / 12

        previous_balance = self.principal  # initial val is principal
        rolling_sum_interest = Decimal('0')
        for month_num, period_obj in enumerate(period_list, start = 1):
            period_obj.month = month_num
            period_obj.starting_balance = previous_balance
            period_obj.fixed_payment = fixed_payment_per_period
            period_obj.interest_payment = previous_balance * interest_per_month
            period_obj.principal_payment = fixed_payment_per_period - period_obj.interest_payment
            
            previous_balance -= period_obj.principal_payment
            period_obj.ending_balance = previous_balance

            rolling_sum_interest += period_obj.interest_payment
            period_obj.total_interest = rolling_sum_interest
            period_list[month_num-1] = period_obj.monetize()

        return period_list
