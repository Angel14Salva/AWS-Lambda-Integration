# AWS Lambda Integration — Image Processor

Pipeline serverless en AWS que recibe imágenes vía API Gateway, las almacena en S3 y las procesa de forma asíncrona con Lambda para generar miniaturas circulares de 40×40 px.

## Arquitectura

```
Client
  │  POST /upload
  ▼
API Gateway HTTP v2
  ▼
upload-lambda (subred privada)
  │  sube imagen a S3
  ▼
S3 Bucket (uploads/)
  │  notificación ObjectCreated
  ▼
SQS Queue
  ▼
crop-lambda (subred privada)
  │  recorta a 40×40 circular con sharp
  ▼
S3 Bucket (processed/)
```

Todo el tráfico entre las funciones Lambda y los servicios AWS viaja por la red interna mediante VPC Endpoints.

## Entornos

| Entorno | VPC CIDR | Retención logs | Memoria crop |
|---------|----------|----------------|--------------|
| dev | 10.0.0.0/16 | 7 días | 512 MB |
| qa | 10.1.0.0/16 | 14 días | 512 MB |
| prod | 10.2.0.0/16 | 30 días | 1024 MB |

## Requisitos

- Terraform v1.5 o superior
- AWS CLI v2
- Node.js 20 LTS
- Credenciales AWS configuradas

Para configurar las credenciales:

```
aws configure
```

## Instalación

Instalar dependencias de las funciones Lambda:

```
cd lambda_src/upload
npm install
```

Para crop, sharp necesita compilarse para Linux:

```
cd lambda_src/crop
npm install --platform=linux --arch=x64 sharp
```

## Despliegue

Inicializar Terraform:

```
terraform init
```

Desplegar el entorno deseado:

```
terraform apply -var-file=environments/dev/terraform.tfvars
terraform apply -var-file=environments/qa/terraform.tfvars
terraform apply -var-file=environments/prod/terraform.tfvars
```

Al terminar se muestran los outputs con el endpoint, el bucket y los nombres de las funciones.

## Prueba

```
curl -X POST https://XXXX.execute-api.us-east-1.amazonaws.com/upload \
  -F "file=@imagen.jpg"
```

También se puede probar desde Postman con método POST y el archivo en form-data.

## Destruir recursos

```
terraform destroy -var-file=environments/dev/terraform.tfvars
terraform destroy -var-file=environments/qa/terraform.tfvars
terraform destroy -var-file=environments/prod/terraform.tfvars
```

## Recursos creados por entorno

| Recurso | Nombre |
|---------|--------|
| VPC | image-processor-{env}-vpc |
| Subnets | image-processor-{env}-private-a/b |
| NAT Gateways | image-processor-{env}-nat-a/b |
| S3 Bucket | image-processor-{env}-images-{hash} |
| SQS Queue | image-processor-{env}-image-queue |
| SQS DLQ | image-processor-{env}-image-dlq |
| Lambda Upload | image-processor-{env}-upload |
| Lambda Crop | image-processor-{env}-crop |
| API Gateway | image-processor-{env}-api |
| IAM Roles | image-processor-{env}-*-role |
| CloudWatch Alarm | image-processor-{env}-dlq-alarm |

## Estructura del proyecto

```
aws-lambda-integration/
├── main.tf
├── variables.tf
├── outputs.tf
├── environments/
│   ├── dev/terraform.tfvars
│   ├── qa/terraform.tfvars
│   └── prod/terraform.tfvars
├── modules/
│   ├── vpc/
│   ├── s3/
│   ├── sqs/
│   ├── lambda/
│   ├── api_gateway/
│   ├── iam/
│   └── cloudwatch/
└── lambda_src/
    ├── upload/
    └── crop/
```

## Seguridad

- Las funciones Lambda corren en subnets privadas
- El tráfico a S3 y SQS va por VPC Endpoints
- El bucket S3 tiene acceso público bloqueado y cifrado AES-256
- Los roles IAM tienen mínimo privilegio

## Autor

Angel Salva — UPAO 2026