# Copyright (c) 2016
# Milan Bohacek <milan.bohacek+commandpalette@gmail.com>
# All rights reserved.
# 
# ==============================================================================
# 
# This file is part of Command Palette.
# 
# Command Palette is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# ==============================================================================


import idaapi
import idautils
from idaapi import PluginForm
from PyQt5 import QtCore, QtGui, QtWidgets
import re
import time

last_command = ""
last_search = ""
#timing = 0

# --------------------------------------------------------------------------

def active_actions():
    actions = idaapi.get_registered_actions()
    enabled_actions = []
    for action_name in actions:
        (a, b) = idaapi.get_action_state(action_name)
        if b <= idaapi.AST_ENABLE:
            enabled_actions.append(action_name)
    return sorted(enabled_actions)

# --------------------------------------------------------------------------

class MyEdit(QtWidgets.QLineEdit):

    def keyPressEvent(self, event):
        if event.key() in  [QtCore.Qt.Key_Down, QtCore.Qt.Key_Up, QtCore.Qt.Key_PageDown, QtCore.Qt.Key_PageUp]:
            QtWidgets.QApplication.sendEvent(self.lst, event)

        QtWidgets.QLineEdit.keyPressEvent(self, event)
# --------------------------------------------------------------------------


class MyList(QtWidgets.QListView):

    def keyPressEvent(self, event):
        super(MyList, self).keyPressEvent(event)

    def moveCursor(self,  cursorAction, modifiers):
        #print "move {}".format(repr(cursorAction))
        idx = self.currentIndex()
        row = idx.row()
        cnt = idx.model().rowCount()
        

        if cursorAction in [ QtWidgets.QAbstractItemView.MoveUp, QtWidgets.QAbstractItemView.MovePrevious]:
            if row == 0:
                cursorAction = QtWidgets.QAbstractItemView.MoveEnd
            

        if cursorAction in [ QtWidgets.QAbstractItemView.MoveDown, QtWidgets.QAbstractItemView.MoveNext ]:
            if row+1 == cnt:
                cursorAction = QtWidgets.QAbstractItemView.MoveHome

        return super(MyList, self).moveCursor(cursorAction, modifiers)

