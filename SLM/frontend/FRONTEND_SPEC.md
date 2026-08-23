# Frontend Specification

## Pages

1. **Dashboard** (`app/page.tsx`)
   - System health status
   - Real-time metrics (GPU, memory, disk)
   - Active training jobs
   - Recent activity
   - Quick actions

2. **Models** (`app/models/page.tsx`)
   - Model list with filters
   - Download from HuggingFace
   - Model details
   - Delete models
   - Storage usage

3. **Datasets** (`app/datasets/page.tsx`)
   - Dataset list
   - Upload new datasets
   - Dataset preview
   - Format validation
   - Delete datasets

4. **Training** (`app/training/page.tsx`)
   - Create new training job
   - Training jobs list
   - Real-time progress
   - Controls (pause/resume/cancel)
   - Training metrics charts
   - Job history

5. **Chat Playground** (`app/playground/page.tsx`)
   - Chat interface
   - Model selection
   - Parameter controls (temperature, max_tokens)
   - Conversation history
   - Export conversations
   - Groq integration fallback

6. **Analytics** (`app/analytics/page.tsx`)
   - Training history charts
   - Performance metrics
   - Cost savings calculator
   - GPU utilization trends
   - Model comparison

## Components

### Custom Components
- `SystemStatus` - Real-time system health
- `TrainingJobCard` - Training job with progress
- `ModelCard` - Model display card
- `DatasetCard` - Dataset display card
- `ChatInterface` - Chat UI
- `MetricsChart` - Recharts wrapper
- `ProgressBar` - Animated progress
- `StatusBadge` - Colored status indicator

### Layout
- `Sidebar` - Navigation sidebar
- `Header` - Top header with actions
- `MainLayout` - Wrapper with TooltipProvider

## Features

- ✅ Real-time updates (React Query with refetch)
- ✅ Responsive design (mobile-friendly)
- ✅ Dark mode support
- ✅ Loading states (skeletons)
- ✅ Error handling
- ✅ Optimistic updates
- ✅ Toast notifications
- ✅ Keyboard shortcuts
- ✅ Export data (CSV/JSON)

## Tech Stack

- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui
- React Query (data fetching)
- Zustand (state management)
- Recharts (charts)
- Lucide Icons
- Axios (HTTP client)
