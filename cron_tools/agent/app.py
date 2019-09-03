import argparse
import time
import signal
from threading import Thread, Event

from cron_tools.agent.config import AgentConfiguration
from cron_tools.agent.rpc_server import AgentUnixStreamRPCServer, attach_agent_functions
from cron_tools.agent.queries import SimpleConnectionPool, write_schema, remove_old_jobs, get_key_value_pair, \
    immediate_transaction_manager

agent_argument_parser = argparse.ArgumentParser()
agent_argument_parser.add_argument(
    "-f", "--config-file", type=str, default=None, help="JSON Configuration file for the agent."
)


def build_app(args=None, config=None):
    args = args or agent_argument_parser.parse_args()
    if config:
        pass
    elif args.config_file:
        config = AgentConfiguration.from_file(args.config_file)
    else:
        config = AgentConfiguration.default()

    server = AgentUnixStreamRPCServer(config.listen_socket_path)
    pool = SimpleConnectionPool(config.sqlite_database_path)
    write_schema(pool.get())
    pool.close()
    attach_agent_functions(
        server, pool
    )
    server_thread = Thread(target=server.serve_forever)
    shutdown_event = Event()
    last_cleanup_time = 0

    def run():
        server_thread.start()
        while not shutdown_event.is_set():
            time.sleep(3)
            current_time = time.time()
            if config.clean_up_policy['enabled'] \
                    and (current_time - last_cleanup_time) > config.clean_up_policy['check_interval_minutes']*60:
                conn = pool.get()
                with immediate_transaction_manager(conn) as t:
                    last_replicated_sequence_number = get_key_value_pair(
                        pool.get(), 'REPLICATION_LAST_SUCCESSFUL_SEQ_NUMBER', -1
                    )
                    remove_old_jobs(
                        t, config.clean_up_policy['replicated']['min_age_hours'], last_replicated_sequence_number
                    )
                    remove_old_jobs(
                        t, config.clean_up_policy['unreplicated']['min_age_hours']
                    )

        server.shutdown()
        server.server_close()

    def shutdown():
        shutdown_event.set()

    return run, shutdown


def main(args=None, config=None):
    run, shutdown = build_app(args=args, config=config)
    signal.signal(signal.SIGTERM, lambda *args, **kwargs: shutdown())
    signal.signal(signal.SIGHUP, lambda *args, **kwargs: shutdown())
    return run()
