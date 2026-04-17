# GraphQL Service Changes

## Files Added
1. **graphql_server.py** - FastAPI + Strawberry GraphQL server
2. **example_queries.graphql** - Sample queries

## Files Modified
1. **requirements.txt** - Added FastAPI, Strawberry GraphQL, Uvicorn
2. **Dockerfile** - Changed CMD to run GraphQL server, exposed port 8000
3. **docker-compose.yml** - Added graphql-server service + CLI service with profiles

## Usage

### Start GraphQL Server
```bash
docker-compose up
```
Server: http://localhost:8000/graphql

### Run CLI Scraper
```bash
docker-compose run --rm scraper-cli
```

### Query Example (GraphQL Playground)
```graphql
query {
  scrapeJobs(
    companies: "amazon,simplify"
    keywords: "software engineer"
    limit: 50
  ) {
    count
    jobs {
      title
      company
      location
      jobUrl
    }
  }
}
```

### cURL Example
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ scrapeJobs(companies: \"simplify\", limit: 10) { count jobs { title company } } }"}'
```

## Dependencies Added
- strawberry-graphql[fastapi]==0.243.0
- uvicorn[standard]==0.32.1
- fastapi==0.115.6