# --------------------------------------------------------------------------

        
class HTMLDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent):
        self.cached_size = None
        super(HTMLDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        model = index.model()
        row = index.row()
        action = model.data(model.index(row, 0, QtCore.QModelIndex()))
        command = model.data(model.index(row, 1, QtCore.QModelIndex()))
        shortcut = model.data(model.index(row, 2, QtCore.QModelIndex()))
        description = model.data(model.index(row, 3, QtCore.QModelIndex()))

        doc = QtGui.QTextDocument();

        global ImpExpForm

        if len(ImpExpForm.regex_pattern) > 1:
            action = ImpExpForm.regex.sub( r'<b>\1</b>', action )
            command = ImpExpForm.regex.sub( r'<b>\1</b>', command )
            description = ImpExpForm.regex.sub( r'<b>\1</b>', description )
            shortcut = ImpExpForm.regex.sub( r'<b>\1</b>', shortcut )

        document = "<table cellspacing=0 width=750 cellpadding=0><tr><td width = 30% >{}</td><td width = 30% >{}</td><td width=30%>{}</td><td align=right width=100%>{}</td></tr></table>".format(action, command, description, shortcut)


        doc.setHtml( document );

        painter.save()
        option.widget.style().drawControl(QtWidgets.QStyle.CE_ItemViewItem, option, painter);

        
        painter.translate(option.rect.left(), option.rect.top());
        clip = QtCore.QRectF(0, 0, option.rect.width(), option.rect.height());        
        doc.drawContents(painter, clip);
        painter.restore()

    def sizeHint(self, option, index):
        if self.cached_size is None:
            self.initStyleOption(option, index);
            doc = QtGui.QTextDocument();
            document = "<table cellspacing=0 width=750 cellpadding=0><tr><td width = 30% >{}</td><td width = 30% >{}</td><td width=30%>{}</td><td align=right width=100%>{}</td></tr></table>".format("action", "command", "description", "ctrl-alt-delete")
            doc.setHtml(document)
            doc.setTextWidth(option.rect.width());
            self.cached_size = QtCore.QSize(doc.idealWidth(), doc.size().height());
        return self.cached_size



# --------------------------------------------------------------------------

class MyFilter(QtCore.QSortFilterProxyModel):

    def filterAcceptsRow__(self, sourceRow, sourceParent):
        t1 = time.clock()
        r = self.filterAcceptsRow_( sourceRow, sourceParent)
        t2 = time.clock()
        #global timing
        #timing += t2-t1
        #return r

    def filterAcceptsRow(self, sourceRow, sourceParent):
        regex = self.filterRegExp()
        if len( regex.pattern() ) == 0:
            return True

        m = self.sourceModel()
        ind = lambda i: m.index(sourceRow, i, sourceParent)
        st = lambda x: (regex.indexIn(m.data(x)) != -1)
        test = lambda x: st(ind(x))

        for i in xrange(4):
            if test( i ):
                return True
        return False
# --------------------------------------------------------------------------


class ActionPaletteForm_t(QtWidgets.QDialog):

    def mousePressEvent(self, event):
        #print "mouse: ", event
        event.ignore();
        event.accept();
        if not self.rect().contains(event.pos()):
            close();



    def select(self, row):
        idx = self.proxyModel.index( row, 0,  QtCore.QModelIndex() );
        #m = self.lst.selectionModel();
        self.lst.setCurrentIndex( idx )
        #print self.lst.selectedIndexes()
        #print "data: ", idx.data()
        #print "xa", self.lst.currentIndex().data(),"ya"

    def on_text_changed(self):
        filter = self.filter.text()
        self.regex = re.compile("(%s)"%(re.escape(filter)), flags = re.IGNORECASE)
        self.regex_pattern = filter
        self.proxyModel.setFilterRegExp( QtCore.QRegExp(filter, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.FixedString) )

        #self.lst.currentIndex()
        self.select(0)
        #print dir(self.proxyModel)
        self.lst.viewport().update()
        #print filter

    def on_enter(self):
        self.report_action(self.lst.currentIndex())
        


    def report_action(self, index):
        if not index.isValid():
            return
        self.setResult(1)
        self.action_name = str(index.data())
        global last_search
        last_search = self.filter.text()
        
        self.done(1)


    def focusOutEvent(self, event):
        #print "focusout"
        pass

    #def event(self, event):
    #    #print event, event.type()
    #    return super(ActionPaletteForm_t, self).event(event)


    def __init__(self, parent = None, flags = None):
        """
        Called when the plugin form is created
        """
        # Get parent widget
        #self.parent = idaapi.PluginForm.FormToPyQtWidget(form)
        #super(ActionPaletteForm_t, self).__init__( parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint  )
        #super(ActionPaletteForm_t, self).__init__( parent, QtCore.Qt.Popup )
        #super(ActionPaletteForm_t, self).__init__( parent, QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint )
        super(ActionPaletteForm_t, self).__init__( parent, QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint )
        

        self.setFocusPolicy( QtCore.Qt.ClickFocus )

        
        self.setWindowTitle("Command Palette")
        self.resize(800, 500)

        # Create tree control        
        self.lst = MyList()        
        self.actions = active_actions()
        self.action_name = None

        self.model = QtGui.QStandardItemModel(len(self.actions), 4)

        self.proxyModel = MyFilter()
        self.proxyModel.setDynamicSortFilter(True)

        self.model.setHeaderData(0, QtCore.Qt.Horizontal, "Action")
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Command")
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, "Shortcut")
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, "Description")


        
        for row, i in enumerate( self.actions ):
            #self.lst.addItem(i)             
             label = idaapi.get_action_label(i).replace("~", "").replace("&","")
             shortcut = idaapi.get_action_shortcut(i)
             tooltip = idaapi.get_action_tooltip(i)

             self.model.setData(self.model.index(row, 0, QtCore.QModelIndex()), i)
             self.model.setData(self.model.index(row, 1, QtCore.QModelIndex()), label)
             self.model.setData(self.model.index(row, 2, QtCore.QModelIndex()), shortcut)
             self.model.setData(self.model.index(row, 3, QtCore.QModelIndex()), tooltip)
             row += 1

        self.proxyModel.setSourceModel(self.model)
        self.lst.setModel(self.proxyModel)

        global last_search

        self.filter = MyEdit(last_search)
        self.regex = re.compile("(%s)"%re.escape(last_search), flags = re.IGNORECASE)
        self.regex_pattern = last_search

        self.proxyModel.setFilterRegExp( QtCore.QRegExp(self.regex_pattern, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.FixedString) )

        self.filter.setMaximumHeight( 30 )
        self.filter.textChanged.connect( self.on_text_changed )
        self.filter.returnPressed.connect( self.on_enter )
        
                
        self.lst.clicked.connect(self.on_clicked)        
        #self.lst.activated.connect(self.on_activated)

        self.lst.setSelectionMode(1)#QtSingleSelection

        self.lst.setEditTriggers( QtWidgets.QAbstractItemView.NoEditTriggers )
        self.lst.setSelectionBehavior( QtWidgets.QAbstractItemView.SelectRows )        
        self.lst.setItemDelegate( HTMLDelegate(self.lst) )
        
        #self.lst.setSectionResizeMode( QtWidgets.QHeaderView.Fixed )

        self.filter.lst = self.lst
        self.lst.filter = self.filter


        self.filter.setStyleSheet('border: 0px solid black; border-bottom:0px;');
        self.lst.setStyleSheet('QListView{border: 0px solid black; background-color: #F0F0F0;}; ');

        #self.completer = QtWidgets.QCompleter(self.model)
        #self.completer.setCompletionMode(QtWidgets.QCompleter.InlineCompletion)
        #self.filter.setCompleter(self.completer)



        # Create layout
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.addWidget( self.filter )        
        layout.addWidget( self.lst )

        # Populate PluginForm
        self.setLayout(layout)
        self.filter.setFocus()
        self.filter.selectAll()        

        found = False
        if len(last_command)>0:
            for row in xrange(self.proxyModel.rowCount()):
                idx = self.proxyModel.index(row, 0)
                if self.proxyModel.data(idx) == last_command:
                    self.lst.setCurrentIndex( idx )
                    found = True
                    break
        if not found:
            self.lst.setCurrentIndex( self.proxyModel.index(0, 0) )
        
    def on_clicked(self, item):
        #print "clicked"
        self.report_action(item)        


    def on_activated(self, item):
        #print "activate"
        self.report_action(item)
    


