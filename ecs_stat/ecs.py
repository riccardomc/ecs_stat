import boto3
import json
from subprocess import check_output

ecs = boto3.client('ecs')
ec2 = boto3.client('ec2')


class ECS(object):

    def __init__(self):
        self.clusters = self.describe_clusters()

    def list_clusters(self):
        cluster_arns = ecs.list_clusters()['clusterArns']
        return map((lambda x: x.split('/')[1]), cluster_arns)

    def describe_clusters(self, clusters=[]):
        if len(clusters) == 0:
            clusters = self.list_clusters()
        cluster_dicts = ecs.describe_clusters(clusters=clusters)['clusters']
        return [Cluster(cluster_dict) for cluster_dict in cluster_dicts]

    def refresh(self):
        self.clusters = self.describe_clusters()

    def get_container_by_branch(self, cluster, service, task, container):
        target_cluster = self.clusters[cluster]
        target_service = target_cluster.services[service]
        target_task = target_service.tasks[task]
        return target_task.containers[container]

    def to_dict(self):
        return {'clusters': [cluster.to_dict() for cluster in self.clusters]}

    def __repr__(self):
        return str(self.to_dict())


class Cluster(object):

    keys = ['activeServicesCount',
            'clusterArn',
            'clusterName',
            'pendingTasksCount',
            'registeredContainerInstancesCount',
            'runningTasksCount',
            'status',
            'services',
            'containerInstances',
            'containerInstancesByArn']

    def __init__(self, cluster_dictionary):
        self.__dict__.update(cluster_dictionary)
        self.containerInstances = self.describe_container_instances()
        self.containerInstancesByArn = self.container_instances_by_arn(
                self.containerInstances)
        self.services = self.describe_services()

    def list_services(self):
        service_arns = ecs.list_services(
                cluster=self.clusterName)['serviceArns']
        return map((lambda x: x.split('/')[1]), service_arns)

    def describe_services(self, services=[]):
        if len(services) == 0:
            services = self.list_services()

        service_dicts = []
        if len(services) > 0:
            service_dicts = ecs.describe_services(
                    cluster=self.clusterName, services=services)['services']

        return [Service(service_dict, self) for service_dict in service_dicts]

    def list_container_instances(self):
        container_instance_arns = ecs.list_container_instances(
                cluster=self.clusterName)['containerInstanceArns']
        return map((lambda x: x.split('/')[1]), container_instance_arns)

    def describe_container_instances(self, container_instances=[]):
        if (len(container_instances) == 0):
            container_instances = self.list_container_instances()

        container_instances_dicts = []
        if (len(container_instances) > 0):
            container_instances_dicts = ecs.describe_container_instances(
                    containerInstances=container_instances,
                    cluster=self.clusterName)['containerInstances']

        return [ContainerInstance(container_instance) for
                container_instance in container_instances_dicts]

    def container_instances_by_arn(self, container_instances=[]):
        if len(container_instances) == 0:
            container_instances = self.describe_container_instances()
        return {c.containerInstanceArn: c for c in container_instances}

    def to_dict(self):
        return {k: self.__dict__.get(k) for k in self.keys}

    def __repr__(self):
        return str(self.to_dict())

    def __str__(self):
        return '%s %s (Services: %s, Tasks Running: %s, Tasks Pending: %s, Instances: %s)' % (
            self.clusterName,
            self.status,
            len(self.services),
            self.runningTasksCount,
            self.pendingTasksCount,
            self.registeredContainerInstancesCount)


class Service(object):

    keys = ['status',
            'taskDefinition',
            'pendingCount',
            'tasks',
            'loadBalancers',
            'roleArn',
            'desiredCount',
            'serviceName',
            'clusterArn',
            'serviceArn',
            'deployments',
            'runningCount',
            'cluster']

    def __init__(self, service_dictionary, cluster=None):
        self.__dict__.update(service_dictionary)
        self.cluster = cluster
        self.tasks = self.describe_tasks()

    def list_tasks(self):
        task_arns = ecs.list_tasks(
                cluster=self.clusterArn.split('/')[1],
                serviceName=self.serviceName)['taskArns']

        return map((lambda x: x.split('/')[1]), task_arns)

    def describe_tasks(self, tasks=[]):
        if len(tasks) == 0:
            tasks = self.list_tasks()

        task_dicts = []
        if len(tasks) > 0:
            task_dicts = ecs.describe_tasks(
                    cluster=self.clusterArn.split('/')[1],
                    tasks=tasks)['tasks']

        return [Task(task_dict, self) for task_dict in task_dicts]

    def to_dict(self):
        return {k: self.__dict__.get(k) for k in self.keys}

    def __repr__(self):
        return str(self.to_dict())

    def __str__(self):
        return '%s %s (Tasks: %s, Running/Pending/Desired: %s/%s/%s)' % (
                self.serviceName,
                self.status,
                len(self.tasks),
                self.runningCount,
                self.pendingCount,
                self.desiredCount)


