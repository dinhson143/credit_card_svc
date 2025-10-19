from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
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

        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
                "yum update -y",
                "yum install -y git python3 python3-pip curl",
                "curl -sSL https://install.python-poetry.org | python3 -",
                "export PATH=$PATH:/root/.local/bin",
                "cd /home/ec2-user",
                "git clone https://github.com/dinhson143/credit_card_svc.git",
                "cd credit_card_svc",
                "~/.local/bin/poetry config virtualenvs.create false",
                "~/.local/bin/poetry install --no-root",
                "nohup ~/.local/bin/poetry run uvicorn src.main:app --host 0.0.0.0 --port 80 &",
        )

        ec2.Instance(
                self,
                f"credit-card-svc-{pr_number if pr_number else "master"}",
                vpc=vpc,
                instance_type=ec2.InstanceType("t3.micro"),
                machine_image=ec2.MachineImage.latest_amazon_linux2023(),
                security_group=sg,
                user_data=user_data,
                key_name="test",
        )

