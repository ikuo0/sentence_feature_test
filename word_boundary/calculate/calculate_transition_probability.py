
class Summarize:
    def count_transitions(self, text):
        """
        Count the number of transitions in the text.
        """
        transitions = 0
        for i in range(1, len(text)):
            if text[i] != text[i - 1]:
                transitions += 1
        return transitions