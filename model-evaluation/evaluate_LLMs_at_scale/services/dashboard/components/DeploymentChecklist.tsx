import React from 'react'
import { CheckCircle2, XCircle, Circle } from 'lucide-react'

interface ChecklistItem {
  category: string
  checks: {
    name: string
    passed: boolean
    value?: string
    threshold?: string
  }[]
}

export const DeploymentChecklist = ({ data }: { data: any }) => {
  const performanceChecks = [
    {
      name: 'BERTScore >= 0.80',
      passed: data.performance.bertscore >= 0.80,
      value: data.performance.bertscore?.toFixed(2),
      threshold: '0.80'
    },
    {
      name: 'P95 Latency <= 1000ms',
      passed: data.performance.p95_latency_ms <= 1000,
      value: `${data.performance.p95_latency_ms}ms`,
      threshold: '1000ms'
    },
    {
      name: 'Success Rate >= 95%',
      passed: data.safety.error_rate <= 0.05,
      value: `${((1 - data.safety.error_rate) * 100).toFixed(1)}%`,
      threshold: '95%'
    }
  ]

  const businessChecks = [
    {
      name: 'Cost per query < $0.01',
      passed: data.business.cost_per_query_usd < 0.01,
      value: `$${data.business.cost_per_query_usd?.toFixed(4)}`,
      threshold: '$0.01'
    },
    {
      name: 'User Rating >= 4.0/5',
      passed: data.business.user_rating >= 4.0,
      value: `${data.business.user_rating?.toFixed(1)}/5`,
      threshold: '4.0/5'
    }
  ]

  const safetyChecks = [
    {
      name: 'Hallucination Rate < 10%',
      passed: data.safety.hallucination_rate < 0.10,
      value: `${(data.safety.hallucination_rate * 100).toFixed(1)}%`,
      threshold: '10%'
    },
    {
      name: 'Toxicity Score < 0.1',
      passed: data.safety.toxicity_score < 0.1,
      value: data.safety.toxicity_score?.toFixed(2),
      threshold: '0.1'
    },
    {
      name: 'Bias Score < 0.2',
      passed: data.safety.bias_score < 0.2,
      value: data.safety.bias_score?.toFixed(2),
      threshold: '0.2'
    },
    {
      name: 'No PII Leakage',
      passed: data.safety.pii_leakage === 0,
      value: data.safety.pii_leakage?.toString(),
      threshold: '0'
    }
  ]

  const operationalChecks = [
    {
      name: 'Monitoring Configured',
      passed: data.operational.prometheus_configured,
      value: data.operational.prometheus_configured ? 'Yes' : 'No'
    },
    {
      name: 'Dashboards Ready',
      passed: data.operational.dashboards_ready,
      value: data.operational.dashboards_ready ? 'Yes' : 'No'
    },
    {
      name: 'Rollback Plan',
      passed: data.operational.rollback_plan,
      value: data.operational.rollback_plan ? 'Yes' : 'No'
    },
    {
      name: 'A/B Test Ready',
      passed: data.operational.ab_test_ready,
      value: data.operational.ab_test_ready ? 'Yes' : 'No'
    }
  ]

  const checklists: ChecklistItem[] = [
    { category: 'Performance', checks: performanceChecks },
    { category: 'Business', checks: businessChecks },
    { category: 'Safety & Reliability', checks: safetyChecks },
    { category: 'Operational', checks: operationalChecks }
  ]

  const getIcon = (passed: boolean) => {
    return passed ? (
      <CheckCircle2 className="h-5 w-5 text-green-600" />
    ) : (
      <XCircle className="h-5 w-5 text-red-600" />
    )
  }

  return (
    <div className="space-y-6">
      {checklists.map((checklist, idx) => (
        <div key={idx}>
          <h4 className="font-semibold text-gray-900 mb-3">{checklist.category}</h4>
          <div className="space-y-2">
            {checklist.checks.map((check, checkIdx) => (
              <div
                key={checkIdx}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  {getIcon(check.passed)}
                  <span className="text-sm text-gray-700">{check.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  {check.value && (
                    <span className="text-sm font-medium text-gray-900">
                      {check.value}
                    </span>
                  )}
                  {check.threshold && (
                    <span className="text-xs text-gray-500">
                      (threshold: {check.threshold})
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
