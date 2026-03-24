# Optional: Kafka/Zookeeper Cleanup Guide

**Purpose:** Remove legacy Kafka architecture components that are no longer needed  
**Status:** OPTIONAL - Can be done now or later  
**Impact:** Frees up ~100MB RAM and reduces container count

---

## What's Being Removed

1. **pyu-zookeeper** container (currently running but unused)
2. **kafka/** directory and docker-compose.yml (not in use)
3. Any Zookeeper-related volumes

---

## Before You Start

**Check if anything depends on Zookeeper:**

```bash
# Check if any other containers are connected to Zookeeper
docker network inspect kafka_pyu-main | grep -A 10 pyu-zookeeper

# Check if Zookeeper is actively being used
docker stats --no-stream pyu-zookeeper

# Check logs for any connections
docker logs pyu-zookeeper --tail 50
```

**Expected Result:** No active connections (it's orphaned from Kafka setup)

---

## Cleanup Steps

### Step 1: Stop and Remove Zookeeper Container

```bash
# Stop the container
docker stop pyu-zookeeper

# Verify it stopped
docker ps -a | grep zookeeper

# Remove the container
docker rm pyu-zookeeper

# Verify removal
docker ps -a | grep zookeeper  # Should return nothing
```

### Step 2: Remove Kafka Directory (Optional)

```bash
cd ~/opennms-pyu-lab/opennms-pyu-ver2

# Check what's in kafka directory
ls -la kafka/

# Backup first (just in case)
cp -r kafka/ kafka.backup-$(date +%Y%m%d)

# Remove the directory
rm -rf kafka/

# Verify
ls -la | grep kafka  # Should show only kafka.backup-*
```

### Step 3: Clean Up Orphaned Volumes

```bash
# List all volumes
docker volume ls

# Look for Zookeeper-related volumes
docker volume ls | grep -i zookeeper

# Remove Zookeeper volumes (careful - check IDs match!)
# Example (your IDs will be different):
# docker volume rm 18c15164f4cf0554654c5b764d1d386d97005ffaaa459efa053a1ecba33226c0
# docker volume rm 6421c36d7054933995e258b871a480121e47c764bc7c36c694b85d38438babb1
# docker volume rm 95e1046fdbcd41b433387843d589e9245c6481752e8571174838f358cf559e3b

# Safer approach: Prune all unused volumes
docker volume prune
# Warning: This removes ALL unused volumes, not just Zookeeper's
```

### Step 4: Verify System State

```bash
# Check running containers (should be 6 now, not 7)
docker ps

# Expected containers:
# - pyu-horizon
# - pyu-postgres
# - pyu-activemq
# - pyu-py-server
# - hamhung-minion
# - chongjin-minion
# Total: 6 containers
```

---

## Rollback (If Needed)

If you removed Zookeeper but need it back:

```bash
cd ~/opennms-pyu-lab/opennms-pyu-ver2/kafka.backup-*/

# Restart from backup
docker-compose up -d zookeeper
```

---

## Resources Freed

After cleanup:
- **RAM:** ~80-100 MB
- **Storage:** ~500 MB (volumes + images)
- **Containers:** -1 (from 7 to 6)

---

## Alternative: Keep Zookeeper (Why You Might)

**Reasons to keep it:**
1. Minimal resource usage (~100MB)
2. Future Kafka experimentation
3. Avoid breaking any hidden dependencies
4. "If it's not broken, don't fix it"

**Decision:** It's safe to remove, but also safe to keep. Your choice.

---

## For Your Academic Report

**If you remove it:**
- Document the architectural pivot from Kafka to ActiveMQ
- Explain the troubleshooting process
- Show understanding of different messaging architectures
- Demonstrate systematic cleanup methodology

**If you keep it:**
- Mention it as "reserved for future Kafka integration experiments"
- No need to explain why it's there

---

**Recommendation:** Remove it now to clean up the environment. If you need Kafka later, you have the backup.

**Proceed?** This is entirely optional - VLE implementation can proceed either way.
