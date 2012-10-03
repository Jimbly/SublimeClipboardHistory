"""

Jimbly's Clipboard History (JCH)
Derived from Emacs-style kill ring commands from sublemacspro module,
blended with behaviors from Visual Assist's clipboard history.

"""

import sublime_plugin
import sublime
import functools
import string, re

class JchUtil:
    whitespace_regex = re.compile('^\s+$')
    trailing_cr_regex = re.compile('(.|\n)*\n\s*$')

    @classmethod
    def is_partial_copy(cls, view):
        ret = False
        for s in view.sel():
            if not s.empty():
                pre_select = view.substr(sublime.Region(view.full_line(s.begin()).begin(), s.begin()))
                if not JchUtil.whitespace_regex.match(pre_select):
                    ret = True
        return ret

class JchKillRingEntry:
    def __init__(self, text, partial):
        self.text = text
        self.partial = partial

class JchKillRing:
    def __init__(self):
        self.limit = 16
        self.buffer = []
        self.kill_points = []
        self.kill_id = 0
        self.expect_modification = False

    def seal(self):
        self.kill_id = 0

    def push(self, text, partial):
        """This method pushes the string to the kill ring.

        However, we do need some kind of sanitation to make sure
        we don't push too many white spaces."""

        sanitized = string.strip(text)
        if len(sanitized) == 0:
            return False

        obj = JchKillRingEntry(text, partial)
        self.buffer.insert(0, obj)
        if len(self.buffer) > self.limit:
            self.buffer.pop()
        return True

    def add(self, view, text, cut, partial):
        if (view.id() != self.kill_id) or not cut:
            # view has changed, ensure the last kill ring entry will not be
            # appended to
            self.kill_id = 0
            self.kill_points = []

        regions = []
        for s in view.sel():
            if s.empty():
                s = view.full_line(s.begin())
            regions.append(s.begin())

        if regions == self.kill_points:
            # Selection hasn't moved since the last kill, append/prepend the
            # text to the current entry
            self.buffer[0].text = self.buffer[0].text + text
            # Also update OS clipboard
            sublime.set_clipboard(self.buffer[0].text)
        else:
            # Create a new entry in the kill ring for this text
            if self.push(text, partial) and cut:
                self.kill_points = regions
                self.kill_id = view.id()

    def get(self, index):
        return self.buffer[index % self.limit]

    def isEmpty(self):
        return len(self.buffer) == 0

    def __len__(self):
        return len(self.buffer)

    def insert(self, view, edit, idx):

        if idx == -1:
            return

        # Doing a paste, don't append the next copy
        self.seal();

        regions = [r for r in view.sel()]
        regions.reverse()

        obj = self.get(idx)
        text = obj.text
        sublime.set_clipboard(text)

        if len(regions) > 1:
            # Multiple regions, let sublime handle it
            view.run_command("paste")
        else:
            for s in regions:
                # act like paste
                if text.find("\n") == -1 or not s.empty() or obj.partial:
                    # Regular text, no newline
                    # Or it was a partial-line copy, don't do full-line insert
                    num = view.insert(edit, s.begin(), text)
                    view.erase(edit, sublime.Region(s.begin() + num,
                        s.end() + num))
                else:
                    # Pasted text has a newline, insert it on the line before
                    #  the selection, instead of in the middle of the line
                    # Before that, check if pasting onto an empty line
                    if JchUtil.whitespace_regex.match(view.substr(view.full_line(s))):
                        # Only whitespace, just insert
                        pass
                    else:
                        # Some non-whitespace, if our text does not end with a
                        # carriage return, add one
                        if not JchUtil.trailing_cr_regex.match(text):
                            text = text + '\n'
                    view.insert(edit, view.line(s.begin()).begin(), text)

jch_kill_ring = JchKillRing()


class JchPasteChoiceCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        names = [string.strip(jch_kill_ring.get(idx).text)[:100] for idx in range(len(jch_kill_ring))]
        if len(names) > 0:
            self.view.window().show_quick_panel(names, functools.partial(jch_kill_ring.insert, self.view, edit))

class JchPasteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if jch_kill_ring.isEmpty() or sublime.get_clipboard() != jch_kill_ring.get(0).text:
            # Initial state, or OS clipboard updated, read from that
            self.view.run_command("paste")
        else:
            jch_kill_ring.insert(self.view, edit, 0)


class JchCopyCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        partial = JchUtil.is_partial_copy(self.view)
        self.view.run_command("copy")
        jch_kill_ring.add(self.view, sublime.get_clipboard(), False, partial)


class JchCutCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        partial = JchUtil.is_partial_copy(self.view)
        self.view.run_command("cut")
        jch_kill_ring.add(self.view, sublime.get_clipboard(), True, partial)
        jch_kill_ring.expect_modification = True


class JchEventListener(sublime_plugin.EventListener):
    # restore on load for new opened tabs or previews.
    def on_modified(self, view):
        # Really just care about catching "undo" events, so this prevents
        # Cut, Undo, Cut from appending to the buffer.
        if not jch_kill_ring.expect_modification:
            jch_kill_ring.kill_id = 0
        jch_kill_ring.expect_modification = False
