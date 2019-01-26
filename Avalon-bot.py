# Works with Python 3.4
# Written by Fomalhaut

import discord
import asyncio
import random
import datetime
import numpy

client = discord.Client()

@client.event
@asyncio.coroutine
def on_ready():
	print("I'm in.")
	print("Bot name: " + client.user.name)
	print("User ID: " + client.user.id)
	print("--------")

def game_master(txt_chan, player_list):
	global player_roles
	global assassinate_flag
	player_n = len(player_list)
	captain = random.randint(1, 1000) % player_n
	gamestate = [0, 0, 0, 0, captain]	#round counter, team counter, success counter, failure counter, captain indicator
	roles =  {0:"忠臣", 1:"派西维尔", 2:"梅林", 3:"奥伯伦", 4:"刺客", 5:"莫甘娜", 6:"莫德雷德的爪牙", 7:"莫德雷德"}
	yield from client.send_message(txt_chan, "############游戏开始############\n请所有玩家查看身份！")
	player_roles = assign_roles(player_list)
	bandit_list_str = ""
	overwrite = discord.PermissionOverwrite()
	overwrite.read_messages = True
	overwrite.send_messages = True
	for i in range(player_n):
		yield from client.send_message(player_list[i], "----------------------------------------------------\n你是" + str(i + 1) + "号玩家\n你的角色是：" + roles[player_roles[i]])
		yield from client.change_nickname(player_list[i], str(i+1) + ":" + player_list[i].display_name)
		if player_roles[i] == 1:
			yield from client.send_message(player_list[i], str(player_roles.index(2) + 1) + "号和" + str(player_roles.index(5) + 1) + "号之间有一个是梅林，另一个是莫甘娜")
		elif player_roles[i] == 2:
			yield from client.send_message(player_list[i], "莫德雷德阵营有: " + " ".join([str(player_roles.index(i)) for i in player_roles if i > 2 and i < 7]) + "号玩家")
		elif player_roles[i] > 3:
			bandit_list_str += (str(i + 1) + "号玩家：" + roles[player_roles[i]] + "  ")
			yield from client.send_message(player_list[i], "请在莫德雷德阵营专用频道确认同伴" )
			yield from client.edit_channel_permissions(client.get_channel(BANDIT_CHANNEL_ID), player_list[i], overwrite)
	yield from client.send_message(client.get_channel(BANDIT_CHANNEL_ID), "----------------------------------------------------\n本局游戏中莫德雷德阵营有（奥伯伦不可见）：\n" + bandit_list_str)
	yield from asyncio.sleep(5)
	while True:
		yield from client.send_message(txt_chan, "================\n              第" + str(gamestate[0] + 1) + "回合\n================")
		team_member = yield from team_maker(txt_chan, player_list, gamestate)
		if team_member is None:
			break
		else:
			if (yield from quest(txt_chan, player_list, gamestate, player_roles, team_member)) != 0:
				break
			else:
				gamestate[0] += 1
	while assassinate_flag == True:
		yield from asyncio.sleep(1)
	overwrite.read_messages = False
	overwrite.send_messages = False
	player_roles_str = ""
	for i in range(player_n):
		yield from client.change_nickname(player_list[i], player_list[i].display_name.split(":")[1])
		player_roles_str += (str(i + 1) + "号玩家：" + player_list[i].display_name + "：" + roles[player_roles[i]] + "\n")
		if player_roles[i] > 3:
			yield from client.edit_channel_permissions(client.get_channel(BANDIT_CHANNEL_ID), player_list[i], overwrite)
	player_roles = None
	yield from client.send_message(txt_chan, "----------------------------------------------------\n本局的演员表为：\n" + player_roles_str)
	yield from client.send_message(txt_chan, "############游戏结束############")
			
