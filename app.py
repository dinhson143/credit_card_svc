import os
import aws_cdk as cdk
from infrastructure.ec2 import InfrastructureStack

app = cdk.App()

pr_number = os.getenv('PR_NUMBER') if os.getenv('PR_NUMBER') else ""

InfrastructureStack(
        app,
        f"InfrastructureStack{pr_number}",
        pr_number=pr_number,
        env=cdk.Environment(
                account=os.getenv("CDK_DEFAULT_ACCOUNT", "575755867754"),
                region=os.getenv("CDK_DEFAULT_REGION", "ap-southeast-1")
        )
)

app.synth()
