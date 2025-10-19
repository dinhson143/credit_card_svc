# Credit Card Service

## 📖 Overview
**credit_card_svc** is a lightweight FastAPI-based microservice that validates credit card numbers using the **Luhn algorithm**.

---

## 🚀 Deployment

**Live Demo:**  
👉 [http://ec2-13-229-94-7.ap-southeast-1.compute.amazonaws.com:8000/docs](http://ec2-13-229-94-7.ap-southeast-1.compute.amazonaws.com:8000/docs)

### 1. Prerequisites
- Amazon Linux 2023 EC2 instance
- Python 3.12.x
- Poetry
- Git installed
- Security Group allows inbound TCP port **8000**

---

### 2. Installation

```bash
sudo yum update -y
sudo yum install -y git python3.12 python3.12-pip amazon-cloudwatch-agent --allowerasing

# --- Set Python 3.12 as default ---
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
sudo alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.12 1

# --- Install Poetry for ec2-user ---
runuser -l ec2-user -c 'curl -sSL https://install.python-poetry.org | python3 -'

# --- Add Poetry to PATH permanently ---
echo 'export PATH=$HOME/.local/bin:$PATH' >> /home/ec2-user/.bashrc
source /home/ec2-user/.bashrc

# --- Clone the repository ---
runuser -l ec2-user -c 'cd ~ && git clone https://github.com/dinhson143/credit_card_svc.git || (cd ~/credit_card_svc && git pull)'

# --- Install project dependencies with Poetry ---
runuser -l ec2-user -c 'source ~/.bashrc && cd ~/credit_card_svc && \
poetry env use python3.12 && poetry install --no-root --no-interaction'

# --- Create log folder and fix permissions ---
sudo mkdir -p /var/log/credit_card_svc
sudo chown -R ec2-user:ec2-user /var/log/credit_card_svc

# --- Configure CloudWatch Agent for app logs ---
sudo tee /opt/aws/amazon-cloudwatch-agent/config.json > /dev/null <<EOF
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/credit_card_svc/uvicorn.log",
            "log_group_name": "/credit-card-svc",
            "log_stream_name": "{instance_id}",
            "timestamp_format": "%Y-%m-%d %H:%M:%S"
          }
        ]
      }
    }
  }
}
EOF

# --- Start CloudWatch Agent ---
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/config.json -s

# --- Run FastAPI app on port 8000 (detached, as ec2-user) ---
runuser -l ec2-user -c 'source ~/.bashrc && cd ~/credit_card_svc && \
nohup poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 \
> /var/log/credit_card_svc/uvicorn.log 2>&1 &'

```
Then open your browser at:
```
http://<PublicDNS>:8000/docs
```

### 3. Verify Service Status:
## Verify Service Status

```bash
# Check cloud-init output (user-data script logs)
sudo cat /var/log/cloud-init-output.log

# Check if FastAPI (uvicorn) is running
ps aux | grep uvicorn

# Check FastAPI log for runtime messages or errors
sudo cat /var/log/credit_card_svc/uvicorn.log
````

## 🧠 API Endpoints

### `POST /validate`
Validate a credit card number using the **Luhn algorithm**.

#### 📝 Request Body
```json
{
  "number": "4539578809285153"
}
```


## 🧩 Project Structure

The project follows a clean, modular architecture for readability and maintainability.

```
credit_card_svc/
├── infrastructure/
│   ├── __init__.py
│   └── ec2.py                     # AWS EC2/CDK deployment logic
│
├── src/
│   ├── apis/
│   │   ├── __init__.py
│   │   └── credit_card_router.py  # API routes for validation endpoint
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── credit_card_request.py # Request model with input validation
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── credit_card_service.py # Service layer calling Luhn logic
│   │   └── luhn_service.py        # Core Luhn algorithm implementation
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── dependencies.py        # Dependency injection and setup
│   │   ├── logging.py             # Logging configuration (no PAN logging)
│   ├── main.py                    # FastAPI app instance (entry point)
│   │
├── test/
│   ├── __init__.py
│   └── test_credit_card_service.py
│
├── app.py                         
├── poetry.lock
├── pyproject.toml                
├── README.md
└── .gitignore

```

## 💻 Run Locally
```aiignore
# Clone the repo
git clone https://github.com/dinhson143/credit_card_svc.git
cd credit_card_svc

# Install dependencies
poetry install

# Run the FastAPI app
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000

```