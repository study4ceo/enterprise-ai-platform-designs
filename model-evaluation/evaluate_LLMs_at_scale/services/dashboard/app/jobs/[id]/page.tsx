'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, Download, Trash2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { TasksTable } from '@/components/TasksTable'
import { MetricsDisplay } from '@/components/MetricsDisplay'
import { api } from '@/lib/api'

interface JobDetails {
  id: string
  name: string
  status: string
  total_tasks: number
  completed_tasks: number
  failed_tasks: number
  total_cost_usd: number
  created_at: string
  started_at?: string
  completed_at?: string
  metadata: any
}

export default function JobDetailPage() {
  const params = useParams()
  const router = useRouter()
  const jobId = params.id as string
  
  const [job, setJob] = useState<JobDetails | null>(null)
  const [tasks, setTasks] = useState([])
  const [results, setResults] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (jobId) {
      fetchJobDetails()
      // Refresh every 3 seconds while job is running
      const interval = setInterval(() => {
        if (job?.status === 'running' || job?.status === 'queued') {
          fetchJobDetails()
        }
      }, 3000)
      return () => clearInterval(interval)
    }
  }, [jobId, job?.status])

  const fetchJobDetails = async () => {
    try {
      const [jobData, tasksData, resultsData] = await Promise.all([
        api.getJob(jobId),
        api.getJobTasks(jobId),
        api.getJobResults(jobId)
      ])
      setJob(jobData)
      setTasks(tasksData)
      setResults(resultsData)
    } catch (error) {
      console.error('Failed to fetch job details:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to cancel this job?')) return
    
    try {
      await api.deleteJob(jobId)
      router.push('/jobs')
    } catch (error) {
      console.error('Failed to delete job:', error)
      alert('Failed to delete job')
    }
  }

  const handleExport = async () => {
    try {
      const data = await api.exportJob(jobId, 'json')
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `job-${jobId}-results.json`
      a.click()
    } catch (error) {
      console.error('Failed to export job:', error)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-96">Loading...</div>
  }

  if (!job) {
    return <div className="text-center py-12">Job not found</div>
  }

  const progress = job.total_tasks > 0 
    ? ((job.completed_tasks / job.total_tasks) * 100).toFixed(1)
    : 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => router.push('/jobs')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{job.name}</h1>
            <p className="text-gray-600 mt-1">Job ID: {job.id}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button variant="destructive" onClick={handleDelete}>
            <Trash2 className="h-4 w-4 mr-2" />
            Cancel
          </Button>
        </div>
      </div>

      {/* Status Overview */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-600">Status</div>
            <Badge status={job.status} className="mt-2">
              {job.status.toUpperCase()}
            </Badge>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-600">Progress</div>
            <div className="text-2xl font-bold mt-2">{progress}%</div>
            <div className="text-xs text-gray-500 mt-1">
              {job.completed_tasks} / {job.total_tasks} tasks
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-600">Total Cost</div>
            <div className="text-2xl font-bold mt-2">
              ${job.total_cost_usd.toFixed(4)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-600">Failed Tasks</div>
            <div className="text-2xl font-bold mt-2 text-red-600">
              {job.failed_tasks}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Progress Bar */}
      <Card>
        <CardContent className="pt-6">
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </CardContent>
      </Card>

      {/* Metrics Summary */}
      {results && (
        <Card>
          <CardHeader>
            <CardTitle>Evaluation Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <MetricsDisplay results={results} />
          </CardContent>
        </Card>
      )}

      {/* Tasks Table */}
      <Card>
        <CardHeader>
          <CardTitle>Tasks ({tasks.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <TasksTable tasks={tasks} />
        </CardContent>
      </Card>
    </div>
  )
}
