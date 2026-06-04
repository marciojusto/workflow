#!/bin/bash
# Script para executar análise SonarQube para o projeto deal-bs (Java/Spring Boot)
# Usage: ./scan-deal-bs.sh [options]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-/Users/marcio_oliveira/Development/teamwill/mobilize/deal-bs}"

# Load .env if exists
if [ -f "$SCRIPT_DIR/.env" ]; then
  source "$SCRIPT_DIR/.env"
fi

# Default values
SONAR_HOST="${SONAR_HOST:-http://localhost:9002}"
SONAR_TOKEN="${SONAR_TOKEN:-}"
SONAR_USER="${SONAR_USER:-admin}"
SONAR_PASSWORD="${SONAR_PASSWORD:-admin}"
SONAR_PROJECT_KEY="${SONAR_PROJECT_KEY:-deal-bs}"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --token)
      SONAR_TOKEN="$2"
      shift 2
      ;;
    --user)
      SONAR_USER="$2"
      shift 2
      ;;
    --password)
      SONAR_PASSWORD="$2"
      shift 2
      ;;
    --project-key|--project)
      SONAR_PROJECT_KEY="$2"
      shift 2
      ;;
    --host)
      SONAR_HOST="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  --token <token>          SonarQube token (recommended)"
      echo "  --user <username>        SonarQube username (default: admin)"
      echo "  --password <password>   SonarQube password (default: admin)"
      echo "  --project-key <key>       Project key (default: deal-bs)"
      echo "  --host <url>             SonarQube host (default: http://localhost:9002)"
      echo "  --help, -h               Show this help"
      echo ""
      echo "Examples:"
      echo "  $0 --token YOUR_TOKEN"
      echo "  $0 --user admin --password mypassword"
      echo "  $0 --token YOUR_TOKEN --project-key deal-bs-prod"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Check if SonarQube is running
if ! curl -sf -u "$SONAR_USER:$SONAR_PASSWORD" "$SONAR_HOST/api/system/health" > /dev/null 2>&1; then
  echo "Error: SonarQube is not running or not accessible at $SONAR_HOST"
  echo "Start it with: docker run -d --name sonarqube -p 9002:9000 sonarqube:community"
  exit 1
fi

echo "Running SonarQube analysis for deal-bs..."
echo "Project Key: $SONAR_PROJECT_KEY"
echo "Host: $SONAR_HOST"
echo "Project Dir: $PROJECT_DIR"

# Run Maven SonarQube analysis
cd "$PROJECT_DIR"

# Build authentication parameters
AUTH_ARGS=""
if [ -n "$SONAR_TOKEN" ]; then
  AUTH_ARGS="-Dsonar.login=$SONAR_TOKEN -Dsonar.token=$SONAR_TOKEN"
else
  AUTH_ARGS="-Dsonar.login=$SONAR_USER -Dsonar.password=$SONAR_PASSWORD"
fi

# Using Maven SonarQube Scanner
./mvnw sonar:sonar \
  -Dsonar.host.url="$SONAR_HOST" \
  -Dsonar.projectKey="$SONAR_PROJECT_KEY" \
  $AUTH_ARGS \
  -Dsonar.sourceEncoding=UTF-8 \
  -Dsonar.java.source=21 \
  -Dsonar.java.target=21

echo "SonarQube analysis completed!"
echo "View results at: $SONAR_HOST/dashboard?id=$SONAR_PROJECT_KEY"