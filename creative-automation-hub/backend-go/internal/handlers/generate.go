package handlers

import (
	"net/http"

	"creative-automation-hub/internal/models"
	"creative-automation-hub/internal/services"

	"github.com/gin-gonic/gin"
)

// GenerateText handles text generation requests
func GenerateText(jobService *services.JobService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req models.TextGenerationRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		// Set defaults
		if req.Variants == 0 {
			req.Variants = 3
		}
		if req.MaxLength == 0 {
			req.MaxLength = 500
		}

		// Create job
		input := map[string]interface{}{
			"prompt":     req.Prompt,
			"type":       req.Type,
			"tone":       req.Tone,
			"variants":   req.Variants,
			"max_length": req.MaxLength,
		}

		job, err := jobService.CreateJob(c.Request.Context(), "text", input)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create job"})
			return
		}

		c.JSON(http.StatusAccepted, gin.H{
			"job_id": job.ID,
			"status": job.Status,
			"message": "Text generation started",
		})
	}
}

// GenerateImage handles image generation requests
func GenerateImage(jobService *services.JobService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req models.ImageGenerationRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		// Set defaults
		if req.Width == 0 {
			req.Width = 1024
		}
		if req.Height == 0 {
			req.Height = 1024
		}
		if req.Variants == 0 {
			req.Variants = 2
		}

		// Create job
		input := map[string]interface{}{
			"prompt":   req.Prompt,
			"width":    req.Width,
			"height":   req.Height,
			"variants": req.Variants,
			"style":    req.Style,
		}

		job, err := jobService.CreateJob(c.Request.Context(), "image", input)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create job"})
			return
		}

		c.JSON(http.StatusAccepted, gin.H{
			"job_id": job.ID,
			"status": job.Status,
			"message": "Image generation started",
		})
	}
}

// GetJobStatus retrieves job status
func GetJobStatus(jobService *services.JobService) gin.HandlerFunc {
	return func(c *gin.Context) {
		jobID := c.Param("id")

		job, err := jobService.GetJob(c.Request.Context(), jobID)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Job not found"})
			return
		}

		c.JSON(http.StatusOK, job)
	}
}
