# Containerlab Installation and Setup

## 1. Overview
Containerlab was installed to create a simulated network environment for testing the automated network troubleshooting system. This allows controlled generation of network faults such as interface failures and neighbour changes.

---

## 2. Installation Steps

The following steps were carried out to install and configure Containerlab:

### Step 1: Install WSL (Windows Subsystem for Linux)
- Opened PowerShell as Administrator
- Ran the following command:
  wsl --install
- Restarted the system
- Completed Ubuntu setup (username and password)

---

### Step 2: Install Docker Desktop
- Downloaded Docker Desktop from the official website
- Installed Docker Desktop with WSL integration enabled
- Ensured Docker was connected to the Ubuntu distribution

- Verified installation using:
  docker --version
  docker ps
  
---

### Step 3: Install Containerlab
- Opened Ubuntu terminal
- Ran the following command:
  bash -c "$(curl -sL https://get.containerlab.dev)"
- Verified installation using:
  containerlab version
---

## 3. Initial Deployment Test

A basic test topology file (`test.yml`) was created to verify that Containerlab was working correctly.

The lab was deployed using:
containerlab deploy -t test.yml

---

## 4. Issues Encountered

During deployment, the following error occurred:
Failed to lookup link "br-xxxx": Link not found

This indicated that Containerlab could not detect the Docker bridge interface associated with the network.

---

## 5. Troubleshooting and Resolution

The issue was resolved using the following steps:

### Step 1: Remove existing Docker network
docker network rm clab

### Step 2: Restart environment
- Closed Docker Desktop
- Ran:
  wsl --shutdown
- Restarted Docker Desktop
- Reopened Ubuntu terminal

### Step 3: Redeploy the lab
containerlab deploy -t test.yml

After these steps, the deployment completed successfully.

---

## 6. Outcome

- Containerlab was successfully installed and configured
- A test topology was deployed successfully
- The environment is now ready for:
  - Creating network topologies
  - Simulating faults
  - Integrating with monitoring and automation tools
