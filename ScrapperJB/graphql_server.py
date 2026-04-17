from typing import List, Optional
from datetime import datetime
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from main import scrape_company as scrape_jobs_fn

@strawberry.type
class Job:
    title: str
    company: str
    location: str
    job_url: str
    category: Optional[str] = None
    job_type: Optional[str] = None
    description: Optional[str] = None
    posted_date: Optional[str] = None
    scraped_at: str

@strawberry.type
class ScrapeResult:
    jobs: List[Job]
    count: int
    companies: List[str]
    timestamp: str

@strawberry.type
class Query:
    @strawberry.field
    def scrape_jobs(
        self,
        companies: str = "amazon,simplify",
        keywords: str = "software engineer",
        location: str = "",
        limit: int = 50
    ) -> ScrapeResult:
        company_list = [c.strip().lower() for c in companies.split(',')]
        all_jobs = []

        for company in company_list:
            jobs = scrape_jobs_fn(company, keywords, location, limit)
            all_jobs.extend(jobs)

        job_objects = [
            Job(
                title=job.title,
                company=job.company,
                location=job.location,
                job_url=job.job_url,
                category=job.category if hasattr(job, 'category') else None,
                job_type=job.job_type if hasattr(job, 'job_type') else None,
                description=job.description if hasattr(job, 'description') else None,
                posted_date=job.posted_date if hasattr(job, 'posted_date') else None,
                scraped_at=str(job.scraped_at)
            )
            for job in all_jobs
        ]

        return ScrapeResult(
            jobs=job_objects,
            count=len(job_objects),
            companies=company_list,
            timestamp=datetime.now().isoformat()
        )

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def root():
    return {"message": "Job Scraper GraphQL API", "endpoint": "/graphql"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
