import os
from typing import List, Optional
from datetime import datetime, date
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@strawberry.type
class JobComment:
    id: int
    job_id: int
    comment: str
    created_at: str
    updated_at: str


@strawberry.type
class JobAction:
    id: int
    job_id: int
    action: str
    action_date: Optional[str]
    completed: bool
    created_at: str
    updated_at: str


@strawberry.type
class JobLabel:
    id: int
    job_id: int
    label: str
    created_at: str


@strawberry.type
class Job:
    id: int
    title: str
    company: str
    location: Optional[str]
    job_url: str
    description: Optional[str]
    job_type: Optional[str]
    category: Optional[str]
    posted_date: Optional[str]
    source: Optional[str]
    scraped_at: str
    created_at: str
    updated_at: str
    comments: List[JobComment]
    actions: List[JobAction]
    labels: List[JobLabel]


@strawberry.type
class JobsResponse:
    jobs: List[Job]
    total: int
    page: int
    page_size: int


def get_db_connection():
    db_url = os.getenv('DATABASE_URL', 'postgresql://scraper:scraper_password@jobs-postgres:5432/jobs_db')
    return psycopg2.connect(db_url, cursor_factory=RealDictCursor)


def get_job_interactions(conn, job_id: int):
    cursor = conn.cursor()

    # Get comments
    cursor.execute("SELECT * FROM job_comments WHERE job_id = %s ORDER BY created_at DESC", (job_id,))
    comments = [
        JobComment(
            id=row['id'],
            job_id=row['job_id'],
            comment=row['comment'],
            created_at=row['created_at'].isoformat(),
            updated_at=row['updated_at'].isoformat()
        )
        for row in cursor.fetchall()
    ]

    # Get actions
    cursor.execute("SELECT * FROM job_actions WHERE job_id = %s ORDER BY action_date NULLS LAST, created_at DESC", (job_id,))
    actions = [
        JobAction(
            id=row['id'],
            job_id=row['job_id'],
            action=row['action'],
            action_date=row['action_date'].isoformat() if row['action_date'] else None,
            completed=row['completed'],
            created_at=row['created_at'].isoformat(),
            updated_at=row['updated_at'].isoformat()
        )
        for row in cursor.fetchall()
    ]

    # Get labels
    cursor.execute("SELECT * FROM job_labels WHERE job_id = %s ORDER BY created_at DESC", (job_id,))
    labels = [
        JobLabel(
            id=row['id'],
            job_id=row['job_id'],
            label=row['label'],
            created_at=row['created_at'].isoformat()
        )
        for row in cursor.fetchall()
    ]

    cursor.close()
    return comments, actions, labels


