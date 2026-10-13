"""Exact field Q(sqrt2, sqrt3, sqrt5, sqrt7) and exact record numbers in both certifiers (13 Oct 2026)."""
import os, subprocess, sys, unittest
from fractions import Fraction as Fr
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import multiquad as M


class TestField(unittest.TestCase):
    def test_arithmetic_and_signs(self):
        s2, s3, s5, s7 = (M.MQ.sqrt(k) for k in (2, 3, 5, 7))
        self.assertEqual((s2 + s3) ** 2, 5 + 2 * M.MQ.sqrt(6))
        self.assertEqual(s3 * s7, M.MQ.sqrt(21))
        x = 4 + 2 * s3 - s7 / 3
        self.assertEqual(x * x.inv(), 1)
        for e in ('sqrt7-sqrt2-sqrt3+1/5', 'sqrt5+sqrt7-sqrt2*sqrt3-2', '(1+sqrt7)/2-sqrt(5)', 'sqrt2*sqrt3*sqrt5*sqrt7-14.4'):
            y = M.parse(e)
            f = float(y); self.assertEqual(y.sign(), (f > 0) - (f < 0))
            lo, hi = y.enclose(120); self.assertTrue(lo <= Fr(f) + Fr(1, 10 ** 9) and hi >= Fr(f) - Fr(1, 10 ** 9))
        self.assertEqual(M.parse('sqrt(12)*sqrt(21)/6'), s7)
        self.assertEqual(M.num('3/4'), Fr(3, 4))

    def test_closed_forms(self):
        from records import closed_form
        self.assertEqual(closed_form(1 + 2 * 3 ** .5), '1 + 2√3')
        self.assertEqual(closed_form((2 ** .5 + 6 ** .5) / 2), '(√2 + √6)/2')
        self.assertEqual(closed_form((1 + 7 ** .5) / 2), '(1 + √7)/2')

    def test_certifiers_accept_exact_numbers(self):
        fx = os.path.join(ROOT, 'tests', 'fixtures')
        for script, rec in (('certify_general.py', 'exact_sqrt3_pr6incub_n18.json'),
                            ('certify_general.py', 'exact_sqrt7_cube_rotated.json'),
                            ('certify_exact.py', 'exact_sqrt7_cube_rotated.json')):
            r = subprocess.run([sys.executable, os.path.join(ROOT, script), os.path.join(fx, rec)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn('CERTIFIED', r.stdout)


if __name__ == '__main__':
    unittest.main()
