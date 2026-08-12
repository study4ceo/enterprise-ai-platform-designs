package models

import "time"

// Job represents a generation job
type Job struct {
	ID         string                 `json:"id"`
	Type       string                 `json:"type"` // "text" or "image"
	Status     string                 `json:"status"` // "pending", "processing", "completed", "failed"
	Input      map[string]interface{} `json:"input"`
	Output     interface{}            `json:"output,omitempty"`
	Error      string                 `json:"error,omitempty"`
	CreatedAt  time.Time              `json:"created_at"`
	CompletedAt *time.Time            `json:"completed_at,omitempty"`
}

// Asset represents generated content
type Asset struct {
	ID        string                 `json:"id"`
	ProjectID string                 `json:"project_id"`
	Type      string                 `json:"type"` // "text", "image", "video"
	Content   string                 `json:"content,omitempty"`
	URL       string                 `json:"url,omitempty"`
	Metadata  map[string]interface{} `json:"metadata"`
	CreatedAt time.Time              `json:"created_at"`
}

// BrandKit represents brand styling
type BrandKit struct {
	ID        string   `json:"id"`
	ProjectID string   `json:"project_id"`
	Colors    []string `json:"colors"`
	Fonts     []string `json:"fonts"`
	LogoURL   string   `json:"logo_url,omitempty"`
	CreatedAt time.Time `json:"created_at"`
}

// TextGenerationRequest for text content
type TextGenerationRequest struct {
	Prompt     string   `json:"prompt" binding:"required"`
	Type       string   `json:"type"` // "blog", "social", "ad"
	Tone       string   `json:"tone"` // "professional", "casual", "friendly"
	Variants   int      `json:"variants"` // Number of variants to generate
	MaxLength  int      `json:"max_length,omitempty"`
}

// ImageGenerationRequest for image content
type ImageGenerationRequest struct {
	Prompt     string `json:"prompt" binding:"required"`
	Width      int    `json:"width"`
	Height     int    `json:"height"`
	Variants   int    `json:"variants"`
	Style      string `json:"style,omitempty"`
}
