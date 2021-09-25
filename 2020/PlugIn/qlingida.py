# Cross Platform and Multi Architecture Advanced Binary Emulation Framework Plugin For IDA
# Built on top of Unicorn emulator (www.unicorn-engine.org)
# Learn how to use? Please visit https://docs.qiling.io/en/latest/ida/

UseAsScript = True

import sys
import collections
import time
import struct
import logging
from enum import Enum

# Qiling
from qiling import *
from qiling.const import *
from qiling.arch.x86_const import reg_map_32 as x86_reg_map_32
from qiling.arch.x86_const import reg_map_64 as x86_reg_map_64
from qiling.arch.x86_const import reg_map_misc as x86_reg_map_misc
from qiling.arch.x86_const import reg_map_st as x86_reg_map_st
from qiling.arch.arm_const import reg_map as arm_reg_map
from qiling.arch.arm64_const import reg_map as arm64_reg_map
from qiling.arch.mips_const import reg_map as mips_reg_map
from qiling.utils import ql_get_arch_bits
from qiling import __version__ as QLVERSION
from qiling.os.filestruct import ql_file

# IDA Python SDK
from idaapi import *
from idc import *
from idautils import *
import idc
import ida_ua
import ida_idaapi
import ida_funcs
import ida_nalt
import idautils
import ida_xref
import ida_kernwin
import ida_ida
import ida_bytes
import ida_segment
import ida_name
import ida_gdl
import ida_frame
import ida_idp
import ida_auto
import ida_netnode
# PyQt
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (QPushButton, QHBoxLayout)

QilingHomePage = 'https://www.qiling.io'
QilingStableVersionURL = 'https://raw.githubusercontent.com/qilingframework/qiling/master/qiling/__version__.py'
logging.basicConfig(level=logging.INFO, format='[%(levelname)s][%(module)s:%(lineno)d] %(message)s')

class Colors(Enum):
    Blue = 0xE8864A
    Pink = 0xC0C0FB
    White = 0xFFFFFF
    Black = 0x000000
    Green = 0xd3ead9
    Gray = 0xd9d9d9
    Beige = 0xCCF2FF

class IDA:
    def __init__(self):
        pass
    
    @staticmethod
    def get_function(addr):
        return ida_funcs.get_func(addr)
    
    @staticmethod
    def get_function_start(addr):
        return IDA.get_function(addr).start_ea

    @staticmethod
    def get_function_end(addr):
        return IDA.get_function(addr).end_ea
    
    @staticmethod
    def get_function_framesize(addr):
        return IDA.get_function(addr).frsize

    @staticmethod
    def get_function_name(addr):
        return ida_funcs.get_func_name(addr)

    @staticmethod
    def get_functions():
        return [IDA.get_function(func) for func in idautils.Functions()]

    @staticmethod
    def set_color(addr, what, color):
        return idc.set_color(addr, what, color)

    @staticmethod
    def color_block(bb, color):
        for i in range(bb.start_ea, bb.end_ea):
            IDA.set_color(i, idc.CIC_ITEM, color)

    # note:
    # corresponds to IDA graph view
    # a good example to iterate the graph
    # https://github.com/idapython/src/blob/bc9b51b1c70083815a574a57b7a783698de3698d/examples/core/dump_flowchart.py
    # arg can be a function or a (start, end) tuple or an address in the function
    @staticmethod
    def get_flowchart(arg):
        if type(arg) is int:
            func = IDA.get_function(arg)
            if func is None:
                return None
            return ida_gdl.FlowChart(func)
        return ida_gdl.FlowChart(arg)

    @staticmethod
    def get_block(addr):
        flowchart = IDA.get_flowchart(addr)
        for bb in flowchart:
            if bb.start_ea <= addr and addr < bb.end_ea:
                return bb
        return None

    @staticmethod
    def block_is_terminating(bb):
        # fcb_ret: has a retn instruction in the end
        # fcb_noret: in most cases, exit() is called
        # fcb_indjump: jmp $eax
        if (bb.type == ida_gdl.fcb_ret or bb.type == ida_gdl.fcb_noret or
                (bb.type == ida_gdl.fcb_indjump and len(list(bb.succs())) == 0)):
            return True
        for b in bb.succs():
            if b.type == ida_gdl.fcb_extern:
                return True
        return False

    @staticmethod
    def get_starting_block(addr):
        flowchart = IDA.get_flowchart(addr)
        if flowchart is None:
            return None
        func = IDA.get_function(addr)
        for bb in flowchart:
            if bb.start_ea == func.start_ea:
                return bb
        return None
    
    @staticmethod
    def get_terminating_blocks(addr):
        flowchart = IDA.get_flowchart(addr)
        return [bb for bb in flowchart if IDA.block_is_terminating(bb)]

    @staticmethod
    def get_prev_head(addr, minea=0):
        return ida_bytes.prev_head(addr, minea)

    @staticmethod
    def get_segments():
        r = []
        seg = ida_segment.get_first_seg()
        while seg is not None:
            r.append(seg)
            seg = ida_segment.get_next_seg(seg.start_ea)
        return r
    
    @staticmethod
    def get_segment_name(s):
        return ida_segment.get_segm_name(s)

    @staticmethod
    def get_segment_by_name(name):
        return ida_segment.get_segm_by_name(name)
    
    @staticmethod
    def __addr_in_seg(addr):
        segs = IDA.get_segments()
        for seg in segs:
            if addr < seg.end_ea and addr >= seg.start_ea:
                return seg
        return None

    # note: accept name and address in the segment
    @staticmethod
    def get_segment(arg):
        if type(arg) is int:
            return IDA.__addr_in_seg(arg)
        else: # str
            return IDA.get_segment_by_name(arg)

    @staticmethod
    def get_segment_start(arg):
        seg = IDA.get_segment(arg)
        if seg is not None:
            return seg.start_ea
        return None
    
    @staticmethod
    def get_segment_end(arg):
        seg = IDA.get_segment(arg)
        if seg is not None:
            return seg.end_ea
        return None

    @staticmethod
    def get_segment_perm(arg):
        seg = IDA.get_segment(arg)
        if seg is not None:
            return seg.perm # RWX e.g. 0b101 = R + X
        return None
    
    @staticmethod
    def get_segment_type(arg):
        seg = IDA.get_segment(arg)
        if seg is not None:
            return seg.type # 0x1 SEG_DATA 0x2 SEG_CODE See doc for details
        return None

    @staticmethod
    def get_instruction(addr):
        r = ida_ua.print_insn_mnem(addr)
        if r == "":
            return None
        return r

    # immidiate value
    @staticmethod
    def get_operand(addr, n):
        return (idc.get_operand_type(addr, n), idc.get_operand_value(addr, n))

    # eax, ecx, etc
    @staticmethod
    def print_operand(addr, n):
        return idc.print_operand(addr, n)

    @staticmethod
    def get_instruction_size(addr):
        return ida_bytes.get_item_size(addr)

    @staticmethod
    def get_instructions_count(begin, end):
        p = begin
        cnt = 0
        while p < end:
            sz = IDA.get_instruction_size(p)
            cnt += 1
            p += sz
        return cnt

    @staticmethod
    def get_name(addr):
        return ida_name.get_name(addr)
    
    @staticmethod
    def get_name_address(name, addr=0):
        return ida_name.get_name_ea(addr, name)

    @staticmethod
    def get_bytes(addr, l):
        return ida_bytes.get_bytes(addr, l)

    @staticmethod
    def get_byte(addr):
        return ida_bytes.get_byte(addr)

    @staticmethod
    def get_word(addr):
        return ida_bytes.get_word(addr)

    @staticmethod
    def get_dword(addr):
        return ida_bytes.get_dword(addr)
    
    @staticmethod
    def get_qword(addr):
        return ida_bytes.get_qword(addr)

    @staticmethod
    def get_xrefsto(addr, flags=ida_xref.XREF_ALL):
        return [ref.frm for ref in idautils.XrefsTo(addr, flags)]

    @staticmethod
    def get_xrefsfrom(addr, flags=ida_xref.XREF_ALL):
        return [ref.frm for ref in idautils.XrefsFrom(addr, flags)]

    @staticmethod
    def get_input_file_path():
        return ida_nalt.get_input_file_path()
    
    @staticmethod
    def get_info_structure():
        return ida_idaapi.get_inf_structure()

    @staticmethod
    def get_main_address():
        return IDA.get_info_structure().main
    
    @staticmethod
    def get_max_address():
        return IDA.get_info_structure().max_ea
    
    @staticmethod
    def get_min_address():
        return IDA.get_info_structure().min_ea

    @staticmethod
    def is_big_endian():
        return IDA.get_info_structure().is_be()

    @staticmethod
    def is_little_endian():
        return not IDA.is_big_endian()

    @staticmethod
    def get_filetype():
        info = IDA.get_info_structure()
        ftype = info.filetype
        if ftype == ida_ida.f_MACHO:
            return "macho"
        elif ftype == ida_ida.f_PE or ftype == ida_ida.f_EXE or ftype == ida_ida.f_EXE_old: # is this correct?
            return "pe"
        elif ftype == ida_ida.f_ELF:
            return "elf"
        else:
            return None

    @staticmethod
    def get_ql_arch_string():
        info = IDA.get_info_structure()
        proc = info.get_procName()
        result = None
        if proc == "metapc":
            result = "x86"
            if info.is_64bit():
                result = "x8664"
        elif "mips" in proc:
            result = "mips"
        elif "arm" in proc:
            result = "arm32"
            if info.is_64bit():
                result = "arm64"
        # That's all we support :(
        return result
    
    @staticmethod
    def get_current_address():
        return ida_kernwin.get_screen_ea()

    # return (?, start, end)
    @staticmethod
    def get_last_selection():
        return ida_kernwin.read_range_selection(None)
    
    # Use with skipcalls
    # note that the address is the end of target instruction
    # e.g.:
    # 0x1 push eax
    # 0x4 mov eax, 0
    # call get_frame_sp_delta(0x4) and get -4.
    @staticmethod
    def get_frame_sp_delta(addr):
        return ida_frame.get_sp_delta(IDA.get_function(addr), addr)
    
    @staticmethod
    def patch_bytes(addr, bs):
        return ida_bytes.patch_bytes(addr, bs)
    
    @staticmethod
    def fill_bytes(start, end, bs = b'\x90'):
        return ida_bytes.patch_bytes(start, bs*(end-start))
    
    @staticmethod
    def nop_selection():
        _, start, end = IDA.get_last_selection()
        return IDA.fill_bytes(start, end)
    
    @staticmethod
    def fill_block(bb, bs=b'\x90'):
        return IDA.fill_bytes(bb.start_ea, bb.end_ea, bs)

    @staticmethod
    def assemble(ea, cs, ip, use32, line):
        return ida_idp.assemble(ea, cs, ip, use32, line)

    @staticmethod
    def create_data(ea, dataflag, size, tid=ida_netnode.BADNODE):
        return ida_bytes.create_data(ea, dataflag, size, tid)

    @staticmethod
    def create_bytes_array(start, end):
        return IDA.create_data(start, ida_bytes.byte_flag(), end-start)

    @staticmethod
    def create_byte(ea, length, force=False):
        return ida_bytes.create_byte(ea, length, force)

    @staticmethod
    def perform_analysis(start, end, final_pass=True):
        return ida_auto.plan_and_wait(start, end)

