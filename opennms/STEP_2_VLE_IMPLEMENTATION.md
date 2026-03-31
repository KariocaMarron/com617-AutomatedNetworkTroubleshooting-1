# Step 2: VLE (Virtual Learning Environment) Implementation

**Priority:** HIGHEST (Primary student service per case study)  
**Location:** Pyongyang (Central Campus)  
**Integration:** Must be monitored by OpenNMS Horizon

---

## Decision Point: VLE Platform Selection

### Option A: Lightweight Moodle (Recommended)
**Pros:**
- Real VLE platform (academically authentic)
- Generates real traffic for monitoring
- Supports LDAP integration (future)
- Can demonstrate service availability monitoring
- Lightweight Docker images available

**Cons:**
- Requires additional database (or shares PostgreSQL)
- More complex configuration
- Resource usage ~500MB RAM

**Academic Value:** HIGH ✓

---

### Option B: Simulated VLE (Simple NGINX)
**Pros:**
- Minimal resources (~20MB RAM)
- Simple SNMP/HTTP monitoring
- Quick deployment
- You already have pyu-py-server (NGINX)

**Cons:**
- Not a real VLE
- Limited monitoring scenarios
- Lower academic authenticity

**Academic Value:** MEDIUM

---

## RECOMMENDATION: Option A (Lightweight Moodle)

**Rationale:**
1. Case study explicitly mentions VLE as primary service
2. Demonstrates realistic service monitoring
3. Shows understanding of educational infrastructure
4. Supports future LDAP/authentication integration
5. Still lightweight enough for lab environment

---

## Implementation Plan - Lightweight Moodle

### Architecture Addition

```
Pyongyang (Central Campus)
├── pyu-horizon (OpenNMS) ✓ existing
├── pyu-postgres (shared DB) ✓ existing
├── pyu-activemq ✓ existing
├── pyu-zookeeper ✓ existing
└── pyu-vle (NEW - Moodle)
    ├── HTTP: Port 8081
    ├── Database: Shared pyu-postgres
    └── Monitoring: ICMP, HTTP, PostgreSQL
```

### Required Changes

1. **Modify horizon/docker-compose.yml**
   - Add Moodle service
   - Share PostgreSQL database
   - Expose port 8081

2. **Create VLE database in PostgreSQL**
   - Database: `moodle`
   - User: `moodle` / Password: `moodle`

3. **Configure OpenNMS Monitoring**
   - Add VLE node to requisitions
   - Configure HTTP service monitor
   - Configure PostgreSQL connection monitor
   - Set up alerts for downtime

---

## Docker Compose Configuration

### Modified horizon/docker-compose.yml

```yaml
services:
  database:
    image: postgres:14
    container_name: pyu-postgres
    environment:
      POSTGRES_HOST: database
      POSTGRES_PORT: 5432
      POSTGRES_USER: opennms
      POSTGRES_PASSWORD: opennms
      POSTGRES_DB: opennms
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d  # NEW - for moodle DB
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U opennms"]
      interval: 10s
      timeout: 3s
      retries: 3
    networks:
      - kafka_pyu-main

  activemq:
    image: apache/activemq-classic:5.18.3
    container_name: pyu-activemq
    environment:
      ACTIVEMQ_ADMIN_LOGIN: admin
      ACTIVEMQ_ADMIN_PASSWORD: admin
    ports:
      - "61616:61616/tcp"
      - "8161:8161/tcp"
    networks:
      - kafka_pyu-main

  horizon:
    image: opennms/horizon:33.0.2
    container_name: pyu-horizon
    environment:
      POSTGRES_HOST: database
      POSTGRES_PORT: 5432
      POSTGRES_USER: opennms
      POSTGRES_PASSWORD: opennms
    volumes:
      - horizon-data:/opennms-data
      - ./overlay:/opt/opennms-overlay
    command: ["-s"]
    ports:
      - "8980:8980/tcp"
      - "8101:8101/tcp"
    depends_on:
      database:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "-I", "http://localhost:8980/opennms/login.jsp"]
      interval: 30s
      timeout: 5s
      retries: 3
    networks:
      - kafka_pyu-main

  # NEW - VLE Service (Moodle)
  vle:
    image: bitnami/moodle:4.3
    container_name: pyu-vle
    hostname: pyu-vle
    environment:
      # Database configuration (shared PostgreSQL)
      MOODLE_DATABASE_TYPE: pgsql
      MOODLE_DATABASE_HOST: database
      MOODLE_DATABASE_PORT_NUMBER: 5432
      MOODLE_DATABASE_NAME: moodle
      MOODLE_DATABASE_USER: moodle
      MOODLE_DATABASE_PASSWORD: moodle
      
      # Moodle admin credentials
      MOODLE_USERNAME: admin
      MOODLE_PASSWORD: Admin123!
      MOODLE_EMAIL: admin@pyu.edu.kp
      MOODLE_SITE_NAME: "Pyongyang University VLE"
      
      # Skip initial configuration
      MOODLE_SKIP_BOOTSTRAP: "no"
      
      # PHP settings (lightweight)
      PHP_MEMORY_LIMIT: 256M
      PHP_MAX_EXECUTION_TIME: 300
    volumes:
      - vle-data:/bitnami/moodle
      - vle-moodledata:/bitnami/moodledata
    ports:
      - "8081:8080/tcp"  # HTTP access
    depends_on:
      database:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    networks:
      - kafka_pyu-main

volumes:
  postgres-data:
  horizon-data:
  vle-data:          # NEW
  vle-moodledata:    # NEW

networks:
  kafka_pyu-main:
    external: true

#Jose Vasconcelos - Dec 2025
#GitHub - KariocaMarron
#acme5bataj10@outlook.com
```

