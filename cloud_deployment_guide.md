# Guía de Despliegue en la Nube

Esta guía detalla el proceso para desplegar la API REST de migración CSV a SQL en diferentes plataformas de nube.

## Índice
1. [Despliegue en AWS](#despliegue-en-aws)
2. [Despliegue en Google Cloud Platform](#despliegue-en-google-cloud-platform)
3. [Despliegue en Microsoft Azure](#despliegue-en-microsoft-azure)
4. [Despliegue en Heroku](#despliegue-en-heroku)

## Despliegue en AWS

### Opción 1: AWS Elastic Beanstalk

AWS Elastic Beanstalk es un servicio que facilita el despliegue y la administración de aplicaciones en la nube de AWS.

#### Requisitos previos
- Cuenta de AWS
- AWS CLI instalado y configurado
- EB CLI instalado (`pip install awsebcli`)

#### Pasos para el despliegue

1. **Preparar la aplicación para Elastic Beanstalk**

   Crea un archivo `Procfile` en la raíz del proyecto:
   ```
   web: uvicorn app.main_updated:app --host 0.0.0.0 --port $PORT
   ```

2. **Inicializar la aplicación EB**

   ```bash
   eb init -p python-3.9 csv-api-migration
   ```
   
   Sigue las instrucciones para configurar tu aplicación.

3. **Crear un entorno y desplegar**

   ```bash
   eb create csv-api-migration-env
   ```

4. **Verificar el despliegue**

   ```bash
   eb open
   ```
   
   Esto abrirá la URL de tu aplicación en el navegador.

5. **Actualizar la aplicación cuando sea necesario**

   Después de realizar cambios en tu código:
   ```bash
   eb deploy
   ```

### Opción 2: AWS ECS con Docker

Amazon Elastic Container Service (ECS) es un servicio de orquestación de contenedores.

#### Requisitos previos
- Cuenta de AWS
- AWS CLI instalado y configurado
- Docker instalado

#### Pasos para el despliegue

1. **Crear un repositorio en Amazon ECR**

   ```bash
   aws ecr create-repository --repository-name csv-api-migration
   ```

2. **Autenticar Docker con ECR**

   ```bash
   aws ecr get-login-password --region <tu-region> | docker login --username AWS --password-stdin <tu-cuenta-aws>.dkr.ecr.<tu-region>.amazonaws.com
   ```

3. **Construir y etiquetar la imagen Docker**

   ```bash
   docker build -t csv-api-migration .
   docker tag csv-api-migration:latest <tu-cuenta-aws>.dkr.ecr.<tu-region>.amazonaws.com/csv-api-migration:latest
   ```

4. **Subir la imagen a ECR**

   ```bash
   docker push <tu-cuenta-aws>.dkr.ecr.<tu-region>.amazonaws.com/csv-api-migration:latest
   ```

5. **Crear un clúster de ECS**

   Desde la consola de AWS:
   - Navega a Amazon ECS
   - Crea un nuevo clúster
   - Selecciona el tipo de clúster (Fargate es recomendado para empezar)

6. **Crear una definición de tarea**

   - Navega a "Task Definitions" en ECS
   - Crea una nueva definición de tarea
   - Selecciona Fargate como tipo de lanzamiento
   - Configura la memoria y CPU según tus necesidades
   - Añade un contenedor usando la imagen de ECR
   - Mapea el puerto 8000 del contenedor al puerto 8000 del host

7. **Crear un servicio ECS**

   - En tu clúster, crea un nuevo servicio
   - Selecciona la definición de tarea que creaste
   - Configura el número de tareas (1 para empezar)
   - Configura la red y los grupos de seguridad
   - Opcionalmente, configura un balanceador de carga

## Despliegue en Google Cloud Platform

### Google Cloud Run

Cloud Run es un servicio de computación gestionado que permite ejecutar contenedores sin servidor.

#### Requisitos previos
- Cuenta de Google Cloud
- Google Cloud SDK instalado y configurado
- Docker instalado

#### Pasos para el despliegue

1. **Habilitar las APIs necesarias**

   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   ```

2. **Construir y subir la imagen a Google Container Registry**

   ```bash
   gcloud builds submit --tag gcr.io/<tu-proyecto>/csv-api-migration
   ```

3. **Desplegar en Cloud Run**

   ```bash
   gcloud run deploy csv-api-migration \
     --image gcr.io/<tu-proyecto>/csv-api-migration \
     --platform managed \
     --region <tu-region> \
     --allow-unauthenticated
   ```

4. **Verificar el despliegue**

   La URL de tu servicio se mostrará en la salida del comando anterior.

## Despliegue en Microsoft Azure

### Azure Container Instances

Azure Container Instances (ACI) permite ejecutar contenedores Docker sin administrar máquinas virtuales.

#### Requisitos previos
- Cuenta de Azure
- Azure CLI instalado y configurado
- Docker instalado

#### Pasos para el despliegue

1. **Iniciar sesión en Azure**

   ```bash
   az login
   ```

2. **Crear un grupo de recursos**

   ```bash
   az group create --name csv-api-migration-rg --location eastus
   ```

3. **Crear un registro de contenedores de Azure**

   ```bash
   az acr create --resource-group csv-api-migration-rg --name csvapimigrationacrvld001 --sku Basic
   ```

4. **Iniciar sesión en el registro de contenedores**

   ```bash
   az acr login --name csvapimigrationacrvld001
   ```

5. **Construir y etiquetar la imagen Docker**

   ```bash
   docker build -t csv-api-migration .
   docker tag csv-api-migration csvapimigrationacrvld001.azurecr.io/csv-api-migration:latest
   ```

6. **Subir la imagen al registro de contenedores**

   ```bash
   docker push csvapimigrationacrvld001.azurecr.io/csv-api-migration:latest
   ```

7. **Habilitar la cuenta de administrador para el registro**

   ```bash
   az acr update --name csvapimigrationacrvld001 --admin-enabled true
   ```

8. **Obtener las credenciales del registro**

   ```bash
   az acr credential show --name csvapimigrationacrvld001
   ```

9. **Crear una instancia de contenedor**

   ```bash
   az container create \
     --resource-group csv-api-migration-rg \
     --name csv-api-migration \
     --image csvapimigrationacr.azurecr.io/csv-api-migration:latest \
     --cpu 1 \
     --memory 1.5 \
     --registry-login-server csvapimigrationacr.azurecr.io \
     --registry-username <username-from-credentials> \
     --registry-password <password-from-credentials> \
     --dns-name-label csv-api-migration \
     --ports 8001 \
     --ip-address public \
     --command-line "uvicorn app.main_alternative:app --host 0.0.0.0 --port 8001" \
     --os-type Linux
   ```

10. **Verificar el despliegue**

    ```bash
    az container show \
      --resource-group csv-api-migration-rg \
      --name csv-api-migration \
      --query "{FQDN:ipAddress.fqdn,ProvisioningState:provisioningState}" \
      --output table
    ```

    La API estará disponible en `http://<FQDN>:8001`.

## Despliegue en Heroku

Heroku es una plataforma como servicio (PaaS) que permite a los desarrolladores construir, ejecutar y operar aplicaciones en la nube.

#### Requisitos previos
- Cuenta de Heroku
- Heroku CLI instalado
- Git instalado

#### Pasos para el despliegue

1. **Iniciar sesión en Heroku**

   ```bash
   heroku login
   ```

2. **Crear una aplicación Heroku**

   ```bash
   heroku create csv-api-migration
   ```

3. **Añadir un archivo Procfile**

   Crea un archivo `Procfile` en la raíz del proyecto:
   ```
   web: uvicorn app.main_updated:app --host 0.0.0.0 --port $PORT
   ```

4. **Configurar Heroku para usar contenedores**

   ```bash
   heroku stack:set container
   ```

5. **Crear un archivo heroku.yml**

   Crea un archivo `heroku.yml` en la raíz del proyecto:
   ```yaml
   build:
     docker:
       web: Dockerfile
   ```

6. **Desplegar la aplicación**

   ```bash
   git add .
   git commit -m "Preparar para despliegue en Heroku"
   git push heroku master
   ```

7. **Verificar el despliegue**

   ```bash
   heroku open
   ```

## Consideraciones Generales

Independientemente de la plataforma de nube que elijas, hay algunas consideraciones importantes:

1. **Base de datos**: La aplicación actual usa SQLite, que es adecuado para desarrollo pero no para producción en la nube. Considera migrar a:
   - AWS: Amazon RDS (PostgreSQL, MySQL)
   - GCP: Cloud SQL
   - Azure: Azure Database for PostgreSQL/MySQL
   - Heroku: Heroku Postgres

2. **Variables de entorno**: Usa variables de entorno para configuraciones sensibles o específicas del entorno.

3. **Monitoreo y logging**: Configura herramientas de monitoreo y logging para tu aplicación en la nube.

4. **Escalado**: Configura el escalado automático según tus necesidades de carga.

5. **Seguridad**: Implementa medidas de seguridad adicionales como HTTPS, autenticación y autorización.

## Conclusión

Has aprendido a desplegar la API REST de migración CSV a SQL en diferentes plataformas de nube. Cada plataforma tiene sus propias ventajas y consideraciones, así que elige la que mejor se adapte a tus necesidades y familiaridad.