class Task(object):

    keys = ['taskArn',
            'overrides',
            'lastStatus',
            'containerInstanceArn',
            'clusterArn',
            'desiredStatus',
            'taskDefinitionArn',
            'startedBy',
            'containers',
            'taskId',
            'service']

    def __init__(self, task_dictionary, service=None):
        self.__dict__.update(task_dictionary)
        self.taskId = self.taskArn.split('/')[1]
        self.service = service
        self.containers = [Container(c_dict, self) for c_dict in self.containers]

    def to_dict(self):
        return {k: self.__dict__.get(k) for k in self.keys}

    def __repr__(self):
        return str(self.to_dict())

    def __str__(self):
        return '%s Containers: %s' % (
                self.taskId,
                len(self.containers)
                )


class Container(object):

    keys = ['containerArn',
            'taskArn',
            'name',
            'networkBindings',
            'lastStatus',
            'exitCode',
            'task',
            'containerInstance']

    def __init__(self, container_dictionary, task=None):
        self.__dict__.update(container_dictionary)
        self.task = task
        containerInstanceArn = self.task.containerInstanceArn
        self.containerInstance = self.task.service.cluster.containerInstancesByArn[containerInstanceArn]

    def to_dict(self):
        return {k: self.__dict__.get(k) for k in self.keys}

    def __repr__(self):
        return str(self.to_dict())

    def __str__(self):
        return '%s %s | %s' % (self.name, self.lastStatus, self.containerInstance.EC2Instance)


class ContainerInstance(object):

    keys = ['status',
            'ec2InstanceId',
            'agentConnected',
            'containerInstanceArn',
            'pendingTasksCount',
            'runningTasksCount',
            'versionInfo',
            'EC2Instance']

    def __init__(self, container_instance_dictionary):
        self.__dict__.update(container_instance_dictionary)
        self.EC2Instance = self.describe_ec2_instance()

    def describe_ec2_instance(self):
        reservation = ec2.describe_instances(
                InstanceIds=[self.ec2InstanceId])['Reservations'][0]
        instance = reservation['Instances'][0]
        return EC2Instance(instance)

    def inspect_docker(self, private_key, user_name=None):
        if not user_name:
            user_name = 'ec2-user'
        dns = self.EC2Instance.PublicDnsName
        cmd = 'ssh -l %s -i %s ' + \
              '%s curl -s http://localhost:51678/v1/tasks' % (
                      user_name, private_key, dns)
        self.docker = json.loads(check_output(cmd.split()))

    def to_dict(self):
        return {k: self.__dict__.get(k) for k in self.keys}


class EC2Instance(object):

    keys = ['Monitoring',
            'PublicDnsName',
            'State',
            'EbsOptimized',
            'LaunchTime',
            'PublicIpAddress',
            'PrivateIpAddress',
            'ProductCodes',
            'VpcId',
            'StateTransitionReason',
            'InstanceId',
            'ImageId',
            'PrivateDnsName',
            'KeyName',
            'SecurityGroups',
            'ClientToken',
            'SubnetId',
            'InstanceType',
            'NetworkInterfaces',
            'SourceDestCheck',
            'Placement',
            'Hypervisor',
            'BlockDeviceMappings',
            'Architecture',
            'RootDeviceType',
            'IamInstanceProfile',
            'RootDeviceName',
            'VirtualizationType',
            'Tags',
            'AmiLaunchIndex']

    def __init__(self, ec2_instance_dictionary):
        self.__dict__.update(ec2_instance_dictionary)

    def to_dict(self):
        return {k: self.__dict__.get(k) for k in self.keys}

    def __repr__(self):
        return self.to_dict()

    def __str__(self):
        return str('InstanceId: %s DNS: %s KeyName: %s' % (
            self.InstanceId, self.PublicIpAddress, self.__dict__.get('KeyName', None)))
