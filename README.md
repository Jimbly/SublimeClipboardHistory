SublimeClipboardHistory
=======================

Jimbly's Clipboard History plugin for Sublime Text 2.  A perfect blend
of behaviors from Visual Assist's clipboard history and emacs.

Some code derived from [sublemacspro](https://github.com/grundprinzip/sublemacspro).

Features:
* Paste from menu of previous clipboard entries
* Integrates with OS clipboard
* Multiple sequential cuts will append to most recent clipboard entry
* Full-line copy (when nothing is selected or an entire line is selected) pastes as full lines (similar to default Sublime/Visual Studio behaviors)

Installation
------------

1. Using [Package Control](http://wbond.net/sublime_packages/package_control), install "Jimbly's Clipboard Manager"

Or:

1. Open the Sublime Text 2 Packages folder using Preferences | Browse Packages...
2. Clone this repo

Usage
-----

By default, this plugin overrides the OS default cut, copy, paste, and shift-paste keys.
After copying or cutting, use shift+(paste) to access the clipboard history (e.g. shift+ctrl+v on Windows),
and select and previous element to paste it.

If you do not like the auto-assigned default keybinds:

1. [Let me know](https://github.com/Jimbly), I'll seriously consider having them not be part of the package, as I realize they may step on other keybinds.
2. Manually add the appropriate bindings so your cut/copy/paste keys call jch_cut/jch_copy/jch_paste, and add another key to call jch_paste_choice.
3. Remove the appropriate .sublime-keymap file from the JimblysClipboardHistory folder (e.g. "Default (Windows).sublime-keymap").

Command Reference
-----------------
`jch_cut`: Performs a cut, appending to the most recent cut if it appears to be from the same location, and populates both the OS clipboard and the clipboard history.

`jch_copy`: Performs a copy, populating both the OS clipboard and the clipboard history.

`jch_paste`: Pastes the most recently copied data, either from the clipboar history, or the OS clipboad if it was more recently modified.

`jch_paste_choice`: Shows a menu displaying the clipboard history allowing for a choice of what to paste.

Feedback and Future Plans
-------------------------

Do you not like some behavior?  Are you missing some feature another clipboard history plugin has?  Please let me
know, it would be easy to extend this with a few settings to adjust subtle behaviors.  The current behavior is
simply what grew organically from starting with an existing plugin, and any time I pressed one of the 4 relevant
hotkeys, if it did not do exactly what I expected (based primarily on my expectations coming from Visual Studio
and Visual Assist), I made it do so.
