
import common
setup_module = common.setup_module

import py.test

class TestString(object):
	def eval_test(self, value):
		print "eval", repr(value)

		m1 = common.Inter()
		a = m1.eval('"%s"' % value)

		assert a.type() in (str, unicode)
		assert a.topython() == value

	def passthru_test(self, value):
		print "passthru", repr(value)

		m1 = common.Inter()
		scm = m1.to_scheme(value)
	
		assert scm.type() in (str, unicode)
		assert scm.topython() == value

	def test_string(self):
		"""
		Checks that the eval returns strings for various input.
		"""
		strings = [ \
			 "", u"abc", u"t\n\t\n\r",  "a\0\0tl;\0a",
			u"", u"abc", u"t\n\t\n\r", u"a\0\0tl;\0a",
		]
		for value in strings:
			yield self.eval_test, value
			yield self.passthru_test, value
