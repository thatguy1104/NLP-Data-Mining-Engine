

class RabinKarp:

	def __init__(self):
		self.prime = 101

	def search(self, text, pattern):
		d = 255
		text_length = len(text)
		text_hash = 0
		pattern_length = len(pattern)
		pattern_hash = 0
		found = False
		h = pow(d, pattern_length - 1)

		# Find hash value of the pattern and the initial 'window' hash value from the text
		for i in range(0, pattern_length):
			pattern_hash = (d*pattern_hash + ord(pattern[i])) % self.prime
			text_hash = (d*text_hash + ord(text[i])) % self.prime

		for i in range(0, text_length - pattern_length + 1):
			if pattern_hash == text_hash:
				for j in range(0, pattern_length):
					if text[i + j] != pattern[j]:
						break
				j = j + 1
				if j == pattern_length:
					print("Found at index", i)
					found = True

			if i < text_length - pattern_length:
				text_hash = (
					d*(text_hash - h*(ord(text[i]))) + ord(text[i+pattern_length])) % self.prime
				if text_hash < 0:
					text_hash = text_hash + self.prime

		if not found:
			print("Not found any matches")