### View Class

class QlEmuRegView(simplecustviewer_t):
    def __init__(self, ql_emu_plugin):
        super(QlEmuRegView, self).__init__()
        self.hooks = None
        self.ql_emu_plugin = ql_emu_plugin

    def Create(self):
        title = "QL Register View"
        if not simplecustviewer_t.Create(self, title):
            return False

        self.menu_update = 1

        class Hooks(UI_Hooks):
            class PopupActionHandler(action_handler_t):
                def __init__(self, subview, menu_id):
                    action_handler_t.__init__(self)
                    self.subview = subview
                    self.menu_id = menu_id

                def activate(self, ctx):
                    self.subview.OnPopupMenu(self.menu_id)

                def update(self, ctx):
                    return AST_ENABLE_ALWAYS

            def __init__(self, form):
                UI_Hooks.__init__(self)
                self.form = form

            def finish_populating_widget_popup(self, widget, popup):
                if self.form.title == get_widget_title(widget):
                    attach_dynamic_action_to_popup(widget, popup, action_desc_t(None, "Edit Register", self.PopupActionHandler(self.form, self.form.menu_update),  None, None, -1))     
        
        if self.hooks is None:
            self.hooks = Hooks(self)
            self.hooks.hook()

        return True

    def SetReg(self, addr, ql:Qiling):
        arch = ql.archtype
        if arch == "":
            return
        
        #clear
        self.ClearLines()

        view_title = COLSTR("Reg value at { ", SCOLOR_AUTOCMT)
        view_title += COLSTR("IDA Address:0x%X | QL Address:0x%X" % (addr, addr - self.ql_emu_plugin.qlemu.baseaddr + get_imagebase()), SCOLOR_DREF)
        # TODO: Add disass should be better
        view_title += COLSTR(" }", SCOLOR_AUTOCMT)
        self.AddLine(view_title)
        self.AddLine("")

        reglist = QlEmuMisc.get_reg_map(ql)
        line = ""
        cols = 3
        reglist = [reglist[i:i+cols] for i in range(0,len(reglist),cols)]
        for regs in reglist:
            for reg in regs:
                line += COLSTR(" %4s: " % str(reg), SCOLOR_REG)
                regvalue = ql.reg.read(reg)
                if arch in [QL_ARCH.X8664, QL_ARCH.ARM64]:
                    value_format = "0x%.16X"
                else:
                    value_format = "0x%.8X"
                line += COLSTR(str(value_format % regvalue), SCOLOR_NUMBER)
                # TODO: ljust will looks better
            self.AddLine(line)
            line = ''
        self.AddLine(line)
        self.Refresh()

    def OnPopupMenu(self, menu_id):
        if menu_id == self.menu_update:
            self.ql_emu_plugin.ql_chang_reg()

    def OnClose(self):
        if self.hooks:
            self.hooks.unhook()
            self.hooks = None
        self.ql_emu_plugin.ql_close_reg_view()

class QlEmuStackView(simplecustviewer_t):
    def __init__(self, ql_emu_plugin):
        super(QlEmuStackView, self).__init__()
        self.ql_emu_plugin = ql_emu_plugin

    def Create(self):
        title = "QL Stack View"
        if not simplecustviewer_t.Create(self, title):
            return False
        return True

    def SetStack(self, ql:Qiling):
        self.ClearLines()
        if ql is None:
            return
        
        sp = ql.reg.arch_sp
        self.AddLine('')
        self.AddLine(COLSTR('  Stack at 0x%X' % sp, SCOLOR_AUTOCMT))
        self.AddLine('')

        arch = ql.archtype
        if arch == "":
            return

        reg_bit_size = ql_get_arch_bits(arch)
        reg_byte_size = reg_bit_size // 8
        value_format = '% .16X' if reg_bit_size == 64 else '% .8X'

        for i in range(-30, 30):
            clr = SCOLOR_DREF if i < 0 else SCOLOR_INSN
            cur_addr = (sp + i * reg_byte_size)
            line = ('  ' + value_format + ': ') % cur_addr
            try:
                value = ql.mem.read(cur_addr, reg_byte_size)
                value, = struct.unpack('Q' if reg_bit_size == 64 else 'I', value)
                line += value_format % value
            except Exception:
                line += '?' * reg_byte_size * 2

            self.AddLine(COLSTR(line, clr))  

    def OnClose(self):
        self.ql_emu_plugin.ql_close_stack_view()

