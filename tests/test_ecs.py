from ecs_stat import ecs
import boto3
import moto
from sure import expect


@moto.mock_ecs
def test_list_clusters():
    # Given
    ecs_mock = boto3.client('ecs')
    ecs_mock.create_cluster(clusterName='test_cluster_name')
    myECS = ecs.ECS()

    # When
    cluster_names = myECS.list_clusters()

    # Then
    expect(cluster_names).to.contain('test_cluster_name')


@moto.mock_ecs
def test_describe_clusters():
    # Given
    ecs_mock = boto3.client('ecs')
    ecs_mock.create_cluster(clusterName='test_cluster_name')
    myECS = ecs.ECS()

    # When
    clusters = myECS.describe_clusters()

    # Then
    clusters.should.have.length_of(1)
