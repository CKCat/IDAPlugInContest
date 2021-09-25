IDAStealth v1.1, created 11/14/2009, Jan Newger

CONTENTS OF THIS FILE
---------------------
  * Installation
  * Configuration
  * Usage
  * Known issues
  * Compiling
  * License
  * Changelog
  * Files


INSTALLATION
------------

a) IDAStealth
Copy both, HideDebugger.dll and IDAStealth.plw to your IDA plugin
directory.
Optionally, you can copy the provided HideDebugger.ini from
\sample_config to the IDAStealth configuration directory.
The example config includes a profile to hide the IDA debugger from the
newest version of Themida and ASProtect, respectively.

b) IDAStealthRemote
Copy both, IDAStealthRemote.exe and HideDebugger.dll to any directory.
No further installation is required.


CONFIGURATION
-------------

a) IDAStealth
The plugin is configured via the GUI, but you can also directly edit the
configuration file, which can be found at
C:\%APPDATA%\IDAStealth\HideDebugger.ini
The file is created upon startup, so it's not necessary to create it manually.

b) IDAStealthRemote
The server doesn't use any persistent configuration.
The stealth options are transmitted via TCP by the client side IDA plugin.
The TCP port can be configured via command line, i.e.
IDAStealthRemote.exe <port>


USAGE
-----

a) IDAStealth
The plugin is started as usual from the IDA plugins menu.
Note that this menu only appears if a file has been loaded into IDA.
The plugin automatically detects if IDA uses remote debugging and will
try to connect to the IDAStealthRemote server if that's the case.
The configuration options are automatically transferred, so the plugin
behaves exactly the same as if it was started with the local debugger.

IMPORTANT:
The option "Randomize driver name" should be used with caution!
When using this option, you must be sure to NOT have two or more instances
of this driver running at the same time, because there is no way for
IDAStealth to check if another instance already started this driver.
Otherwise your system might crash!

b) IDAStealthRemote
Just run the executable - everything else is fully automatic.


KNOWN ISSUES
------------

The plugin was only thoroughly tested on Windows XP SP3 32-bit.
It is designed only for 32-bit applications and doesn't work
with 64-bit applications.
However, it should also work with Vista/Win7 32-bit, but it wasn't
thoroughly tested on these systems.
In the remote scenario, the "Swallow DBG_PRINTEXCEPTION" technique
doesn't work.
The technique "Improved NtClose" doesn't work on 64-bit operating systems.


COMPILING
---------

Both projects are VS 2008 solutions and compile out of the box, given
that WTL[1], boost[2] and the IDA SDK headers are in the include path.
The RDTSC driver needs ddkbuild[3] and the Vista WDK[4]. The driver as well as
the plugin itself make use of the diStorm disassembler library[5].


LICENSE
-------

IDAStealth can be freely used without any restrictions.
For the diStorm license, see the accompanying license file.


CHANGELOG
---------

11/14/2009 - v1.1
  
  * Bugfix: OpenProcess failed on XP when started from a restricted user account
  * Bugfix: Bound imports directory is only cleared if necessary
  * Bugfix: DBG_PRINT DoS due to improper parameter checking
  * Bugfix: BSOD in RDTSC driver
  * Added: Remote debugging support
  * Added: Profiles support
  * Added: Exceptions with unknown exception code can be automatically passed
    to the debuggee
  * Added: Inline hooks can be forced to use absolute jumps
  * Improved: GUI has been redesigned to be more usable
  * Improved: AWESOME gfx :)
  * Changed: HideDebugger.ini is now located in the user's directory at:
    %APPDATA%\IDAStealth\HideDebugger.ini
  * Improved: Whole project compiles with WL4 and "treat warnings as error"

03/25/2009 - v1.0

  * Bugfix: API hook of GetThreadContext erroneously returned the complete
    context even if the flags specified that only the DRs should be returned.
    This interfered with newer Armadillo versions
  * Improved: GetTickCount hook now mimics the original API algorithm and
    allows for controlling the increasing delta
  * Added: RDTSC emulation driver with optional driver name randomization to
    increase stealthiness. Read these notes carefully before using this feature