def assign_roles(player_list):
	# roles =  {0:"忠臣", 1:"派西维尔", 2:"梅林", 3:"奥伯伦", 4:"刺客", 5:"莫甘娜", 6:"莫德雷德的爪牙", 7:"莫德雷德"}
	global player_roles
	random.seed(datetime.time())
	player_n = len(player_list)
	# for test only
	if player_n == 1:
		player_roles = [4, ]
	elif player_n == 2:
		player_roles = [2, 4]
	elif player_n == 3:
		player_roles = [0, 0, 0]
	elif player_n == 4:
		player_roles = [0, 0, 0, 0]		
	#end test
	elif player_n == 5:
		player_roles = [0, 1, 2, 4, 5]
	elif player_n == 6:
		player_roles = [0, 0, 1, 2, 4, 5]
	elif player_n == 7:
		player_roles = [0, 0, 1, 2, 3, 4, 5]
	elif player_n == 8:
		player_roles = [0, 0, 0, 1, 2, 4, 5, 6]
	elif player_n == 9:
		player_roles = [0, 0, 0, 0, 1, 2, 4, 5, 7]
	elif player_n == 10:
		player_roles = [0, 0, 0, 0, 1, 2, 3, 4, 5, 7]
	else:
		return
	random.shuffle(player_roles)
	return player_roles
		
def team_size(player_n, round):
	rules = [[1, 1, 1, 1, 1], [2, 2, 2, 2, 2], [3, 3, 3, 3, 3], [4, 4, 4, 4, 4], [2, 3, 2, 3, 3], [2, 3, 4, 3, 4], [2, 3, 3, 4, 4], [3, 4, 4, 5, 5], [3, 4, 4, 5, 5], [3, 4, 4, 5, 5]]
	return rules[player_n][round]

def timer(msg_channel = None, msg_rcpt = None, timelapse = 0, input = False, prompt = True, not_in_assassinate = True):
	global assassinate_flag
	now = datetime.datetime.now()
	dt = datetime.timedelta(seconds = timelapse + 1)
	while (now + dt - datetime.datetime.now()).days >= 0:
		if input == True:
			try:
				if assassinate_flag == not_in_assassinate:
					return
				msg = yield from client.wait_for_message(channel = msg_channel, author = msg_rcpt, timeout = 1, content = None)
				if msg.content is not None:
					if msg.content == "pass":
						return
					else:
						return  msg.content
			except:
				pass
		if prompt == True:
			if (now + dt - datetime.datetime.now()).seconds == 5:
				yield from client.send_message(msg_channel or msg_rcpt, "还剩5秒")
	yield from client.send_message(msg_channel or msg_rcpt, "时间到！")
	return None
			
def team_maker(txt_chan, player_list, gamestate):
	global assassinate_flag
	player_n = len(player_list)
	while True:
		captain = gamestate[4]
		if gamestate[1] >= player_n:
				yield from client.send_message(txt_chan, "组队次数已用尽\n莫德雷德阵营胜利！")
				return
		yield from client.send_message(txt_chan, ">>>>第" + str(gamestate[1] + 1) + "轮组队")
		yield from client.send_message(txt_chan, "本轮的队长是" + str(captain + 1) + "号玩家")
		yield from client.send_message(txt_chan, "请队长选择" + str(team_size(player_n-1, gamestate[0])) + "名玩家做任务（号码之间用空格分开）：")
		team_member = yield from timer(msg_channel = txt_chan, msg_rcpt = player_list[captain], timelapse = 15, input = True)
		if assassinate_flag == True:
				return
		if team_member is None or len(team_member.split(" ")) != team_size(player_n-1, gamestate[0]) or not all([i.isdigit() and int(i) >0 and int(i) <= player_n for i in team_member.split(" ")]):
			yield from client.send_message(txt_chan, "由于" + str(captain + 1) + "号玩家没有组队，自动进入下一轮\n----------------------------------------------------")
			gamestate[1] += 1
			gamestate[4] = (captain + 1) % player_n
			continue
		else:
			yield from client.send_message(txt_chan, "本轮的队伍是：" + str(team_member))
		for i in range(player_n):
			active_player = (captain + i) % player_n
			yield from client.server_voice_state(player_list[active_player], mute = False)
			yield from client.send_message(txt_chan, str(active_player + 1) + "号玩家开始发言")
			yield from timer(msg_channel = txt_chan, msg_rcpt = player_list[active_player], timelapse = 15, input = True)
			yield from client.server_voice_state(player_list[active_player], mute = True)
			if assassinate_flag == True:
				return
		yield from client.server_voice_state(player_list[captain], mute = False)
		yield from client.send_message(txt_chan, "队长总结发言")
		yield from timer(msg_channel = txt_chan, msg_rcpt = player_list[captain], timelapse = 15, input = True)
		if assassinate_flag == True:
				return
		yield from client.server_voice_state(player_list[captain], mute = True)
		yield from client.send_message(txt_chan, "----------------------------------------------------\n请队长确认队伍成员（号码之间用空格分开）：")
		new_team_member = yield from timer(msg_channel = txt_chan, timelapse = 15, input = True)
		if assassinate_flag == True:
				return
		if new_team_member is None or len(new_team_member.split(" ")) != team_size(player_n-1, gamestate[0]) or not all([i.isdigit() and int(i) >0 and int(i) <= player_n for i in new_team_member.split(" ")]):
			new_team_member = team_member
		yield from client.send_message(txt_chan, "本轮的队伍是：" + str(new_team_member))
		rejections = yield from team_vote(txt_chan, player_n)
		if rejections == -1:
			return
		if rejections >= player_n/2:
			yield from client.send_message(txt_chan, "组队失败！请下一位玩家组队\n----------------------------------------------------")
			gamestate[1] += 1
			gamestate[4] = (captain + 1) % player_n
		else:
			yield from client.send_message(txt_chan,  "组队成功！请在队玩家做任务\n----------------------------------------------------\n等待中...")
			gamestate[1] = 0
			gamestate[4] = (captain + 1) % player_n
			return new_team_member
	
