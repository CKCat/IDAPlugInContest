
An impressive 15 submissions were sent in for this year’s contest! As usual, many thanks to all the participants for their hard work. After having analyzed and deliberated about all the submitted plugins, our panel of judges selected the following winners:

First prize: [Tenet](#Tenet)

Second prize: [D-810](#D-810)

Third prize: [nmips](#nmips)

## Special mention
Aside from this year’s winners, we would like to give special credit to a couple of plugins that didn’t make it to the top three, but we feel deserve special attention:

- [IPyIDA](#ipyida): despite it being conceptually simple (“an alternative console specifically for scripting in Python”), can have a huge impact on productivity, for very little hassle
- [Yagi](#Yagi): during evaluation, we uncovered a few issues that got in the way of testing. Once those are solved, and support for more processors is added, Yagi will no doubt become a very handy tool for any reverser targeting less mainstream architectures

# Full list of submissions
*   [CollaRE](#CollaRE)
*   [CTO – Call Tree Overviewer](#CTO)
*   [D-810](#D-810)
*   [FunctionInliner](#FunctionInliner)
*   [IDA2Obj](#IDA2Obj)
*   [IDAPatternSearch](#IDAPatternSearch)
*   [IPyIDA](#ipyida)
*   [jside](#jside)
*   [nmips](#nmips)
*   [qscripts](#qscripts)
*   [RefHunter](#RefHunter)
*   [SyncReven](#SyncReven)
*   [Tenet](#Tenet)
*   [wilhelm](#wilhelm)
*   [Yagi](#Yagi)

# CollaRE

Martin Petran (Accenture)

[CollaRE-master-1.1.zip](PlugIn/CollaRE-master-1.1.zip)

https://github.com/Martyx00/CollaRE

> CollaRE enables collaboration using multiple reverse engineering tools for more complex projects where one tool cant provide all required features or where each member of the team prefers a different tool to do the job.

**Our opinion:** CollaRE facilitates collaborative reverse engineering. It centralizes the storage of the relevant files and allows users to open the databases with the corresponding tool. The CollaRE client comes with a set of plugins to import and export some data (comments and functions names) to share between the most common reverse engineering tools.

![](2021%20Plug-In%20Contest/CollaRE.png)


# CTO – Call Tree Overviewer


Hiroshi Suzuki (Internet Initiative Japan Inc.)

[CTO.zip](PlugIn/CTO.zip)

> CTO (Call Tree Overviewer) is an IDA Pro plugin for visualizing function call tree.  
> It can also summarize function information such as internal function calls, API calls, static linked library function calls, unresolved function calls, string references, structure member accesses, specific comments.  
> It can also find paths to/from a function, get arguments of unresolved calls by applying type information and collect other tools result such as ironstrings and fincrypt.py and so on.r

**Our opinion:** The CTO plugin offers a Proximity View style presentation of the function call graph. It lets you check paths between functions (and will produce new, dedicated graphs showing those). In addition, the plugin provides an alternative functions list featuring a summary of cross-references, string literals, and many other things (this information is also available as graph hints).

![](2021%20Plug-In%20Contest/cto.png)

# D-810

Boris Batteux (eShard)

[d810-master.zip](PlugIn/d810-master.zip)

https://gitlab.com/eshard/d810

> D-810 is a plugin which aims at removing several obfuscation layer (including MBA, opaque predicate and control flow flattening) during decompilation. It relies on the Hex-Rays microcode API to perform optimization during the decompilation. The plugin has been developed so that it is easy to use and can be easily extended and configured.

**Our opinion:** Inspired by Rolf Rolles’s [HexRaysDeob plugin](https://hex-rays.com/contests_details/contest2018/#hexraysdeob), the authors wrote a flexible and powerful deobfuscator that is easily extensible and configurable. The plugin comes with an impressive collection of rules implemented as Python classes, and a set of predefined templates (projects). Each project includes certain rules from the collection, and can be fine-tuned (add/remove rules) using a special dialog. The plugin offers a Python API that can be used to define rules, and offers helpers for finding patterns for new rules.  
A noticeable feature is Z3-based microcode optimization, which helps to write rules in a more generalized fashion.

![](2021%20Plug-In%20Contest/d810.png)

# FunctionInliner

Tomer Harpaz (Cellebrite Research Labs)

[FunctionInliner-master.zip](PlugIn/FunctionInliner-master.zip)

https://github.com/cellebrite-srl/FunctionInliner

> FunctionInliner is an IDA plugin that can be used to ease the reversing of binaries that have been space-optimized with function outlining (e.g. clang –moutline).

**Our opinion:** FunctionInliner offers an interesting approach to solving the problem posed by outlined functions (which causes issues ranging from “difficulty to read” to “erroneous decompilation”). In our testing, we uncovered a few glitches that should eventually be ironed out for a better user experience. Still, it’s already very useful, and shows a lot of potential. Inspiring!

![](2021%20Plug-In%20Contest/FunctionInliner.png)

# IDA2Obj
[Mickey Jin](https://twitter.com/patch1t) (Trend Micro)

[IDA2Obj-main.zip](PlugIn/IDA2Obj-main.zip)

https://github.com/jhftss/IDA2Obj

> IDA2Obj is a tool to implement SBI (Static Binary Instrumentation).

**Our opinion:** IDA2Obj offers a novel approach to instrumentation of closed-source binaries. It uses IDA to analyze the file, then dumps the database contents to relocatable object files with instrumentation hooks injected. The object files are then linked together with the instrumentation stub code, providing an instrumented binary equivalent in behavior to the original one. Currently it only implements support for x64 PE files, but the same approach could be extended to other platforms.

![](2021%20Plug-In%20Contest/IDA2Obj.png)

# IDAPatternSearch
David Lazar (Argus Cyber Security)

[IDAPatternSearch-main.zip](PlugIn/IDAPatternSearch-main.zip)

https://github.com/david-lazar/IDAPatternSearch

> The IDA Pattern Search plugin adds a capability of finding functions according to bit-patterns into the well-known IDA Pro disassembler based on Ghidra’s function patterns format. Using this plugin, it is possible to define new patterns according to the appropriate CPU architecture and analyze the target binary to find and define new functions in it.

**Our opinion:** IDAPatternSearch offers yet another angle to function recognition: it (partly) implements Ghidra’s function pattern format to look for functions that IDA didn’t spot during auto-analysis.While ideally IDA’s auto-analysis should uncover all functions, in practice that can fail, and having the ability to resuse already-existing list of patterns is a nice addition!

![](2021%20Plug-In%20Contest/IDAPatternSearch.png)

# IPyIDA
Marc-Etienne M.Léveillé (ESET)

[ipyida-master.zip](PlugIn/ipyida-master.zip)

https://github.com/eset/ipyida

> IPyIDA is a python-only solution to add an IPython console to IDA Pro. Use Shift-. to open a window with an embedded Qt console. You can then benefit from IPython’s autocompletion, online help, monospaced font input field, graphs, and so on.  
> You can also connect to the kernel outside of IDA using ipython console –existing.

**Our opinion:** IPyIDA offers the integration ot IPython kernel for IDAPython API. For newcomers and intermediate users of idapython it helps tremendously with autocompletion, documentation retrieval, and the ability to use Jupyter notebooks.

![](2021%20Plug-In%20Contest/ipyida.png)

# jside

David Zimmer

[IDA_JScript-master.zip](PlugIn/IDA_JScript-master.zip)

https://github.com/dzzie/IDA_JScript

http://sandsprite.com//blogs/index.php?uid=7&pid=361


> This plugin comes in two parts. There is a small IPC based server which sits in IDA and allows remote automation, and then there is an external Javascript IDE which supports intellisense, syntax highlighting, and a full on javascript debugger.

**Our opinion:** jside adds JavaScript scripting to IDA, including an IDE with syntax highlighting, auto-completion and interactive debugger. The project consists of a plugin which implements an RPC server in IDA (using windows messages), and an external IDE which can connect to any instance of IDA and control it using JavaScript.  
The minimalistic IDE is written in VB6 and works quite well with x64 IDA even on the latest Windows version. Several sample scripts are provided. Overall, an interesting approach to extending IDA, although currently limited to Windows.

![](2021%20Plug-In%20Contest/jside.png)

# nmips
[Leonardo Galli](https://twitter.com/galli_leo_) – [organizers](https://twitter.com/0rganizers)

[nmips-main.zip](PlugIn/nmips-main.zip)

https://github.com/0rganizers/nmips

> IDA plugin to enable nanoMIPS processor support. This is not limited to simple disassembly, but fully supports decompilation and even fixes up the stack in certain functions using custom microcode optimizers. It also supports relocations and automatic ELF detection (even though the UI might not show it, it kinda works). Debugging also works thanks to GDB, and it also does some other stuff, such as automatic switch detections.

**Our opinion:** The plugin adds nanoMIPS support to IDA. nanoMIPS is a new encoding of the MIPS instruction set not yet supported by IDA itself. The author cleverly reused existing MIPS instructions when possible and added custom ones for new instructions. The ELF loader extension automatically picks up the MIPS processor module for nanoMIPS files and the processor extension handles decoding (using the disassembler from binutils). The decompiler extension handles microcode generation for instructions not covered by the standard MIPS decompiler.  
This way nanoMIPS files can be opened in IDA (with a few warnings), providing disassembly and decompilation of nanoMIPS code.

![](2021%20Plug-In%20Contest/nmips.png)

# qscripts
Elias Bachaalany

[ida-qscripts.zip](PlugIn/ida-qscripts.zip)

https://github.com/0xeb/ida-qscripts

> QScripts is productivity tool and an alternative to IDA’s “Recent scripts” (Alt-F9) and “Execute Scripts” (Shift-F2) facilities. QScripts allows you to develop and run any supported scripting language (*.py; *.idc, etc.) from the comfort of your own favorite text editor as soon as you save the active script or any of its dependencies.

**Our opinion:** QScripts bridges IDA & your favourite text editor. It will be especially useful when writing complex scripts, or during heavy development. The fact that the list of scripts it knows of, is the same as the default “Recent scripts” widget, is also very comfortable since it lets you seamlessly switch between using QScripts and the built-in list.

![](2021%20Plug-In%20Contest/qscripts.png)

# RefHunter
Jiwon Choi

[RefHunter-main.zip](PlugIn/RefHunter-main.zip)

https://github.com/eternalklaus/RefHunter

> RefHunter find all references in simple and lightweighted manner.  
> – User-friendly view  
> – Runs without any 3rd-party application  
> – Runs without installing itself, it’s just portable.  
> – Analyze the function and show tiny little report for you!

**Our opinion:** RefHunter provides a summary of references for a function, which includes more information than the built-in “Function calls” widget (in particular: string literals, and data references). The summary is clickable (jumps to the address in the disassembly view) and can color-highlight the referring line.

![](2021%20Plug-In%20Contest/RefHunter.png)

# SyncReven
Cyrille Bagard

[SyncReven-master.zip](SyncReven-master.zip)

https://github.com/riskeco/SyncReven

> Axion is the main application of the Reven platform, which captures a time slice of a full system execution.  
> It can then be connected to many tools, including IDA Pro, for the analysis. A plugin to synchronize the IDA view from inside Reven already exists, but there is no plugin for the reverse direction yet.  
> Thus, the SyncReven plugin for IDA has been developed in order to reach two goals:  
> – synchronize the Axion current analysis window with some code opened in IDA;  
> – discover the Python API available for extending the IDA GUI features.  
> The aim of the plugin is to quickly target the currently running code for a given position (dynamic view), which can at first hold encrypted data for instance (static view).  
> As a side effect, browsing code inside IDA can also provide some kind of code coverage because the number of captures is displayed for each of the browsed instructions.

**Our opinion:** SyncReven lets the user connect IDA to a running Reven/Axion instance, in order to investigate a previously captured execution trace. In this setup, communication between IDA & Axion can go both ways: not only will IDA play the part of a visualizer/browser for an Axion session, it can also drive it and switch between “transitions” (i.e., instruction executions).

![](2021%20Plug-In%20Contest/SyncReven.png)

# Tenet
Markus Gaasedelen

[tenet-0.2.0.zip](PlugIn/tenet-0.2.0.zip)

https://github.com/gaasedelen/tenet/archive/refs/tags/v0.2.0.zip

> Tenet is an IDA Pro plugin which enables reverse engineers to explore execution traces of native code. It demonstrates how visualization can augment time-travel-debugging technologies to create more fluid controls for exploring the execution runtime. The basis of this work stems from the desire to research new methods of studying complex execution patterns in software.

**Our opinion:** It took us a few minutes to grow accustomed to Tenet’s user interface, but once we have familiarized ourselves with it, it becomes clear there’s a lot of potential behind this seemingly simple UI. We tried both the provided test case, and a custom one (we built the pin tracer on linux, and used it with `/bin/ls`), and were pleasantly surprised by the ease of use, and the responsiveness (the `/bin/ls` trace is ~30MB, which is certainly not huge, but not trivial neither).  
The author pitches this plugin as research in studying complex execution patterns in software, and his efforts are already paying off: a bunch of very nice ideas, wrapped in an easy-to-install, easy-to-use plugin!

![](2021%20Plug-In%20Contest/Tenet.png)

# wilhelm
Xinyu Zhuang

[wilhelm-main.zip](PlugIn/wilhelm-main.zip)

https://github.com/zerotypic/wilhelm

> wilhelm is a Python API that provides a better interface for working with Hex-Rays. In particular, I designed it with the IDAPython REPL (aka console) in mind; while it works fine in scripts, it’s meant to be used interactively to quickly automate some analysis while reversing.

**Our opinion:** wilhelm takes an interesting stab at solving the “working with decompilation data” issue, by offering an approach that (as far as we can tell) has not yet been explored yet: fetching data using XMLPath-style paths (so-called “wilpaths”). This contrasts with the more traditional tree traversal methods, and proves very useful in certain situations. A clever, and well-designed API!  
Historically, we at Hex-Rays have been concentrating on the availability & robustness of the core SDK APIs, and part of the reason for this, is that it’s unclear what the higher-level, more “Pythonic” APIs should look like. wilhelm offers interesting insights on what should ideally be there – to help with certain use-cases, at least.

![](2021%20Plug-In%20Contest/wilhelm.png)

# Yagi
Sylvain Peyrefitte (Airbus CERT)

[Yagi-1.1.0.zip](PlugIn/Yagi-1.1.0.zip)

https://github.com/airbus-cert/Yagi

> Yagi is a C++ plugin that includes the Ghidra decompiler into IDA 7.5 and 7.6.

**Our opinion:** This plugin integrates Ghidra’s decompiler into IDA. This is very interesting because it allows IDA to decompile more architectures than it supports out of the box. Yagi is able to invoke Ghidra’s core decompiler engine from within IDA itself, and displays the decompilation result in a custom interactive source viewer window. It even allows the user to interactively edit variable types, which is impressive.  
The plugin is sophisticated, but also clean. It has a lot of potential to be improved, and support for more architectures can be added easily. It definitely has a promising future!

![](2021%20Plug-In%20Contest/Yagi.png)


# Final notes

It is often the case, and this year was no exception: picking the winners was not a trivial task. Creativity, impact on the user base, ease of use, … are all axes on which the different plugins lie (and that we must consider). Some plugins will be immediately beneficial to use, while others are offering insights, ideas & inspiration for the future. We are glad this year’s entries were so spread across those various axes: it shows the reverse-engineering community is not done innovating and pushing the boundaries!

As always, many thanks to all the participants for their useful and interesting submissions. We are already looking forward to the next contest!

**The usual disclaimer**  
Please be aware that all files come from third parties. While we did our best to verify them, we cannot guarantee that they work as advertised, so use them at your own risk.  
For plugin support questions, please contact the authors directly.

Date: September 23, 2021
