package services

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"time"

	"creative-automation-hub/internal/models"

	"github.com/google/uuid"
	"github.com/redis/go-redis/v9"
)

type JobService struct {
	redis *redis.Client
	db    *sql.DB
}

func NewJobService(rdb *redis.Client, db *sql.DB) *JobService {
	return &JobService{redis: rdb, db: db}
}

// CreateJob creates a new job and adds to Redis queue
func (s *JobService) CreateJob(ctx context.Context, jobType string, input map[string]interface{}) (*models.Job, error) {
	job := &models.Job{
		ID:        uuid.New().String(),
		Type:      jobType,
		Status:    "pending",
		Input:     input,
		CreatedAt: time.Now(),
	}

	// Serialize job
	jobData, err := json.Marshal(job)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal job: %w", err)
	}

	// Add to Redis queue
	queueName := fmt.Sprintf("queue:%s", jobType)
	if err := s.redis.LPush(ctx, queueName, jobData).Err(); err != nil {
		return nil, fmt.Errorf("failed to queue job: %w", err)
	}

	// Store job metadata
	if err := s.redis.Set(ctx, fmt.Sprintf("job:%s", job.ID), jobData, 24*time.Hour).Err(); err != nil {
		return nil, fmt.Errorf("failed to store job: %w", err)
	}

	return job, nil
}

// GetJob retrieves job status
func (s *JobService) GetJob(ctx context.Context, jobID string) (*models.Job, error) {
	data, err := s.redis.Get(ctx, fmt.Sprintf("job:%s", jobID)).Result()
	if err != nil {
		return nil, fmt.Errorf("job not found: %w", err)
	}

	var job models.Job
	if err := json.Unmarshal([]byte(data), &job); err != nil {
		return nil, fmt.Errorf("failed to unmarshal job: %w", err)
	}

	return &job, nil
}

// UpdateJobStatus updates job status and notifies via WebSocket
func (s *JobService) UpdateJobStatus(ctx context.Context, jobID string, status string, output interface{}, errorMsg string) error {
	job, err := s.GetJob(ctx, jobID)
	if err != nil {
		return err
	}

	job.Status = status
	job.Output = output
	job.Error = errorMsg
	now := time.Now()
	job.CompletedAt = &now

	// Update in Redis
	jobData, err := json.Marshal(job)
	if err != nil {
		return err
	}

	if err := s.redis.Set(ctx, fmt.Sprintf("job:%s", jobID), jobData, 24*time.Hour).Err(); err != nil {
		return err
	}

	// Publish update for WebSocket
	update := map[string]interface{}{
		"job_id": jobID,
		"status": status,
		"output": output,
		"error":  errorMsg,
	}
	updateData, _ := json.Marshal(update)
	s.redis.Publish(ctx, "job_updates", updateData)

	return nil
}