class QlEmuMemView(simplecustviewer_t):
    def __init__(self, ql_emu_plugin, addr, size):
        super(QlEmuMemView, self).__init__()
        self.ql_emu_plugin = ql_emu_plugin
        self.viewid = addr
        self.addr = addr
        self.size = size
        self.lastContent = []

    def Create(self, title):
        if not simplecustviewer_t.Create(self, title):
            return False
        return True

    def SetMem(self, ql:Qiling):
        self.ClearLines()

        if ql is None:
            return

        try:
            memory = ql.mem.read(self.addr, self.size)
        except:
            return

        size = len(memory)

        view_title = COLSTR("  Memory at [ ", SCOLOR_AUTOCMT)
        view_title += COLSTR("0x%X: %d byte(s)" % (self.addr, size), SCOLOR_DREF)
        view_title += COLSTR(" ]", SCOLOR_AUTOCMT)
        self.AddLine(str(view_title))
        self.AddLine("")
        self.AddLine(COLSTR("                0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F", SCOLOR_AUTOCMT))

        startAddress = self.addr
        line = ""
        chars = ""
        get_char = lambda byte: chr(byte) if 0x20 <= byte <= 0x7E else '.'

        if size != 0:
            for x in range(size):
                if x%16==0:
                    line += COLSTR(" %.12X: " % startAddress, SCOLOR_AUTOCMT)
                if len(self.lastContent) == len(memory):
                    if memory[x] != self.lastContent[x]:
                        line += COLSTR(str("%.2X " % memory[x]), SCOLOR_VOIDOP)
                        chars += COLSTR(get_char(memory[x]), SCOLOR_VOIDOP)
                    else:
                        line += COLSTR(str("%.2X " % memory[x]), SCOLOR_NUMBER)
                        chars += COLSTR(get_char(memory[x]), SCOLOR_NUMBER)
                else:
                    line += COLSTR(str("%.2X " % memory[x]), SCOLOR_NUMBER)
                    chars += COLSTR(get_char(memory[x]), SCOLOR_NUMBER)

                if (x+1)%16==0:
                    line += "  " + chars
                    self.AddLine(line)
                    startAddress += 16
                    line = ""
                    chars = ""

            # add padding
            tail = 16 - size%16
            if tail != 0:
                for x in range(tail): line += "   "
                line += "  " + chars
                self.AddLine(line)

        self.Refresh()
        self.lastContent = memory

    def OnClose(self):
        self.ql_emu_plugin.ql_close_mem_view(self.viewid)

### Dialog Class
class QlEmuMemDialog(Form):
    def __init__(self):
        Form.__init__(self, r"""STARTITEM {id:mem_addr}
BUTTON YES* Add
BUTTON CANCEL Cancel
Show Memory Range
Specify start address and size of new memory range.
<##Address\::{mem_addr}> <##Size\::{mem_size}>
<##Comment\::{mem_cmnt}>
""", {
        'mem_addr': Form.NumericInput(swidth=20, tp=Form.FT_HEX),
        'mem_size': Form.NumericInput(swidth=10, tp=Form.FT_DEC),
        'mem_cmnt': Form.StringInput(swidth=41)
    })

class QlEmuSetupDialog(Form):
    def __init__(self):
        Form.__init__(self, r"""STARTITEM {id:path_name}
BUTTON YES* Start
BUTTON CANCEL Cancel
Setup Qiling
<#Select Rootfs to open#Rootfs path\:        :{path_name}>
<#Custom script path   #Custom script path\: :{script_name}>
""", {
        'path_name': Form.DirInput(swidth=50),
        'script_name': Form.DirInput(swidth=50),
    })
 
class QlEmuSaveDialog(Form):
    def __init__(self):
        Form.__init__(self, r"""STARTITEM {id:path_name}
BUTTON YES* Save
BUTTON CANCEL Cancel
Save Path
<#Save to#Path\::{path_name}>
""", {
        'path_name': Form.FileInput(swidth=50, save=True),
    })    

class QlEmuLoadDialog(Form):
    def __init__(self):
        Form.__init__(self, r"""STARTITEM {id:file_name}
BUTTON YES* Load
BUTTON CANCEL Cancel
Load File
<#Load From#File\::{file_name}>
""", {
        'file_name': Form.FileInput(swidth=50, open=True)
    })   

class QlEmuAboutDialog(Form):
    def __init__(self, version):
        super(QlEmuAboutDialog, self).__init__(
            r"""STARTITEM 0
BUTTON YES* Open Qiling Website
Qiling:: About
            {FormChangeCb}
            Qiling IDA plugin v%s with Qiling Framework v%s.
            Author:
            Ziqiao Kong,
            Chenxu Wu,
            Qiling Team.
            Qiling is released under the GPL v2.
            Find more info at https://www.qiling.io
            """ %(version, QLVERSION), {
            'FormChangeCb': self.FormChangeCb(self.OnFormChange),
            })

        self.Compile()

    # callback to be executed when any form control changed
    def OnFormChange(self, fid):
        if fid == -2:   # Goto homepage
            import webbrowser
            # open Keypatch homepage in a new tab, if possible
            webbrowser.open(QilingHomePage, new = 2)

        return 1

class QlEmuUpdateDialog(Form):
    def __init__(self, version, message):
        super(QlEmuUpdateDialog, self).__init__(
            r"""STARTITEM 0
BUTTON YES* Open Qiling Website
Qiling:: Check for update
            {FormChangeCb}
            Your Qiling is v%s
            %s
            """ %(version, message), {
            'FormChangeCb': self.FormChangeCb(self.OnFormChange),
            })
        self.Compile()

    # callback to be executed when any form control changed
    def OnFormChange(self, fid):
        if fid == -2:   # Goto homepage
            import webbrowser
            # open Keypatch homepage in a new tab, if possible
            webbrowser.open(QilingHomePage, new = 2)

        return 1

class QlEmuRegEditDialog(Form):
    def __init__(self, regName):
        Form.__init__(self, r"""STARTITEM {id:reg_val}
BUTTON YES* Save
BUTTON CANCEL Cancel
Register Value
{reg_label}
<##:{reg_val}>
""", {
        'reg_label': Form.StringLabel("Edit [ " + regName + " ] value"),
        'reg_val': Form.NumericInput(tp=Form.FT_HEX, swidth=20)
        })

class QlEmuRegDialog(Choose):
    def __init__(self, reglist, flags=0, width=None, height=None, embedded=False):
        Choose.__init__(
            self, "QL Register Edit", 
            [ ["Register", 10 | Choose.CHCOL_PLAIN], 
              ["Value", 30] ])
        self.popup_names = ["", "", "Edit Value", ""]
        self.items = reglist

    def show(self):
        return self.Show(True) >= 0

    def OnEditLine(self, n):
        edit_dlg = QlEmuRegEditDialog(self.items[n][0])
        edit_dlg.Compile()
        edit_dlg.reg_val.value = self.items[n][1]
        ok = edit_dlg.Execute()
        if ok == 1:
            newvalue = edit_dlg.reg_val.value
            self.items[n][1] = int("%X" % newvalue, 16)
        self.Refresh()

    def OnGetLine(self, n):
        if self.items[n][2] == 32:
            return [ self.items[n][0], "0x%08X" % self.items[n][1] ]
        if self.items[n][2] == 64:
            return [ self.items[n][0], "0x%16X" % self.items[n][1] ]        

    def OnGetSize(self):
        return len(self.items)

    def OnClose(self):
        pass

