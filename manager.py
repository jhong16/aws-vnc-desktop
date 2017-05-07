import argparse
import boto3
import logging
import os
import sys


class Manager(object):
    UBUNTU_IMAGE_ID = 'AMI_IMAGE_ID'
    SSH_KEY_NAME = 'SSH_KEY_NAME'
    SECURITY_GROUP_ID = 'SECURITY_GROUP'

    def __init__(self):
        self._ec2 = boto3.client('ec2')

    def deploy(self, script_file):
        with open(script_file, 'r') as handler:
            result = self._ec2.run_instances(
                MinCount=1,
                MaxCount=1,
                KeyName=self.SSH_KEY_NAME,
                InstanceType='t2.micro',
                ImageId=self.UBUNTU_IMAGE_ID,
                SecurityGroupIds=[self.SECURITY_GROUP_ID],
                UserData=handler.read())

        instances = list(map(lambda instance: instance.get('InstanceId'), result.get('Instances')))
        logging.info('Deployed instances: %s', instances)

        waiter = self._ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=instances)
        logging.info('Instances are running: %s', instances)

        result = self._ec2.describe_instances(InstanceIds=instances)
        reservations = result.get('Reservations', [])
        for reservation in reservations:
            instances = reservation.get('Instances', [])
            for instance in instances:
                logging.info('  %s: %s', instance.get('InstanceId'), instance.get('PublicDnsName'))

    def destroy(self, instance_id):
        self._ec2.terminate_instances(InstanceIds=[instance_id])

    def list(self):
        logging.info('Available instances:')

        result = self._ec2.describe_instances()
        reservations = result.get('Reservations', [])
        for reservation in reservations:
            instances = reservation.get('Instances', [])
            for instance in instances:
                logging.info('  %s: %s', instance.get('InstanceId'), instance.get('PublicDnsName'))

    @staticmethod
    def main():
        logging.basicConfig(level=logging.INFO)
        parser = argparse.ArgumentParser()

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--deploy',
                           help='deploy an instance and run the provided script on start up')
        group.add_argument('--destroy', help='instance ID of the instance to terminate')
        group.add_argument('--list', action='store_true', help='list currently deployed instances')

        manager = Manager()
        args = parser.parse_args()
        status = os.EX_OK

        if args.deploy:
            if os.path.exists(args.deploy):
                manager.deploy(args.deploy)

            else:
                logging.error('script file does not exist')
                status = os.EX_OSFILE

        elif args.destroy:
            manager.destroy(args.destroy)

        elif args.list:
            manager.list()

        else:
            logging.error('invalid command')
            status = os.EX_USAGE

        return status


if __name__ == '__main__':
    sys.exit(Manager.main())
