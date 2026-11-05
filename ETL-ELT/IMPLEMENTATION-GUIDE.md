# Quick Implementation Guide

## 1. Setup Foundation (Week 1)

### AWS Account Setup
```bash
# Configure AWS CLI
aws configure

# Create S3 buckets
aws s3 mb s3://company-raw-data-prod
aws s3 mb s3://company-curated-data-prod
aws s3 mb s3://company-ml-artifacts-prod

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket company-raw-data-prod \
  --versioning-configuration Status=Enabled
```

### Infrastructure as Code (Terraform)
```hcl
# main.tf
resource "aws_s3_bucket" "raw_data" {
  bucket = "company-raw-data-prod"
  
  lifecycle_rule {
    enabled = true
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

resource "aws_glue_catalog_database" "main" {
  name = "etl_database"
}
```

## 2. ETL Pipeline Example

### Glue ETL Job (Python/PySpark)
```python
# glue_etl_job.py
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Extract
datasource = glueContext.create_dynamic_frame.from_catalog(
    database = "etl_database",
    table_name = "raw_customers"
)

# Transform
transformed = datasource.apply_mapping([
    ("customer_id", "string", "customer_id", "string"),
    ("name", "string", "customer_name", "string"),
    ("email", "string", "email", "string"),
    ("created_at", "string", "created_at", "timestamp")
])

# Load to Redshift
glueContext.write_dynamic_frame.from_jdbc_conf(
    frame = transformed,
    catalog_connection = "redshift-connection",
    connection_options = {
        "dbtable": "curated.customers",
        "database": "analytics"
    },
    redshift_tmp_dir = "s3://company-temp/redshift/"
)

job.commit()
```

## 3. ELT Pattern with Athena

### Create External Table
```sql
-- athena_table.sql
CREATE EXTERNAL TABLE raw_events (
    event_id STRING,
    user_id STRING,
    event_type STRING,
    event_data STRING,
    timestamp TIMESTAMP
)
PARTITIONED BY (year INT, month INT, day INT)
STORED AS PARQUET
LOCATION 's3://company-raw-data-prod/events/';

-- Load partitions
MSCK REPAIR TABLE raw_events;
```

### Transform with Athena
```sql
-- transform_query.sql
CREATE TABLE curated.user_activity AS
SELECT 
    user_id,
    DATE_TRUNC('day', timestamp) as activity_date,
    COUNT(*) as event_count,
    COUNT(DISTINCT event_type) as unique_events,
    MAX(timestamp) as last_activity
FROM raw_events
WHERE year = 2024
GROUP BY user_id, DATE_TRUNC('day', timestamp);
```

## 4. Streaming Pipeline (Kinesis + Lambda)

### Lambda Handler
```python
# lambda_stream_processor.py
import json
import boto3
import base64
from datetime import datetime

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime')

def lambda_handler(event, context):
    for record in event['Records']:
        # Decode Kinesis data
        payload = base64.b64decode(record['kinesis']['data'])
        data = json.loads(payload)
        
        # Enrich with Bedrock LLM
        if 'text' in data:
            response = bedrock.invoke_model(
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [{
                        "role": "user",
                        "content": f"Extract entities from: {data['text']}"
                    }],
                    "max_tokens": 500
                })
            )
            
            llm_result = json.loads(response['body'].read())
            data['enriched'] = llm_result['content'][0]['text']
        
        # Write to S3
        timestamp = datetime.now().strftime('%Y/%m/%d/%H')
        key = f"enriched/{timestamp}/{record['kinesis']['sequenceNumber']}.json"
        
        s3.put_object(
            Bucket='company-raw-data-prod',
            Key=key,
            Body=json.dumps(data)
        )
    
    return {'statusCode': 200}
```

## 5. ML Feature Pipeline

