import re

def convert_percent_encoding(percent_encoded):
	"""
	Converts a percent-encoded string to unicode
	Input: 'page%20with%20space.html'
	Output: 'page with space.html'	
	"""
	decoded = percent_encoded.replace('%20', ' ')
	decoded = decoded.replace('%3A', ':')
	decoded = decoded.replace('%2F', '/')
	return decoded