09/15/2008 - v1.0 Beta 3

  * Bugfix: NtQuerySystemInformation hook possibly returned wrong error code
    when handling SystemKernelDebuggerInformation query
  * Bugfix: NtQueryObject hook mistakenly assumed that all object names are
    zero terminated strings
  * Improved: NtQueryInformationProcess considers the case that the debuggee
    itself might act as a debugger (see Tuts4You baord)
  * Improved: Exception triggered by NtClose is now blocked in the first place
  * Added: Countermeasures against anti-attach techniques

09/02/2008 - v1.0 Beta 2

  * Bugfix: Due to improper checking of input parameters in the
    NtQuerySystemInformation hook, the debugged process could raise an
	exception, finally unveiling the existence of IDA Stealth
  * Bugfix: Hiding of possibly existing kernel debugger now working correctly
  * Bugfix: Fake parent process and Hide IDA from process list are no longer
    mutual exclusive
  * Bugfix: NtQueryInformationProcess hook accepted too small input buffers
  * Bugfix: NtQueryInformationProcess hook erroneously assumed the process
    handle to be always that of the current process
  * Bugfix: Exception caused by closing an invalid handle is now properly
    hidden from the debugged process by using SEH or Vectored exception handling
  * Bugfix: NtSetInformationThread wasn't hooked at all due to a typo
  * Bugfix: Added checks to hook functions so they behave as expected when an
    invalid handle is passed. Affected functions:
    + NtSetInformationThread
    + SuspendThread
    + SwitchDesktop
    + NtTerminateThread
    + NtTerminateProcess
  * Bugfix: RtlGetVersion returned wrong platform ID and build number
  * Added: Console version of IDA is also hidden from process list

07/24/2008 - v1.0 Beta 1

  * Bugfix: Multiple minor bugfixes
  * Added: Fake OS version
  * Added: Disable NtTerminateThread/NtTerminateProcess

07/14/2008 - v1.0 Alpha 4

  * Bugfix: Injection of stealth dll could fail in some cases

07/13/2008 - v1.0 Alpha 3

  * Added: Multiple stealth techniques (OpenProcess, DBG_PRINTEXCEPTION,
    hardware breakpoint protection, hide IDA process and windows, to name but a few)
  * Improved: Overall stealth: xADT as well as Extreme Debugger Detector 0.5
    are unable to detect an attached debugger (except for RDTSC based tests and
	scanning the HDD for various tools)
  * Bugfix: Plugin didn't correctly de-register from debug callback and
    crashed with newly created databases

07/06/2008 - v1.0 Alpha 2

  * Bugfix: Injection of stealth dll failed if IMAGE_DIRECTORY_ENTRY_IAT of
    process was zero, so the plugin didn't work with most packed executables
  * Bugfix: NtQueryInformationProcess didn't work (CheckRemoteDebuggerPresent
    was implicitly affected)

07/04/2008 - v1.0 Alpha

  * First alpha release, some features still missing, needs testing, major bugs
  * Known Bugs:
    + Problems when modifying import directory of packed executables
	  (error 0xC000007B)


FILES
-----

\bin\IDAStealth       --- the plugin and the stealth dll
    \IDAStealthRemote --- the remote server and the stealth dll
\distorm              --- the license of the diStorm disassembler library
\sample_config        --- sample configuration file with pre defined profiles
                          for Themida and ASProtect
\src                  --- source code
    \HideDebugger     --- stealth dll
    \IDAStealth       --- IDA plugin
    \IDAStealthRemote --- remote server
    \IniFileAccess    --- utility class to read/write ini files
    \NInjectLib       --- library to inject dlls into a process
    \RDTSCEmu         --- kernel mode driver to fake RDTSC return values    


[1] WTL - http://wtl.sourceforge.net/
[2] boost - http://www.boost.org/
[3] ddkbuild - http://ddkwizard.assarbad.net/
[4] WDK - http://www.microsoft.com/whdc/devtools/wdk/default.mspx
[5] diStorm - http://ragestorm.net/distorm/