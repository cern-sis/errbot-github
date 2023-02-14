from errbot import BotPlugin, botcmd
from kubernetes import client, config

class Kubernetes(BotPlugin):
    """List resources on the production kubernetes cluster"""

    @arg_botcmd('namespace', type=str)
    def k8s_list_jobs_running(self, msg, namespace=None):
        config.load_kube_config()
        v1 = client.CoreV1Api()

        jobs = v1.list_namespaced_job(
            namespace,
            pretty='true',
            field_selector='status.phase=Running'
        )

        return jobs
