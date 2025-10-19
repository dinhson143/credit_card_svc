from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
)
from constructs import Construct


class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, pr_number: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)

        sg = ec2.SecurityGroup(
                self,
                "credit-card-svc-sg",
                vpc=vpc,
                allow_all_outbound=True,
                description="Allow SSH (22) and HTTP (80) access for FastAPI app",
        )
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "Allow SSH")
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP")
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(8000), "Allow FastAPI")

        role = iam.Role(
                self,
                "EC2RoleWithCWLogs",
                assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
                    iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchAgentServerPolicy")
                ],
        )

        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
                # --- System update & base dependencies ---
                "yum update -y",
                "yum install -y git python3.12 python3.12-pip amazon-cloudwatch-agent --allowerasing",

                # --- Set Python 3.12 as default ---
                "alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1",
                "alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.12 1",

                # --- Install Poetry for ec2-user ---
                "runuser -l ec2-user -c 'curl -sSL https://install.python-poetry.org | python3 -'",

                # --- Add Poetry to PATH permanently ---
                "echo 'export PATH=$HOME/.local/bin:$PATH' >> /home/ec2-user/.bashrc",

                # --- Clone the repository ---
                "runuser -l ec2-user -c 'cd ~ && git clone https://github.com/dinhson143/credit_card_svc.git || (cd ~/credit_card_svc && git pull)'",

                # --- Install project dependencies with Poetry ---
                "runuser -l ec2-user -c 'source ~/.bashrc && cd ~/credit_card_svc && "
                "poetry env use python3.12 && poetry install --no-root --no-interaction'",

                # --- Create log folder and fix permissions ---
                "mkdir -p /var/log/credit_card_svc",
                "chown -R ec2-user:ec2-user /var/log/credit_card_svc",

                # --- Configure CloudWatch Agent for app logs ---
                "cat <<EOF > /opt/aws/amazon-cloudwatch-agent/config.json\n"
                "{\n"
                "  \"logs\": {\n"
                "    \"logs_collected\": {\n"
                "      \"files\": {\n"
                "        \"collect_list\": [\n"
                "          {\n"
                "            \"file_path\": \"/var/log/credit_card_svc/uvicorn.log\",\n"
                "            \"log_group_name\": \"/credit-card-svc\",\n"
                "            \"log_stream_name\": \"{instance_id}\",\n"
                "            \"timestamp_format\": \"%Y-%m-%d %H:%M:%S\"\n"
                "          }\n"
                "        ]\n"
                "      }\n"
                "    }\n"
                "  }\n"
                "}\n"
                "EOF",

                # --- Start CloudWatch Agent ---
                "/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl "
                "-a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/config.json -s",

                # --- Run FastAPI app on port 80 (as ec2-user, detached) ---
                "runuser -l ec2-user -c 'source ~/.bashrc && cd ~/credit_card_svc && "
                "nohup poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 "
                "> /var/log/credit_card_svc/uvicorn.log 2>&1 &'"
        )

        ec2.Instance(
                self,
                f"credit-card-svc-{pr_number if pr_number else 'master'}",
                vpc=vpc,
                instance_type=ec2.InstanceType("t3.micro"),
                machine_image=ec2.MachineImage.latest_amazon_linux2023(),
                security_group=sg,
                user_data=user_data,
                key_name="test",
                role=role,
        )
