class HandleError(Exception):
	def __init__(self, err_code, err_str):
		# *args is used to get a list of the parameters passed in
		(self.code, self.str) = self.getErrorCode(err_code, err_str)

	def getErrorCode(self, code, string):
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
		if int(code) == 6:
			code = str(6)
			string = "FTP " + string

		return (code, string)