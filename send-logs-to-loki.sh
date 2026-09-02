#!/bin/bash

# Send recent logs from each microservice to Loki
echo "Forwarding logs to Loki..."

for app in auth user product payment order; do
  echo "Processing $app logs..."
  
  # Get recent logs
  logs=$(kubectl logs -l app=$app --tail=20 2>/dev/null | jq -Rs .)
  
  if [ ! -z "$logs" ] && [ "$logs" != "null" ]; then
    # Send to Loki
    kubectl run curl-$app --image=curlimages/curl:latest --rm -i --restart=Never -- \
      curl -X POST -H "Content-Type: application/json" \
      -d "{\"streams\": [{\"stream\": {\"namespace\": \"default\", \"app\": \"$app\"}, \"values\": [[\"$(date +%s)000000000\", $logs]]}]}" \
      http://loki.monitoring.svc.cluster.local:3100/loki/api/v1/push
    
    echo "✓ Sent $app logs to Loki"
  fi
done

echo "Done! Now query in Grafana with: {namespace=\"default\"}"
