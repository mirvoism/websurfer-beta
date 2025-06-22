import unittest
from skills.browser_mcp_skills import BrowserMCPSkills

class TestBrowserMCPSkills(unittest.TestCase):

    def setUp(self):
        self.browser = BrowserMCPSkills()

    def test_open(self):
        with self.assertLogs(level='INFO') as cm:
            self.browser.open("http://example.com")
            self.assertIn("Opening URL: http://example.com", cm.output[0])

    def test_click(self):
        with self.assertLogs(level='INFO') as cm:
            self.browser.click("button.submit")
            self.assertIn("Clicking element with selector: button.submit", cm.output[0])

    def test_type(self):
        with self.assertLogs(level='INFO') as cm:
            self.browser.type("input#username", "testuser")
            self.assertIn("Typing 'testuser' into element with selector: input#username", cm.output[0])

    def test_scroll(self):
        with self.assertLogs(level='INFO') as cm:
            self.browser.scroll(100, 200)
            self.assertIn("Scrolling to x=100, y=200", cm.output[0])

    def test_wait(self):
        with self.assertLogs(level='INFO') as cm:
            self.browser.wait(1)
            self.assertIn("Waiting for 1 seconds", cm.output[0])

    def test_extract_text(self):
        with self.assertLogs(level='INFO') as cm:
            text = self.browser.extract_text("div.content")
            self.assertIn("Extracting text from element with selector: div.content", cm.output[0])
            self.assertEqual(text, "Extracted text placeholder")

    def test_screenshot(self):
        with self.assertLogs(level='INFO') as cm:
            screenshot_path = self.browser.screenshot()
            self.assertIn("Taking screenshot", cm.output[0])
            self.assertEqual(screenshot_path, "screenshot_path.png")

if __name__ == '__main__':
    unittest.main()


