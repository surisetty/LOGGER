class HandleError(Exception):
	def __init__(self, err_code, err_str):
		# *args is used to get a list of the parameters passed in
		(self.code, self.str) = self.getErrorCode(err_code, err_str)

	def getErrorCode(self, code, string):
# FTP ERRORS

		# FTP username/password error
		if int(code) == 530:
			code = str(1)
			string = "FTP " + string

		# FTP path Error
		if int(code) == 550:
			code = str(2)
			string = "FTP " + string

		# FTP connection refused error
		if int(code) == 111:
			code = str(3)
			string = "FTP " + string

		# FTP file upload error
		if int(code) == 4:
			code = str(4)
			string = "FTP " + string

		# FTP file delete error
		if int(code) == 5:
			code = str(5)
			string = "FTP " + string

		# FTP No route to host (Error in IP address)
		if int(code) == 113:
			code = str(6)
			string = "FTP " + string

		# FTP Other Errors (Not defined anywhere)
		if int(code) == 7:
			code = str(7)
			string = "FTP " + string

# MODBUS Errors
		# RTU file read error
		if int(code) == 51:
			code = str(51)
			string = "MODBUS " + string

		# Modbus init error
		if int(code) == 52:
			code = str(52)
			string = "MODBUS " + string

		# Modbus read address error, Retrying
		if int(code) == 53:
			code = str(53)
			string = "MODBUS " + string

		# Modbus error in file conversion
		if int(code) == 54:
			code = str(54)
			string = "MODBUS " + string

		# Modbus error can't create file
		if int(code) == 55:
			code = str(55)
			string = "MODBUS " + string

# Logger Errors
		
		# cant read config json file
		if int(code) == 101:
			code = str(101)
			string = "LOGGER " + string

		# cant create threads
		if int(code) == 102:
			code = str(102)
			string = "LOGGER " + string
		return (code, string)