@strawberry.type
class Query:
    @strawberry.field
    def jobs(
        self,
        company: Optional[str] = None,
        source: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> JobsResponse:
        """Get jobs with optional filtering and pagination"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            where_clauses = []
            params = []
            if company:
                where_clauses.append("LOWER(company) = LOWER(%s)")
                params.append(company)
            if source:
                where_clauses.append("LOWER(source) = LOWER(%s)")
                params.append(source)

            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

            count_query = f"SELECT COUNT(*) as count FROM jobs {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()['count']

            offset = (page - 1) * page_size
            query = f"""
                SELECT * FROM jobs
                {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([page_size, offset])
            cursor.execute(query, params)

            rows = cursor.fetchall()
            jobs = []
            for row in rows:
                comments, actions, labels = get_job_interactions(conn, row['id'])
                jobs.append(Job(
                    id=row['id'],
                    title=row['title'],
                    company=row['company'],
                    location=row['location'],
                    job_url=row['job_url'],
                    description=row['description'],
                    job_type=row['job_type'],
                    category=row['category'],
                    posted_date=row['posted_date'],
                    source=row['source'],
                    scraped_at=row['scraped_at'].isoformat(),
                    created_at=row['created_at'].isoformat(),
                    updated_at=row['updated_at'].isoformat(),
                    comments=comments,
                    actions=actions,
                    labels=labels
                ))

            return JobsResponse(
                jobs=jobs,
                total=total,
                page=page,
                page_size=page_size
            )

        finally:
            cursor.close()
            conn.close()

    @strawberry.field
    def job(self, id: int) -> Optional[Job]:
        """Get a single job by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM jobs WHERE id = %s", (id,))
            row = cursor.fetchone()

            if not row:
                return None

            comments, actions, labels = get_job_interactions(conn, row['id'])

            return Job(
                id=row['id'],
                title=row['title'],
                company=row['company'],
                location=row['location'],
                job_url=row['job_url'],
                description=row['description'],
                job_type=row['job_type'],
                category=row['category'],
                posted_date=row['posted_date'],
                source=row['source'],
                scraped_at=row['scraped_at'].isoformat(),
                created_at=row['created_at'].isoformat(),
                updated_at=row['updated_at'].isoformat(),
                comments=comments,
                actions=actions,
                labels=labels
            )

        finally:
            cursor.close()
            conn.close()

    @strawberry.field
    def companies(self) -> List[str]:
        """Get list of all companies"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT DISTINCT company FROM jobs ORDER BY company")
            companies = [row['company'] for row in cursor.fetchall()]
            return companies

        finally:
            cursor.close()
            conn.close()

    @strawberry.field
    def sources(self) -> List[str]:
        """Get list of all job sources"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT DISTINCT source FROM jobs WHERE source IS NOT NULL ORDER BY source")
            sources = [row['source'] for row in cursor.fetchall()]
            return sources

        finally:
            cursor.close()
            conn.close()


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_comment(self, job_id: int, comment: str) -> JobComment:
        """Add a comment to a job"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO job_comments (job_id, comment) VALUES (%s, %s) RETURNING *",
                (job_id, comment)
            )
            row = cursor.fetchone()
            conn.commit()

            return JobComment(
                id=row['id'],
                job_id=row['job_id'],
                comment=row['comment'],
                created_at=row['created_at'].isoformat(),
                updated_at=row['updated_at'].isoformat()
            )

        finally:
            cursor.close()
            conn.close()

    @strawberry.mutation
    def add_action(self, job_id: int, action: str, action_date: Optional[str] = None) -> JobAction:
        """Add an action/next step for a job"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO job_actions (job_id, action, action_date) VALUES (%s, %s, %s) RETURNING *",
                (job_id, action, action_date)
            )
            row = cursor.fetchone()
            conn.commit()

            return JobAction(
                id=row['id'],
                job_id=row['job_id'],
                action=row['action'],
                action_date=row['action_date'].isoformat() if row['action_date'] else None,
                completed=row['completed'],
                created_at=row['created_at'].isoformat(),
                updated_at=row['updated_at'].isoformat()
            )

        finally:
            cursor.close()
            conn.close()

    @strawberry.mutation
    def toggle_action_completed(self, action_id: int) -> JobAction:
        """Toggle action completed status"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE job_actions SET completed = NOT completed WHERE id = %s RETURNING *",
                (action_id,)
            )
            row = cursor.fetchone()
            conn.commit()

            return JobAction(
                id=row['id'],
                job_id=row['job_id'],
                action=row['action'],
                action_date=row['action_date'].isoformat() if row['action_date'] else None,
                completed=row['completed'],
                created_at=row['created_at'].isoformat(),
                updated_at=row['updated_at'].isoformat()
            )

        finally:
            cursor.close()
            conn.close()

    @strawberry.mutation
    def add_label(self, job_id: int, label: str) -> JobLabel:
        """Add a label/domain to a job"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO job_labels (job_id, label) VALUES (%s, %s) ON CONFLICT (job_id, label) DO NOTHING RETURNING *",
                (job_id, label)
            )
            row = cursor.fetchone()

            if not row:
                # Label already exists, fetch it
                cursor.execute(
                    "SELECT * FROM job_labels WHERE job_id = %s AND label = %s",
                    (job_id, label)
                )
                row = cursor.fetchone()
            else:
                conn.commit()

            return JobLabel(
                id=row['id'],
                job_id=row['job_id'],
                label=row['label'],
                created_at=row['created_at'].isoformat()
            )

        finally:
            cursor.close()
            conn.close()

    @strawberry.mutation
    def remove_label(self, label_id: int) -> bool:
        """Remove a label from a job"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM job_labels WHERE id = %s", (label_id,))
            conn.commit()
            return True

        finally:
            cursor.close()
            conn.close()

    @strawberry.mutation
    def delete_comment(self, comment_id: int) -> bool:
        """Delete a comment"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM job_comments WHERE id = %s", (comment_id,))
            conn.commit()
            return True

        finally:
            cursor.close()
            conn.close()

    @strawberry.mutation
    def delete_action(self, action_id: int) -> bool:
        """Delete an action"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM job_actions WHERE id = %s", (action_id,))
            conn.commit()
            return True

        finally:
            cursor.close()
            conn.close()


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Job Scraper API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def root():
    return {
        "service": "Job Scraper API Gateway",
        "graphql_endpoint": "/graphql",
        "graphql_playground": "/graphql (browser)"
    }


@app.get("/health")
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting API Gateway on port 8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)