### SageMaker Processing Job
```python
# feature_engineering.py
import pandas as pd
import boto3
from sagemaker.feature_store.feature_group import FeatureGroup

# Read from S3
df = pd.read_parquet('s3://company-curated-data-prod/customers/')

# Feature engineering
df['days_since_signup'] = (pd.Timestamp.now() - df['created_at']).dt.days
df['email_domain'] = df['email'].str.split('@').str[1]
df['is_gmail'] = (df['email_domain'] == 'gmail.com').astype(int)

# Add event time for Feature Store
df['event_time'] = pd.Timestamp.now().timestamp()

# Write to Feature Store
feature_group = FeatureGroup(name='customer-features', sagemaker_session=sagemaker_session)
feature_group.ingest(data_frame=df, max_workers=3, wait=True)
```

### Feature Store Setup
```python
# setup_feature_store.py
from sagemaker.feature_store.feature_group import FeatureGroup
from sagemaker.feature_store.feature_definition import FeatureDefinition

feature_group = FeatureGroup(name='customer-features', sagemaker_session=session)

feature_group.load_feature_definitions(data_frame=df)

feature_group.create(
    s3_uri=f's3://company-ml-artifacts-prod/feature-store',
    record_identifier_name='customer_id',
    event_time_feature_name='event_time',
    role_arn=role_arn,
    enable_online_store=True
)
```

## 6. LLM-Powered Data Processing

### Document Processing Pipeline
```python
# document_processor.py
import boto3
import json

s3 = boto3.client('s3')
textract = boto3.client('textract')
bedrock = boto3.client('bedrock-runtime')

def process_document(bucket, key):
    # Extract text with Textract
    response = textract.start_document_text_detection(
        DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': key}}
    )
    job_id = response['JobId']
    
    # Wait and get result
    result = textract.get_document_text_detection(JobId=job_id)
    full_text = ' '.join([item['Text'] for item in result['Blocks'] if item['BlockType'] == 'LINE'])
    
    # Analyze with Bedrock
    prompt = f"""Analyze this document and extract:
    1. Key entities (names, dates, amounts)
    2. Document type
    3. Summary (2-3 sentences)
    
    Document text:
    {full_text}
    
    Return as JSON.
    """
    
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        })
    )
    
    analysis = json.loads(response['body'].read())
    
    # Store result
    output_key = key.replace('raw/', 'processed/')
    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=json.dumps({
            'original_text': full_text,
            'analysis': analysis
        })
    )
    
    return analysis
```

## 7. Orchestration with Step Functions

### ETL Workflow Definition
```json
{
  "Comment": "ETL Pipeline with ML",
  "StartAt": "ExtractData",
  "States": {
    "ExtractData": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "extract-raw-data"
      },
      "Next": "TransformData"
    },
    "TransformData": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "transform-and-load"
      },
      "Next": "DataQualityCheck"
    },
    "DataQualityCheck": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:invoke",
      "Parameters": {
        "FunctionName": "data-quality-validator"
      },
      "Next": "QualityCheckPassed"
    },
    "QualityCheckPassed": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.quality_score",
          "NumericGreaterThan": 0.95,
          "Next": "TriggerMLPipeline"
        }
      ],
      "Default": "SendAlert"
    },
    "TriggerMLPipeline": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:invoke",
      "Parameters": {
        "FunctionName": "trigger-sagemaker-pipeline"
      },
      "Next": "Success"
    },
    "SendAlert": {
      "Type": "Task",
      "Resource": "arn:aws:sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-east-1:123456789:data-quality-alerts",
        "Message": "Data quality check failed"
      },
      "End": true
    },
    "Success": {
      "Type": "Succeed"
    }
  }
}
```

## 8. Monitoring Setup

### CloudWatch Dashboard
```python
# create_dashboard.py
import boto3

cloudwatch = boto3.client('cloudwatch')

dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/Glue", "glue.driver.aggregate.numCompletedTasks", {"stat": "Sum"}],
                    ["AWS/Lambda", "Invocations", {"stat": "Sum"}]
                ],
                "period": 300,
                "stat": "Sum",
                "region": "us-east-1",
                "title": "ETL Pipeline Metrics"
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName='ETL-Pipeline-Monitor',
    DashboardBody=json.dumps(dashboard_body)
)
```

