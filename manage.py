
"""
>>> from plumbum import SshMachine
>>> remote = SshMachine("dev")
>>> hostname = remote["hostname"]
>>> with remote.cwd("/lib"):

1. LOCAL: push de la branch en cours vers local
    !!! nok car oblige commit, il faut rsync
2. REMOTE: se déplacer dans le clone pour faire un git pull
3. REMOTE: build si nécessaire ?
4. REMOTE: docker run

"""