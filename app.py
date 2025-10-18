import os

import aws_cdk as cdk

from infrastructure.ec2 import InfrastructureStack

app = cdk.App()
pr_number = os.getenv('PR_NUMBER') if os.getenv('PR_NUMBER') else ""
InfrastructureStack(app, f"InfrastructureStack{pr_number}", pr_number=pr_number)

app.synth()