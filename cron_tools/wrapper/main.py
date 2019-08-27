import argparse
import subprocess
import select
import signal
import sys
import signalfd
import os
import getpass
import uuid
import socket
import time
import logging
from threading import Lock as NullLock


from cron_tools.wrapper.config import WrapperConfiguration
from cron_tools.common.models import AgentJob
from cron_tools.common.flock import FlockLock
from cron_tools.common.rpc_client import RPCClient

wrapper_argument_parser = argparse.ArgumentParser()
wrapper_argument_parser.add_argument(
    "-j", "--job-name", type=str, default=None, help="The name of the job being run."
)
wrapper_argument_parser.add_argument(
    "-L", "--lock-file", type=str, default=None, help="The file to flock to prevent other jobs from running."
)
wrapper_argument_parser.add_argument(
    "-Lt", "--lock-file-timeout", type=int, default=120,
    help="The timeout (in seconds) to wait for the lock file to clear, if used."
)
wrapper_argument_parser.add_argument(
    "-t", "--tag", type=str, nargs="+", default=None, help="Tags for the job."
)
wrapper_argument_parser.add_argument(
    "--capture-stdout", action="store_true", help="Capture stdout and log to the configured facility."
)
wrapper_argument_parser.add_argument(
    "--capture-stderr", action="store_true", help="Capture stderr and log to the configured facility."
)
wrapper_argument_parser.add_argument(
    "-f", "--config-file", type=str, default=None, help="The JSON configuration file for the wrapper script."
)
wrapper_argument_parser.add_argument(
    "wrapped_executable", type=str, nargs="+", help="The wrapped executable and its arguments."
)


wrapper_logger = logging.getLogger(__name__)


def read_at_most(fd, at_most_bytes, increment=8192):
    data_read = bytearray()
    delta = True
    remaining = at_most_bytes
    while delta and remaining > 0:
        delta = os.read(fd, min(remaining, increment))
        data_read.extend(delta)
    return data_read


def main(args=None, config=None):
    args = args or wrapper_argument_parser.parse_args()
    if config is not None:
        pass
    elif args.config_file:
        config = WrapperConfiguration.from_file(args.config_file)
    else:
        config = WrapperConfiguration.default()

    try:
        rpc_client = RPCClient(config.agent_socket_path)
        rpc_client.connect()
    except Exception:
        wrapper_logger.warning("Unable to connect to agent!")
        rpc_client = None
    read_fds = []
    sigchld_fd = signalfd.signalfd(-1, [signal.SIGCLD, signal.SIGCHLD], signalfd.SFD_CLOEXEC)
    signalfd.sigprocmask(signalfd.SIG_BLOCK, [signal.SIGCLD, signal.SIGCHLD])
    read_fds.append(sigchld_fd)

    if args.capture_stdout:
        stdout_read, stdout_write = os.pipe()
        read_fds.append(stdout_read)
    else:
        stdout_read = stdout_write = None

    if args.capture_stderr:
        stderr_read, stderr_write = os.pipe()
        read_fds.append(stderr_read)
    else:
        stderr_read = stderr_write = None

    end_time = None
    if args.lock_file is not None:
        lock_constructor = lambda: FlockLock.from_file(args.lock_file, args.lock_file_timeout)
    else:
        lock_constructor = NullLock
    
    with lock_constructor():
        start_time = time.time()
        process = subprocess.Popen(
            args.wrapped_executable, stdout=stdout_write, stderr=stdout_write
        )
        if stdout_write is not None:
            os.close(stdout_write)
        if stderr_write is not None:
            os.close(stderr_write)

        job = AgentJob(
            job_id=None,
            uuid=str(uuid.uuid4()),
            name=args.job_name or args.wrapped_executable[0],
            args=args.wrapped_executable,
            user=getpass.getuser(),
            host=socket.gethostname(),
            tags=args.tag,
            status_code=None,
            start_time=start_time,
            end_time=None,
            created_time=None,
            last_updated_time=None,
            last_updated_sequence_number=None
        )

        if rpc_client:
            rpc_client.handle_rpc_call(
                "add_new_job", {'raw_job_record': job.serialize()}
            )

        status_code = process.poll()
        current_read = True
        while status_code is None or current_read:
            current_read, _, _ = select.select(read_fds, [], [], 1.0 if status_code is None else 0)
            for read_fd in current_read:
                if read_fd == sigchld_fd and end_time is None:
                    end_time = time.time()
                if stdout_read is not None and read_fd == stdout_read:
                    raw_read_stdout = read_at_most(stdout_read, 1024*64)
                    read_stdout = raw_read_stdout.decode('utf-8', 'replace')
                    for line in read_stdout.split("\n"):
                        wrapper_logger.info("CAPTURED (STDOUT): {0}".format(line))
                if stderr_read is not None and read_fd == stderr_read:
                    raw_read_stderr = read_at_most(stderr_read, 1024 * 64)
                    read_stderr = raw_read_stderr.decode('utf-8', 'replace')
                    for line in read_stderr.split("\n"):
                        wrapper_logger.info("CAPTURED (STDERR): {0}".format(line))
            status_code = process.poll()

        if rpc_client:
            rpc_client.handle_rpc_call(
                "update_job_end_time_and_status_code",
                {
                    'job_uuid': job.uuid,
                    'job_end_time': end_time,
                    'job_status_code': status_code
                }
            )
        try:
            if rpc_client:
                rpc_client.disconnect()
        except BaseException:
            wrapper_logger.warning("Unable to close agent RPC connection!")
        sys.exit(status_code)