---

## Database Initialisation Script

### Create: `horizon/init-scripts/01-init-moodle-db.sql`

```sql
-- Create Moodle database and user
-- This runs automatically when postgres container starts for the first time

-- Check if database exists, if not create it
SELECT 'CREATE DATABASE moodle'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'moodle')\gexec

-- Create moodle user if not exists
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'moodle') THEN
      CREATE USER moodle WITH PASSWORD 'moodle';
   END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE moodle TO moodle;

-- Connect to moodle database and set permissions
\c moodle
GRANT ALL ON SCHEMA public TO moodle;
```

---

## Deployment Steps

### 1. Prepare Database Init Script

```bash
# Navigate to horizon directory
cd ~/opennms-pyu-lab/opennms-pyu-ver2/horizon

# Create init-scripts directory
mkdir -p init-scripts

# Create the SQL init script
cat > init-scripts/01-init-moodle-db.sql << 'EOF'
-- Create Moodle database and user
SELECT 'CREATE DATABASE moodle'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'moodle')\gexec

DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'moodle') THEN
      CREATE USER moodle WITH PASSWORD 'moodle';
   END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE moodle TO moodle;
\c moodle
GRANT ALL ON SCHEMA public TO moodle;
EOF
```

### 2. Backup Current Configuration

```bash
# Backup existing docker-compose.yml
cp docker-compose.yml docker-compose.yml.backup-$(date +%Y%m%d)
```

### 3. Update docker-compose.yml

```bash
# Replace with new configuration (provided above)
# Or manually edit to add VLE service
```

### 4. Deploy VLE

```bash
# Stop current stack (if running)
docker-compose down

# Start with new configuration
docker-compose up -d

# Watch logs
docker-compose logs -f vle
```

### 5. Verify Deployment

```bash
# Check all containers running
docker ps

# Test VLE access
curl -I http://localhost:8081

# Check VLE is healthy
docker inspect pyu-vle | grep -A 5 Health
```

### 6. Access VLE

**URL:** http://localhost:8081  
**Username:** admin  
**Password:** Admin123!

---

## OpenNMS Integration

### Add VLE to Requisitions

Create: `requisitions/vle-services.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<model-import xmlns="http://xmlns.opennms.org/xsd/config/model-import"
              date-stamp="2025-12-28T00:00:00.000Z"
              foreign-source="pyu-services">
    
    <!-- VLE Server -->
    <node foreign-id="pyu-vle" node-label="Pyongyang VLE Server">
        <interface ip-addr="172.18.0.9" status="1" snmp-primary="N">
            <monitored-service service-name="ICMP"/>
            <monitored-service service-name="HTTP-8080"/>
        </interface>
        
        <category name="Production"/>
        <category name="VLE"/>
        <category name="Pyongyang"/>
    </node>
    
</model-import>
```

