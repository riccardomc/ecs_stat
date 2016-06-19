import subprocess
import json
import sys
from os import path


def fetch_docker_id(container, ssh_private_key=None, ssh_username='ec2-user'):
    inspection_url = 'http://localhost:51678/v1/tasks?taskarn='
    instance = container.containerInstance.EC2Instance

    if not ssh_private_key:
        ssh_private_key = guess_ssh_private_key(instance)

    cmd = 'ssh -l %s -i %s %s curl -s %s%s' % (
            ssh_username,
            ssh_private_key,
            instance.PublicIpAddress,
            inspection_url,
            container.task.taskArn)

    cmd_output = subprocess.check_output(cmd.split())
    containers = json.loads(cmd_output)['Containers']
    return filter(lambda x: x['Name'] == container.name, containers)[0]['DockerId']


def tail_logs(container, ssh_private_key=None, ssh_username='ec2-user'):
    instance = container.containerInstance.EC2Instance

    if not ssh_private_key:
        ssh_private_key = guess_ssh_private_key(instance)

    cmd = 'ssh -l %s -i %s %s docker logs --tail=10 --follow %s' % (
            ssh_username,
            ssh_private_key,
            instance.PublicIpAddress,
            fetch_docker_id(container, ssh_private_key, ssh_username))

    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    for line in iter(process.stdout.readline, ''):
        sys.stdout.write(line)


def print_ecs_tree(ecs):
    cluster_count = 0
    for cluster in ecs.clusters:
        print 'Cluster %d %s\n' % (cluster_count, cluster)
        cluster_count += 1
        service_count = 0
        for service in cluster.services:
            print ' Service %d %s \n' % (service_count, service)
            service_count += 1
            task_counter = 0
            for task in service.tasks:
                print '  Task %d %s' % (task_counter, task)
                task_counter += 1
                container_count = 0
                for container in task.containers:
                    print '   Container %d %s' % (container_count, container)
                    container_count += 1
                print


def guess_ssh_private_key(instance):
    guessed_private_key = '%s.pem' % instance.KeyName
    return path.expanduser(path.join('~/.ssh/', guessed_private_key))
