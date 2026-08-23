'use client';

import { useQuery } from '@tanstack/react-query';
import { getDatasets } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Database, Upload, Trash2, FileText } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function DatasetsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['datasets'],
    queryFn: () => getDatasets().then(res => res.data),
    refetchInterval: 10000,
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Datasets</h1>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      </div>
    );
  }

  const getFormatColor = (format: string) => {
    switch (format.toLowerCase()) {
      case 'json':
      case 'jsonl':
        return 'default';
      case 'csv':
        return 'secondary';
      case 'parquet':
        return 'outline';
      default:
        return 'outline';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Datasets</h1>
        <Button>
          <Upload className="mr-2 h-4 w-4" />
          Upload Dataset
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {data?.datasets.map((dataset) => (
          <Card key={dataset.dataset_id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <Database className="h-5 w-5 text-primary" />
                  <CardTitle className="text-lg">{dataset.name}</CardTitle>
                </div>
                <Badge variant={getFormatColor(dataset.format)}>
                  {dataset.format.toUpperCase()}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Dataset ID</span>
                  <span className="font-mono text-xs">{dataset.dataset_id}</span>
                </div>
                
                {dataset.num_samples && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Samples</span>
                    <span>{dataset.num_samples.toLocaleString()}</span>
                  </div>
                )}

                {dataset.size_mb && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Size</span>
                    <span>{dataset.size_mb.toFixed(2)} MB</span>
                  </div>
                )}

                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Uploaded</span>
                  <span>{formatDistanceToNow(new Date(dataset.created_at), { addSuffix: true })}</span>
                </div>
              </div>

              <div className="flex gap-2 pt-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="flex-1"
                >
                  <FileText className="mr-2 h-3 w-3" />
                  Preview
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {data?.datasets.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <Database className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-lg font-medium">No datasets found</p>
            <p className="text-sm text-muted-foreground mt-1">
              Upload a dataset to start training
            </p>
            <Button className="mt-4">
              <Upload className="mr-2 h-4 w-4" />
              Upload Your First Dataset
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
