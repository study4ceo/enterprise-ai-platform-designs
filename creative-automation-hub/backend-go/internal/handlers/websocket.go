package handlers

import (
	"context"
	"encoding/json"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"github.com/redis/go-redis/v9"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // Allow all origins for MVP
	},
}

// WebSocketHandler handles WebSocket connections for real-time updates
func WebSocketHandler(rdb *redis.Client) gin.HandlerFunc {
	return func(c *gin.Context) {
		conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
		if err != nil {
			log.Println("WebSocket upgrade error:", err)
			return
		}
		defer conn.Close()

		ctx := context.Background()
		pubsub := rdb.Subscribe(ctx, "job_updates")
		defer pubsub.Close()

		ch := pubsub.Channel()

		log.Println("Client connected to WebSocket")

		for msg := range ch {
			var update map[string]interface{}
			if err := json.Unmarshal([]byte(msg.Payload), &update); err != nil {
				log.Println("Failed to parse update:", err)
				continue
			}

			if err := conn.WriteJSON(update); err != nil {
				log.Println("Failed to send update:", err)
				break
			}
		}

		log.Println("Client disconnected from WebSocket")
	}
}
