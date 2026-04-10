#!/bin/bash
# save as: fix-infra-images.sh

CLUSTER_NAME="kind-test"

echo "🔧 Re-pulling infrastructure images for linux/amd64..."

INFRA_IMAGES=(
  "nginx:latest"
  "postgres:16"
  "grafana/grafana:latest"
  "prom/prometheus:latest"
  "prom/node-exporter:latest"
  "nginx/nginx-prometheus-exporter:latest"
)

for IMAGE in "${INFRA_IMAGES[@]}"; do
  echo ""
  echo "  ⏳ Re-pulling $IMAGE for linux/amd64..."
  
  # Remove old image
  docker rmi "$IMAGE" 2>/dev/null || true

  # Pull fresh for correct platform
  docker pull --platform linux/amd64 "$IMAGE"

  echo "  📦 Loading $IMAGE into kind-test..."
  if kind load docker-image "$IMAGE" --name "$CLUSTER_NAME"; then
    echo "  ✅ $IMAGE loaded successfully"
  else
    echo "  ❌ Still failed: $IMAGE"
  fi
done

echo ""
echo "🎉 Done! Verify with:"
echo "  docker exec -it kind-test-control-plane crictl images"