### Misc
class QlEmuMisc:
    MenuItem = collections.namedtuple("MenuItem", ["action", "handler", "title", "tooltip", "shortcut", "popup"])
    class menu_action_handler(action_handler_t):
        def __init__(self, handler, action):
            action_handler_t.__init__(self)
            self.action_handler = handler
            self.action_type = action

        def activate(self, ctx):
            if ctx.form_type == BWN_DISASM:
                self.action_handler.ql_handle_menu_action(self.action_type)
            return 1

        # This action is always available.
        def update(self, ctx):
            return AST_ENABLE_ALWAYS

    @staticmethod
    def get_reg_map(ql:Qiling):
        tables = {
            QL_ARCH.X86     : list({**x86_reg_map_32, **x86_reg_map_misc, **x86_reg_map_st}.keys()),
            QL_ARCH.X8664   : list({**x86_reg_map_64, **x86_reg_map_misc, **x86_reg_map_st}.keys()),
            QL_ARCH.ARM     : list({**arm_reg_map}.keys()),
            QL_ARCH.ARM64   : list({**arm64_reg_map}.keys()),
            QL_ARCH.MIPS    : list({**mips_reg_map}.keys()),
        }

        if ql.archtype == QL_ARCH.X86:
            return tables[QL_ARCH.X86]
        elif ql.archtype == QL_ARCH.X8664:
            return tables[QL_ARCH.X8664]
        elif ql.archtype == QL_ARCH.ARM:
            return tables[QL_ARCH.ARM]
        elif ql.archtype == QL_ARCH.ARM64:
            return tables[QL_ARCH.ARM64]
        elif ql.archtype == QL_ARCH.MIPS:
            return tables[QL_ARCH.MIPS]
        else:
            return []

    @staticmethod
    def url_download(url):
        try:
            from urllib2 import Request, urlopen, URLError, HTTPError
        except:
            from urllib.request import Request, urlopen
            from urllib.error import URLError, HTTPError

        # create the url and the request
        req = Request(url)

        # Open the url
        try:
            # download this URL
            f = urlopen(req)
            content = f.read()
            return (0, content)

        # handle errors
        except HTTPError as e:
            # print "HTTP Error:", e.code , url
            # fail to download this file
            return (1, None)
        except URLError as e:
            # print "URL Error:", e.reason , url
            # fail to download this file
            return (1, None)
        except Exception as e:
            # fail to save the downloaded file
            # print("Error:", e)
            return (2, None)

    class QLStdIO(ql_file):
        def __init__(self, path, fd):
            super().__init__(path, fd)
            self.__fd = fd

        def write(self, write_buf):
            super().write(write_buf) 
            msg(write_buf.decode('utf-8'))

        def flush(self):
            pass

        def isatty(self):
            return False   

### Qiling wrapper

class QlEmuQiling:
    def __init__(self):
        self.path = get_input_file_path()
        self.rootfs = None
        self.ql = None
        self.status = None
        self.exit_addr = None
        self.baseaddr = None

    def start(self):
        if sys.platform != 'win32':
            qlstdin = QlEmuMisc.QLStdIO('stdin', sys.__stdin__.fileno())
            qlstdout = QlEmuMisc.QLStdIO('stdout', sys.__stdout__.fileno())
            qlstderr = QlEmuMisc.QLStdIO('stderr', sys.__stderr__.fileno())
            
        if sys.platform != 'win32':
            self.ql = Qiling(filename=[self.path], rootfs=self.rootfs, output="debug", stdin=qlstdin, stdout=qlstdout, stderr=qlstderr)
        else:
            self.ql = Qiling(filename=[self.path], rootfs=self.rootfs, output="debug")
        
        self.exit_addr = self.ql.os.exit_point
        if self.ql.ostype == QL_OS.LINUX:
            self.baseaddr = self.ql.os.elf_mem_start
        else:
            self.baseaddr = 0x0

    def run(self, begin=None, end=None):
        self.ql.run(begin, end)

    def set_reg(self):
        reglist = QlEmuMisc.get_reg_map(self.ql)
        regs = [ [ row, int(self.ql.reg.read(row)), ql_get_arch_bits(self.ql.archtype) ] for row in reglist ]
        regs_len = len(regs)
        RegDig = QlEmuRegDialog(regs)
        if RegDig.show():
            for idx, val in enumerate(RegDig.items[0:regs_len-1]):
                self.ql.reg.write(reglist[idx], val[1])
            return True
        else:
            return False

    def save(self):
        savedlg = QlEmuSaveDialog()
        savedlg.Compile()

        if savedlg.Execute() != 1:
            return False

        savepath = savedlg.path_name.value

        self.ql.save(reg=True, mem=True,fd=True, cpu_context=True, snapshot=savepath)
        logging.info('Save to ' + savepath)
        return True
    
    def load(self):
        loaddlg = QlEmuLoadDialog()
        loaddlg.Compile()

        if loaddlg.Execute() != 1:
            return False

        loadname = loaddlg.file_name.value

        self.ql.restore(snapshot=loadname)
        logging.info('Restore from ' + loadname)
        return True

    def remove_ql(self):
        if self.ql is not None:
            del self.ql
            self.ql = None

### Plugin

