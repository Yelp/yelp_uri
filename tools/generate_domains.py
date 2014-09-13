import urllib2

"""
This reads the IANA-maintained list of tlds and formats/outputs them for use
in the domains regular expression. All you have to do is replace the 
existing "domains = ..." line in search.py with this script's output.
"""

def create_regex(url='http://data.iana.org/TLD/tlds-alpha-by-domain.txt'):
	try:
		domains_data = urllib2.urlopen(url)
	except URLError as e:
		print "Could not get the domains from the given URL. Perhaps the IANA \
			   has changed the location of the file or it no longer exists."
		return e.reason

	domains = []

	for line in domains_data:
		if line[0] != '#': # Ignore the version number comment at start of file.
			domains.append(line)

	# Convert all newlines except the last one to '|', so 'foo\nbar\n' -> 'foo|bar'.
	domains_string = ''.join(domains).replace('\n', '|')[:-1]

	return 'domains = r"' + domains_string + '"'

if __name__ == "__main__":
	print create_regex()