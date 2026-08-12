'use client'

import { useEffect, useState } from 'react'
import { CheckCircle2, XCircle, AlertTriangle, Info } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { DeploymentChecklist } from '@/components/DeploymentChecklist'
import { DeploymentScoreCard } from '@/components/DeploymentScoreCard'
import { api } from '@/lib/api'

interface DeploymentReadiness {
  model_name: string
  overall_score: number
  performance_score: number
  business_score: number
  safety_score: number
  operational_score: number
  deployment_ready: boolean
  status: 'APPROVED' | 'CONDITIONAL' | 'REJECTED'
  critical_issues: string[]
  warnings: string[]
  recommendations: string[]
  performance: any
  business: any
  safety: any
  operational: any
  evaluated_at: string
}

export default function DeploymentPage() {
  const [models, setModels] = useState<DeploymentReadiness[]>([])
  const [selectedModel, setSelectedModel] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDeploymentReadiness()
  }, [])

  const fetchDeploymentReadiness = async () => {
    try {
      const data = await api.getDeploymentReadiness()
      setModels(data)
      if (data.length > 0) {
        setSelectedModel(data[0].model_name)
      }
    } catch (error) {
      console.error('Failed to fetch deployment readiness:', error)
    } finally {
      setLoading(false)
    }
  }

  const selectedModelData = models.find(m => m.model_name === selectedModel)

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return <CheckCircle2 className="h-6 w-6 text-green-600" />
      case 'CONDITIONAL':
        return <AlertTriangle className="h-6 w-6 text-yellow-600" />
      case 'REJECTED':
        return <XCircle className="h-6 w-6 text-red-600" />
      default:
        return <Info className="h-6 w-6 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return 'bg-green-100 text-green-800'
      case 'CONDITIONAL':
        return 'bg-yellow-100 text-yellow-800'
      case 'REJECTED':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-96">Loading...</div>
  }

  if (models.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">No deployment readiness data available.</p>
        <p className="text-sm text-gray-500 mt-2">
          Run evaluations to generate deployment readiness reports.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Deployment Readiness</h1>
        <p className="text-gray-600 mt-2">
          Production readiness assessment based on 4 pillars
        </p>
      </div>

      {/* Model Selector */}
      <div className="flex gap-2 flex-wrap">
        {models.map((model) => (
          <Button
            key={model.model_name}
            variant={selectedModel === model.model_name ? 'default' : 'outline'}
            onClick={() => setSelectedModel(model.model_name)}
          >
            {model.model_name}
            <Badge
              className={`ml-2 ${getStatusColor(model.status)}`}
              variant="secondary"
            >
              {model.overall_score.toFixed(0)}%
            </Badge>
          </Button>
        ))}
      </div>

      {selectedModelData && (
        <>
          {/* Overall Status */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {getStatusIcon(selectedModelData.status)}
                  <div>
                    <h2 className="text-2xl font-bold">
                      {selectedModelData.model_name}
                    </h2>
                    <p className="text-gray-600 mt-1">
                      Overall Score: {selectedModelData.overall_score.toFixed(1)}%
                    </p>
                  </div>
                </div>
                <Badge className={`text-lg px-4 py-2 ${getStatusColor(selectedModelData.status)}`}>
                  {selectedModelData.status}
                </Badge>
              </div>

              <div className="mt-6 grid gap-4 md:grid-cols-4">
                <DeploymentScoreCard
                  title="Performance"
                  score={selectedModelData.performance_score}
                  weight={25}
                  color="blue"
                />
                <DeploymentScoreCard
                  title="Business"
                  score={selectedModelData.business_score}
                  weight={25}
                  color="green"
                />
                <DeploymentScoreCard
                  title="Safety"
                  score={selectedModelData.safety_score}
                  weight={35}
                  color="red"
                />
                <DeploymentScoreCard
                  title="Operational"
                  score={selectedModelData.operational_score}
                  weight={15}
                  color="purple"
                />
              </div>
            </CardContent>
          </Card>

          {/* Critical Issues */}
          {selectedModelData.critical_issues.length > 0 && (
            <Card className="border-red-300 bg-red-50">
              <CardHeader>
                <CardTitle className="text-red-900 flex items-center gap-2">
                  <XCircle className="h-5 w-5" />
                  Critical Issues ({selectedModelData.critical_issues.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {selectedModelData.critical_issues.map((issue, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-red-800">
                      <span className="text-red-600 mt-1">•</span>
                      <span>{issue}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Warnings */}
          {selectedModelData.warnings.length > 0 && (
            <Card className="border-yellow-300 bg-yellow-50">
              <CardHeader>
                <CardTitle className="text-yellow-900 flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  Warnings ({selectedModelData.warnings.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {selectedModelData.warnings.map((warning, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-yellow-800">
                      <span className="text-yellow-600 mt-1">•</span>
                      <span>{warning}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Deployment Checklist */}
          <Card>
            <CardHeader>
              <CardTitle>Deployment Checklist</CardTitle>
            </CardHeader>
            <CardContent>
              <DeploymentChecklist data={selectedModelData} />
            </CardContent>
          </Card>

          {/* Recommendations */}
          {selectedModelData.recommendations.length > 0 && (
            <Card className="border-blue-300 bg-blue-50">
              <CardHeader>
                <CardTitle className="text-blue-900 flex items-center gap-2">
                  <Info className="h-5 w-5" />
                  Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {selectedModelData.recommendations.map((rec, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-blue-800">
                      <span className="text-blue-600 mt-1">•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
