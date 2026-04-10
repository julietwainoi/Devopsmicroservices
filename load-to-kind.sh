#!/bin/bash
# save as: load-to-kind.sh

CLUSTER_NAME="kind-test"

echo "🚀 Loading ONLY custom microservice images into Kind..."
echo "ℹ️  Infrastructure images will be pulled automatically by Kind"

# Only your custom built microservices
CUSTOM_IMAGES=(
  "devopsmicroservices-auth-service:latest"
  "devopsmicroservices-user-service:latest"
  "devopsmicroservices-order-service:latest"
  "devopsmicroservices-payment-service:latest"
  "devopsmicroservices-product-service:latest"
)

for IMAGE in "${CUSTOM_IMAGES[@]}"; do
  echo "  ⏳ Loading $IMAGE..."
  if kind load docker-image "$IMAGE" --name "$CLUSTER_NAME"; then
    echo "  ✅ $IMAGE loaded"
  else
    echo "  ❌ Failed to load $IMAGE"
  fi
done

echo ""
echo "🎉 Custom images loaded!"
echo "👉 Now run: kubectl apply -f k8s/"
echo "👉 Kind will auto-pull nginx, postgres, grafana etc from Docker Hub"
