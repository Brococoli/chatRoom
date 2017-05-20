from CommandHandler import CommandHandler

class EndSession(Exception):
	"""专门处理logout"""
	pass

class Room(CommandHandler):
	'''
	包括一个或多个用户(回话) 的泛型环境. 负责基本的命令处理和广播
	包含4个基本的命令: add, remove, broadcast, logout
	'''
	def __init__(self, server): # 一个server一个room
		self.server = server
		# 一个Room会有多个用户(session), 一个session即一个用户
		self.sessions = []

	def add(self, session):
		'一个会话已进入房间'
		self.sessions.append(session)

	def remove(self, session):
		'一个会话已离开房间'
		self.sessions.remove(session)

	def broadcast(self, message):
		'向房间中所有会话发送一行message'
		for session in self.sessions:
			session.push(bytes(message, 'utf-8'))

	def do_logout(self, session, line):
		'响应logout命令'
		raise EndSession

class LoginRoom(Room):
	'''
	连接上的用户准备的房间
	有以下命令: login, logout
	'''

	def add(self, session):
		super().add(session) # 调用父类方法, 不用重新写了
		# 问候新用户
		self.broadcast('Welcome to {}\r\n'.format(self.server.name))

	def unknown(self, session, cmd):
		'除了login, logout 命令都是未知命令'
		# 向该用户发信息
		session.push('Please log in\nUse "login <nick>"\r\n'.encode('utf-8'))

	def do_login(self, session, line):
		name = line.strip()

		if not name:
			session.push('Please enter a name.\r\n'.encode('utf-8'))
		elif name in self.server.users:
			session.push('The name "{}" is taken.\nPlease try again.\r\n'.format(name).encode('utf-8'))
		else:
			session.name = name
			session.enter(self.server.main_room)

class ChatRoom(Room):
	'''
	为多用户互相聊天准备的房间
	有以下命令: say, login, say, look, who
	'''

	def add(self, session):
		'告诉所有人有新用户进入'
		self.broadcast(session.name + ' has entered the room.\r\n')
		self.server.users[session.name] = session
		Room.add(self, session)

	def remove(self, session):
		Room.remove(self, session)
		# 告诉所有人有用户离开
		self.broadcast(session.name + ' has left the room.\r\n')

	def do_say(self, session, message):
		self.broadcast(session.name + ': ' + message + '\r\n')

	def do_look(self, session, line):
		session.push('The following are in this room.\r\n'.encode('utf-8'))
		for other in self.sessions:
			session.push((other.name + '\r\n').encode('utf-8'))

	def do_who(self, session, line):
		'查看登录的人,并不是在这个房间'
		session.push('The following are logged in:\r\n'.encode('utf-8'))
		for name in self.server.users:
			session.push((name + '\r\n').encode('utf-8'))

class LogoutRoom(Room):
	"""
	为单用户准备的简单房间,只用于将用户名从服务器移除
	有以下命令: logout
	"""
	def add(self, session):
		try:
			del self.server.users[session.name]
		except KeyError:
			pass


		



		