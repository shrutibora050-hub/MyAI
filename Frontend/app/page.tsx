'use client'

import { useQuery } from 'urql'
import { useEffect, useState } from 'react'
import JobCard from './components/JobCard'

const JobsQuery = `
  query Jobs($company: String, $source: String, $page: Int, $pageSize: Int) {
    jobs(company: $company, source: $source, page: $page, pageSize: $pageSize) {
      total
      page
      jobs {
        id
        title
        company
        location
        jobUrl
        postedDate
        source
        description
        jobType
        category
        scrapedAt
        createdAt
        updatedAt
        comments {
          id
          comment
          createdAt
        }
        actions {
          id
          action
          actionDate
          completed
          createdAt
        }
        labels {
          id
          label
          createdAt
        }
      }
    }
    companies
    sources
  }
`

export default function Home() {
  const [selectedCompany, setSelectedCompany] = useState<string>('')
  const [selectedSource, setSelectedSource] = useState<string>('')
  const [page, setPage] = useState(1)

  const [result, reexecuteQuery] = useQuery({
    query: JobsQuery,
    variables: {
      company: selectedCompany || null,
      source: selectedSource || null,
      page,
      pageSize: 20,
    },
  })

  // Poll every 30 seconds for database updates
  useEffect(() => {
    const interval = setInterval(() => {
      reexecuteQuery({ requestPolicy: 'network-only' })
    }, 30000)

    return () => clearInterval(interval)
  }, [reexecuteQuery])

  const { data, fetching, error } = result

  const handleUpdate = () => {
    reexecuteQuery({ requestPolicy: 'network-only' })
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-red-600">Error: {error.message}</div>
      </div>
    )
  }

  const jobs = data?.jobs?.jobs || []
  const companies = data?.companies || []
  const sources = data?.sources || []
  const total = data?.jobs?.total || 0

  return (
    <div
      className="min-h-screen p-8 bg-cover bg-center bg-fixed"
      style={{
        backgroundImage: 'url(/financial_district_nyc.png)',
      }}
    >
      <div className="max-w-6xl mx-auto">
        <header className="mb-8 backdrop-blur-md bg-white/10 p-6 rounded-xl border border-white/20">
          <h1 className="text-4xl font-light mb-2 text-white">Software Engineering Jobs</h1>
          <p className="text-white/80 text-sm">
            {total} jobs available • Auto-refreshes every 30s
          </p>
        </header>

        <div className="mb-6 flex gap-3 flex-wrap backdrop-blur-md bg-white/10 p-4 rounded-xl border border-white/20">
          <select
            className="px-4 py-2 border border-white/30 rounded-lg bg-white/20 backdrop-blur text-white text-sm"
            value={selectedCompany}
            onChange={(e) => {
              setSelectedCompany(e.target.value)
              setPage(1)
            }}
          >
            <option value="">All Companies</option>
            {companies.map((company: string) => (
              <option key={company} value={company}>
                {company}
              </option>
            ))}
          </select>

          <select
            className="px-4 py-2 border border-white/30 rounded-lg bg-white/20 backdrop-blur text-white text-sm"
            value={selectedSource}
            onChange={(e) => {
              setSelectedSource(e.target.value)
              setPage(1)
            }}
          >
            <option value="">All Sources</option>
            {sources.map((source: string) => (
              <option key={source} value={source}>
                {source}
              </option>
            ))}
          </select>

          {(selectedCompany || selectedSource) && (
            <button
              onClick={() => {
                setSelectedCompany('')
                setSelectedSource('')
                setPage(1)
              }}
              className="px-4 py-2 text-sm text-white/90 hover:bg-white/10 rounded-lg transition-colors"
            >
              Clear filters
            </button>
          )}
        </div>

        {fetching ? (
          <div className="text-center py-12 backdrop-blur-md bg-white/10 rounded-xl border border-white/20">
            <div className="text-white text-sm">Loading...</div>
          </div>
        ) : (
          <div className="space-y-3">
            {jobs.map((job: any) => (
              <JobCard key={job.id} job={job} onUpdate={handleUpdate} />
            ))}
          </div>
        )}

        {total > 20 && (
          <div className="mt-8 flex justify-center gap-3 backdrop-blur-md bg-white/10 p-4 rounded-xl border border-white/20">
            <button
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
              className="px-4 py-2 border border-white/30 rounded-lg disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white/10 bg-white/20 text-white text-sm transition-colors"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-white text-sm">
              Page {page} of {Math.ceil(total / 20)}
            </span>
            <button
              disabled={page >= Math.ceil(total / 20)}
              onClick={() => setPage(page + 1)}
              className="px-4 py-2 border border-white/30 rounded-lg disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white/10 bg-white/20 text-white text-sm transition-colors"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
