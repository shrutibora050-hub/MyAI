'use client'

import { useMemo } from 'react'
import { Client, Provider, fetchExchange } from 'urql'

export function Providers({ children }: { children: React.ReactNode }) {
  const client = useMemo(
    () =>
      new Client({
        url: 'http://localhost:8002/graphql',
        exchanges: [fetchExchange],
      }),
    []
  )

  return <Provider value={client}>{children}</Provider>
}
