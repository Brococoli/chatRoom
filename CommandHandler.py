class CommandHandler():
	'类似于标准库中cmd.Cmd的简单命令处理程序'

	def unknown(self, session, cmd):
		'响应未知的命令'
		session.push(bytes('Unknown command: {}\r\n'.format(cmd), 'utf-8'))

	def handle(self, session, line): # type(line) is str
		'''
		处理给定会话中接收到的行
		handle会在本类中查找相应的命令并调用
		'''
		if not line.strip():
			return 

		# 分离命令
		parts = line.split(' ', 1)
		cmd = parts[0]

		try:
			line = parts[1].strip()
		except IndexError :
			line = ''

		# 查找处理程序
		methor = getattr(self, 'do_' + cmd, None)
		try:
			# 假设可调用
			methor(session, line)
		except TypeError:
			self.unknown(session, cmd)