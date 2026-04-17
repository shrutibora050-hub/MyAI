'use client'

import { useState } from 'react'
import { useMutation } from 'urql'

const AddCommentMutation = `
  mutation AddComment($jobId: Int!, $comment: String!) {
    addComment(jobId: $jobId, comment: $comment) {
      id
      comment
      createdAt
    }
  }
`

const AddActionMutation = `
  mutation AddAction($jobId: Int!, $action: String!, $actionDate: String) {
    addAction(jobId: $jobId, action: $action, actionDate: $actionDate) {
      id
      action
      actionDate
      completed
    }
  }
`

const AddLabelMutation = `
  mutation AddLabel($jobId: Int!, $label: String!) {
    addLabel(jobId: $jobId, label: $label) {
      id
      label
    }
  }
`

const ToggleActionMutation = `
  mutation ToggleAction($actionId: Int!) {
    toggleActionCompleted(actionId: $actionId) {
      id
      completed
    }
  }
`

const RemoveLabelMutation = `
  mutation RemoveLabel($labelId: Int!) {
    removeLabel(labelId: $labelId)
  }
`

export default function JobCard({ job, onUpdate }: any) {
  const [showDetails, setShowDetails] = useState(false)
  const [newComment, setNewComment] = useState('')
  const [newAction, setNewAction] = useState('')
  const [actionDate, setActionDate] = useState('')
  const [newLabel, setNewLabel] = useState('')

  const [, addComment] = useMutation(AddCommentMutation)
  const [, addAction] = useMutation(AddActionMutation)
  const [, addLabel] = useMutation(AddLabelMutation)
  const [, toggleAction] = useMutation(ToggleActionMutation)
  const [, removeLabel] = useMutation(RemoveLabelMutation)

  // Calculate relative time for posted date
  const getRelativeTime = (dateString: string) => {
    if (!dateString) return null
    try {
      const date = new Date(dateString)
      const now = new Date()
      const diffInMs = now.getTime() - date.getTime()
      const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24))

      if (diffInDays === 0) return 'Today'
      if (diffInDays === 1) return 'Yesterday'
      if (diffInDays < 7) return `${diffInDays} days ago`
      if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`
      if (diffInDays < 365) return `${Math.floor(diffInDays / 30)} months ago`
      return `${Math.floor(diffInDays / 365)} years ago`
    } catch {
      return dateString
    }
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return null
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    } catch {
      return dateString
    }
  }

  const handleAddComment = async () => {
    if (!newComment.trim()) return
    await addComment({ jobId: job.id, comment: newComment })
    setNewComment('')
    onUpdate()
  }

  const handleAddAction = async () => {
    if (!newAction.trim()) return
    await addAction({
      jobId: job.id,
      action: newAction,
      actionDate: actionDate || null,
    })
    setNewAction('')
    setActionDate('')
    onUpdate()
  }

  const handleAddLabel = async () => {
    if (!newLabel.trim()) return
    await addLabel({ jobId: job.id, label: newLabel })
    setNewLabel('')
    onUpdate()
  }

  const handleToggleAction = async (actionId: number) => {
    await toggleAction({ actionId })
    onUpdate()
  }

  const handleRemoveLabel = async (labelId: number) => {
    await removeLabel({ labelId })
    onUpdate()
  }

  return (
    <div className="backdrop-blur-md bg-white/10 p-5 rounded-xl border border-white/20 hover:bg-white/15 transition-all">
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <h2 className="text-lg font-medium text-white">{job.title}</h2>
          <p className="text-white/80 text-sm mt-1">{job.company}</p>
          {job.location && (
            <p className="text-xs text-white/70 mt-1">📍 {job.location}</p>
          )}
        </div>
        <div className="text-right">
          {job.postedDate && (
            <div className="text-xs text-white/70">
              Posted {getRelativeTime(job.postedDate) || job.postedDate}
            </div>
          )}
        </div>
      </div>

      {/* Job metadata row */}
      <div className="flex flex-wrap gap-2 text-xs">
        {job.source && (
          <span className="px-2 py-1 bg-white/10 text-white/70 rounded">
            {job.source}
          </span>
        )}
        {job.jobType && (
          <span className="px-2 py-1 bg-white/10 text-white/70 rounded">
            {job.jobType}
          </span>
        )}
        {job.category && (
          <span className="px-2 py-1 bg-white/10 text-white/70 rounded">
            {job.category}
          </span>
        )}
        {job.scrapedAt && (
          <span className="px-2 py-1 bg-white/10 text-white/70 rounded">
            Scraped {getRelativeTime(job.scrapedAt)}
          </span>
        )}
      </div>

      {/* Labels */}
      {job.labels && job.labels.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-3">
          {job.labels.map((label: any) => (
            <span
              key={label.id}
              className="px-2.5 py-1 bg-white/20 text-white text-xs rounded-full flex items-center gap-1.5"
            >
              {label.label}
              <button
                onClick={() => handleRemoveLabel(label.id)}
                className="text-white/70 hover:text-white"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}

      <div className="mt-4 flex gap-2">
        <a
          href={job.jobUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2 bg-white/20 text-white text-sm rounded-lg hover:bg-white/30 transition-colors"
        >
          View Job →
        </a>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="px-4 py-2 bg-white/10 text-white/90 text-sm rounded-lg hover:bg-white/20 transition-colors"
        >
          {showDetails ? 'Hide Details' : 'Show Details'}
        </button>
      </div>

      {showDetails && (
        <div className="mt-4 border-t border-white/20 pt-4 space-y-3">
          {/* Job Description */}
          {job.description && (
            <div>
              <h3 className="text-sm text-white/90 mb-2">Job Description</h3>
              <div className="text-xs text-white/70 bg-white/5 p-3 rounded-lg max-h-40 overflow-y-auto">
                {job.description}
              </div>
            </div>
          )}

          {/* Metadata Details */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            {job.createdAt && (
              <div className="bg-white/5 p-2 rounded">
                <span className="text-white/60">Added to DB</span>
                <div className="text-white/90">{formatDate(job.createdAt)}</div>
              </div>
            )}
            {job.scrapedAt && (
              <div className="bg-white/5 p-2 rounded">
                <span className="text-white/60">Scraped on</span>
                <div className="text-white/90">{formatDate(job.scrapedAt)}</div>
              </div>
            )}
            {job.postedDate && (
              <div className="bg-white/5 p-2 rounded">
                <span className="text-white/60">Posted on</span>
                <div className="text-white/90">{formatDate(job.postedDate)}</div>
              </div>
            )}
            {job.updatedAt && (
              <div className="bg-white/5 p-2 rounded">
                <span className="text-white/60">Last updated</span>
                <div className="text-white/90">{formatDate(job.updatedAt)}</div>
              </div>
            )}
          </div>

          {/* Comments Section */}
          <div>
            <h3 className="text-sm text-white/90 mb-2">Comments</h3>
            <div className="space-y-2 mb-2">
              {job.comments?.map((comment: any) => (
                <div key={comment.id} className="text-xs bg-white/5 p-2 rounded text-white/80">
                  {comment.comment}
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add a comment..."
                className="flex-1 px-3 py-2 bg-white/10 border border-white/20 rounded text-xs text-white placeholder-white/50 focus:bg-white/15 focus:outline-none"
                onKeyPress={(e) => e.key === 'Enter' && handleAddComment()}
              />
              <button
                onClick={handleAddComment}
                className="px-3 py-2 bg-white/20 text-white text-xs rounded hover:bg-white/30 transition-colors"
              >
                Add
              </button>
            </div>
          </div>

          {/* Actions Section */}
          <div>
            <h3 className="text-sm text-white/90 mb-2">Next Actions</h3>
            <div className="space-y-2 mb-2">
              {job.actions?.map((action: any) => (
                <div
                  key={action.id}
                  className="flex items-center gap-2 text-xs bg-white/5 p-2 rounded"
                >
                  <input
                    type="checkbox"
                    checked={action.completed}
                    onChange={() => handleToggleAction(action.id)}
                    className="h-3 w-3 rounded"
                  />
                  <span
                    className={action.completed ? 'line-through text-white/50' : 'text-white/80'}
                  >
                    {action.action}
                    {action.actionDate && (
                      <span className="text-white/60 ml-2">
                        ({new Date(action.actionDate).toLocaleDateString()})
                      </span>
                    )}
                  </span>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newAction}
                onChange={(e) => setNewAction(e.target.value)}
                placeholder="Add action..."
                className="flex-1 px-3 py-2 bg-white/10 border border-white/20 rounded text-xs text-white placeholder-white/50 focus:bg-white/15 focus:outline-none"
                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleAddAction()}
              />
              <input
                type="date"
                value={actionDate}
                onChange={(e) => setActionDate(e.target.value)}
                className="px-3 py-2 bg-white/10 border border-white/20 rounded text-xs text-white focus:bg-white/15 focus:outline-none"
              />
              <button
                onClick={handleAddAction}
                className="px-3 py-2 bg-white/20 text-white text-xs rounded hover:bg-white/30 transition-colors"
              >
                Add
              </button>
            </div>
          </div>

          {/* Labels Section */}
          <div>
            <h3 className="text-sm text-white/90 mb-2">Add Label</h3>
            <div className="flex gap-2">
              <input
                type="text"
                value={newLabel}
                onChange={(e) => setNewLabel(e.target.value)}
                placeholder="e.g., Backend, ML, Frontend..."
                className="flex-1 px-3 py-2 bg-white/10 border border-white/20 rounded text-xs text-white placeholder-white/50 focus:bg-white/15 focus:outline-none"
                onKeyPress={(e) => e.key === 'Enter' && handleAddLabel()}
              />
              <button
                onClick={handleAddLabel}
                className="px-3 py-2 bg-white/20 text-white text-xs rounded hover:bg-white/30 transition-colors"
              >
                Add
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