# --------------------------------------------------------------------------
def AskForAction():
    global ImpExpForm
    #todo change [x for x in QtWidgets.QApplication.topLevelWidgets() if repr(x).find('QMainWindow') != -1][0] into something non-crazy
    parent = [x for x in QtWidgets.QApplication.topLevelWidgets() if repr(x).find('QMainWindow') != -1][0]
    ImpExpForm = ActionPaletteForm_t( parent )
    ImpExpForm.setModal(True)   
    idaapi.disable_script_timeout()

    #ImpExpForm.setStyleSheet("background:transparent;");
    ImpExpForm.setAttribute(QtCore.Qt.WA_DeleteOnClose, True);
    #ImpExpForm.setAttribute(QtCore.Qt.WA_TranslucentBackground, True);

    result = None
    

    #print "result value:", repr( ImpExpForm.res )
    #print "result action:", repr( ImpExpForm.action_name )
    
    if ImpExpForm.exec_() == 1:
        global last_command
        last_command = ImpExpForm.action_name

        result = last_command

    del ImpExpForm
    return result

# --------------------------------------------------------------------------


class command_palette_ah(idaapi.action_handler_t):
    def __init__(self):
        idaapi.action_handler_t.__init__(self)
    
    def activate(self, ctx):
        action = AskForAction()

        if action:
            idaapi.process_ui_action( action )
        return 1
    
    def update(self, ctx):
        return idaapi.AST_ENABLE_ALWAYS

command_palette_action_desc = idaapi.action_desc_t("mb:command_palette", "Command Palette", command_palette_ah(), "Shift+W", "Opens Sublime-like command palette.", -1)

class repeat_action_ah_t(idaapi.action_handler_t):
    def activate(self, ctx):
        global last_command
        return idaapi.process_ui_action( last_command )

    def update(self, ctx):
        return idaapi.AST_ENABLE_ALWAYS

repeat_action_action_desc = idaapi.action_desc_t( "mb:repeat_last_palette_command", "Repeat last palette command", repeat_action_ah_t(), "W", "Repeat last command issued with the Command Palette.", -1 )
    

def register_actions():
    idaapi.register_action(command_palette_action_desc)
    idaapi.register_action(repeat_action_action_desc)

def unregister_actions():
    idaapi.unregister_action( command_palette_action_desc.name );
    idaapi.unregister_action( repeat_action_action_desc.name );


class CommandPalettePlugin(idaapi.plugin_t):
    flags = idaapi.PLUGIN_FIX | idaapi.PLUGIN_HIDE
    comment = "Sublime-like command palette for IDA"
    help = "Sublime-like command palette"
    wanted_name = "command palette"
    wanted_hotkey = ""

    def init(self):
        addon = idaapi.addon_info_t();
        addon.id = "milan.bohacek.command_palette";
        addon.name = "Command Palette";
        addon.producer = "Milan Bohacek";
        addon.url = "milan.bohacek+commandpalette@gmail.com";
        addon.version = "6.95";
        idaapi.register_addon( addon );
        register_actions()

        return idaapi.PLUGIN_KEEP

    def term(self):
        unregister_actions()
        pass

    def run(self, arg):
        pass


def PLUGIN_ENTRY():
    return CommandPalettePlugin()

#if __name__ == "__main__":
#    print "got action:", CommandPalettePlugin()