class QlEmuPlugin(plugin_t, UI_Hooks):
    ### Ida Plugin Data

    popup_menu_hook = None

    flags = PLUGIN_HIDE
    comment = ""

    help = "Qiling Emulator"
    wanted_name = "Qiling Emulator"
    wanted_hotkey = ""

    ### View Data

    qlemuregview = None
    qlemustackview = None
    qlemumemview = {}

    def __init__(self):
        super(QlEmuPlugin, self).__init__()
        self.plugin_name = "Qiling Emulator"
        self.qlemu = None
        self.ql = None
        self.stepflag = True
        self.stephook = None
        self.qlinit = False
        self.lastaddr = None
        self.is_change_addr = -1
        self.userobj = None
        self.customscriptpath = None
        self.bb_mapping = {}

    ### Main Framework

    def init(self):
        # init data
        logging.info('---------------------------------------------------------------------------------------')
        logging.info('Qiling Emulator Plugin For IDA, by Qiling Team. Version {0}, 2020'.format(QLVERSION))
        logging.info('Based on Qiling v{0}'.format(QLVERSION))
        logging.info('Find more information about Qiling at https://qiling.io')
        logging.info('---------------------------------------------------------------------------------------')
        self.qlemu = QlEmuQiling()
        self.ql_hook_ui_actions()
        return PLUGIN_KEEP

    def run(self, arg = 0):
        logging.info(f"Registering actions.")
        self.ql_register_menu_actions()
        self.ql_attach_main_menu_actions()

    def ready_to_run(self):
        logging.info(f"UI is ready, register our menu actions.")
        self.run()

    def term(self):
        self.qlemu.remove_ql()
        self.ql_unhook_ui_actions()
        self.ql_detach_main_menu_actions()
        self.ql_unregister_menu_actions()

    ### Actions

    def ql_start(self):
        if self.qlemu is None:
            self.qlemu = QlEmuQiling()
        if self.ql_set_rootfs():
            logging.info(f'Rootfs: {self.qlemu.rootfs}')
            logging.info(f"Custom user script: {self.customscriptpath}")
            show_wait_box("Qiling is processing ...")
            try:
                self.qlemu.start()
                self.qlinit = True
                self.lastaddr = None
            finally:
                hide_wait_box()
                logging.info("Qiling is initialized successfully.")
        if self.customscriptpath is not None:
            self.ql_load_user_script()
            self.userobj.custom_prepare(self.qlemu.ql)

    def ql_load_user_script(self):
        if self.qlinit :
            self.ql_get_user_script(is_reload=True, is_start=True)
        else:
            logging.error('Qiling should be setup firstly.')

    def ql_reload_user_script(self):
        if self.qlinit:
            self.ql_get_user_script(is_reload=True)
        else:
            logging.error('Qiling should be setup firstly.')

    def ql_continue(self):
        if self.qlinit:
            userhook = None
            pathhook = self.qlemu.ql.hook_code(self.ql_path_hook)
            if self.userobj is not None:
                userhook = self.userobj.custom_continue(self.qlemu.ql)
            if self.qlemu.status is not None:
                self.qlemu.ql.restore(self.qlemu.status)
                show_wait_box("Qiling is processing ...")
                try:
                    self.qlemu.run(begin=self.qlemu.ql.reg.arch_pc, end=self.qlemu.exit_addr)
                finally:
                    hide_wait_box()
            else:
                show_wait_box("Qiling is processing ...")
                try:
                    self.qlemu.run()
                finally:
                    hide_wait_box()
            self.qlemu.ql.hook_del(pathhook)
            if userhook and userhook is not None:
                for hook in userhook:
                    self.qlemu.ql.hook_del(hook)
            self.ql_update_views(self.qlemu.ql.reg.arch_pc, self.qlemu.ql)
        else:
            logging.error('Qiling should be setup firstly.')

    def ql_run_to_here(self):
        if self.qlinit:
            curr_addr = get_screen_ea()
            untillhook = self.qlemu.ql.hook_code(self.ql_untill_hook)
            if self.qlemu.status is not None:
                self.qlemu.ql.restore(self.qlemu.status)
                show_wait_box("Qiling is processing ...")
                try:
                    self.qlemu.run(begin=self.qlemu.ql.reg.arch_pc, end=curr_addr+self.qlemu.baseaddr-get_imagebase())
                finally:
                    hide_wait_box()
            else:
                show_wait_box("Qiling is processing ...")
                try:
                    self.qlemu.run(end=curr_addr+self.qlemu.baseaddr-get_imagebase())
                finally:
                    hide_wait_box()
            
            set_color(curr_addr, CIC_ITEM, 0x00B3CBFF)
            self.qlemu.ql.hook_del(untillhook)
            self.qlemu.status = self.qlemu.ql.save()
            self.ql_update_views(self.qlemu.ql.reg.arch_pc, self.qlemu.ql)
        else:
            logging.error('Qiling should be setup firstly.')

    def ql_step(self):
        if self.qlinit:
            userhook = None
            self.stepflag = True
            self.qlemu.ql.restore(saved_states=self.qlemu.status)
            self.stephook = self.qlemu.ql.hook_code(callback=self.ql_step_hook)
            if self.userobj is not None:
                userhook = self.userobj.custom_step(self.qlemu.ql)
            self.qlemu.run(begin=self.qlemu.ql.reg.arch_pc, end=self.qlemu.exit_addr)
            if userhook and userhook is not None:
                for hook in userhook:
                    self.qlemu.ql.hook_del(hook)
            self.ql_update_views(self.qlemu.ql.reg.arch_pc, self.qlemu.ql)
        else:
            logging.error('Qiling should be setup firstly.')

    def ql_save(self):
        if self.qlinit:
            if self.qlemu.save() != True:
                logging.error('Fail to save the snapshot.')
        else:
            logging.error('Qiling should be setup firstly.')

    def ql_load(self):
        if self.qlinit:
            if self.qlemu.load() != True:
                logging.error('Fail to load the snapshot.')
        else:
            logging.error('Qiling should be setup firstly.')

    def ql_chang_reg(self):
        if self.qlinit:
            self.qlemu.set_reg()
            self.ql_update_views(self.qlemu.ql.reg.arch_pc, self.qlemu.ql)
            self.qlemu.status = self.qlemu.ql.save()
        else:
            logging.error('Qiling should be setup firstly.')    

    def ql_reset(self):
        if self.qlinit:
            self.ql_close()
            self.qlemu = QlEmuQiling()
            self.ql_start()
        else:
            logging.error('Qiling should be setup firstly.')

    def ql_close(self):
        if self.qlinit:
            heads = Heads(get_segm_start(get_screen_ea()), get_segm_end(get_screen_ea()))
            for i in heads:
                set_color(i, CIC_ITEM, 0xFFFFFF)
            self.qlemu.remove_ql()
            del self.qlemu
            self.qlemu = None
            self.qlinit = False
            logging.info('Qiling is deleted.')
        else:
            logging.error('Qiling is not started.')

    def ql_show_reg_view(self):
        if self.qlinit:
            if self.qlemuregview is None:
                self.qlemuregview = QlEmuRegView(self)
                QlEmuRegView(self)
                self.qlemuregview.Create()
                self.qlemuregview.SetReg(self.qlemu.ql.reg.arch_pc, self.qlemu.ql)
                self.qlemuregview.Show()
                self.qlemuregview.Refresh()
        else:
            logging.error('Qiling should be setup firstly.')

    def ql_show_stack_view(self):
        if self.qlinit:
            if self.qlemustackview is None:
                self.qlemustackview = QlEmuStackView(self)
                self.qlemustackview.Create()
                self.qlemustackview.SetStack(self.qlemu.ql)
                self.qlemustackview.Show()
                self.qlemustackview.Refresh()
        else:
            logging.error('Qiling should be setup firstly.')

    def ql_show_mem_view(self, addr=get_screen_ea(), size=0x10):
        if self.qlinit:
            memdialog = QlEmuMemDialog()
            memdialog.Compile()
            memdialog.mem_addr.value = addr
            memdialog.mem_size.value = size
            ok = memdialog.Execute()
            if ok == 1:
                mem_addr = memdialog.mem_addr.value - self.qlemu.baseaddr + get_imagebase()
                mem_size = memdialog.mem_size.value
                mem_cmnt = memdialog.mem_cmnt.value

                if mem_addr not in self.qlemumemview:
                    if not self.qlemu.ql.mem.is_mapped(mem_addr, mem_size):
                        ok = ask_yn(1, "Memory [%X:%X] is not mapped!\nDo you want to map it?\n   YES - Load Binary\n   NO - Fill page with zeroes\n   Cancel - Close dialog" % (mem_addr, mem_addr + mem_size))
                        if ok == 0:
                            self.qlemu.ql.mem.map(mem_addr, mem_size)
                            self.qlemu.ql.mem.write(self.qlemu.ql.mem.align(mem_addr), b"\x00"*mem_size)
                        elif ok == 1:
                            # TODO: map_binary
                            return
                        else:
                            return
                    self.qlemumemview[mem_addr] = QlEmuMemView(self, mem_addr, mem_size)
                    if mem_cmnt == []:
                        self.qlemumemview[mem_addr].Create("QL Memory")
                    else:
                        self.qlemumemview[mem_addr].Create("QL Memory [ " + mem_cmnt + " ]")
                    self.qlemumemview[mem_addr].SetMem(self.qlemu.ql)
                self.qlemumemview[mem_addr].Show()
                self.qlemumemview[mem_addr].Refresh() 
        else:
            logging.error('Qiling should be setup firstly.')

    def ql_unload_plugin(self):
        heads = Heads(get_segm_start(get_screen_ea()), get_segm_end(get_screen_ea()))
        for i in heads:
            set_color(i, CIC_ITEM, 0xFFFFFF)
        self.ql_close()
        self.ql_detach_main_menu_actions()
        self.ql_unregister_menu_actions()
        logging.info('Unload plugin successfully!')

    def ql_menu_null(self):
        pass

    def ql_about(self):
        self.aboutdlg = QlEmuAboutDialog(QLVERSION)
        self.aboutdlg.Execute()
        self.aboutdlg.Free()

    def ql_check_update(self):
        (r, content) = QlEmuMisc.url_download(QilingStableVersionURL)
        content = content.decode("utf-8")
        if r == 0:
            try:
                version_stable = re.findall(r"\"([\d\.]+)\"", content)[0]
            except (TypeError, IndexError):
                warning("ERROR: Failed to find the Qiling version string from response.")
                logging.warning("Failed to find the Qiling version string from response.")

            # compare with the current version
            if version_stable == QLVERSION:
                self.updatedlg = QlEmuUpdateDialog(QLVERSION, "Good, you are already on the latest stable version!")
                self.updatedlg.Execute()
                self.updatedlg.Free()
            else:
                self.updatedlg = QlEmuUpdateDialog(QLVERSION, "Download latest stable version {0} from https://github.com/qilingframework/qiling/blob/master/qiling/extensions/idaplugin".format(version_stable))
                self.updatedlg.Execute()
                self.updatedlg.Free()
        else:
            # fail to download
            warning("ERROR: Failed to connect to Github. Try again later.")
            logging.warning("Failed to connect to Github when checking for the latest update. Try again later.")
    
    def _remove_from_bb_lists(self, bbid):
        if bbid in self.real_blocks:
            self.real_blocks.remove(bbid)
        elif bbid in self.fake_blocks:
            self.fake_blocks.remove(bbid)
        elif bbid in self.retn_blocks:
            self.retn_blocks.remove(bbid)

    def ql_mark_real(self):
        cur_addr = IDA.get_current_address()
        cur_block = IDA.get_block(cur_addr)
        self._remove_from_bb_lists(cur_block.id)
        self.real_blocks.append(cur_block.id)
        IDA.color_block(cur_block, Colors.Green.value)

    def ql_mark_fake(self):
        cur_addr = IDA.get_current_address()
        cur_block = IDA.get_block(cur_addr)
        self._remove_from_bb_lists(cur_block.id)
        self.fake_blocks.append(cur_block.id)
        IDA.color_block(cur_block, Colors.Gray.value)

    def ql_mark_retn(self):
        cur_addr = IDA.get_current_address()
        cur_block = IDA.get_block(cur_addr)
        self._remove_from_bb_lists(cur_block.id)
        self.retn_blocks.append(cur_block.id)
        IDA.color_block(cur_block, Colors.Pink.value)

    def _guide_hook(self, ql, addr, data):
        logging.info(f"Executing: {hex(addr)}")
        start_bb_id = self.hook_data['startbb']
        cur_bb = IDA.get_block(addr)
        if "force" in self.hook_data and addr in self.hook_data['force']:
            if self.hook_data['force'][addr]:
                reg1 = IDA.print_operand(addr, 0)
                reg2 = IDA.print_operand(addr, 1)
                reg2_val = ql.reg.__getattribute__(reg2)
                ql.reg.__setattr__(reg1, reg2_val)
            else:
                pass
            ins_size = IDA.get_instruction_size(addr)
            ql.reg.arch_pc += ins_size
        # TODO: Maybe we can detect whether the program will access unmapped
        #       here so that we won't map the memory.
        next_ins = IDA.get_instruction(addr)
        if "call" in next_ins:
            ql.reg.arch_pc += IDA.get_instruction_size(addr)
            return
        if start_bb_id == cur_bb.id:
            return
        if cur_bb.id in self.real_blocks or cur_bb.id in self.retn_blocks:
            if cur_bb.id not in self.paths[start_bb_id]:
                self.paths[start_bb_id].append(cur_bb.id)
            ql.emu_stop()

    def _skip_unmapped_rw(self, ql, type, addr, size, value):
        map_addr = ql.mem.align(addr)
        map_size = ql.mem.align(size)
        if not ql.mem.is_mapped(map_addr, map_size):
            logging.warning(f"Invalid memory R/W, trying to map {hex(map_size)} at {hex(map_addr)}")
            ql.mem.map(map_addr, map_size)
            ql.mem.write(map_addr, b'\x00'*map_size)
        return True

    def _find_branch_in_real_block(self, bb):
        paddr = bb.start_ea
        while paddr < bb.end_ea:
            ins = IDA.get_instruction(paddr)
            sz = IDA.get_instruction_size(paddr)
            if ins.lower().startswith("cmov"):
                return paddr
            paddr += sz
        return None

    def _log_paths_str(self):
        for bbid, succs in self.paths.items():
            if len(succs) == 1:
                logging.info(f"{self._block_str(bbid)} -> {self._block_str(succs[0])}")
            elif len(succs) == 2:
                logging.info(f"{self._block_str(bbid)} --(force jump)--> {self._block_str(succs[0])}")
                logging.info(f"|----(skip jump)----> {self._block_str(succs[1])}")

    def _search_path(self):
        self.paths = {bbid: [] for bbid in self.bb_mapping.keys()}
        reals = [self.first_block, *self.real_blocks]
        self.deflatqlemu = QlEmuQiling() 
        self.deflatqlemu.rootfs = self.qlemu.rootfs
        self.deflatqlemu.start()
        ql = self.deflatqlemu.ql
        self.hook_data = None
        ql.hook_code(self._guide_hook)
        ql.hook_mem_read_invalid(self._skip_unmapped_rw)
        ql.hook_mem_write_invalid(self._skip_unmapped_rw)
        ql.hook_mem_unmapped(self._skip_unmapped_rw)
        for bbid in reals:
            bb = self.bb_mapping[bbid]
            braddr = self._find_branch_in_real_block(bb)
            self.hook_data = {
                "startbb": bbid
            }
            if braddr is None:
                ql.run(begin=bb.start_ea)
            else:
                self.hook_data['force'] = {braddr: True}
                ql.run(begin=bb.start_ea)
                self.hook_data['force'] = {braddr: False}
                ql.run(begin=bb.start_ea)
        del self.deflatqlemu
        self.deflatqlemu = None
        self._log_paths_str()

    def _patch_codes(self):
        if len(self.paths[self.first_block]) != 1:
            logging.error(f"Found wrong ways in first block: {self._block_str(self.bb_mapping[self.first_block])}, should be 1 path but get {len(self.paths[self.first_block])}, exit.")
            return
        logging.info("NOP dispatcher block")
        dispatcher_bb = self.bb_mapping[self.dispatcher]
        IDA.fill_block(dispatcher_bb, b'\x00')
        first_jmp_addr = dispatcher_bb.start_ea
        instr_to_assemble = f"jmp {self.bb_mapping[self.paths[self.first_block][0]].start_ea:x}h"
        logging.info(f"Assemble {instr_to_assemble} at {hex(first_jmp_addr)}")
        IDA.assemble(first_jmp_addr, 0, first_jmp_addr, True, instr_to_assemble)
        for bbid in self.real_blocks:
            bb = self.bb_mapping[bbid]
            braddr = self._find_branch_in_real_block(bb)
            if braddr is None:
                last_instr_address = IDA.get_prev_head(bb.end_ea)
                logging.info(f"Patch NOP from {hex(last_instr_address)} to {hex(bb.end_ea)}")
                IDA.fill_bytes(last_instr_address, bb.end_ea, b'\x00')
                if len(self.paths[bbid]) != 1:
                    logging.warning(f"Found wrong ways in block: {self._block_str(bb)}, should be 1 path but get {len(self.paths[bbid])}")
                    continue
                instr_to_assemble = f"jmp {self.bb_mapping[self.paths[bbid][0]].start_ea:x}h"
                logging.info(f"Assemble {instr_to_assemble} at {hex(last_instr_address)}")
                IDA.assemble(last_instr_address, 0, last_instr_address, True, instr_to_assemble)
                IDA.perform_analysis(bb.start_ea, bb.end_ea)
            else:
                if len(self.paths[bbid]) != 2:
                    logging.warning(f"Found wrong ways in block: {self._block_str(bb)}, should be 2 paths but get {len(self.paths[bbid])}")
                    continue
                cmov_instr = IDA.get_instruction(braddr).lower()
                logging.info(f"Patch NOP from {hex(braddr)} to {hex(bb.end_ea)}")
                IDA.fill_bytes(braddr, bb.end_ea, b'\x00')
                jmp_instr = f"j{cmov_instr[4:]}"
                instr_to_assemble = f"{jmp_instr} {self.bb_mapping[self.paths[bbid][0]].start_ea:x}h"
                logging.info(f"Assemble {instr_to_assemble} at {hex(braddr)}")
                IDA.assemble(braddr, 0, braddr, True, instr_to_assemble)
                IDA.perform_analysis(bb.start_ea, bb.end_ea)
                time.sleep(0.5)
                next_instr_address = IDA.get_instruction_size(braddr) + braddr
                instr_to_assemble = f"jmp {self.bb_mapping[self.paths[bbid][1]].start_ea:x}h"      
                logging.info(f"Assemble {instr_to_assemble} at {hex(next_instr_address)}")
                IDA.assemble(next_instr_address, 0, next_instr_address, True, instr_to_assemble)
                IDA.perform_analysis(bb.start_ea, bb.end_ea)
        for bbid in self.fake_blocks:
            bb = self.bb_mapping[bbid]
            logging.info(f"Patch NOP for block: {self._block_str(bb)}")
            IDA.fill_block(bb, b'\x00')
        logging.info(f"Patch NOP for pre_dispatcher.")
        bb = self.bb_mapping[self.pre_dispatcher]
        IDA.fill_block(bb, b'\x00')
    
    def ql_deflat(self):
        if len(self.bb_mapping) == 0:
            self.ql_parse_blocks_for_deobf()
        self._search_path()
        self._patch_codes()
        IDA.perform_analysis(self.deflat_func.start_ea, self.deflat_func.end_ea)

    def _block_str(self, bb):
        if type(bb) is int:
            bb = self.bb_mapping[bb]
        return f"Block id: {bb.id}, start_address: {bb.start_ea:x}, end_address: {bb.end_ea:x}, type: {bb.type}"

    def ql_parse_blocks_for_deobf(self):
        cur_addr = IDA.get_current_address()
        flowchart = IDA.get_flowchart(cur_addr)
        self.deflat_func = IDA.get_function(cur_addr)
        self.bb_mapping = {bb.id:bb for bb in flowchart}
        if flowchart is None:
            return
        bb_count = {}
        for bb in flowchart:
            for succ in bb.succs():
                if succ.id not in bb_count:
                    bb_count[succ.id] = 0
                bb_count[succ.id] += 1
        max_ref_bb_id = None
        max_ref = 0
        for bb_id, ref in bb_count.items():
            if ref > max_ref:
                max_ref = ref
                max_ref_bb_id = bb_id
        self.pre_dispatcher = max_ref_bb_id
        try:
            self.dispatcher = list(self.bb_mapping[self.pre_dispatcher].succs())[0].id
            self.first_block = flowchart[0].id
        except IndexError:
            logging.error("Fail to get dispatcher and first_block.")
            return
        self.real_blocks = []
        self.fake_blocks = []
        self.retn_blocks = []
        for bb in flowchart:
            if self.pre_dispatcher in [b.id for b in bb.succs()] and IDA.get_instructions_count(bb.start_ea, bb.end_ea) > 1:
                self.real_blocks.append(bb.id)
            elif IDA.block_is_terminating(bb):
                self.retn_blocks.append(bb.id)
            elif bb.id != self.first_block and bb.id != self.pre_dispatcher and bb.id != self.dispatcher:
                self.fake_blocks.append(bb.id)
        for bbid in self.real_blocks:
            IDA.color_block(self.bb_mapping[bbid], Colors.Green.value)
        for bbid in self.fake_blocks:
            IDA.color_block(self.bb_mapping[bbid], Colors.Gray.value)
        for bbid in self.retn_blocks:
            IDA.color_block(self.bb_mapping[bbid], Colors.Pink.value)
        IDA.color_block(self.bb_mapping[self.dispatcher], Colors.Blue.value)
        IDA.color_block(self.bb_mapping[self.pre_dispatcher], Colors.Blue.value)
        IDA.color_block(self.bb_mapping[self.first_block], Colors.Beige.value)
        logging.info(f"First block: {self._block_str(self.first_block)}")
        logging.info(f"Dispatcher: {self._block_str(self.dispatcher)}")
        logging.info(f"Pre dispatcher: {self._block_str(self.pre_dispatcher)}")
        logging.info(f"Real blocks:")
        for s in map(self._block_str, self.real_blocks): logging.info(s)
        logging.info(f"Fake blocks:")
        for s in map(self._block_str, self.fake_blocks): logging.info(s)
        logging.info(f"Return blocks:")
        for s in map(self._block_str, self.retn_blocks): logging.info(s)
        logging.info(f"Auto analysis finished, please check whether the result is correct.")
        logging.info(f"You may change the property of each block manually if necessary.")


    ### Hook

    def ql_step_hook(self, ql, addr, size):
        self.stepflag = not self.stepflag
        addr = addr - self.qlemu.baseaddr + get_imagebase()
        if self.stepflag:
            set_color(addr, CIC_ITEM, 0x00FFD700)
            self.ql_update_views(self.qlemu.ql.reg.arch_pc, ql)
            self.qlemu.status = ql.save()
            ql.os.stop()
            self.qlemu.ql.hook_del(self.stephook)
            jumpto(addr)

    def ql_path_hook(self, ql, addr, size):
        addr = addr - self.qlemu.baseaddr + get_imagebase()
        set_color(addr, CIC_ITEM, 0x007FFFAA)
        bp_count = get_bpt_qty()
        bp_list = []
        if bp_count > 0:
            for num in range(0, bp_count):
                bp_list.append(get_bpt_ea(num))

            if addr in bp_list and (addr != self.lastaddr or self.is_change_addr>1):
                self.qlemu.status = ql.save()
                ql.os.stop()
                self.lastaddr = addr
                self.is_change_addr = -1
                jumpto(addr)

            self.is_change_addr += 1
            

    def ql_untill_hook(self, ql, addr, size):
        addr = addr - self.qlemu.baseaddr + get_imagebase()
        set_color(addr, CIC_ITEM, 0x00B3CBFF)

    ### User Scripts

    def ql_get_user_script(self, is_reload=False, is_start=False):
        def get_user_scripts_obj(scriptpath:str, classname:str, is_reload:bool):
            try:
                import sys
                import importlib

                modulepath,filename = os.path.split(scriptpath)
                scriptname,_ = os.path.splitext(filename)

                sys.path.append(modulepath)
                module = importlib.import_module(scriptname)

                if is_reload:
                    importlib.reload(module)
                cls = getattr(module, classname)
                return cls()
            except:
                return None

        self.userobj = get_user_scripts_obj(self.customscriptpath, 'QILING_IDA', is_reload)
        if self.userobj is not None:
            if is_reload and not is_start:
                logging.info('Custom user script is reloaded.')
            else:
                logging.info('Custom user script is loaded successfully.')
        else:
            logging.info('Custom user script not found.')

    ### Dialog

    def ql_set_rootfs(self):
        setupdlg = QlEmuSetupDialog()
        setupdlg.Compile()

        if setupdlg.Execute() != 1:
            return False

        rootfspath = setupdlg.path_name.value
        customscript = setupdlg.script_name.value

        if customscript != '':
            self.customscriptpath = customscript

        if self.qlemu is not None:
            self.qlemu.rootfs = rootfspath
            return True
        return False    

    ### Menu

    menuitems = []

    def ql_register_new_action(self, act_name, act_text, act_handler, shortcut, tooltip, icon):
        new_action = action_desc_t(
            act_name,       # The action name. This acts like an ID and must be unique
            act_text,       # The action text.
            act_handler,    # The action handler.
            shortcut,       # Optional: the action shortcut
            tooltip,        # Optional: the action tooltip (available in menus/toolbar)
            icon)           # Optional: the action icon (shows when in menus/toolbars)
        register_action(new_action)

    def ql_handle_menu_action(self, action):
        [x.handler() for x in self.menuitems if x.action == action]

    def ql_register_menu_actions(self):
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":start",             self.ql_start,                 "Setup",                      "Setup",                     None,                   True   ))
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":reloaduserscripts", self.ql_reload_user_script,      "Reload User Scripts",        "Reload User Scripts",       None,                   True   ))
        self.menuitems.append(QlEmuMisc.MenuItem("-",                                     self.ql_menu_null,              "",                           None,                        None,                   True   ))        
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":runtohere",         self.ql_run_to_here,             "Execute Till",               "Execute Till",              None,                   True   ))
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":runfromhere",       self.ql_continue,              "Continue",                   "Continue",                  None,                   True   ))
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":step",              self.ql_step,                  "Step",                       "Step (CTRL+SHIFT+F9)",      "CTRL+SHIFT+F9",        True   ))
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":changreg",          self.ql_chang_reg,              "Edit Register",              "Edit Register",             None,                   True   ))
        self.menuitems.append(QlEmuMisc.MenuItem("-",                                     self.ql_menu_null,              "",                           None,                        None,                   True   ))
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":reset",             self.ql_reset,                 "Restart",                    "Restart Qiling",            None,                   True   ))
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":close",             self.ql_close,                 "Close",                      "Close Qiling",              None,                   False  ))
        self.menuitems.append(QlEmuMisc.MenuItem("-",                                     self.ql_menu_null,              "",                           None,                        None,                   True   ))
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":reg view",          self.ql_show_reg_view,           "View Register",              "View Register",             None,                   True   ))     
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":stack view",        self.ql_show_stack_view,         "View Stack",                 "View Stack",                None,                   True   ))  
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":memory view",       self.ql_show_mem_view,           "View Memory",                "View Memory",               None,                   True   ))
        self.menuitems.append(QlEmuMisc.MenuItem("-",                                     self.ql_menu_null,              "",                           None,                        None,                   True   ))
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":save",              self.ql_save,                  "Save Snapshot",              "Save Snapshot",             None,                   True   ))
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":load",              self.ql_load,                  "Load Snapshot",              "Load Snapshot",             None,                   True   ))
        self.menuitems.append(QlEmuMisc.MenuItem("-",                                     self.ql_menu_null,              "",                           None,                        None,                   True   ))
        if UseAsScript:
            self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":unload",            self.ql_unload_plugin,           "Unload Plugin",              "Unload Plugin",             None,                   False  ))
            self.menuitems.append(QlEmuMisc.MenuItem("-",                                     self.ql_menu_null,              "",                           None,                        None,                   False  ))  
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":about",             self.ql_about,                 "About",                      "About",                     None,                   False  ))
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":checkupdate",       self.ql_check_update,           "Check Update",               "Check Update",              None,                   False  ))
        self.menuitems.append(QlEmuMisc.MenuItem("-",                                     self.ql_menu_null,              "",                           None,                        None,                   True   ))
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":parseblocks",       self.ql_parse_blocks_for_deobf,           "Auto Analysis For Deflat",               "Auto Analysis For Deflat",              None,                   True  ))
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":markreal",       self.ql_mark_real,           "Mark as Real Block",               "Mark as Real Block",              None,                   True  ))
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":markfake",       self.ql_mark_fake,           "Mark as Fake Block",               "Mark as Fake Block",              None,                   True  ))
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":markretn",       self.ql_mark_retn,           "Mark as Return Block",               "Mark as Return Block",              None,                   True  ))
        self.menuitems.append(QlEmuMisc.MenuItem(self.plugin_name + ":deflat",       self.ql_deflat,           "Deflat",               "Deflat",              None,                   True  ))

        for item in self.menuitems:
            if item.action == "-":
                continue
            self.ql_register_new_action(item.action, item.title, QlEmuMisc.menu_action_handler(self, item.action), item.shortcut, item.tooltip,  -1)

    def ql_unregister_menu_actions(self):
        for item in self.menuitems:
            unregister_action(item.action)

    def ql_attach_main_menu_actions(self):
        for item in self.menuitems:
            attach_action_to_menu("Edit/Plugins/" + self.plugin_name + "/" + item.title, item.action, SETMENU_APP)

    def ql_detach_main_menu_actions(self):
        for item in self.menuitems:
            detach_action_from_menu("Edit/Plugins/" + self.plugin_name + "/" + item.title, item.action)

    ### POPUP MENU

    def ql_hook_ui_actions(self):
        self.popup_menu_hook = self
        self.popup_menu_hook.hook()

    def ql_unhook_ui_actions(self):
        if self.popup_menu_hook != None:
            self.popup_menu_hook.unhook()

    # IDA 7.x

    def finish_populating_widget_popup(self, widget, popup_handle):
        if get_widget_type(widget) == BWN_DISASM:
            for item in self.menuitems:
                if item.popup:
                    attach_action_to_popup(widget, popup_handle, item.action, self.plugin_name + "/")

    ### Close View

    def ql_close_reg_view(self):
        self.qlemuregview = None

    def ql_close_stack_view(self):
        self.qlemustackview = None
    
    def ql_close_mem_view(self, viewid):
        del self.qlemumemview[viewid]

    def ql_close_all_views(self):
        if self.qlemuregview is not None:
            self.qlemuregview.Close()
        if self.qlemustackview is not None:
            self.qlemustackview.Close()
        
        for viewid in self.qlemumemview:
            self.qlemumemview[viewid].Close()
            self.qlemumemview = None

    def ql_update_views(self, addr, ql):
        if self.qlemuregview is not None:
            self.qlemuregview.SetReg(addr, ql)

        if self.qlemustackview is not None:
            self.qlemustackview.SetStack(self.qlemu.ql)

        for id in self.qlemumemview:
            self.qlemumemview[id].SetMem(self.qlemu.ql)


def PLUGIN_ENTRY():
    qlEmu = QlEmuPlugin()
    return qlEmu

if UseAsScript:
    if __name__ == "__main__":
        qlEmu = QlEmuPlugin()
        qlEmu.init()
        qlEmu.run()
