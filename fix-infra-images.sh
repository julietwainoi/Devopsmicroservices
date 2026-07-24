#!/bin/bash
# save as: fix-infra-images.sh

CLUSTER_NAME="kind-test"

echo "🔧 Pulling infrastructure images and loading into kind..."

INFRA_IMAGES=(
  "nginx:latest"
  "postgres:16"
  "grafana/grafana:latest"
  "prom/prometheus:latest"
  "prom/node-exporter:latest"
  "nginx/nginx-prometheus-exporter:latest"
  "grafana/loki:2.9.0"
  "grafana/promtail:2.9.0"
)

for IMAGE in "${INFRA_IMAGES[@]}"; do
  echo ""
  echo "  ⏳ Pulling $IMAGE..."
  
  # Remove old image
  docker rmi "$IMAGE" 2>/dev/null || true

  # Pull for current platform
  docker pull "$IMAGE"

  echo "  📦 Loading $IMAGE into kind-test..."
  if docker save "$IMAGE" | docker exec -i kind-test-control-plane ctr --namespace=k8s.io images import - && \
     docker save "$IMAGE" | docker exec -i kind-test-worker ctr --namespace=k8s.io images import -; then
    echo "  ✅ $IMAGE loaded successfully"
  else
    echo "  ❌ Still failed: $IMAGE"
  fi
done

echo ""
echo "🎉 Done! Verify with:"
echo "  docker exec -it kind-test-control-plane crictl images"
