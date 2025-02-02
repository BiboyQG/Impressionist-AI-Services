import unittest
from app.services.services import yes_or_no, extract_reply_from_prompt, prettify_conversation_history, retrieve_relevant_knowledge_from_personal_kb

class TestYesOrNo(unittest.TestCase):
    def test_yes(self):
        self.assertTrue(yes_or_no("yes"))
        self.assertTrue(yes_or_no(" yes "))
        self.assertTrue(yes_or_no("Yes"))
        self.assertTrue(yes_or_no("Yes."))
        # self.assertTrue(yes_or_no("yes!"))

    def test_no(self):
        self.assertFalse(yes_or_no("no"))
        self.assertFalse(yes_or_no(" yesn"))
        self.assertFalse(yes_or_no("ye s"))


class TestExtractReplyFromPrompt(unittest.TestCase):
    def test_extract_reply(self):
        prompt = """
        <Reply>
Hey there! How's it going? I've had a pretty chill day so far, just catching up on some reading. What about you? Anything interesting happening today?
</Reply>"""
        self.assertEqual(extract_reply_from_prompt(prompt), "Hey there! How's it going? I've had a pretty chill day so far, just catching up on some reading. What about you? Anything interesting happening today?")

    def test_no_reply_tag(self):
        prompt = "Hello, how are you?"
        self.assertEqual(extract_reply_from_prompt(prompt), "")



class TestPrettifyConversationHistory(unittest.TestCase):
    def test_prettify(self):
        conversation_history = [
            {"role": "user", "content": "Hello", "sender": "user"},
            {"role": "assistant", "content": "Hi, how can I help you?", "sender": "Rizky"},
            {"role": "system", "content": "System message", "sender": "system"},
        ]
        expected_output = "user: Hello\nRizky: Hi, how can I help you?"
        self.assertEqual(prettify_conversation_history(conversation_history, "Rizky"), expected_output)


class TestRetrieveRelevantKnowledge(unittest.TestCase):
    def test_retrieve_knowledge(self):
        self.assertEqual(retrieve_relevant_knowledge_from_personal_kb(), "")

if __name__ == '__main__':
    unittest.main()
