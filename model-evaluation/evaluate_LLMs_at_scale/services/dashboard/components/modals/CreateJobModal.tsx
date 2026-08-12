'use client'

import { useState } from 'react'
import { X } from 'lucide-react'
import { Button } from '../ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card'

interface CreateJobModalProps {
  onClose: () => void
  onSubmit: (data: any) => void
}

export const CreateJobModal = ({ onClose, onSubmit }: CreateJobModalProps) => {
  const [formData, setFormData] = useState({
    name: '',
    models: ['gemini-pro'],
    prompts: [''],
    metrics: ['bleu', 'rouge', 'bertscore'],
    priority: 1
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      ...formData,
      prompts: formData.prompts.filter(p => p.trim())
    })
  }

  const addPrompt = () => {
    setFormData({ ...formData, prompts: [...formData.prompts, ''] })
  }

  const updatePrompt = (index: number, value: string) => {
    const newPrompts = [...formData.prompts]
    newPrompts[index] = value
    setFormData({ ...formData, prompts: newPrompts })
  }

  const toggleModel = (model: string) => {
    const newModels = formData.models.includes(model)
      ? formData.models.filter(m => m !== model)
      : [...formData.models, model]
    setFormData({ ...formData, models: newModels })
  }

  const availableModels = [
    // Groq (⚡ Fast & Cheap) - Recommended!
    { id: 'llama-3.1-70b-versatile', name: 'Llama 3.1 70B (Groq)', provider: 'Groq', speed: '⚡⚡⚡', cost: '$' },
    { id: 'llama-3.1-8b-instant', name: 'Llama 3.1 8B (Groq)', provider: 'Groq', speed: '⚡⚡⚡', cost: '$' },
    { id: 'llama-3.1-405b-reasoning', name: 'Llama 3.1 405B (Groq)', provider: 'Groq', speed: '⚡⚡', cost: 'FREE' },
    { id: 'mixtral-8x7b-32768', name: 'Mixtral 8x7B (Groq)', provider: 'Groq', speed: '⚡⚡⚡', cost: '$' },
    { id: 'gemma2-9b-it', name: 'Gemma 2 9B (Groq)', provider: 'Groq', speed: '⚡⚡⚡', cost: '$' },
    
    // Premium APIs (Slower & Expensive)
    { id: 'gemini-pro', name: 'Gemini Pro', provider: 'Google', speed: '⚡', cost: '$$' },
    { id: 'gpt-4', name: 'GPT-4', provider: 'OpenAI', speed: '⚡', cost: '$$$$$' },
    { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'OpenAI', speed: '⚡⚡', cost: '$$' },
    { id: 'claude-sonnet', name: 'Claude Sonnet', provider: 'Anthropic', speed: '⚡', cost: '$$$' },
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Create Evaluation Job</CardTitle>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X className="h-5 w-5" />
          </button>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Job Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Name
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Q&A Model Comparison"
              />
            </div>

            {/* Models */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Models to Evaluate
              </label>
              <div className="space-y-2">
                {availableModels.map((model) => (
                  <label
                    key={model.id}
                    className="flex items-center justify-between gap-2 p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
                  >
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={formData.models.includes(model.id)}
                        onChange={() => toggleModel(model.id)}
                        className="rounded"
                      />
                      <div>
                        <span className="text-sm font-medium">{model.name}</span>
                        <div className="text-xs text-gray-500">{model.provider}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <span title="Speed">{model.speed}</span>
                      <span title="Cost" className="font-medium">{model.cost}</span>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Prompts */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Prompts
              </label>
              <div className="space-y-2">
                {formData.prompts.map((prompt, index) => (
                  <textarea
                    key={index}
                    value={prompt}
                    onChange={(e) => updatePrompt(index, e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter your prompt..."
                    rows={2}
                  />
                ))}
                <Button type="button" variant="outline" onClick={addPrompt}>
                  + Add Prompt
                </Button>
              </div>
            </div>

            {/* Priority */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Priority
              </label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value={1}>Low (1)</option>
                <option value={2}>Medium (2)</option>
                <option value={3}>High (3)</option>
              </select>
            </div>

            {/* Buttons */}
            <div className="flex gap-2 justify-end">
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit">
                Create Job
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
