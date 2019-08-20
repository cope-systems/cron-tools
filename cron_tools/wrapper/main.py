import argparse
import subprocess
import select
import signal
import signalfd

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
    "wrapped_executable", type=str, nargs="+", help="The wrapped executable and its arguments."
)


def main():
    args = wrapper_argument_parser.parse_args()
    read_fds = []
    process = subprocess.Popen(args.wrapped_executable)

    sigchld_fd = signalfd.signalfd(-1, [signal.SIGCLD, signal.SIGCHLD], signalfd.SFD_CLOEXEC)
    signalfd.sigprocmask(signalfd.SIG_BLOCK, [signal.SIGCLD, signal.SIGCHLD])
    read_fds.append(sigchld_fd)

    status_code = process.poll()
    while status_code is None:
        current_read, _, _ = select.select(read_fds, [], [], 1.0)
        for read_fd in current_read:
            if read_fd == sigchld_fd:
                pass
        status_code = process.poll()
