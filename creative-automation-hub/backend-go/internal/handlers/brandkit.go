package handlers

import (
	"database/sql"
	"net/http"

	"github.com/gin-gonic/gin"
)

// SaveBrandKit stores brand kit
func SaveBrandKit(db *sql.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req struct {
			ProjectID string   `json:"project_id" binding:"required"`
			Colors    []string `json:"colors"`
			Fonts     []string `json:"fonts"`
			LogoURL   string   `json:"logo_url"`
		}

		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		// TODO: Store in database

		c.JSON(http.StatusCreated, gin.H{
			"message": "Brand kit saved",
			"project_id": req.ProjectID,
		})
	}
}

// GetBrandKit retrieves brand kit
func GetBrandKit(db *sql.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		projectID := c.Param("projectId")

		// TODO: Query from database

		c.JSON(http.StatusOK, gin.H{
			"project_id": projectID,
			"colors":     []string{"#FF5733", "#3357FF"},
			"fonts":      []string{"Inter", "Roboto"},
		})
	}
}
