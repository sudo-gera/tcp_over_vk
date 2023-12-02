import asyncio
import sys
import aiohttp
import logging
import argparse
import urllib.parse
import os
import itertools
import traceback

import object
import storage
import local_file
import api

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(
    level=LOGLEVEL,
    format='%(asctime)s %(levelname)s: %(message)s'
)


def forwarding(arg):
    urls = []
    try:
        while arg:
            for q in range(len(arg)):
                try:
                    assert not q or arg[q-1] == ':'
                    url = urllib.parse.urlsplit('http://' + arg[q:])
                    urld = object.Object(
                        host = '127.0.0.1' if url.port is None else url.hostname,
                        port = int(url.hostname) if url.port is None else url.port,
                    )
                    for surl in [
                        f'{urld.host}:{urld.port}',
                        f'[{urld.host}]:{urld.port}'
                    ]:
                        try:
                            url1 = urllib.parse.urlsplit('http://' + surl)
                            assert url1.port == urld.port
                            assert url1.hostname == urld.host
                            assert arg[q:] == surl or f'127.0.0.1:{arg[q:]}' == surl
                            break
                        except Exception:
                            pass
                    else:
                        raise Exception
                    urls.append(urld)
                    arg = arg[:q]
                    arg = arg[:-1]
                    break
                except Exception:
                    pass
            else:
                raise GeneratorExit
    except GeneratorExit:
        raise ValueError
    if len(urls) == 1:
        urls.append(object.Object(
            host = '127.0.0.1',
            port = urls[0].port,
        ))
    if len(urls) != 2:
        raise ValueError
    urls = urls[::-1]
    return urls

class int_or_commands:
    def __init__(self, *commands):
        self.commands = commands
    
    def __call__(self, arg):
        if arg in self.commands:
            return arg
        return int(arg)
    
    def __repr__(self):
        return f'{self.__class__.__name__}{self.commands!r}'

def parse_args(args = sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-L', action='append', type=forwarding, help='create forwarding to remote, [[[listen_host:]listen_port:]connect_host:]connect_port')
    parser.add_argument('-R', action='append', type=forwarding, help='create forwarding to local,  [[[listen_host:]listen_port:]connect_host:]connect_port')
    parser.add_argument('-l', action='append', type=forwarding, help='remove forwarding to remote, [[[listen_host:]listen_port:]connect_host:]connect_port')
    parser.add_argument('-r', action='append', type=forwarding, help='remove forwarding to local,  [[[listen_host:]listen_port:]connect_host:]connect_port')
    parser.add_argument('-g', type=int_or_commands('new', 'list'), help=f'group_id to act as, or a command (-g help to list them)')
    parser.add_argument('--meta', type=str, nargs='?')
    parser.add_argument('--set-default', action='store_true', help='set given group_id as default to act as, set by default if there is no group ids')
    parser.add_argument('connect_id', type=int, help='group_id to connect or a command')
    parser.add_argument('--list', action='store_true', help='list all forwardings')
    return parser.parse_args()

def get_token(group_id):
    if group_id is not None:
        print(f'There is no token for {group_id = } at https://vk.com/club{group_id}', file=sys.stderr)
    print('Follow instructions for creating token at https://http.cat/status/404', file=sys.stderr)
    token = input('paste your token here: ')
    return token

# async def setup_remote_file_id(api, group_id, local_storage):
#     if not local_storage.groups[group_id].remote_file_id:
#         for q in itertools.count(1):
#             try:
#                 s = await api.messages.get_conversation_members([], peer_id = 2000000000 + q)
#                 if len(s.items) == 1:
#                     local_storage.groups[group_id].remote_file_id = q
#                     break
#             except TabError as e:
#                 if e.msg.error_code == 10:
#                     break
#     if not local_storage.groups[group_id].remote_file_id:
#         s = await api.messages.create_chat(title=f'remote_file_id')
#         local_storage.groups[group_id].remote_file_id = s

async def process_args(args = sys.argv):
    async with aiohttp.ClientSession(trust_env=True) as session:
        args = parse_args(args)
        local_storage = storage.Storage(local_file.file())
        group_storage = None
        groups = local_file.list_groups()
        if args.g == 'list':
            for group_id in groups:
                if group_id == local_storage.default_group_id:
                    print(group_id, 'default')
                else:
                    print(group_id)
            exit(0)
        if local_storage.default_group_id and args.g is None:
            args.g = local_storage.default_group_id()
            logging.info(f'group_id = {args.g} is selected by default.')
        if not groups:
            args.set_default = True
        if groups and not local_storage.default_group_id and args.g is None:
            logging.error('There are several groups, but none is selected as default.')
            logging.error('Use -g list to list them.')
            logging.error('Use -g <id> to select one.')
            logging.error('Use -g new to add new one.')
            logging.error('Add --set-default to set it as default')
            exit(1)
        if isinstance(args.g, int):
            args.g = abs(args.g)
            group_storage = storage.Storage(local_file.file(args.g))
        if args.g == 'new' or not groups or not group_storage.token:
            token = get_token(args.g if isinstance(args.g, int) else None)
            API = api.API(session, token)
            if not (await API.groups.get_token_permissions()).mask & 4096:
                logging.error('Given token has no messages permission.')
                exit(1)
            args.g = (await API.groups.get_by_id()).groups[0].id
            logging.info(f'group_id for given token is {args.g}.')
            group_storage = storage.Storage(local_file.file(args.g))
            if not local_storage.default_group_id:
                local_storage.default_group_id = args.g
                logging.info(f'Selecting group_id = {args.g} as default for this device.')
            group_storage.token = token
        else:
            token = group_storage.token()
            API = api.API(session, token)
        assert isinstance(args.g, int)
        # if not group_storage.creator:
        #     group_storage.creator = ([q.id for q in (await API.groups.get_members([], filter='managers', group_id = args.g)).items if q.role == 'creator'] + [1])[0]
        # await setup_remote_file_id(API, args.g, local_storage)
        if args.set_default:
            local_storage.default_group_id = args.g
        return args

__all__ = ['process_args']

async def main():
    print(await process_args())

if __name__ == '__main__':
    asyncio.run(main())
