package handlers

import (
	"net/http"

	"creative-automation-hub/internal/services"

	"github.com/gin-gonic/gin"
)

// ListAssets retrieves all assets
func ListAssets(assetService *services.AssetService) gin.HandlerFunc {
	return func(c *gin.Context) {
		projectID := c.Query("project_id")
		
		assets, err := assetService.ListAssets(projectID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch assets"})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"assets": assets,
			"count":  len(assets),
		})
	}
}

// GetAsset retrieves a single asset
func GetAsset(assetService *services.AssetService) gin.HandlerFunc {
	return func(c *gin.Context) {
		assetID := c.Param("id")

		asset, err := assetService.GetAsset(assetID)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Asset not found"})
			return
		}

		c.JSON(http.StatusOK, asset)
	}
}