### Import into OpenNMS

```bash
# Copy requisition to OpenNMS
# Option 1: Via UI (Provisions → Requisitions → Import)
# Option 2: Via REST API

curl -X POST -H "Content-Type: application/xml" \
  -u admin:admin \
  --data @requisitions/vle-services.xml \
  http://localhost:8980/opennms/rest/requisitions
```

### Configure HTTP Service Monitor

```bash
# Access OpenNMS Karaf console
docker exec -it pyu-horizon ssh -p 8101 admin@localhost

# Add HTTP-8080 service (if not exists)
# This should be configured in overlay files
```

Or create overlay configuration:

`horizon/overlay/etc/poller-configuration.xml` (add service definition)

---

## Testing & Validation

### Functional Tests

```bash
# 1. VLE is accessible
curl -I http://localhost:8081
# Expected: HTTP/1.1 200 OK

# 2. VLE login page loads
curl -s http://localhost:8081 | grep -i "moodle"
# Expected: Should contain "Moodle" or "Login"

# 3. Database connection works
docker exec pyu-postgres psql -U moodle -d moodle -c "\dt"
# Expected: List of Moodle tables

# 4. Container is healthy
docker ps | grep pyu-vle
# Expected: Status should show "(healthy)"
```

### OpenNMS Monitoring Tests

```bash
# 1. VLE appears in node list
# Access: http://localhost:8980/opennms
# Navigate: Info → Nodes → Search for "VLE"

# 2. Services are monitored
# Check: ICMP and HTTP-8080 services show as "Up"

# 3. Test alert (optional)
docker stop pyu-vle
# Wait 2-3 minutes
# Check OpenNMS: Alarms should show "VLE down"
docker start pyu-vle
```

---

## Resource Impact

**Additional Resources:**
- RAM: ~400-500 MB (Moodle container)
- Storage: ~2-3 GB (Moodle data volumes)
- Network: Minimal (internal Docker network)

**Total System Load After VLE:**
- Containers: 8 (was 7)
- Estimated RAM: 3-4 GB total
- Still within lab environment limits ✓

---

## Troubleshooting

### Issue: Moodle won't start / Database connection failed

```bash
# Check database exists
docker exec pyu-postgres psql -U postgres -c "\l" | grep moodle

# If missing, create manually
docker exec pyu-postgres psql -U postgres -c "CREATE DATABASE moodle;"
docker exec pyu-postgres psql -U postgres -c "CREATE USER moodle WITH PASSWORD 'moodle';"
docker exec pyu-postgres psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE moodle TO moodle;"

# Restart VLE
docker restart pyu-vle
```

### Issue: Port 8081 already in use

```bash
# Check what's using the port
sudo lsof -i :8081

# Change port in docker-compose.yml
# Change: - "8082:8080/tcp"  # Use 8082 instead
```

### Issue: VLE shows as unhealthy

```bash
# Check container logs
docker logs pyu-vle --tail 50

# Check Moodle installation status
docker exec pyu-vle ls -la /bitnami/moodle/
```

---

## Next Steps After VLE

Once VLE is deployed and monitored:

1. **Verify monitoring** - Ensure OpenNMS shows VLE as up
2. **Document access** - Note VLE URL and credentials
3. **Create test content** (optional) - Add a sample course to look realistic
4. **Proceed to Step 3** - Add remaining Pyongyang services (LDAP, DNS, etc.)

---

## Academic Documentation Notes

**For Your Report:**
- Explain VLE choice (Moodle) as industry-standard educational platform
- Document monitoring approach (HTTP health checks, database connectivity)
- Justify shared database (resource efficiency in lab environment)
- Screenshot: VLE login page + OpenNMS showing VLE as monitored node

**Key Points:**
- VLE is critical infrastructure (primary student-facing service)
- Monitoring ensures availability for "several thousand students"
- Demonstrates understanding of educational IT requirements
- Realistic simulation without excessive resource use

---

**Status:** Ready for Implementation  
**Estimated Time:** 30-45 minutes  
**Risk Level:** Low (non-breaking addition to existing stack)
