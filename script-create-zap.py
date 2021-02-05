from kubernetes import client, config
import time

DEPLOYMENT_NAME = "zap1-deployment"


def create_deployment_object():
    # Configureate Pod template container
    container = client.V1Container(
        name="zaproxy",
        image="owasp/zap2docker-stable",
        command=["zap.sh"],
        args=["-daemon", "-host", "0.0.0.0", "-port", "8090", "-config", "api.disablekey=true", "-config",
              "api.addrs.addr.name=.*", "-config", "api.addrs.addr.regex=true"],
        ports=[client.V1ContainerPort(container_port=8090)],
        resources=client.V1ResourceRequirements(
            requests={"cpu": "100m", "memory": "200Mi"},
            limits={"cpu": "500m", "memory": "500Mi"}
        )
    )
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={'app': 'zap-app', 'name': 'zap-application'}),
        spec=client.V1PodSpec(containers=[container]))
    # Create the specification of deployment
    spec = client.V1DeploymentSpec(
        replicas=1,
        template=template,
        selector={'matchLabels': {'app': 'zap-app', 'name': 'zap-application'}})
    # Instantiate the deployment object
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=DEPLOYMENT_NAME, labels={'app': 'archerysec-app'}),
        spec=spec)

    return deployment


def create_deployment(api_instance, deployment):
    # Create deployement
    api_response = api_instance.create_namespaced_deployment(
        body=deployment,
        namespace="default")
    print("Deployment created. status='%s'" % str(api_response.status))


def create_service():
    core_v1_api = client.CoreV1Api()
    body = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(name=DEPLOYMENT_NAME, labels={'app': 'zap-app', 'name': 'zap-application'}
                                     ),
        spec=client.V1ServiceSpec(
            selector={"app": "zap-app", "name": "zap-application"},
            ports=[client.V1ServicePort(
                port=8090,
                target_port=8090
            )]
        )
    )
    # Creation of the Deployment in specified namespace
    # (Can replace "default" with a namespace you may have created)
    core_v1_api.create_namespaced_service(namespace="default", body=body)


def delete_deployment(api_instance):
    # Delete deployment
    api_response = api_instance.delete_namespaced_deployment(
        name=DEPLOYMENT_NAME,
        namespace="default",
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
    print("Deployment deleted. status='%s'" % str(api_response.status))


def main():
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()

    deployment = create_deployment_object()
    print(deployment)

    # create_deployment(apps_v1, deployment)
    # print("Deployment Created")
    #
    # create_service()
    # print("service created")


if __name__ == '__main__':
    main()
