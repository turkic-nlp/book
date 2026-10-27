"""Boundary tests for the measurement, with deliberately non-additive encoding."""
import unittest
from exp_chunk_content import pack_sentences

class PackingTests(unittest.TestCase):
    def test_joined_text_is_reencoded(self):
        counts={'aa':2,'bb':2,'cc':2,'aa bb':3,'aa bb cc':7}
        result=pack_sentences(['aa','bb','cc'],counts.__getitem__,4)
        self.assertEqual([(c['sentences'],c['tokens'],c['final_tail']) for c in result],[(2,3,0),(1,2,1)])
        self.assertEqual([(c['first_row'],c['last_row']) for c in result],[(1,2),(3,3)])
    def test_space_counts_toward_budget(self):
        result=pack_sentences(['aa','bb'],len,4)
        self.assertEqual([c['sentences'] for c in result],[1,1])
    def test_exact_boundary_and_final_tail(self):
        result=pack_sentences(['aa','bb','cc'],len,5)
        self.assertEqual(result[0]['tokens'],5)
        self.assertEqual(result[0]['words'],2)
        self.assertEqual(sum(c['sentences'] for c in result),3)
        self.assertEqual(sum(c['final_tail'] for c in result),1)
    def test_rejects_oversize_instead_of_truncating(self):
        with self.assertRaisesRegex(ValueError,'exceeding'):pack_sentences(['abcdef'],len,5)
    def test_rejects_empty_or_unclean_input(self):
        for ss in ([],[''],[' abc']):
            with self.assertRaises(ValueError):pack_sentences(ss,len,5)

if __name__=='__main__':unittest.main()