def team_vote(txt_chan, player_n):
	global assassinate_flag
	yield from client.send_message(txt_chan, "----------------------------------------------------\n下面开始投票，请在公屏确认是否同意该队伍：(y/n)")
	approve_list = []
	reject_list = []
	i = 0
	while i < player_n:
		msg = yield from client.wait_for_message(channel = txt_chan, content = None)
		if assassinate_flag == True:
			return -1
		if msg.content == "y" or msg.content == "Y":
			approve_list.append(str(msg.author).split("#")[0])
			i += 1
		elif msg.content == "n" or msg.content == "N":
			reject_list.append(str(msg.author).split("#")[0])
			i += 1
		else:
			continue
	if approve_list:
		yield from client.send_message(txt_chan,  " ".join(approve_list) + " 同意组队")
	else:
		yield from client.send_message(txt_chan,  "无人同意组队")
	if reject_list:
		yield from client.send_message(txt_chan,  " ".join(reject_list) + " 拒绝组队")
	else:
		yield from client.send_message(txt_chan,  "无人拒绝组队")
	return len(reject_list)


def quest(txt_chan, player_list, gamestate, player_roles, team_member):
	global assassinate_flag
	player_n = len(player_list)
	team_member_list = [player_list[int(i)-1] for i in team_member.split(" ")]
	fails = 0
	if player_n >= 7 and gamestate[0] == 3:
		fails_needed = 2
	else:
		fails_needed = 1
	for i in range(len(team_member_list)):
		yield from client.send_message(team_member_list[i], "----------------------------------------------------\n这是本局游戏第" + str(gamestate[0] + 1) + "回合的任务\n请选择是否让任务成功：(y/n)")
	for i in range(len(team_member_list)):
		msg = yield from client.wait_for_message(author = team_member_list[i], content = None)
		if assassinate_flag == True:
			return -1
		if msg.content == "y" or msg.content == "Y":
			pass
		elif msg.content == "n" or msg.content == "N":
			fails += 1
		else:
			i -= 1
			continue
		yield from client.send_message(team_member_list[i], "收到！")
	if fails < fails_needed:
		gamestate[2] += 1
		yield from client.send_message(txt_chan,  "任务成功！已累计成功" + str(gamestate[2]) + "次，失败" + str(gamestate[3]) + "次")
	else:
		gamestate[3] += 1
		yield from client.send_message(txt_chan,  "任务失败！已累计成功" + str(gamestate[2]) + "次，失败" + str(gamestate[3]) + "次")
	if gamestate[2] == 3:
		assassinate_flag = True
		yield from assassinate(txt_chan, player_list, player_roles)
		return 1
	elif gamestate[3] == 3:
		yield from client.send_message(txt_chan,  "莫德雷德阵营胜利！")
		return 1
	return 0
	
