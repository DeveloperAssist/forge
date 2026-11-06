"""Plain-text loan summary for the student-loan page."""
from emi import monthly_emi, total_interest


def rupees(paise: int) -> str:
    return f"₹{paise / 100:,.2f}"


def report(name: str, principal: int, rate: float, months: int) -> str:
    emi = monthly_emi(principal, rate, months)
    lines = [
        f"Loan for {name}",
        f"Amount: {rupees(principal)} at {rate}% for {months} months",
        f"EMI: {rupees(emi)}",
        f"Total interest: {rupees(total_interest(principal, rate, months))}",
    ]
    return "\n".join(lines)