### CloudWatch Alarms
```python
# create_alarms.py
cloudwatch.put_metric_alarm(
    AlarmName='Glue-Job-Failure',
    ComparisonOperator='GreaterThanThreshold',
    EvaluationPeriods=1,
    MetricName='glue.driver.aggregate.numFailedTasks',
    Namespace='AWS/Glue',
    Period=300,
    Statistic='Sum',
    Threshold=1,
    ActionsEnabled=True,
    AlarmActions=['arn:aws:sns:us-east-1:123456789:etl-alerts']
)
```

## 9. Data Quality with Great Expectations

```python
# data_validation.py
import great_expectations as gx
import pandas as pd

context = gx.get_context()

# Read data
df = pd.read_parquet('s3://company-curated-data-prod/customers/')

# Create expectations
df_expectation = context.sources.pandas_default.read_dataframe(df)

validator = df_expectation.get_validator()

# Add expectations
validator.expect_column_to_exist('customer_id')
validator.expect_column_values_to_be_unique('customer_id')
validator.expect_column_values_to_not_be_null('email')
validator.expect_column_values_to_match_regex('email', r'^[^@]+@[^@]+\.[^@]+$')

# Run validation
results = validator.validate()

if not results.success:
    raise Exception(f"Data quality check failed: {results}")
```

## 10. Deployment Script

```bash
#!/bin/bash
# deploy.sh

# Set variables
ENVIRONMENT="prod"
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Deploy infrastructure
cd terraform
terraform init
terraform apply -var="environment=$ENVIRONMENT" -auto-approve

# Deploy Glue jobs
aws glue create-job \
  --name "customer-etl-$ENVIRONMENT" \
  --role "arn:aws:iam::$ACCOUNT_ID:role/GlueServiceRole" \
  --command "Name=glueetl,ScriptLocation=s3://company-scripts/glue_etl_job.py" \
  --default-arguments '{
    "--job-language":"python",
    "--TempDir":"s3://company-temp/glue/"
  }'

# Deploy Lambda functions
for func in lambda-functions/*.py; do
    func_name=$(basename "$func" .py)
    zip "${func_name}.zip" "$func"
    
    aws lambda create-function \
      --function-name "${func_name}-${ENVIRONMENT}" \
      --runtime python3.11 \
      --role "arn:aws:iam::$ACCOUNT_ID:role/LambdaExecutionRole" \
      --handler "${func_name}.lambda_handler" \
      --zip-file "fileb://${func_name}.zip"
done

# Deploy Step Functions
aws stepfunctions create-state-machine \
  --name "etl-pipeline-$ENVIRONMENT" \
  --definition file://step-function.json \
  --role-arn "arn:aws:iam::$ACCOUNT_ID:role/StepFunctionsRole"

echo "Deployment complete!"
```

## Key Implementation Tips

1. **Start Small**: Begin with one data source and one pipeline
2. **Version Control**: Store all scripts in Git
3. **Test in Dev**: Use separate AWS accounts for dev/prod
4. **Monitor Early**: Set up CloudWatch from day one
5. **Document**: Maintain data dictionary and lineage
6. **Secure**: Use IAM roles, never hardcode credentials
7. **Cost**: Enable cost allocation tags on all resources
8. **Iterate**: Build → Test → Monitor → Optimize

## Recommended Timeline

- **Week 1-2**: Infrastructure setup, S3 buckets, IAM roles
- **Week 3-4**: First batch ETL pipeline (Glue)
- **Week 5-6**: ELT pattern with Athena/Redshift
- **Week 7-8**: Streaming pipeline (Kinesis + Lambda)
- **Week 9-10**: ML feature pipeline (SageMaker)
- **Week 11-12**: LLM integration (Bedrock)
- **Ongoing**: Monitoring, optimization, new use cases
