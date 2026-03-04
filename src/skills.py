def search_company(query: str) -> dict:
    return {
        "name": "TechCorp Berlin",
        "location": "Berlin, Germany",
        "industry": "Software / SaaS",
        "founded": 2015,
    }


def get_financials(company_name: str) -> dict:
    return {
        "revenue": "$50M",
        "employees": 250,
        "funding_stage": "Series B",
        "last_funding": "$12M",
    }


def write_summary(company_data: dict, financial_data: dict) -> str:
    return (
        f"Company Report: {company_data['name']}\n"
        f"Location:       {company_data['location']}\n"
        f"Industry:       {company_data['industry']}\n"
        f"Founded:        {company_data.get('founded', 'N/A')}\n"
        f"\n"
        f"Financials:\n"
        f"  Revenue:       {financial_data.get('revenue', 'N/A')}\n"
        f"  Employees:     {financial_data.get('employees', 'N/A')}\n"
        f"  Funding Stage: {financial_data.get('funding_stage', 'N/A')}\n"
        f"  Last Funding:  {financial_data.get('last_funding', 'N/A')}\n"
    )
