from asyncore import dispatcher
import socket, asyncore
from asynchat import async_chat
from RoomClass import *

"""
ChatSession: 一个用户,用于维护一个用户的连接
ChatServer: Room,一个聊天室
"""

class ChatSession(async_chat):
	"""单会话, 负责与单用户通信"""
	def __init__(self, server, sock):
		# 一个用户(sock)要在一个Room(server)中
		super(ChatSession, self).__init__(sock)
		self.server = server
		self.set_terminator(b'\r\n') # 默认的终止符'\r\n', 注意是bytes
		# 该用户发的数据data
		self.data = []
		# self.bdata = []
		# 还未login, 暂无名字
		self.name = None

		# 进入LoginRoom (loginRoom是专门用于登录的)
		self.enter(LoginRoom(server))

	def enter(self, room):
		'进入一个房间'
		# 若已经进入了一个房间就更新
		try:
			cur = self.room
		except AttributeError:
			pass
		else:
			# 在一开始的那个房间退出(Room.remove())
			cur.remove(self)

		# 更新到新的房间
		self.room = room
		room.add(self)

	def collect_incoming_data(self, data):
		if data == b'\x08': # 如果接收到的是回车(backspace), 就去掉一个
			if self.data: 
				self.data.pop()
		else: 
			self.data.append(data.decode('utf-8'))
			
		print(''.join(self.data))
		print(self.data)

		print('Receive data #{}#'.format(str(data, 'utf-8')))

	def found_terminator(self):
		line = ''.join(self.data)
		self.data = []

		print('#'+line+'#')
		print(b'#'+bytes(line,'utf-8')+b'#')
		
		try:
			# 处理命令
			self.room.handle(self, line)
		except EndSession:
			# EndSession指logout
			self.handle_close()
			print(self.name, 'Logout')

	def handle_close(self):
		# print('close')
		async_chat.handle_close(self)
		# 进入logoutRoom, 专门处理logout
		self.enter(LogoutRoom(self.server))
		

class ChatServer(dispatcher): # 一个聊天室
	"""只有一个房间的聊天室"""
	def __init__(self, addr, name):
		super().__init__()
		self.create_socket()
		self.set_reuse_addr()
		self.bind(addr)
		self.listen(5)

		# 这个聊天室用户的users
		self.users = {}
		# 聊天室名字
		self.name = name
		# 主聊天室是ChatRoom
		self.main_room = ChatRoom(self)

	def handle_accept(self):
		conn, addr = self.accept()
		print('Connection attempt from', addr[0])
		# 有用户接进来, 创建个session
		ChatSession(self, conn)

if __name__ == '__main__':
	addr = '', 8888
	s = ChatServer(addr, 'Room 1')
	try:
		asyncore.loop()
	except KeyboardInterrupt as e:
		pass
