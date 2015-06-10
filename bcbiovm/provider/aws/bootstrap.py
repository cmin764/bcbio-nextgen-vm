"""
Helper class for updating or installing the bcbio and its requirements.
"""
import toolz

from bcbiovm.common import constant
from bcbiovm.provider import base


class Bootstrap(base.Bootstrap):

    """
    Update or install the bcbio and its requirements.
    """

    def __init__(self, provider, config, cluster_name, reboot, verbose):
        """
        :param provider:       an instance of
                               :class bcbiovm.provider.base.BaseCloudProvider:
        :param config:         elasticluster config file
        :param cluster_name:   cluster name
        :param reboot:         whether to upgrade and restart the host OS
        :param verbose:        increase verbosity
        """
        super(Bootstrap, self).__init__(provider, config, cluster_name,
                                        reboot, verbose)

    def gof3r(self):
        """Install gof3r."""
        return self._run_playbook(constant.PLAYBOOK.GOF3R)

    def nfs(self):
        """Mount encrypted NFS volume on master node and expose
        across worker nodes.
        """
        nfs_server = None
        nfs_clients = []

        with open(self._inventory_path) as file_handle:
            for line in file_handle.readlines():
                if line.startswith("frontend"):
                    nfs_server = line.split()[0]
                elif line.startswith("compute"):
                    nfs_clients.append(line.split()[0])

        def _extra_vars(cluster_config):
            """Extra variables to inject into a playbook."""
            return {
                "encrypted_mount": "/encrypted",
                "nfs_server": nfs_server,
                "nfs_clients": ",".join(nfs_clients),
                "login_user": toolz.get_in(["nodes", "frontend", "login"],
                                           cluster_config),
                "encrypted_device": toolz.get_in(
                    ["nodes", "frontend", "encrypted_volume_device"],
                    cluster_config, "/dev/xvdf")}

        return self._run_playbook(constant.PLAYBOOK.NFS, _extra_vars)
