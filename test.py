import json
import vk
# import vk_messages
tokens = [*json.load(open('../.IPoVKtoken')).items()]
token, gid = tokens[-1]

api = vk.Api(token=token)
# api = vk_messages.API()
# print(api.groups.getById())
# print(api.groups.getMembers(group_id=218708251, count=0))


