#!/usr/bin/env python

import argparse

from ecs_stat.ecs import ECS
from ecs_stat import ecs_actions

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='ECS status')
    parser.add_argument('--tail_logs', action='store', required=False,
                        help='<cluster_n>,<service_n>,<task_n>,<container_n>')

    args = parser.parse_args()

    my_ecs = ECS()
    if (args.tail_logs):
        [cluster, service, task, container] = args.tail_logs.split(',')
        container = my_ecs.get_container_by_branch(int(cluster),
                                                   int(service),
                                                   int(task),
                                                   int(container))
        print 'Going to tail logs for: %s' % container
        from time import sleep
        sleep(1)
        ecs_actions.tail_logs(container)
    else:
        ecs_actions.print_ecs_tree(my_ecs)