def assassinate(txt_chan, player_list, player_roles):
	global assassinate_flag
	if assassinate_flag == False:
		yield from client.send_message(txt_chan,  "错误调用刺杀功能")
		raise
	if 4 not in player_roles:
		yield from client.send_message(txt_chan,  "不存在刺客")
		assassinate_flag = False
		return
	if 2 not in player_roles:
		yield from client.send_message(txt_chan,  "不存在梅林")
		assassinate_flag = False
		return
	yield from asyncio.sleep(3)
	yield from client.send_message(txt_chan,  "刺杀梅林阶段，莫德雷德阵营自由讨论")
	for i in range(len(player_roles)):	# 奥伯伦的编号是3
		if player_roles[i] > 3:
			yield from client.server_voice_state(player_list[i], mute = False)
		else:
			yield from client.server_voice_state(player_list[i], mute = True)
	yield from timer(msg_chan = txt_chan, timelapse = 15, not_in_assassinate = False)
	yield from client.send_message(txt_chan,  "请刺客决定刺杀目标")
	time_limit = 10
	while True:
		now = datetime.datetime.now()
		target = yield from timer(msg_channel = txt_chan, author = player_list[player_roles.index(4)], timelapse = time_limit, input = True, not_in_assassinate = False)
		if target is None:
			target = player_roles.index(4)
			break
		if target.isdigit():			
			if int(target) <= len(player_list) and int(target) > 0:
				break
		yield from client.send_message(txt_chan,  "无效目标\n请输入要刺杀的玩家号码")
		time_limit -= (datetime.datetime.now()- now).seconds
	if int(target) == player_roles.index(2):
		yield from client.send_message(txt_chan,  "刺杀成功！\n莫德雷德阵营胜利！")
	else:
		yield from client.send_message(txt_chan,  "刺杀失败！\n亚瑟王阵营胜利！")
	assassinate_flag = False

def assassinate_trigger(txt_chan, player_list):
	global player_roles
	global assassinate_flag
	if player_roles is None:
		yield from client.send_message(txt_chan, "不在游戏中！")
		return
	elif assassinate_flag == True:
		yield from client.send_message(txt_chan, "正在刺杀梅林中...")
		return
	else:
		assassinate_flag = True
		yield from assassinate(txt_chan, player_list, player_roles)	
					
@client.event
@asyncio.coroutine
def on_message(msg):
	if msg.author == client.user:	# we do not want the bot to reply to itself
		return
	if not msg.content.startswith("$"):
		return
	txt_chan = client.get_channel(TXT_CHANNEL_ID)
	player_list = client.get_channel(VOICE_CHANNEL_ID).voice_members
	if msg.content.startswith("$disconnect"):
		yield from client.close()
		return
	elif msg.content.startswith("$assassinate"):
		if True:
		#try:
			yield from assassinate_trigger(txt_chan, player_list)
		#except:
		#	yield from client.send_message(txt_chan, "############游戏中断############")
		#finally:
			for i in range(len(player_list)):
				yield from client.server_voice_state(player_list[i], mute = False)
		return
	elif msg.content.startswith("$play"):
		if len(player_list) == 0:
			yield from client.send_message(txt_chan, "玩家数量不足！")
			return
		if len(player_list) > 10:
			yield from client.send_message(txt_chan, "玩家数量过多！")
			return
		for i in range(len(player_list)):
			yield from client.server_voice_state(player_list[i], mute = True)
		if True:
		#try:
			yield from game_master(txt_chan, player_list)
		#except:
		#	yield from client.send_message(txt_chan, "############游戏中断############")
		#finally:
			for i in range(len(player_list)):
				yield from client.server_voice_state(player_list[i], mute = False)
			return
	else:
		yield from client.send_message(msg.channel, "Invalid command!")


if __name__ == "__main__":
	TOKEN = "NTM2MjgyMTg3MTU5MzA2MjQw.DyUdgQ.2da55cMZtXhZWlFQsadqylSBMMo"
	TXT_CHANNEL_ID = "536306066858704916"
	VOICE_CHANNEL_ID = "372573024869810177"
	BANDIT_CHANNEL_ID = "537024584579416075"
	assassinate_flag = False #global variable for assassinate_trigger() to check if it is in game
	player_roles = None	#global variable to pass player role list to assassinate_trigger()
	client.run(TOKEN)

