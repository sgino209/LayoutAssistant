#!/usr/bin/env python
# Created by Shahar Gino at November 2017, sgino209@gmail.com
# Click on Help->Usage for usage guidlines

from sys import version_info
from base64 import b64decode
from os import remove, getcwd
from math import atan2, degrees, sqrt
from pickle import dump, load, HIGHEST_PROTOCOL
try:
  import wx
except ImportError:
  print("wxpython is not installed, you may install it with brew ('brew install wxpython')")
  exit(0)

# ===============================================================================================================
#  __  __       _       _____
# |  \/  | __ _(_)_ __ |  ___| __ __ _ _ __ ___   ___     Main class than
# | |\/| |/ _` | | '_ \| |_ | '__/ _` | '_ ` _ \ / _ \    handles all the GUI,
# | |  | | (_| | | | | |  _|| | | (_| | | | | | |  __/    based on the WX library
# |_|  |_|\__,_|_|_| |_|_|  |_|  \__,_|_| |_| |_|\___|

class MainFrame ( wx.Frame ):
  
  # -------------------------------------------------------------------------------------
  def __init__( self, parent ):
    """ MainFrame GUI constructor """

    # Prolog:
    wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = "Layout Assistant", pos = wx.DefaultPosition, 
                        size = wx.Size( -1,-1 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
    self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
  
    # MenuBar:
    menuBar = wx.MenuBar()
    fileMenu = wx.Menu()
    viewMenu = wx.Menu()
    helpMenu = wx.Menu()
    self.portsEnId = wx.NewId()
    fileMenu.AppendCheckItem(self.portsEnId, "Ports Enabling", "Enable if Partitions contain Ports")
    canvassizeMenuItem = fileMenu.Append(wx.NewId(), "Canvas Size", "Modify the Canvas Size")
    exitMenuItem = fileMenu.Append(wx.NewId(), "Exit", "Exit the application")
    zoominMenuItem = viewMenu.Append(wx.NewId(), "Zoom In", "Zoom in along the Canvas")
    zoomoutMenuItem = viewMenu.Append(wx.NewId(), "Zoom Out", "Zoom out along the Canvas")
    zoomMenuItem = viewMenu.Append(wx.NewId(), "Zoom", "Zoom along the Canvas")
    zoomactualMenuItem = viewMenu.Append(wx.NewId(), "Actual Size", "Actual Size along the Canvas")
    usageMenuItem = helpMenu.Append(wx.NewId(), "Usage", "Usage guidelines the application")
    aboutMenuItem = helpMenu.Append(wx.NewId(), "About", "About the application")
    menuBar.Append(fileMenu, "&File")
    menuBar.Append(viewMenu, "&View")
    menuBar.Append(helpMenu, "&Help")
    self.Bind(wx.EVT_MENU, self.OnCanvasSize, canvassizeMenuItem)
    self.Bind(wx.EVT_MENU, self.OnExit, exitMenuItem)
    self.Bind(wx.EVT_MENU, self.OnZoomIn, zoominMenuItem)
    self.Bind(wx.EVT_MENU, self.OnZoomOut, zoomoutMenuItem)
    self.Bind(wx.EVT_MENU, self.OnZoom, zoomMenuItem)
    self.Bind(wx.EVT_MENU, self.OnZoomActual, zoomactualMenuItem)
    self.Bind(wx.EVT_MENU, self.OnUsage, usageMenuItem)
    self.Bind(wx.EVT_MENU, self.OnAbout, aboutMenuItem)
    self.SetMenuBar(menuBar)

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    # Main Sizer (comprises Canvas and RightSideBar):
    MainSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Main" ), wx.HORIZONTAL )

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    # Canvas Sizer:
    MainCanvasSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"MainCanvas" ), wx.VERTICAL )

    defaultCanvasSize = (10000,10000)
    screenSize = wx.DisplaySize()
    self.ppu_x = int(screenSize[0] / 20)
    self.ppu_y = int(screenSize[1] / 20)

    self.Canvas_panel = wx.ScrolledWindow(self, wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
    self.Canvas_panel.SetScrollbars(self.ppu_x, self.ppu_y, defaultCanvasSize[0]/self.ppu_x, defaultCanvasSize[1]/self.ppu_y)
    self.Canvas_panel.modules = {}
    self.Canvas_panel.RectLast = None
    self.Canvas_panel.LineLast = None
    self.Canvas_panel.LinesLast = []
    self.Canvas_panel.selectionStart = None
    self.Canvas_panel.selectedModule = {}
    self.Canvas_panel.Bind(wx.EVT_PAINT, self.OnPaint)
    self.Canvas_panel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
    self.Canvas_panel.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
    self.Canvas_panel.Bind(wx.EVT_MOTION, self.OnMotion)
    self.Canvas_panel.Bind(wx.EVT_CHAR_HOOK, self.OnKeyUP)
    MainCanvasSizer.Add( self.Canvas_panel, 1, wx.EXPAND|wx.ALL, 5 )
    
    MainSizer.Add( MainCanvasSizer, 8, wx.EXPAND, 5 )
   
    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    # RightSideBar Sizer (comprises Info, Buttons and Logo):
    RightSideBarSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"label" ), wx.VERTICAL )
    
    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    # Info:
    InfoSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Info" ), wx.VERTICAL )
    
    self.infoModuleName_staticText = wx.StaticText( self, wx.ID_ANY, u"Module Name:", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.infoModuleName_staticText.Wrap( -1 )
    InfoSizer.Add( self.infoModuleName_staticText, 0, wx.CENTER, 1 )
    
    self.infoModuleName_textCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER)
    self.infoModuleName_textCtrl.Bind(wx.EVT_TEXT_ENTER, self.OnModuleNameTextEnter)
    InfoSizer.Add( self.infoModuleName_textCtrl, 0, wx.CENTER, 5 )
    InfoSizer.AddSpacer(3)
    
    self.infoModuleType_staticText = wx.StaticText( self, wx.ID_ANY, u"Module Type:", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.infoModuleType_staticText.Wrap( -1 )
    InfoSizer.Add( self.infoModuleType_staticText, 0, wx.CENTER, 1 )
    
    self.infoModuleType_textCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY)
    self.infoModuleType_textCtrl.SetToolTipString( u"Module Type, e.g. Partition, Link, etc." )
    InfoSizer.Add( self.infoModuleType_textCtrl, 0, wx.CENTER, 5 )
    InfoSizer.AddSpacer(3)
    
    self.infoModuleLocation_staticText = wx.StaticText( self, wx.ID_ANY, u"Module Location:", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.infoModuleLocation_staticText.Wrap( -1 )
    self.infoModuleLocation_staticText.SetToolTipString( u"Module position, top-left corner" )
    InfoSizer.Add( self.infoModuleLocation_staticText, 0, wx.CENTER, 1 )
    
    self.infoModuleLocation_textCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
    self.infoModuleLocation_textCtrl.SetToolTipString( u"Module position, top-left corner" )
    InfoSizer.Add( self.infoModuleLocation_textCtrl, 0, wx.CENTER, 5 )
    InfoSizer.AddSpacer(3)
    
    self.infoModuleSize_staticText = wx.StaticText( self, wx.ID_ANY, u"Module Size:", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.infoModuleSize_staticText.Wrap( -1 )
    self.infoModuleSize_staticText.SetToolTipString( u"Module size: (width,height)" )
    InfoSizer.Add( self.infoModuleSize_staticText, 0, wx.CENTER, 1 )
    
    self.infoModuleSize_textCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
    self.infoModuleSize_textCtrl.SetToolTipString( u"Module size: (width,height)" )
    InfoSizer.Add( self.infoModuleSize_textCtrl, 0, wx.CENTER, 5 )
    InfoSizer.AddSpacer(3)
    
    self.infoModulePorts_staticText = wx.StaticText( self, wx.ID_ANY, u"Module Ports:", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.infoModulePorts_staticText.Wrap( -1 )
    self.infoModulePorts_staticText.SetToolTipString( u"Module ports: (array;name1,name2,...)" )
    InfoSizer.Add( self.infoModulePorts_staticText, 0, wx.CENTER, 1 )
    
    self.infoModulePorts_textCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
    self.infoModulePorts_textCtrl.SetToolTipString( u"Module ports: (array;name1,name2,...)" )
    InfoSizer.Add( self.infoModulePorts_textCtrl, 0, wx.CENTER, 5 )
    InfoSizer.AddSpacer(7)
    
    self.infoSeparator1_staticline = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
    InfoSizer.Add( self.infoSeparator1_staticline, 0, wx.EXPAND |wx.CENTER, 5 )
    InfoSizer.AddSpacer(7)
    
    self.infoPartitionsNum_staticText = wx.StaticText( self, wx.ID_ANY, u"#Partitions:", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.infoPartitionsNum_staticText.Wrap( -1 )
    self.infoPartitionsNum_staticText.SetToolTipString( u"Overall Partitions number" )
    InfoSizer.Add( self.infoPartitionsNum_staticText, 0, wx.CENTER, 1 )
    
    self.infoPartitionsNum_textCtrl = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
    InfoSizer.Add( self.infoPartitionsNum_textCtrl, 0, wx.CENTER, 5 )
    InfoSizer.AddSpacer(3)
    
    self.infoLinksNum_staticText = wx.StaticText( self, wx.ID_ANY, u"#Links:", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.infoLinksNum_staticText.Wrap( -1 )
    InfoSizer.Add( self.infoLinksNum_staticText, 0, wx.CENTER, 1 )
    
    self.infoLinksNum_textCtrl = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
    InfoSizer.Add( self.infoLinksNum_textCtrl, 0, wx.CENTER, 5 )
    InfoSizer.AddSpacer(3)
    
    self.AddModule_staticText = wx.StaticText( self, wx.ID_ANY, u"Module Type:", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.AddModule_staticText.Wrap( -1 )
    InfoSizer.Add( self.AddModule_staticText, 0, wx.CENTER, 1 )
    
    self.AddModule_choiceChoices = [ u"Partition", u"Link" ]
    self.AddModule_choice = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.AddModule_choiceChoices, 0 )
    self.AddModule_choice.SetSelection( 0 )
    self.AddModule_choice.Bind(wx.EVT_CHOICE, self.OnAddModuleChoice)
    InfoSizer.Add( self.AddModule_choice, 0, wx.CENTER, 5 )
    InfoSizer.AddSpacer(7)
    for choice in self.AddModule_choiceChoices:
      self.Canvas_panel.modules[choice] = {}
    
    self.DeleteSeparator_staticline = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
    InfoSizer.Add( self.DeleteSeparator_staticline, 0, wx.EXPAND|wx.ALL, 5 )
    InfoSizer.AddSpacer(7)
    
    self.Delete_button = wx.Button( self, wx.ID_ANY, u"Duplicate Module", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.Delete_button.SetToolTipString( u"Duplicate a selected module" )
    self.Delete_button.Bind(wx.EVT_BUTTON, self.OnDuplicateModule)
    InfoSizer.Add( self.Delete_button, 0, wx.CENTER, 5 )
    InfoSizer.AddSpacer(7)

    self.Delete_button = wx.Button( self, wx.ID_ANY, u"Delete Module", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.Delete_button.SetToolTipString( u"Delete a selected module" )
    self.Delete_button.Bind(wx.EVT_BUTTON, self.OnDeleteModule)
    InfoSizer.Add( self.Delete_button, 0, wx.CENTER, 5 )
    InfoSizer.AddSpacer(3)
    
    RightSideBarSizer.Add( InfoSizer, 1, wx.EXPAND, 5 )
    
    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    # Buttons:
    ButtonsSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Buttons" ), wx.VERTICAL )
     
    self.New_button = wx.Button( self, wx.ID_ANY, u"New", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.New_button.SetToolTipString( u"Start a new layout" )
    self.New_button.Bind(wx.EVT_BUTTON, self.OnNew)
    ButtonsSizer.Add( self.New_button, 0, wx.CENTER, 5 )
    ButtonsSizer.AddSpacer(7)
    
    self.Open_button = wx.Button( self, wx.ID_ANY, u"Open", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.Open_button.SetToolTipString( u"Open an existing layout, from either a pickel file or a plist file" )
    self.Open_button.Bind(wx.EVT_BUTTON, self.OnOpen)
    ButtonsSizer.Add( self.Open_button, 0, wx.CENTER, 5 )
    ButtonsSizer.AddSpacer(7)
    
    self.Save_button = wx.Button( self, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.Save_button.SetToolTipString( u"Save layout, as either a pickel file or a plist file" )
    self.Save_button.Bind(wx.EVT_BUTTON, self.OnSave)
    ButtonsSizer.Add( self.Save_button, 0, wx.CENTER, 5 )
    ButtonsSizer.AddSpacer(7)
    
    self.dumpLayout_button = wx.Button( self, wx.ID_ANY, u"Dump Layout", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.dumpLayout_button.SetToolTipString( u"Dump layout into stdout" )
    self.dumpLayout_button.Bind(wx.EVT_BUTTON, self.OnDumpLayout)
    ButtonsSizer.Add( self.dumpLayout_button, 0, wx.CENTER, 5 )
    ButtonsSizer.AddSpacer(7)
    
    self.Exit_button = wx.Button( self, wx.ID_ANY, u"Exit", wx.DefaultPosition, wx.DefaultSize, 0 )
    self.Exit_button.Bind(wx.EVT_BUTTON, self.OnExit)
    ButtonsSizer.Add( self.Exit_button, 0, wx.CENTER, 5 )
    
    RightSideBarSizer.Add( ButtonsSizer, 1, wx.EXPAND, 5 )
    
    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    # Logo:
    LogoSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, "" ), wx.VERTICAL )

    logo_data = b64decode('iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAADO7ElEQVR42ux9B7xU1bX+mt7n9sa99CYgCAqKvUVjVLCg2EBjNCrW5L28JKZonmnvH02eT/NS1WhsWNDYYhRRLKDYRVHpgvR6uW3mTv2vb52zhz37nkGMgOY5+/c7d+bOnDlln72+9a2y13bl83kqt3Irty9nc5UBoNzK7cvbygBQbuX2JW5lACi3cvsStzIAlFu5fYlbGQDKrdy+xK0MAOVWbl/iVgaAciu3L3ErA0C5lduXuJUBoNzK7UvcygBQbuX2JW5lACi3cvsStzIAlFu5fYlbGQDKrdy+xK0MAOVWbl/iVgaAciu3L3ErA0C5lduXuJUBoNzK7UvcygBQbuX2JW5lANiDzeVyfeqflPj8Ex9axOOhS0YOp8GuPL2/pZWaQkHq6EqQN8c/zWVo+Ogx1Hb8BErzfpTL0a+uv54SiQS53e6duo9gMEge3rdwT9q9uYp33qmbw3kxFnPGePzwww8/e8eXW8lWBoA92HYSAD4tSjg+wDIAlNvOtDIA7MG2EwDwqSmC1ooeZBkAym1nWhkA9mD7BAD4LMKvN3mgZQAot51pZQDYg20HAOD6hM/N7/O0Yz9AvgwAPdtvb755lx3rn2mXX3HF53p+p1YGgD3YSgBAKQlxO3yfL/Fe/yyvfvTt0SNpyL8wAFx+2WWDvF7vWblcLsXb3SxAqz5L/9/8OQPAFWUA+HK3TwEA+Mxt/J/XXvWWU68uj5fGjRrpq4hGI+FVK6pHVFZmeudz697b2ppqZgDo/BcBgGnTplWx4P+MP7uAjx/Ad9lstpNBYNJll1321D/b/2UA6NnKALAHmwMAOEmHrvldDu/RdBMgg8d48IB+TacN7PP1vWsqJ/rIvVe2bZu/tb0j39nWsXhFW/vjwUDgls1diRWBLzAAXHXVVa5MNvvv/P5q/qha/46FH+fqzOdyJ10ybdqsf6b/ywDQs5UBYA+2nQAAXfO7qCcImC3t93iyV+wz/LxJgwf8JOJx90vzh9CiuUyOujs7qW3zZkq2t9O2zsTajdncDSziN1IumxsxevQXCgAuv/zyo1nr38zHG4b/MS7lWnAvEH6bIbhdrrZ0JnPCpZdd9tKn7f8yAPRsZQDYg80AgFLa32VsTowADy0T9fnouv1G/fdhvXtd6vJ5KRSLkS8YIDebAjhXclsbbduwnrpa+XXTZkonkrSxO/Xohnz+whFj9t34RQAAFoohLPi/Yc1+gtpXHRNjE+fAzQIE0DwWG2hNpdPHX37FFS9/mv4vA0DPVgaAPdg0ANgR9VcgoIOB/l7ov4fp8BWD+v/XxD69vhuIRqiqpobCvAWrq8gVCBFlM5Tu6qSOjZuobc0aSnd00MaPVlCmrZ3WJ5Kv1Yw/+Iz2iScvT0PgPwcAuPKKKyr5t7DzL+R/AwWNrzWb9hfOgf8ZLBQYtKbT6WMvu/zy13a2/8sA0LOVAWAPth0AgKnx1av5XrXO8RWxg6/q02tmKBTyNjTUU11LM0V481bXkicSZRbAmrK7m9JM/zs+XkmJdetoY3snbY5XUkcFb/HKVdmGxr/6fb6f8xjo2lMA8IOrr3Z1JRLT+Hc/4XPV4TOl3VUTzc/MBK9qM/93W+femM1mv3LJJZfM35n+LwNAz1YGgD3YdgAAJvV3a5vH+D7HOjFxeV31n/YJB6dWVVVQXX0d1bLwVwwcRMGW3uQJRyjPmtLj91E+laYsC8vWQJA+5kMtXb+Rln20nDYyIMTCYRrQv/8TfMxzfv6LX2zLZDIiaDtzH/8MAFx15ZWw8/+Hx9wI+cq28XWhxqscE+PSwSRQ49W1/dgbk8nkkVdceeWCT7ruMgD0bGUA2IPNHsg7sv11re/RNt08SMc97vi/xWNz6rzu5uqKCmpsqKNYUyNVDR5Ccd58NdXkiVWQt7KSslXVlIpXUTuzgU1r19LCDz+kRFcX1Tc0kM/vpyRr/Y0bN77y6GOP/er1119/jMdD5pNSlj8tALDgD+H9fs37n4j/1Zjr4uvYvHmzvHoZeOrq66mC70c/j5gBZNk9ACfW+JS3nYKCiFaIcD3vd/i0Sy9duKPrLgNAz1YGgD3YSgCASfuV8OO9l3qygORIn3f/yX7/E6F8zlMZDlJDYwPFamupesggqhyyF8WYCXiaWyjXuy+5YnHyQuhYaF577TVasWIFNTU1UTcDwkfLl0P4RUij0eimvz3yyJHz589/D5rYz+AAextNsYKC9t1JALj8iitiLNjX8vEu5/MHPHw8tttp0eLFtHzZMtrW1iYC7ubfZvkVwj148GA6+KCDijpInVcLBxauI5vJyLn5/dpcPn8omwNLS/V/GQB6tjIA7MFWAgBMZ58SeGxeKmYB2Kdjf5/3rOPdnt/5clmq9nupIhalaFUl1Q4cQHV77UWBMftR4NAjyBONUZAFGbb9M888Q0uXLKF+/fsLve5OJkWIt23bZgk4tG0+/xQDwGSPx9328tyX6a2335YL3HvvvUVLd3R0FJxynwQAV1511aV83Gv4+wYACX77zjvv0OrVq6mSmUlVVZXsy/SdOjs75RrxftOmTXT00UfTXnwfaAAF3QRQ/ah8FQIgKokol1vJ22HTpk1b4dT/ZQDo2coAsAebqye3NkN+StB1AFCbAoDEfj7vice7XLe6Mlmq4OcX9XsoWhGnyvo6qho1itznfoMiffpSS2MjdbLgPvrooyJ4BxxwgAhWOBSiba2t1M4aGFoYwtmdSokQxWKxZ5qbm8/4zW9+veXue+6Vi9xnn30EANrb2z8RAK607Xz+fISi8O+99x4tW7qUmltaqJ5pPoQax2rjc69fv542s9AH+HjYF4DUp3dvmnTaaarPCra/3n12dmCPKAHvt9wGgR5pw2UA6NnKALAH2w4AwIn6K+3vo+0AID6AXl5P77Pc7n8E0plohK3jAD/CyoCPAvEouS+8mBLDhlMLmwSw819l2t/GQnXA+PE0fPhwikQiIkzQuFvZ/oYg4j22ZUzLsf8++4x6cc6cOZOn33f/OlzkzgDAt771rb78/iYWzInCKPgcK1aupFdffZWaevWiIUOGiIC2MvBA469bt45Wffyx/A9zI8SgBLMEjkgc+4ILLpBXtKIxaqcLF0UrABCkOVnz+aW8z+EXXXzxar2zywDQs5UBYA+2TwAAnf5D4JXg62CALc+H6T4/4P9Dn+7UcVl+fgH+MMSb/9BDaPWRR1GKBXWvoUMJNjc06tixY2kE03jW7nJS2NxpFjQIHMChg/fvYgCAfb6JQeHNN9+kvr2b3/zf3/1+0muvv/HRjgCAqX6MX6/1+XyXskYOQTBx3JdeekkYxkGHHCKgA0HHMbZu3UqLFy+mdWvXigaHeQAAUOMQn+EYX//61ykej28P+VkdaH0PVqA6z36v9lMmAb9+mEqlDrvs8ss3qs4uA0DPVgaAPdgcAEC3/3X6r4RegYCfin0BXaNDwfGn53J3bOtOefFhbUUFJb95Eb29ehXVs429Hwv9Uqbdffr0oUMPPZTq6uqEZuNEHy5cSD4WPGhlaFwIJyIDEFw3a+8kv27csIGFLb3gRz/60SkdnYnFuHQTAL7zne9cygJ8DX/QIJ56HksrWeu/8MILwjZGjhwpdj1ACAwDZsj7778v1B8sAceB999lMwmXLeB4Pf/88wUAiEiP+4uAY9Mdk6aPQAEBtwV8vCMuueSSTfjnpptuUs+h8ADy1g/1Z1T0mTJBXFr04p9tbB593kOwRysDwB5sOwEA+gbh99uvOhvAb/I8yDunRILX7tWVmNKezVPThAm0DkK/YAEdd9xx9DHT63fffZcOZQ3cf8AAamlupgoGBtB8aGdo3kmTJlG/fv1EWCCoCVvLQ1hz9qD/+OMVi++//4ErXnxpzlP4HNr62muuOZTP/1u+jlFuy3koN/DS3LkCOl/96lepgc0PaHv4F/C7JUuW0AcffCAsA8xEaA8Lqoo0SNfwluHv8fnFF10kIKOAhWzHnymIKkyIpo9kZSIwAMxnkEOIsPWOO+6Q4+N6sK8yMXBP8hukTzP4yWc+H2UYjJhFUJQZTAebLfjMyxv9kzJzHrOaL1orA8AebDsAANP7r2t+BQB+2m4KoKWr/P7gt6OBW0Jdqb2bfv4LWspCXF9VJY62W265RTRoX2YAcWYHfVpaqJY/h+ZcweCA8Nnhhx1GjY2NFA6HyR8I0No1a4S2V9fUiI2+aOEiNgk2UWdXZ372c7O/dfzXvvYIC8CvWbgmKUGExoZGf/LJJwVgjjnmGDENtrDwA1AgOAvee48WMwDoGj+vwnm8YX+cH4IFU6SRwWPKlCnbhd228TXNXqT19fdu+5iqSd5APv8Gg8CRlVVV7WkWaIAcjof7RqcHQiErssAbrlc+Y3CAmQSwqOL72sosKcSf6ebKp21nn3PO5z0Ee47JMgDsubaTAKDb/TDvfdqrzgLQugb6fYO/3dz4h2E3/rZmFVPtIYMH0+OPP04fMNUOw+HHAgMgAChUMzjU1NZKJADaDwO+qrpaBjsShDYw7Ud4Dq8ACNjuEI4Ua8VcLptatWpV3h8I4loKtBwVe2Y98wyN239/Ouigg6iTNT4oPxKM2ljQ3nrrLck9gKaXDSm9/HswhBEjhlNjUxOtWbWa3njzTWEHMEeOOuooOZ7Wb0U2vh4OVDa/Dg46ZdciBK/w/19hLd4JVqIAAN+KaWQDAKIm8hkDEgAAzKiSAbSV7ynIn30WADiHQe2L1soAsAfbpwQApfWxBWg7G1AsQB2rfWQ8tu+Nf/zT9dFBg6q6WOjuv/9+8jFVhbcdGhUaFAO6hoUdQo0B3YtNAmzxWIzmzZtHq1n7gw1AMGG/Y1/4BzZs3Ezr1m/g1w3kdWVp+YqVvE+jnPj555+n+e+8QyedfDINHTrUovwwIVhoWvn962+8QWv4uKDOuB4Ij8fjpf3225e+f/X3qaVXL/Lw5x3MIK648ipawKAF5+APf/Qj2V8P/+nJPwUwgHZ37ucCMBQajuN2z2WQOZoBLVkGALuvygCw59ouAAAdBNRv8QBbzz7rrInXXXfdtfPnz6f32daGpkWabZsdb1cgAHsWzAAC3sACj2zAVatXU+/evUXwD2WzACCweXMrvffe+7Ry2XxydW8knydJ4WCOgtFGev39bTT7hbksHAnxI8DBiAQeAI5K5kH4D+eHwECYIWwAn9GjR9N/fOffWfP3okyqm4XUJdGBf/+P70niEZyTF114oWQGFvwLdrcBkJQfQH2nJQHJPvqkITWfACyoEDrM52ezYH+Nt2QZAMoAsEfbTjoBdwQAOhNQgIGW44Gf+NnPfva9UaNGnQDbGwMXSTaw5UHJQXtBsQM8gCGIsPMhLKtXrRImgPRbZPzFKyppzfottPjdZ4k2PE0tDTFq7D2MorEKtoFT9N6SLfT9//o7+UK1dPrpkwRoYO9D+JFdiPNB+HFOmBnYwjbrQDjxkksukYSgTLpbbhtOtXffeZt+8p8/ZcBZQOeeO5V6MTOQm7L9BDr9t/uxSMubSUI6YNia3/qN/R0L9kz+7nh/IJApA0AZAPZY28kwoA4Ayv7XNwUKXipOEU61tLTUXnbppdeMHTduMLQbhHstU+p1yLZjbSwZfzygAQD9+/eX7+CAO+zww6k3C2UwGBEHYWL536hP/ilqrk9RuHoYBRsO5NfB9PjsJfSfNz5K+4wZTxMmHC92PgSjywacj1eulPkGcJwhsQcbJvfA7zBixAg6d+oU6t2nD2Uzae4LCWbItOVb/3wL3X7HnSKw0y691IoU2Jpcz/JTwq7+18ODaGrasO34KzIBFGCo/fj9P/h1AgNYpgwA5bZH2k4AAF4VAChNr7OAIG13CKrcAN0cyLLgV3zzwgvPvvjii49FGHDhokXiBISww8GGxJ9hw4aJkMJBh/Rg1BMIheO0ecNqqul8lEbWLqCakIdcTMd9Ebbd4wPp9tlR+vPDy2jCiRPp4IMPZA3fRu3tbQXhR3jx9ddfFyEG+ESjUapmMwMTj+B0POWUk6lvXwh/1p4GnJOcg1UrltH3f/gTepvp//Ff+5qYIboTT8X8TX+AGQ3Qw4OF98p3YP9OBw372I/y5yczAOTLAFBuu73tZCqwngmoBF3X/vp7tY/OBLI8wPP/9u1vX3DiCScc98STT0pYDQN6JWt30cgsmA899JDY5i1s+wcCEcokt9HYypdov5Y1VFEZYuF3kyedpQwf8sYn3DR7YQOdffYZNGTwIKb8rRIu6+pKUiLZLeHCN998Q24Igo+MQ0Qd4FeAc/Crxx4jCUnKrrdkM8tg0E3/8z//S/c98JD4Js466ywRdp3ui4ffni1o92Gh83o4+qg4VJhz+I3+vw0qM9gUOE2dpwwA5bbb2j8xF0AHAMUEguTsFNSnDmPk56758Y/P33/8+K9s3rhRZuAhEw8OPnjv32TtX1tTQ5ksa8JskiYO/ZAO6rOVohVBcvvchGDf1i4X/fTuHK3qHkbnTZ3MwFEl9n5XZ4et+bvpgw8X0dvvzKdc3i2aH2FERBOQfASmcdihhzDItLDCzxcKe7I4Uy6TpNtvv5Nuv3O6ZB1OnTpVfBF2P/Wg/LrmxiuYhpoV6LIdgnlN4M0CIwXHoO0LUMe02cW9Ab//bFcZAMptdzaH6cClZgPqE4GUkJt+gFIgUJgzwIPb9fOfXXfBySefctCGDZLQI8KGpB3E5FNsa69avZ4Ob15MZx3SyZrbT9muLIOAm5ZvcdNPp7vJWzeezjnjJPEVbNtmTeRJytTdBC1YsEBSe0HlA4EQhaNxqm9opsGDh4jD74ADx1NLcy9b47vs6j9Z5ihJuve+B+jPt91Fmxichg4ZQhMnTiwSLCl9ZP8vhUC1qkGi2fFeq14khUFYYPN2VqLLcA6q+QPwD0DoC3UFVKQgn/8rA9h5YDZlACi33dI+ZT0A0xnoZAro4GBOHsImhXQuu+SbZ379/AsPz/Cgf3bWLPHQIwHog0VLKbliDp3YbyUNGxqkmhoPxaNEr36Qo58/FqQh+xxDp078qgg7MgS7ujBvv0s2+BcWLVooUQCf1yee/tq6OhowaCjts++BkhTU0tIit2VpYLa/c6y1c9300MOP0B9vuZPWrVsrgvb1884Tx6Su8VV/KSAorIxi1B1QGYIQbJ3y66aAdLKdIdiDEdi/l1mGRH/k31xSBoBy2y1tBxWBzKpATiFBJehO2l9/X7QNt9qkQQP7Nx577HFsq79FjU2N5PH66clH76fe7bNoYFWaKqNetu+99ObHRDc9E6Ujj51ERx42njra26zZgl2dAgRdne3isFu2bKnE7D1et/gSYmz7N7f0pX3GHUZHHX2M+Arcbq8tpXC4sXbOJujvf3+Khf+vtGrVKkkVPvHEE2kUswWjj3r8rxx4ZrjPDBWqplcU1oXezBg05xewaXEzn+HKMgCU2y5vO1kUtFRasIoM7GgrsIV+/fr1GTN69FmRaHRvER7exo0bS/F4hXjl123aSrPv/Cn1ybzDn4Uo4s/T2+s89OzqRjp98hTad8wIyebrZIHvEtqPikDb6K033qCVK1ew0HuYmruYTjMAeD3MKGpoyN4H0TEMMvvvvx+FQlEGB59o/lw2xdy7m56Z9ZwI//Lly8WHMGL4cDrppJPMvumhoRWlV985+Qecfo+mA4TLnneQNT7TmYDkCaTTN7Kgf7sMAOW2S9snlAU3QcB0COpMQKf9RYJfW1tbfeSRR06tqqw8immxFzF10GO8JliLN/dqoHPOvYBWr/qIFs34D4pltpIv4KcXV7ppSXoQXfiNb9CA/r1py5YtovWt7L4EtbVupXnzXqa1a1ZRwO8lnycvWXw8gIhBhvrvtT8dfMihdMiBYylaUUnxWDV5fQEW/jRLYYKef2EO3Xr7PVILAJmJfJ10ztlnC/VXfdMjhVcr9IFxqtYEMCsEmaFClSWojgvwU6aCPu2YiHqED9Fsc+KXXp/vBwiXlgGg3HZJ+xQLgzgVCCkFBLJxC5522mlnNzQ0nMUDOAYvOQQD01nxPp3m11Sa0qmETAEes/cQSrx0HXldabr/TS+l6sfSRReeb3n6Rfg7qMtOHNqydRO9PGeO2Ox+Fn6We/K68+RxZSTsN2TkIbT3yJG0/75DxXaOV9ZQvKKa9w3yPlma8/I8uuPOB6QYKHIRIKCTzziDBgwYUEjvlRt3mO6r7Hv9O11jq/oBRQVCDM1uLjBiCrzTFGN7v+vSqdS1yKMoA8Dn1KC5fvGLX9DPf/5zef9/qH1SfUBzXQAvOQOB96wzzzyGhfrbHq+3D7QdprzCww/hwiv6rbs7KZ9jPnyGwaCpsZaGuV6nx19dR6H+R9OFF5wrk3ZU5R7M6kOBkPUb1tOLz8+mzZvWswD4CLIKAMhlUlQRj9EBh36VBrG9P3xgPWvalGT/xdjMiESivIXpjbcW0IMPPUYLPlwhIUTMLDziiCPo4IMPLgg2NHtBy8NDbyT06CE91Ypov5bs0yMZiMjRB6Be1dJjPeTATiFmAP1hOBz+RRkAPuc2c+ZMuuGGG+jpp5/+vC9lV7WdWRvQBAG9UrD3jMmTR7Lm/RELzYHKC45NBB/CblN/CB2EGZ+lUt0seDnJ4sP8/zHjxtOUs8+U30jlHnsOP/ZF3sDs2bMljRiOPi9fgc+bF5u+siJOx504mdlEH2quD1I62cbf5ygc9DIIBCkej9Abby+lJ556njrbNtLyVR20cWuC9t57OH3tuK+K0PvsWYJmyq4+248MLW1q6yKnoU33tdqAhVBh3s4TUPMCpJy4/Rtz6rDZuE//o7Or6wYUUy0DwOfYMJhRbea55577vC9lV7WdXSNQ37wTJ0yoP/iQQ64NBoMonSt2PgY7nFaK+ovdbzMBS/BThaKbWAtg8aJF9LUTTqRTTj5JhL5NPP1dYvNj35UrVnA/zxZQgJCqlkknqb6uiqaedyH16dObYsEUJTu38kBKkt+To4AvRxVRP738xlJ6+Ik5FPCkye/qpkUfJ6mhuS8dcNDhVFdnFSZRaw+o8mDSIZow6n4BPc9fLwle+B1vWXvtQFU4FE0XbCf7X603qNKOzUIj9rly3CffZtPlJtUXpcqE7ah0WBkAdkH78Y9/TD/72c8+78vYVc1V4jPHtQJHjhwZuPCCC77NgvMt1mYxFdcW7c8bXjM2E5CFNuzCn6D9aRsYULIL8wPOYBsc9ffb7LLguvBjH2h+eP9VyS40eMQhvFdedRX179eb3Nk26mzfRLl0J/lYyL3uNLHip7mvLqS7ZrxA8bCHKiJucueS1O2uptNOOYo6kj5K5LECUGWB/oOGu9XkH6LCcuCq6Rl9ZjjQiQ2Yi4eUYgzqeOYKxCbA2OfjLs5eyq9/VKCRtX+rTBDdXCk6hp1nUAaAXdC++93v0vXXX/95X8aubKVAQF8W3H3jjTdOjkaj1/H7fnaoqmhgKxMAQg/tl7HZgICCTXexMMfChQul4u6BBx4oBTykaAgLf5ddFHQRgwOEH8KuCz+84UjsufoHP6A+vVso3bWZOto2CfV357vYJklSLJSlua+9T7fd8xy/d1NtpZ8C3qzYzkNHjqPBg5ppQN9aWrYqRVu66ygaiRaW/CLaPpdfT+DpUfBTqxGgVwhS2YJqX91noGcVyjEMf4Le6bm889Rie38wgYvb29puQcpzOwMnzAKPHZ0A40J/ww+iSpyhH2XNA/58ytSpn/dY63nP/5cAwOfD0lOZz/sS/5lWEgR++9vfjguHwzfwQJT1sjAgFc1H02fMQXujZeyUWLUffjN3zhzR7BdfcolU67U8/ZbgQ9NjYRAU7Xzh+eflOPoiodgHHvuf/uznDAK9ROt3bttMycQ2ymc6yJXtokggTa+89i79+c6nKRxwUV1lgEL+PAWZMdc1tVDfgcOpubGaGupj1K9PLX20Nk2L1oQoFov38Mqbcf4eHaOZCer+VB/Ie9t3oD4zVx8uzClQ0QNtdqHe8g6ORd4vw4zq6wyOd8NXgjqBOgDgFTUQygCwm9qOAOB73zqPXn/rfZr94huF2WP/Qq0IBP7w+983sb35ax7Ak8lmA6ZNrA9+VfVGfa4cXgCBfzz1lNj9l116qUzS0YVfaD9rfpTjQjnvjD0XXzUMckzqQZ9jam9nO7OG9i2U6NxGmVQHZdPtFPKx8L/6Nv3htkdZ4PNUU+FnQCAGAOL/U1RXX0MtfYZSS99B1NRYR9VVQWpsqKCV69L02gc5ikTt9QocQn36KsGFjtIAQHL7be1fyPtX9NsuGabYgnIE6sdTocSiSkJaM2ci2lWIM/zZlM6urvvKALCH244A4Kc/nEYnfu0QuukP0+kvdz32eV/qp20yKm+66aZwPB6/mgfkt3hwRlRxCz1BRrc11ffmHHo4qzD4HnzwQQGBS1n4MRNQVetVwg/aj6W7XnzxRTKXB4dvYNSoUcTmh8zww+8SiU4JESaT7ZRNbqWAJ0GvzHudbvzdfeRzZ6muys8MIC8swMOmQTTYTfXVIerV1ItaBoyipt5DqKamhqIxP1VVBGndlhzNnNdBFZXVRSZAke1uePeVQxBNTwwqMAAN/E3nod5Hen/q58P+en6CKSP2+brZDJvCV/RgGQD2YNsRAFzzvW/SKSceTjMee45+9qtbP+9L/dTtL7fd9g0W3P/kZ4JZNNs1fonil6rplXIhLD4ewIhbT58+Xeb/g/YjYQepvSjYCcqPaa9I8kENQawToLSgathnzL770m//938la08lFInwM2gkEknWvHma99JMuuHG31KOmUMN0/5Y0BZ+SrD9n6TKsJvqq1zUUBukXr36UlP/fammcSjFKispwPtFIz7avM1Fj8zeTDW19aTuW3fkOc0DQFOCrU8KUqCIps8P2NHiHrovQdKF7ePqv1NNOSptZtHNfTKJ3zxRBoA91D4JAE464TB64G+z6L9+c/vnfak73e64/fbD+OU3LPz7mZVvFM017WQzyUXtB82PWoCPPPqoFOE4lwcdZuphNh+of7u9DBgG5ttvvUVz5s4tONFUw3dYpvv2O+6g+rq6Qradqv4DAMD+LzBruO66/6RsqosqYkEKs80fZ4H3urrI7+6ieMhNVTE31cRcVF/ppsb6ENU19Ke6PuMoVj+UQqEYuT05Coe8tKWTVelT66imrrEoF8BM6CncM1FRpEAAwBDwQl9S8fTgwqtmDuigYy5DbiYj6Z/zfgneTsHKymUA2APt/xIA3HbbbYO8Xu9/scaZVPgQYT0Herr967wjCChhwdJcM5j2r1m7Vpb+QoFNqfzT0iJ1ADEQ1fp/r7z8svxen1evhP2WP/+ZDj/iCNH6yBCE0MNXgAENyvsSC/93+Fl0drRRdTwkqcERFvioL0HebAfb9W6qxBZyUW2Fm+oYBOqq3FRbF6aq2gEU73UAhSoHkC/I9j//NhR0UVvCQ9P/sYbq6pt7LPhp3iuR88Qgp1i+2XeFMJ5WO1BpdXVcp98W/AiGA5L/7+RjncSMalYZAHZz+78AAH+9445qfvkpC+YF/BrQw1VoBYeWLQRo5vz2onXwbPsWDrtbb71V6vNB+FHvL2FX6l3PG7QgPgMb+Pvf/y6/12k/jgm/wNfPP59+8pOfyDExWQchxwwSifgVgjOHTYbLLr9cMgTjsQgFvTkGCQ+FPAkKe9opzMIc8RJVVnqohoW/OswgwEygOuqiGgaByipmC5WDKNwwVuoNegJxvhEIjps6u900/cm1VFPTVNDqaBn7HvXVf3ShVanAatUhvQ9VcxkCbIYW9X6Q6IEdTXBrx1T7U0+Q6GRhP46B8qVQGQB2X/tXBoCbb77ZHYvF/t3v93+f+71aL3jRo4CFZs+a4SwnGxmCOWvWLHqCBfvA8eNpwsSJMuiQyYdCoJuZ/mOFHtTeR+wajjjMydcdboj1Y0We37Hd39zcLJo/b4MQogMY1GANX//GN2QBD/gVXC7W/Cy43lyC/Nk2BgQXVbDmj7Hmj/uJamu8VFfNQBAhYQMVvMV4n3AkQIH4APLX7Uu++GDy+CsYjVzk94MB+eivj6+myuqmImcfmk7HdVNBRQPMoiG6w68wKcjqxML3JtV3meBifVk0M1EHDXVebq3d3d3H8w4vlwFgN7V/VQBgrX8ma3ykMA7UC1Wg6YNYb+YAV5Vr9Px1dYwVTP3vuP12mWRz4oQJ4t2Hva8SffD+jTfekJV8kMCCkF5dbW0BBEDxDzvsMLrmmmukViAiBmp1HrkWPjfW+DvzrLMkTTgai0mdP7/fQ35KkCu1jQKs9SH4tSzw1XHL9q/0M/Wv8wgQVHgYLFw5ilZ5peagL+gnX6w/+Wv2I298ELn9MXJ5vOT1sbC7A3T3E2soXtlU6CO9Two2vH1tSkAVY8gZml4Xan0xEYk82MCQ0RyhOnAUJhC5ti9FrvwKenRBfpfLtabS6WO5717LlwFg17d/NQBgwT+AtfNvkMijYsqFqakOMe4iWqmZAKaW0m1hJPhgOTCsqYfFOSHgqOIDk0BCfqzZUbL7/QULZH+1Bl9Tr16yUAh8AkgNvvjii+nluXMlPfi0SZOoT79+hXwCmBWnn3YaLVy8mCricfv8HvLlE+ROtUJ5sx3vppCPNX3ERb0avNRY7Rb7v0qYAINCtZcCqSz5wRpqMAmIqbaPBR4gUD2G3NEBbA5UsUr1MaPJki8QorseW0WRil49+4a2m0y6UCsfhuozHSgVABT6zp4zYDr9dO2vHIu6E1GPGOghSZEl65hbGEyO5Oc+H/UTywCwC9u/CgDceeed/fjll0z3J/OgdLsdvND61NRSYSc008mlPsN+COM9/PDDUlkHGlxWAVLCz4MPDAAr9SDLT8XJcS58Bxse3n4IPuYFPPDgg/TQjBk0oH9/uuCCC2SZ8SCbC3Asnn766ZIvgOrCSvi9LPz+zDaZIswyTX4v2/6g+Kzda9gM6NPipd71HnH+xVj7wycQZ+3vy+at6YxBF2bwsNB7yRPpQ56KkeSJDiRPqJ5cmCXoyVA4GKE72RwIxYtXC3KaPFRgVLZ3X+9nvRiosuldmuBnDe1v5lzohUTNdGVzcRL7+428HZlOpRaUAWAXti86APzlttviwWDwWh4Q0/jfkJ6lpg8ejTIWHE2FQaVNY1XAoA8ytR88+Y899hideeaZ4tzDEtZI3ulUws/vX3nlFcn/12fc4RrAErCm31VXXSVLgqFS8FNPPSWhQpT3xqzLS6dNE+11JrMDLCKCnAKMFszZxyzDfLqTakIpYrknXC6uOMj/xJkBVIaZ+jMIDOzvpb5NXqpmcyDI543EmCXEPOTOWwxI5AxC6WcQCPcmT9UoZgRDyBOsx4n4+zSbG1G65/FV5I80FyoCu7T+UPdUZDKhbLgWLVDNXE7MybTQ9zHrCOrnNh2KZuIQv65PpVKHe7zehWUA2EXtiwoA06dPd7OwTuNB8GMeEA3qc51W6nbpzhSrLLABZY9qy2Uhc++ZmTNlYs/oMWNEcCH4SvgBBKDzqMLj1YQfDXn/Lc3NYs+DASxnev/inDm0ZvVqYRA4xsCBA+nEE06gh5hdvP7aaxRn4cd1wNmo6gzgWvzuDDVEkvwKBiARPTYDXJYPgAGggQV/8CAf9W7yCDPwsvYPRNzkDfM15XjnLASK+4CZgBt1BqO9yVc9lryVI8gFc8CFPklSBTOPux9byb9r7rFwiAmSeoTEzAtAUwJuJgY5Te1Vn+tp2KYPR9/XzGLk92u5rw5lAFg69dxz9+iY3JlWBoBd0O6+666JrGFxUUNKzUrTs83MhS7R9Hr3pH2mmk45Zz7zDM1hgb3oooskT98Ufjj85rLwo/6eqrajGuL60PzwFUDzIxoAMwI2PnIHNqxfLz4AgAaOh+hBhBmBaH41OxATjezoBI4dYBDoHeukEH8d8DETYO0e5tfaCqb/lW6qYzYwaJCXmho9FIStkGEgCbrJF/Fa9foy20HAxUjiZU3vZRDwVe5D7gCbHAQBT1BFVSXd8+hS8scGFTIAhSlpHnpF54uSf4iK5oboJoTZdlRVqFBFSDMl7LkBBd+Cad7Zx1jFIHDIOVOmrNhjg3InWxkAPkNjO38fFvjf8IA4SncIOcWaTW1RijrqZoIeo1ffP/7441KWG6vsQktvVsLPGh/Cj8IeiNPDMagX8kCDEGAJrrHjxtHYsWPpK2z3Y83AJUuWSIgQS4chZ2Dzpk3yOWg+inYozS8FPPiYyHhT9QXU9QfZXh9S3UlRX5aCfhd5wQTYHKhlu1/i/wwC/Qb4qKGOBTzDv4MfAOHDGINAOmevHGR59rEykSfcSN4qBoHqfdk8qBAQyOe7qJIZxfSnNpEnMtjRMdrD8ecwtVfvT7MASamyYyYbcGICTnMG0EQpEC3vTiYPPfe881bv9oH5KVoZAP6JxoLfxIP+ehaKM/jV6zRoSg4YoiJtZca39RRg/Xv87sEZM0SrY2IPltjeagt/h0zOSQp9h2mAstum8KuGkuAQ/ssuu0wG5kcffSSCj1esJrycXxEuROhQhQEh/Ij5Y5572q4wpE9JRgMIhL0ZGlXXSlVBVAayQMDH91DB5gAiA1UhopYWH9XXu8jDAEAQetH4HgEEIT9wzqctJuCJNDAL2I98NWMYBKop7wLgJKmyOk4PPbWKUp5mx3JiSuuTwa5Ms4o02m4Ku6n5zfkC5vNWxzGrG6s066xVrm0pg+fhXyQQKAPAp2h/ue22cCAQ+AELxre43yIuO4XUrD1vpIn2SCHVk1F0u7QowcX2UqvfYWLPmjVrRPjr6usLU3pF+O1lul984QURZBF+Q9uBFqOIBWb3XXvttWL7b2ttlXkDyAXAsT/88EM5D1gFwoNSrIOvoZrNBIT+pK6gXWxU0mjtctvqvnDekDdFB/TaQg3BDP/W8gnkWLhjbPdjnkBFkKipmU2DWhZ82i70nrDtgbfT83MZOAbhK6gjb+W+DAJjyRWotsIN1E0V1VX0+LMrqDPTKKxEp+16TQAnZqD2I+3alXNPtVJFSXT/gg44hYlJDufQG3+3iAH0kClTp27cbULyKVoZAHaiPTRjhiuRTF7IA/wafqgyU6+ULW86oHpkrhEVQEM1l51aSvniab54hca95557ZCbfpay1UaNeTelVoT4I8vMs/KDxEEJz2Kk4Nqb0fv9736OTTznFqiHIx0YoEBvKhCH9F0t+IUFIZsWx5oe/ABsYhlpjoAAAhnCpEl8hb5oO7bWWmmO8XyYv9D6TIgqHXBRhJhDn1waEB+tc5PfYMXfepwACebuPBASYSYRqyVsxhny148gVrLFBIEUVlRU0c+4a2tRVV1Ss0zSx9P4vJFspNmaYYOaEIJ1h9JiURFSYRFVqMVPVdPbA17CAX48488wzN+02QdnJ9i8PAPfec89k7twGvo9/LHrvhcW7GgD4+MfwoP5vfjtCOqyEFjFTedEMR5CjzWjuo/8OVBsz8vAKzQ8ajjJeai4/hBJMAKv9fsw03on26/PkEdr79a9/LUt6KXoPWx6Zfd/85jdpNh8Huf+g+hBkZAsiIzBla35Vd9Cms4U+UIxGBAdrBaLar6ubDm36mPrHk9SdwupARIlkXqYAR8IuirFgNzR5qL6GmQPTBJfHJUDhidggkNWYgBcMoZpBYDT56/ZnJlBrgYA7R/F4jF5+eyN9tDEuaxIU5UlYF1gAV71P1LU7CbmeOegynqs6Zs5O+tH7QP1+h0zDfs8gOp+Pe/jZ55zTurtkZWfavywA3HfffUfztd/Ag220JlDPcsf+4p3Xnpr1WQHgrrvuGsZCcANvx+t95DYQX73XW6nP0Xo4pYxsPwUGoPZ/+ctfxBs/bdo0ScjRa/ZD+EHVn589Wyj8joQf2hECfNNNN9GEE0+UY4fsWnaoCXD22WdLuE8+4/0xV6Bv377UwIxBVRLWy46rY+uaX72q+5Bin6ylD65fRkMrOqmtC4VK8wICPp9LJgxF/cSshJkAgwDSiF0+l/gC4BhEp+TgCwAwIErgZbAMVjEI7MMgcAC5/DAHMpI6HIuF6c33N9MHq+GnCBeuTz2LHbEzuV5yno/hlLTl5PTbUeEQ/RqkyIhigdazfpvB/dApU6Z07DIB+ZTtXw4A7rn77pE8oH/FnXpcIUaupXniNZPNvsDffW/yGWe88mmPf/ddd9WzMGGKLtaLD2S1WWhO88qlEx1sRNWcEnzUdWcNEFH3gDDcLbfeKgtuopgHBFgJv3L4bdq0mWY/9xytWbumpPB7WTiCoaCYCUjuwZoKdXZxDwg7ruObF10kQIP/sQIOpg+jAAi0qRQWBe23w5M5O2nJRdsnK+F+5NWeiWfSbqwJOL52MY2oaqet7VmE/SnJYOBhBhACG7BBoKHBLfMDRLum+NqjHmEEcJ8DBLJp5EEABCoYBEaSv34804IonydFHv4sEg3SwuUJenupVxYlyWmz98xoilNfqedYqviI+t4p89DcV59FmCvxjNVnbFa9wp9/5ayzz+7czaLj2P5lAGD69OlN3HnQ+JO5w706Unu0rLnCw7CEbAZWduHOXfhJx7/jjjsCAb//O3ys7/LDiVuH2E7t9Fryuidfp5x6hp/at2iQ2GCl54+bGgf2+J/+9Ceqr6+niy6+WBiACL+d3APhR32/5559TkJ2KIRq1hS1PPceEXoUSW1rb2MtGZPKP3Dm4ZwQ8Kuvvpquv+EGifPDsThwwAAxMyDwEPycLfSqX9U0WFwTrh/Cr8p6qwk56p4VYxAnYTZF+1UtpNE122hLW04WJkl2I+XfJUKPnIGGWjczDlyzS24HIOAJqzUCrVvMpRkAvIgcxBgERlCgjkEgUMPXgeQDt8wwXL4mTa+8l5XViXQHX556Mi713Ipsf5ve69OOCxONHAqV9jCF7OnZJlPQ8z3Mz7iv5jLTOvqcKVOSe1quvvAAcP9998W4U6/ljruE/404edSdYrMqzMPfdXMHT+ffXj158uS15vHh4GPGcK7bOkd/7Xc9Um/Nabh6DTt9QUsygEH/rTqe7kVW17xhwwb63e9+R3379KEL2SZHk9V6dOHnfZ599lnx3pfU/CyUqAKEdFjUA4DJgIGJzMHhw4fL7/74xz/KnH6ABJx8/fr1Exag7kdtOqDhmj220MtKQcgN4FeYEnrYLat8BVrGYDaTotHxD2lsQyttboUj0QYBL9N/HQTq3ZIujMhANpmzHIMavctJ0lBOtL43zvdSt7+kEGO9Mras+b6DtGZTjp59I0lVVTU9knN0ADDB10zXNtcjMMee/lvzGahXM2tRbzpbYrb1Yj6XO/bMs87aoyDwhQWAW2+91c3a6t+4077LHVXnRL2KbsSw88wkD36TSGcyd/P/d3EnP499pt9772E8kH/D59hPX0G2R8yYtufsKxpvepzN8lImSKEpeqmvcqsEB2G43//hD1LIAxNx8L2+VBeEf8POCD9fG1brhRbqtpcEk0gBmxU/+uEP6T+vu06m9R577LFiavRqbpZqQWAE6hp71CWwnXt4D4HHvgi9wTRRnn+cl+zwpWIQal1COBFlybJ0ikbGFtKBTVtpE0AATCBFssow8o1QSbixzk11NW6KVrhF4AEC3pA90UAekMUOxBwIMBOI70W+mnHkifSzQMCdZVDz04atLvrH3HaqrWvooaX18aF7/YsSuOxn7nbw8ptJXU4RHzVm9LFSNH61PATVb/z5TAbN488488w9Vtv+CwkA999//xmsaX4pGllrPXLkqaegOwmeCRyYqcX/L+PtgEJHGLarLuA6vTdjvWbmn9NKtE6ef6WJ8D9m2/3h97+XGP35558vabYQft3hB+GfxcK/4RM0P7z4eK8vByYgYK9zj4pBmD149913S4mwlt69i2bBmf2nNL6+ll/AXiQTm2ICunZTaxNai5Ja58d7VThzeORDOqhxk5gDmWyeulN5EV7MJQgDBJgF1DMIROJuKxIAcyDktjIFFUNLsVB7wARgDjAIVI0lT7Q/0EQShqw6g256dHYr1dY3FZ6lztbMKI56r/epGc4z/QRmUpA5Np3KjZeaN2BXI/4H99eEc845Z4+AwBcKAO6bPv1wHlSohV8ojllUhKGEhi3SWMpus5vu6dXv1MzIk31tx1HRTDDteIXBo9uUxrXp/ztRxUJ/26/IvPsdCz+y88477zwRFmhm3eEnwj9rliX8UJVG07P1cA8qWSetrQuoVgpSQozwHjz9heuk4tVz8L/H1uw4pwodhuwFMqXunQIATN3V+lHWKORzJm3hxz0IEKBoJoMbrmdoeBEd2msjbevIUXeagSFtndWDoiFBF4OAh+prXWzL2+YAtH7ALWxBkXhEB/AUPZEoC/8QmUTkiQ0kF3wCrgxfI+oM+mjGzI3U1Ny3kFylPwt9MlHBdLT+KTzzomiAa/vKREXMgsgxkUhXHkXgo42/orFsLe/2KPfRpClTp+52EPhCAABr/OF887/iwXRCKUeLW1uDrVDJRdvPRPYeSRs7yAYza8QXOsfYV2kflamnf+5Wk4BKHFsHK7U/cvD/xLb4AePH05QpUyQkpxbpdBT+HWh+OPlw/pQWttOpuEyPtdkMHIx92eZ3ckSqa9dtfaXtofmxQfgBBIoNqElCqi8U+HQbACAVhXlTvoFBwcV0RPN6au/KU1cSfgHr/HgUUSQL1eFaPVJCTDEBd5BBwKv5fTCvgDdvJMzCP0QyBr3xIQwCARawlJQY686EaPpT66ixV79Cn5nUXk8Sckr+UZ8XhQ+1Z2xqepOV9pifoOVOmOMYn3H/zJg8efJpu1v2PlcAuPuuu5rC4fDPuWOnci94lXCZEy0KAmc4W3qgcCn/gPLMqvcOth2ak4NHHVs1p3xv/eHqD1sfFOZ5kHb751tuocMPP1zm86tZfKbwP/PMM/L6ScKvaL8IfybLYJAreOMVIEB7VVdXUx/W/Pq6f7odrBx98OxD8/ttAEBdACX4ARsMUPcuYK/wqwuHAgAdBKSkOECA7zNlTyaCOdDHt4yO6buGOgACCWYHBRBwMROwHYMNDAJREsGXSIC/JwigsIgboBQfRN7qceSJD2X728/mQEb8C5l8iB54egPV1PfuIYxFkQBVds149k5mZeEVmxYFcZpUZI4jJxPRHHt8PfeecuqpZ+9OGfxcAGD69OkxHlRX881eyYMt4hQycbKpDTu+qDOdhFR9V6reuzpfIWHDpnc9NEB+e0ko2c/+Xl+qurAvUQ/Prx5mQoMT7hYW/q985RiafMZkEfiOgvDbDj/W+M/MUsLvRPut1X+stfVyBZs7k8nK/3pf5HLWPSLO39zSXDRFWBeCwmq9DAC6na+0Pl4RNVCfqSQjbHo/A2zTNggo7a8WH1UsAJsCprr8Ujq+3ypKdOepIwHWkrcLj7ikxBjCg/XMBlBwFKQly9972BxwCYGxtbDMMITDMMhMgEGgaj/yVg5jEGAm4MJ6CQghRpgJrGcQ6Gs9Ey1eb64cpMaOU5anCe49Qokl1jXswSaptBIrmFPp9F9PO+2083aXLO5RAHjggQdwd1ehKi53UoOTk0W87Fiv3aaw+kMoleOtz81WHa0ouUe32a1eLmjGUsKr/tfPZe5r2sweB2+v/l69vjN/vtTcP/6EE+jUU08V4Vea31p1J0nr160X2r+ehd/voPlxXgi/iukrjQqaX1jHTl2r3acoqNHIdr9uA6v+UF5+5R+AvQ/tHrS1fMgWfvwftFe+Vfvg+sxBr/wQ6GOZQ8DX1wUg4A1MB5uAAVKMbb9AZW4FTej/Mf8uy2wAPgHL3IK3P4LFRms9EiJEtSGkBiNj0OVDIpJLeQQo122bA9EgeSsAAvsyCAxnoPBL6rDXy9/5o3QfmwMV1b0Lgu8UBSjS1tqz1r8vAj3D+as3p4QxGWtqHFNxynZhuTP73AwCt512+ukX7A6Z3GMA8PDDD5/GnfxzvsEhunY2BdHMzVafmfFo87rN8IoT7SpFy8xJPfp3Jj1zAi39t/qxzEGBslrwwk+cOJFOOeUUqc+P0lw67UeIbxZo/8aNzrTfXvcP5bkwKFWqbmF6rgovaf4K7Iu8fidQU7a+xwYAXePjvVB+zfZXGh/vPXZCkPIZSB+QVXdANwNUNEJpfrXCkAICFSEId6+gkwatYG2epfZOBoGM8o5joVEGgRorY7ACTABpw7AKMY/A67ZYe94CAXzhiTBDiQ0gX/V+5KsYwXTCAgE4GcPRON3z9zVUUdOvoLk9to/JyQfUw9FsPHuTKTj5opxYp2PZMS08qOdWcH/ezArjyl0tl7sdAGbMmHEwcuq5A8brg9JEQxNNTUTWaZYubGZ4Tadieuqueljmw3Oo6Fr0wJy0v/6/7kE2Q4gqDoz22quvYiUgmYlXUvjXrRPav3HDxpI2vxL+vCH8ZklxdU3Q/BB+M3QlQgsA0EJ8ivYrul+w+W0A0M0Cj0oBtkHEzLkHG0nZgg0AwP0pIFDFSpM2K+i2v8fvgt2r6ZRBy8iVy1JbB5iENWYwtTiI6sJVbplOXMlg4EV0IJMXFiDrJ9syiunH4hPwMbBV9JMQoa9qb0aSoMxPdvMjiUaCdM+TaylWPaBHQpYZttvRUuX6s9efkxnqk/208Vgq7Kz/3gQJfsY3Mgh8e1fK524DgAfuv38oD6xf8sA6Rd2U6kyXq3g2VeF7RUuN5uAckVdVmqmH4JXw+DvZXqbTR9EutcKMORjUPZRqRQ5MsmgeynfdcccddApTfgg/wnwQeizAqZJ8kNYLh9/GkprfEn5VlVdpThF+TLVTF26/4vyI+2MKMDSySmpxKaFVCTxK6xv2ftB29ikAUAChzAS3DR4eYyKQzn5wnco0USCgRwawQGlCOQcBEPwqtn+SQWDgMvLmGQQ6s5Y5QBb1D7IGr2/wUFOLV9Yg8AXdYg5YD03rLxQYYXMC1YW9lQwClWwOVI1ithDibzN8LDfF4hG6/x9rKFzRv4emNrNACwLj0sqOaUrIiSkq80of/6Yfq9RY0iNOes0Jft6/4nH0vV0lp7scAFjj17Fg/oIH11Q+tqSXFWZAWT1Q1CFOGtx8CE4OGidvvdnBOug4MQ3zOKYtp6+6qzt9zDCSOofTYMEaen/961/ptNNOE+0vwo8FO7Qkn3Vw+M2cWVr480r4q/BfsfBrC4duPy/byhVxifXrAKacf3qIz6T3ytGHVxXqg+2PiIDMAbAZgzqGzuZMyqxHIfSoQMJenFQ5B3W/ADZZ5DS1nk4esIQCLjCBrDABeF48drJQba1lDlRWeGSVYkkR9qs8AbL8PmDUbE7Ap+SJ92EgGMNMYLT13PLd5A3HpZ8eePJjClYM6HEf+hhyovNOLMEcX+YY0Z9pj+xWPczsYDqo33H/XMeK5NpdIa+7DAAefuihEN/gD3hgXInJNEXJFcaNqISLPDmjoHKyFcJ+dseIh96hQ3qkcTowAbWGnpnU45S0U/RAaHsCUeGa8sVr9qH1uF/eXnzxBbrt9jtk0Y2TTz5ZhN8M9cHmn7kTwo9qPj00v4Pwo39icRb++vrti2DYTj5cm8rf9yrhB+VnQQ/ZYT4FCCrc59My/ny2w09N/lFg4mTzqj6WSUEIDQIAbGelMgcUEKjVinUgkDr93RvopP5LKOLJWEwgY4EATofiIrW1Vp5AVRXSle1MYY81mSivRY2ziYxdcbjZjg7sY7Ekr0/MhHhlnGb8YyUFsDqRkQ9SEF47dt9jmTZtnDo5AnU/l0sbz3nt+ToVltEd1mYIGftgktupkyb94rPK7WcGgEcfecTFD3gaD6wfcsf00uPeumdcr6CqZ1I5aVJ98OsdaiKr3oH6Q9tRtMCMKJghQv0adhSq0a/ZjOHi98/OmkV33XknTT7zzNLCD9rPwr/hE4QfsXsn4XeqQ4AluzC5Rw00l2ajq8KeSqAVvRdbH5sK8dmgoIRe/U4BiA6qep+YQKoYgAICxQZUdqIu9E7OQbm/xAY6sc8SqgikJFcAqcPAWpgDqC5UXW3lCVTGcX/bhVFvuZQVInT7uR/CTeST6kL7MgCEJQWZmGVUVFfS48+uoZy/TwHcitYTLDEGi8aYq2cWaqncFHOBF3PCmZMsmMyT+/M/mAnc8Fnk9zMBAGv9CTxA/h9f9DAnoSn8r9n2pZJmzOmkPTpOeba1DtGR2Dy3U2hGp/TmQzQ7vpSpoQOXrvVlbr89aKDR77zzLjr77LPopE/S/CWSfACSfiX8/L8S/rSd1WfWQED/IRUYc/lV0pTy0iu6Lkk9WkxfaXq1mq1iAX5D6+vRAjTpd/S/8nPYz96RydkaUAGBclqq+oJJW9gVEGDTk4akj5Mb6YS+S6k6kKb2RFbShuUW3RoIgAlUuskXcEn1IXlkbssXQJIH4RJzABEDT7hBQoT+unH8f8wqROpKU0UsRI/MWka54DDpGyeq70TdnV718aILsMoCzBtmqAJrp6QgM0tR9w+kuruvOuXUU2/aowDwyN/+tr/HWu/uYP0mHT2fDvFwJ3vf7GiTQTg5WdyaI898SE6pnmaY0LwOnXGopaJ0IHAK/5kgg6IbqOGHKjtYrgsr87YbDj8l/CVz+/mYEEAIPxqEIa3y+SFIusffPjeKh9RA+DXGpUJ7SoPrtn7QFnbY+xLnt0FBF36V6KO8/eo5KFNA7xM9pq7T3sJzyVsFUFSuglN4EAIP30i3MgsACHbCkDvdSse2LKLGYDdts82BXM4yBxjDuK88wgTw6vVaxUat+gGugg0nJlHaBoFIvfgE/DXjZAES0S+uboqHczTr1W3UQQMKCVimA9lJyTn5kUo1J6ehyTbMGoNFQktF81py3HeXTpo06Y+7HQD+9vDD/RDS4wubVIoKF4RGJTIYHVHoNG1ihlMFVqewoO5cctLSpeZvq3OYoT3lqad8vgd7UCibN8wGXfh1Uwff/f3vf6d7772XzjnnHIn1yzp9WKpLc/itt9N74fUvleQDocMKvYr2y+Qem/qrIhtqIOC8EVvz69VmvErr23a8St+FxldefvVeJfmIw4//92qOPmU+FOL8mplTcoCqfqNiMFbMRTEBYTRgA5pPoFM5BZU5YAODAF/3VjqqcQn1iycYBKw8gaxt64eCLqqqsoqNVtd6pNgoqgiBAWASkeKgInRwGPL33mg9eSpGS7FRT7BWei9PSQZTP73ybhet76iT/jDHrT6uTVPWSXs7OaX1cauPJzNE7hR10CsLqWHD4+TiUydNumW3AMDDDz8Mz/5PeIAgGylQ9KAdtLhTbNP8jS5s+sKNpgDrxzV/64TEei6AE4PQO9Pp+ks1J0RWWg4OtscefZSm3zudpk6dQhMKwg/aX1zJZ+bTM61KPn7nUJ8IPzQ5vP1JCD9r/jQ0vx3r16QfgzoSjcj+6h4L8/M1e99M5Q3Zwq/H/NWkHl37qz7SU4edXs3kGV27mRNl9OhA1p4ZqMBA+QBU2rCKEKj/BQBTHXRI3SLaq7qDWju2gwD6A3kClZVuKTFWXcHmgJes3I6MNYnIAqbtMwmRROSNAQT2ESbgDtXZ3ZukaMRP85d000ebqoUdOdWJcLpvPTHIcU5LifHtJB/6Z3rCXIkIAeuI9DeYdd658+L/CQDwxOOPh/j7b/MD/B6fLO5kzyhvpVMChY5uajafPotOJd44OfJU6FAXfrODHLOs1EPShZ6KpwI72Wtq8Qb9e9OkUXa3nrEF4fjb3/6GykU0Zeq5NPGkCdTaum17bj9oPw/iTZs2Ce3HijulHH5K+GUIJmHzp4qcfuaggDCjZr9iJ0pjm46+oLL1Na0vKb22xvfbE3qU4CvToaDlrQssKv5ZeAa0PaXVfD4F88yYUitVhe0IhsoC7LbTgoX+Q/ND+NUrQAC+AtscSCXb6cCaJbRPQwdt7bDyBAACOCtWJQII1Ne7qabSxczHfoZpa50BlTCE2gK5rPUcfbFaBoFRUljEHWq0fAKUoUjYS4tWdNMHq2MUjcaKFIhTarqpSJxmgjopQDMqIONfkwedAavPdKe2dl6AwJSJJ51032cGgEcfffQgHgT38Yla9EGqLryUjaJfpIlypZwq6obNY5kJPaW8/PrvS12PGdsvlfPvdHyTWaj/ISgzZszAHAc679xz6cSJE6RGf0c7Mvw6CxN7NrLwg/aj6s+OhF9571UN/lLhvoLwV1cXheL0qbu6na8y+pT21zP71G/UjD6l7dX/Zv+Zfe2kxUzTzElTFkqFaeXDlKNTZwGKAah1D9UkonR3F42tWkTjmtpoa7vFBNL2TELUGayIWSHC2mqXlCKHSGe77ZoCXlcheUhe8znyxuvIW7E3g8AB5Ak1UV70VVZMixXrMvTm0iDFYhUFwStVCEY3R00/SCmf046iBQpIzHwL83MNlLoZSKewCfrgZwKA5557bms6lap0Ekin35RKXHDYUWVs9ojpOwmueVydvisbvkjDf4JJY84udLyv/PYcBXWdbnvlF3V+JfwPPvggnXveeTRhAoR/qwi95fAD7U/Qls1bZDHPjz9eZa2z59Bv+Bxz9NGU8Bem9joJfyRC1VVVRbF9n037A1oar3LygQHgNwHN06+n/ioPv9ueBuyy79ejDXb9/AV/CjbNCesk7Iq5mBEbBQJ4VfepFh5Rgo8+6LIBAH2aUCHCQkZhgkFgKR3Qq1UqDiNZKGMTJXR1RcQlTKC2xi3FQXC5AgLMCrD+oCQPkWX5yxyLWLVUHPbV7E+eCPReVoAAILBuc57mvudixlVXUlDN8Wt6/l36WDN8JOI/c8sagkWZf06ORl0uzLCr/b47lU6fziDw2CdeZ6mbefHFF1P8MHwYkKUQv5TzzokOFnnvjWm5pTT8J83T31HH69dkTtPskXRhgI3JPJTWF2+0rSXvY8r/t4ceIiz5zJTL0vxw+MkqvVios0vW7pPS3avX8EDybJ9noPUfBLYg/IlkgfantXn96je4npCt+ZV2LszgM7L6TMovQODg6Vf+AsVoCiaR/d50gDrFo53CpGh6kpRTaSzTL6BChHodAT08qM8hwHsrpyBJo6IL6aDmrWwOwGmas0CALwluFgsEwATchCUDpMR4MicswBP0iGlQePZ8nd4og0DV3uQFCAQaZAIRwZQKumlTa46efTNLdfXFE6tM81W9KtBzkokdaX81TktllzrVJzR9FHnUwEynT2YQePqfAoD7pk9f2LdfvyFA3oxdTaZAd0A3jNTYIq1cAgD0QVEYSJqt7yTgpex9s9SSiZZm55iA4uQfKMRXtX1UqE8XBAj/QzMeonOmTpEpvSjb3SnefhZ+pv+JJAs/a/7Zs5+j1atXiwbGQVMofWVrRDijgsxV6+sb5AokO8729gv1t9fes3tGtBeEuArC77KW7eoR4rOn6wrdV8JvU349008Bhm7vk22Lmg4/vdSVk39H70M1+ckpc03vz6IBSNbsQQUE6t5TyiegAYEwAbWBIdgRklR3kkbEltAhzZulxFgSIICsQYAACzqmEGMqMUAAZcdd/Fm2G5OFuB8D20FArhdgFamSacSYROTyVTJjCDIIBIUJwNx4el6KGpt6W+FY+Eloe3Kbec+6UCvA1PvPycws9KMtH2a/mcrQnASnyUon9+dJJ06YMGunAcBlH/nmm256s6V379HQTsruMtHL5XBxpUwE3dlhgoTT3PydiSLgePoCmqU6VR3TpLPm9ZjeW3VfehIGhB9FNc866yzJ729rsxx+nZ1dPTQ/hN/PasgjWsK2fTM5SqTS5PX5ZaIOmpozX1h405zXb9v8SAc27X2l0ZVtr9v6uuZX++rZffosPvWqNrM4isn+zEFu9r96LfIVqefk7rlkmupjZQqoWYR6xqB6Vf4AtSl/yZDAQjqiz2Zq6wQIqOpCVsXhGAt+vV1xGEuTuezCImLOhdzbVydWIBCKk7d6BHnj+5A72MBAEOANfeqm9kSennipixp79SkOfTuMJSfANJvqI7PQjK4gS/Wzk//K2A8gcOIJJ5ww+9MBwM03v8NvR6JMNbQHklGcLkIXEDWn2gxZmBTR7JgdOvdUB9jZbU4OEOWR1zu0oL3UsYzwn1On6QBQOI59D9hThJ9pP3L7Tz9jMrVvw5TedrZPrTh/Fwt/61Zo/tmy1LZfPOlqJR1LqHA3yLqrqq5lNsBPpythFcbQnH6FWLN9Pwj11dTUFHwPJt1XlN909qnNjO8rD79aSFQvZml6tPV8DRO01cDXf6OneheZdopdGSChSpUpf45iXMovoFc3NtOGVXgVUZa0nWLcx7uIjmpeS13JvFQYsuYPwCfgEhCorQIQeCgateYMiB+Ad3CH7ZWIVDkFXFcwRr7q4bImoSfSGyuZMHtAn5Mc/9EXu6ipuZ+jkPfoR838c+LcBXNL64eiZDaNKTtVmTLlwACmrdw3YxgEVnwaAECO8b9hwIwYMUIOhA42kauUXV7KrlHNSWsXbnYHTiX1OQaAumElsMGgVb02lUIhzExRwoRuIqgEWnNgqmvKZjP2IM/ZLMNFjz/+BBYRocmTJ0sNv+3pvZ228CfECQjN//HKlSycfntgk1YxNy80vbGhXo5phb7SDADYWNOl0na8385k4z/hcEhov9jpLsv/gByCQlJPQAl/oJDLj9LgUr9fpfX6/PIbr9dXVMDDYiXFCT2mp18NLJc26KzvcvJb054tYgxkTdF3ihoVPfvCMyLpc+X4VIlPeB5WTgR8A2ABqCNgZw1KynBSKimlui0W1de3jI5sWSPlxgECGTtrEJZYjM2BqriLn4EFAkL/XRYYgAlQzjLPpAR5DiAQJV/lMJlE5In05c/ZRPJ5BVAALo+80EXxqsYe8qDk0YkFbL//nj5rfRKQGjMCTEY0BiCvy5HTTFrF7Oxn/g4D5f7HHHtskRC7jAssXOGVV14ZGDRo0DP80cEYUMP22qtQ2rkU1XZCJKdsQPNzExh07VF03LyVN9DFVLu3f2Nh5pd1k26m0URPz/2AvnbYSHLn0ozWXikRlfdYAx0Yioe25KP1tNegZqk0I6fGQLaPgw9SmSwtWrqWBvVrlKITf777CfrjXQ/TmWecSWdPOZs62toLwg8tVFii+/nZtOKjjwrC73YVx3ohpCL8BDdttyT4YHCrVXdVIU8l/F62PTG5B1l9CRaAmqpKPrZPQCEUDFEkFGRhxyvTfz52a2sbDR7Ul+KxqJX5x0IfRIjP7xUGAJx8d8GHtO/oEWwbY1Bg2z5vHQCDxToWL/2Ij9PfKrihsSY7IYD7MGvtM7C/1O2D1FhCnle1MZnN5GjJso9oUP/eJI9JlfPOW153gAP6+a33l9KY4QP4XNYYKORiiBYGlc/QB4tXUu+mamulIxZyRAO6OpOSZNXFgt/e2U0rVm3kvvDzGEhTZzJL/aNraHTFRyL8iW4SxyCAFSFBgEB1jEGgyUPhoOXnk5Ag+jzitcZjxroGLFPs9kfIW4my4+PIG+3HSOHnseWRqckIIX60Ajv7JbHIwwABeV28jMfPwCbyixa2790tcxntsZqhhUtX05BBvSxNncsVqEEul8GulOZ935i/hMaMGiiLp6ba2/hyMvJMX18boNqGXkXyogu+Hh5WrDGTTv/lwIMO+sbOAIAww2uuuaaptrZ2Hn/cC76APn36FPwBJqrtGOm2A0Wp8slOrEHXKPoxNq5ZSWODSyjvdclcb4w4XyRAWzZ207w5i+jYU/cnbzbBdp6ngJ6y9DQP8Fa23/5y53N0xbQJ5MklLJRWYRgbETa1peivdz1Hl3zzRLrj4Wfp17c+SZNOO1Xq9iO7r12r249EFeT7v/DCC7R8+TIRuh6an48ZCgVkfr5bhB/TYtNsg2pxfiOpw8MDTBgN6DoPmDVrt9CwIb0pGmJ7n4U9zEAQi4ZZ+AP8GuD9Q/TcC+/Q5FMOo6qoNYc/GLDq+0k1Hd4vnfPTLX95gi664ESKh+zH7LI0ntfnFcDqSnnoD39+jL554fEUY2FJY+ke2/Hr8XkFMLq63fSH256giy88gaK+vLABof1ueL59fDwW1DSO8zhd9M0T+Fw84GFCZiXgZikzaHgK0p9ve5KmTjmSov68CK9QcI9dAt4FMPbyPk/RxBP2ZTD0cb93M9viLYkQIeYMpGlbZ4ZmPvs2DR/RIteS4O/bkzlqDm6ksY3rKJPCCkSWxgYg+Pm+Klj7V/KGrEHGWET8pLCohFVj1qQn+d9thezc3iD5qgYzE0DF4cEWE5D1Ea37aV2zjboZgH1Bvn9XkG7985N06ikHU11DiJ8z910AsymtWYniC8r56Hc3P8ZK5VBqbIlTd0fCVv95K0EJSsHNx7n1aZr4tf2oV0uU0jz2ADgRRoMZH0RorzEHFmREz09Q/+tZobbpl2bmOm78+PHv7AgAdBBw//KXvzwwGo3O5Pf+/v36SeYZNJ5J4UvmCOS3z/Qjh32V3aO+k/LdKu/ffm8uDrLw7VfpiNr1lMqlKNdtzTcPVoRp7fokfbxkMx189FBKd7ZbTh50QsDybOPhsPKmt15ZQoefsB8g1boGCGreylBjlUabN6ZowRtL6T228f93+jPi7Dv/G+eLkw/Cr3L7AQLtfMAXX3ieli5bSgHb5tcBAMeHwMLhh89ShTJeadmyGdi8WQ0ELV9KgK/Zx4IATe1hCt/e2kl9+zVQxO+mCANDJOQX4Y/yFgkzUIRjtPjdlXTgocMp6s3ybbitKj8+tx3JYm0fiNOcZ9+lQ44eRb5clww0CDXlNDs9GKeXnnmHxh46lMLutDWv3uNWwWkLTL0xemHmW7T/4cMo5GIAYyYjz5hPJNNumTrkPGF6/pn5dOCRIyjs4WeUSYsmxAD3MCPJstnjCVfSa7Pfo2HjBlA0YA18McP5eBBkYWWhGM2b9R71H9ZC0bibBZmFv6NbzKVEgtkA79uV8dC7by6leB1LMp+rk9lBivu1g0GgMbiV9u+1XvrZAoGcTCcGE4hG3FRdYeUKxBgMXMxa4BMAEvriXstHkLY0s9Qe9ATYHBhshQhjQ6yy426rcCkWQN24aDWlWUvHm5po3tPvsoaupL6DKxlEk+TmsYFah5KBiAVawhU09+n51NinlgYOwj4JYVC2HcSvOQrW1tKcZz6gQMRHIwfEJRcC5c5iPAZmrq2hwQd8tUdOixJ88T/Zmt+jzQthpfXsPvvsc3QPAHAV83QFBFBYruuvv34aU8gbsQv8ATgQkjH0VXR0FmACg1k73ymhwcln0MOZSBZLev/V5+nEgUgMSUllWJk9xzbR+4u3UFdrksYfMZjSLJh5mRbKFChkLV7pZkHatCZBKz9cT2O/OpIFsF1ywlXZbCxYiRJSnVtz9P9+/wg99NoCKeF1wQXfEOGXFXvE22/l+MMMeOnFF2jJ4sXi7XcrKi2OP1GtrPmDIvz4vDuVLEzqyWqFPPUy3ljVNwjhZ8EMyIaVeYLUvqWTB0ovqZAbDQcEAMJ+lAUPMRtgms+26pL5DABHjmK9mhSN7oU2wxx4XBMEyxelF1m4D/3qGAowQ4LguoXKMviloKWYvvKv581eQCMPHExhBpJcKiODlmxKTuI1j9NcBpLRB+/FgssCBc3t3u5TEZuTwWbu02/R3uMHUSzIfcsCj3NZTkWXCIOHweatFxdS372aqKY2YAk9WTP2Cv4Gpt9vzFlItU1VvI+fUkiRzmM5sYz4TmASdOe99O5by8nHYBiIuamjvZMZQprSfL0d3TmqD7QKCOCcIDS4jXTKYgIoNV5dZWUMVsT5JtM5WYUI+QLemOUvQd4AgIDln8dQgFnAIGECvoqh/EFA9nVJdmGKtn68gVxZF73x8lJhbuPG92Xt3sG/tzOUAKYo6R6O0ryXl4nz8mB7n0x3dnsFYgaAUHUFzXvtY2rbuo0OG9ebUl3WCuJ4Sh8l68g1+Cjx9+i5CHpKtx7q1WQwtWHjxvqDDjxw244YgL7hyL7f/OY3v+MDToXwF5yCdg03s7imHmMnl3NYUDcVnJKCdpQa+cG8Z+i4/t2szbt48LKGZyEJVsTplTdWMc330EHj+1GiXQEAlmyGFmUg8Ado1fI2NiFaaZ9DBlMm0WH5AKw12Sy7myns7x58mX5770ymcCfLKr2w9S3ht2x+VcJ7zksv0qJFi2xvP4kNbWl+qx/CbHc39WqSa0gVinlsBwBd80sMnoU2HPJbICCOPp/87/MGqH1DGw0Z0ZciXhyXtT9AAI4/7MP/uzxB+uCdFXTQ4SMp4GIAYAM1wMxAMvvwfPiYaQoxALzFIDGS36Vk4MLpBYqKzDgIKLEp8fpzC5heDmBw4X5hoAcDgOYBUMiQ8Ebo9effo6Fj+lNVpbXQKQBESnTbPgy3L8LC/T4N5n3iLJQpttPdIihqZh5q+0fpnZcWUq/+9VTfEuFzpaznAVC0OpH80agIE/pj4PB6fq4dLMB5cfLCcZpCxMDtp3deW8a/yVNVY5RaW1FyDSwhg5Q4WWugNtxOY+tWsXCyeWKbA5hDAGdevALzBtxUx0yggllGngUxjzqEfL/esLUwaWqjZQqxvDNwMROotsuOx4bxvYYlYxDFRvM5Pt/mLvpwzlLavLmVxh00kNKJrgK7Ex+IAECEVi5ppY3rN9ABRw2jbtj3uBc4LNCPKG/Oz3Xd+hQtenc5HfIVVmoMBHm3VSV57eY8bet/gqSP60lhhaxOO8rj0ebFKFnjsfyDcePG/fKTTAC3/R4GkXfo0KHhS6dNe5pPMAoLTAzda6/CYhQl4/5229HqrGZ83jyWU8hxy4cv0b41rbKmnLXqj8UAXn93LcXiMRq9dyMlmQHAUQMeKUkV0HBRtsfyIZkm6g2w9uPRjyvL8CDJwRvOFPZPM16h/75rJk2cMIEuvugiMXcQ6++0hT9h2/5z58yhhR9+YM2Xt519lva3bGpo/l5MBfEgkKgCwZfsvqKZfbbDCwgL4WcTxVp9l4VXlvgOiHBjIkrA6+fBGRATADZ/KIDPwyzsLgpFQkwTYzxo2Z5l6uqlbtvu89hr/Lmth+phrfOPN5n97ENBX6awrJYMSpfl+Xb5w9TVzjwghCnFKdGayl1deAy+IGsjptFRBp58Qrzl2aRVaFOeZwbLeseou4sHZYC1WjZZoL/CCMXXArYVprdf+IAqquPUZ2A1901K4vOFPP08GECAkl1u20+REgaA55UVFpAlNhZYoHPU3pnlZ5NkBZ6kDgA0mwfYYCokmQ10stBXBTppbPUyvp6UgACqC8GdhcupqLBShsUciLPGzFuJRLnOrDWTkIUy056xND3GK/wz1QPJWzFGkobc/piYQLJYCQPRpuVbaevKLRRnYPG6c9snkvE5czCZ+HlnGYbTDIzhOI5prY+Q4Wu1+srKJEx6QvT0E6/TccePJHdXG8tcRu4fJ1pceST1GzCoKJtTz+pUq1DrCW0YdzymZzEAfKUUACgToAgA8NhPP/30AYcecshTfIJqlJpubmnZPk3ToR6a08KepVIcnUJRpmmBBoHMLZ9DA2Lt8gA9NsX1BVnjvLaSGlpqeTBVUKaDtSBrwDweMNucljOQH6QflM0rgw20NN3N107WNf3pwZfof+6dRcd/7Xi67LJLxdusCz8YAEyAl1+eSx+8v0AcbJbNhc5yFZxbEP7mXr0EnCyb357SKzZ/VgCgYNLwZflZ8CPRoNj7QRZsLG8NzQ7fQQTOvliE4vEohfhew8x2ovEwC7CH/+d94OyDD8DL71mr8Amg0hlIvKL182Lne6xr88Todablo48eyRqVhRb03mNNjEH/WNlnlnYCrc92JyxfnA2kebFNSfrPEwiKEOf53uRzhM68qmaAxarcgZB4rXE92AdMQp6tvaiHj0HrnefeZwCL0oCR9ZRlTQmGYD3znOUMA4VlEygH9gSgZloHNgFCbTEB+ALShAWGYRJ2tHVQRyeDQEeCumQuAaIGaYk4dGU9FHdtpdGVqDicFhDIZqzIkA4CtXVeqqh0C1vPJrmfurDOgEfmEGBVYqxRCIru4v73Vw1gJjBG5hC4fQzCLOwAATe/drUmqHPNJlboeQscMUbctm/LAzYRtLz9bF5ihgyAAeAJ/4iEYPhe054IPcKM9CtHDyN/tst+VlkxD19oG0BjD/tKj8pNejPzKmTZ+FRq8cEHHzzkkxiAOpICAMxk8U+75JIjhg8ffhfv6h40eLCUqRahNMpp6VmCO0oSMRMjTHAwwQDhturN86hPLElZa20o7kjugFicls1bTfWDGyhS5eaH1i2DB05CKQjJiI1NBZwzLPhpuTbrWv54/4t0/S1/p2OOOYauvOJyGVjbtrUawt9J8+bNo/fefVfousdw+InNHwzJ8lvwA4i2Smur9ojm5wecyyiHrwhpmOm8n8EkFPSJZscmmj8cZPocopDPsvVh9wdlP/4+FBCwADUGe/DygIHTECEmCLIXPgkAm8daVhuOwHTGTy899QYdcMwYse8zLJiyJHV3hrZH4+0cCSklnrft9Zxtv1sVdnN2sj1MAjxBlNqS0J7bAhCXrUJUWrB49mw/rzU92IoYBJhJvs12MIBhzIH9qXtbmzwr8cSHfLYT2CPXJGPGY4UaZZP6gllgib0KcUYAAI7BTjYNOju6qIsFqaPTjhog14K/72QmH3O1SojQR6g45BZFgolEXqQNszauqfZIwVEpNpq3zpftRIqwV2YT5hJ2KTiPRZR9VX2ZBaDY6N58/RWyFJlLfIhZal3FY2j9FmaKHgF/cWp7t8f385hfgnXRYQ7mLDYq7MgeIIHKKnr5H+9RQ99KamkKMlh0iTKJMejPWldHB3z19KJZnDqr1uswGtv6o48+urEIAAwnoNL+2HwaCKA8Svjq73//kubm5n/HT/YeOVJODibgtud+q+QcMwPQnMPskIRU9N5psgNq6FWtfZ7qWdml7XpvsJVQ4TUQr5BBmk8lRWMpPIMDBlrQEwoIC4C9CqG0hJ/otsdfpRvvfpqOPOIo+ta3rhINXRB+e2ovNP+rr86j+fPnC7W2Zs3pob6c5N+3NDeL0CFhJaNV8sna9ftFq9kLXPv4OJEoqu96RbDxHuE9ePdh30f5/xhv8PQDJMJ+v5gJIds/4BNHj9d6DfhE+JF2LKyIj+22NY5LvNlZsbm3rOugaHVQaLkIZs6iusKSMHDSVtwfqilvz5bLwEeAY/st4c8wc0BkpaDteS98lrdpPoTYel728aDt+HrAKnD/kv+P6wkGWVCZhnO/VFUwK2ONLUJBFhvJsCBDc0otQpgPWPuPB76oZmhnpAwD2GSQ56g7k5UQIICgi8G3g1lggvfpZNMAQACnIfZBnkAw38YgsIxJeELCmgABTCcGmwMIVLPwV0WJahu9oowtEMhJspCAQCpnRUdgROYYBCr7kKdqtFQc9gQqkS0h3+N4HZvaKLGxVZieILGthHKyLFpe+lTMKESEJAnN2iXLzMXFz3xTB58r201VoRwl2xMWS2Nq+1GuF/U//CzJ8TAWECnMrFQzS9V7O816w4QJExp2ZAK47U1nAD4bABBBjv/spz/9b9b+hyMjbdSoUUU53IWRYaREmqaAKiahqIpuBjhFF/DbdevWUu3qZ6kq5rUGEwY8YthMS70sBNb53aKpJMXT1iBSU95nJWmkJfvLqgpz6xPz6H/+P3vvAWXXVd2N79em966RNOrNkqzebUu4yb3bgI0LdlyAJED8ORC+sFjfIizCgn9YhBUIITgffMGUxAFsuo0td1vdki0Xdau3mdFo+iv3f377nH3fmaN73xvJsjH4Ha/nN3rlvtt2/+3ffugxOuecc+n+v/k0eyjwMtDYw6QesPwqplyzZg1t3LhRC39EC5YWMHZrGJwzevQoVgwQ/iRc/uRgNuPPgB8t/BG2ntryw5rzo9iU9cpL2PJDw5cVF5s6f6m2+IkEf4erA2z5EatGWPB5v2I6IapLq1HetyiX8PTrEWWWUsqxiyu3Heg5QaIhQRoxngNKVIL6i4rLjm1kPF8IMwO6fAmW3Yi+WFy68syxEf9kjF1ajbg0HgTpcwW/ITWorXu8BMooQ8k+fWMjBubvU8RgBiKsLDjuVpKI3+XXY1HdLcmWTt30ShAHTNIP2X/GCSgvsAf9A+r1HigGKAC1T4NprQSKqYdm1+2iyhgIR5QSy3j+OLKqKqUAqpUiqIhQU2ucZw/AYKR7kRNAcjBuUIQ6jvMyKgytGa0UgFECJfVMKgIvAfV/CO5gdw+XZ/nY0trlB3dZ2pQm4FH5BgL3D85FIkJF6t6KqOty4min+qkU520SMY/2dSrlP/dmholjH+yRbCz0ZjqTP0HKdJkq2dp1ww03jMunAMQDiBnhxwN0YGU3f/jDl7e2tv7vEa2tTVAAGFU1derUIaGAnXV0sfpkOZz2cuHCkhwUNBrW7u1baV70VU6aRIr0ZJqMF6XOniR1dfRS27gmFf/GTEwa50NhxcNKIsouI5cG1We+9aNV9LUHf02LFi+mB/7X/+LfQGcf1/e5wUcn/datW0cb1q+34LNZ1x8Z67LyMho9ahQLIJep/Gz/0Iy/rAQLfwnH6RBsTuihrg+Xv7xUK4CKEvYCUOKrrC5XYUBc5whKtQLANhJKccRJx/BIRCaAd+ByFDGugXnvlKKAQANH8NyL22nrjv00b/oYOveCmUoIVXiiXGbtlkbZc8hkTPUmbRCC6hyjBo6gO1qiMQO80hnj1kc5Yw9X1gfxeFmotbi5WhtFNH+AqRbgubi0jB5/dA1VVlXQgmWTqK+rR98dwBQkTVkw4/nKgD0QYAhwjSNakQz2JVkBpIwAIBxABUAAQ33qOOEN9CI0QHUgpRVFLzoCvV6a37SX6ot7qbtPD5Tt7dOWFASjrATQSDRaewLYtRQSg0VGCaQ07yCzCKlznqgexfmAuPIGYqXN2hMAhiCapv5uJYydJyhmck4cSrGpNWFUSudkWDEPpEy3ocf4hLWrdzJeZeZMtU0kS9VF7unL0KFR19DI0W2+Afa5FtFEZXVU2szMymN46qabblqRSwHYScCYeADXXXfd+JkzZ/6j+tiFjAhUPwR0IARDhQQ0SgmBrQTy4fmFakr+lsYb68NZsLT5+81N62hly36NASjSXW2D0SL62R/eoGP7j9InPn4xeT3oEwD9c4KTOAwsAkskowZJC/9DT9E//tujNH/+fHrggQc4idbR2cGuPhp8esDm06eEf/06Wr92HSsPLrdIOGOy1OVlZeYcRBkbkWQOP1jIJMf8qZShvyKdbU8ogYLwI3YvMbF8uRLy6soyqiwvYWuPf1dWlplQoIiTikUxkFok1HOcXUlYdN0foON7NtQx7e3A0/EMRxZiaWWA6NChbmWhGiiWSdD/PPQIXfehc6hK3cDsuhuBRSkwojOa+gZk9z3GiTncrOwRxHQDDWeq1X8J5ZHImDdWFJ5pwopFjYdmLh+7y3C/PK44IExAHqXr2AD97CdP0dS5k2npOZOoXyld3f4c0TiFhM7zaFQe+UqAFUNa+AU1GhEh1kC/7hvoU/vf293HAs8hwQDmCvTzvxEeACgEeDWUgHJpaH7LHmos6VafibBu6+7RoQoIRuurNGqwaZRSvFF9rtJ9aVa2QA3yVGI2OMSKMl7dSjEQi9TNZ7JR9gQMw9BAjxLI7l6KSyjAHlWKS47a59HtwBp0pfMq//PwGqqtr6Nzz59M1NNF6YF+nW9S1+bxI5PorLmLNJEKGqdM+7RYflEKQsEGL6+qsvKvr73uum8OVwFEx40bV3zvvfd+St1wf6t+qNwe64SbDghBfHXylCnsDeD9oEReUHwfBBDym0fY1R5KPLHp+Sfp6vEqpsqok5bRfd2lIxro6JEk7XltD82/aAYlu7vU9nQUw5lnroWiYqAzpd/6ydP0j995lGbPmkWf+exnubGmo6OD3X1QeHOXmVJkLyuXf/Wa1VoLxmKmZyQr/GjIGDtGK0CO+eF+GgXApT4f6KOtKtz0UuPCc7ZfWfgq4/JD2Gs426+TfggF8BqEv4whwXG29omETPOVzsCYxbsX9RVVRu0LrizyI2SwEHG45SqK27pxO7VNH0nRVJ8G8UhnnhIseAye4ezTACANbPKkSSYR4xBAxnNzOGSy/zJ5KZLRE3vZCzOKgG++uPk7qZXyoNrGth3HqDRerASyn86eM5YGe7v175KOu4EdgCLKGBgxwjxUFLjHAx+K6YA5Y5qH4BEMDKCsC4IVHfdD4PvVNek+0a9DA/QTwAPo12XC3v4Ue5Tzm/dSS+kJOmGUQE+vvofFE6gFuchIzTjMOYh+A3+uUC+kPIOaJF3DrxqhqwPqES2u06GfCQcGetXvdnWr6+nx93Qzms6XiIvPVRL1rSeeeZM6utL04dvOo+Sxg9TfcZyvE36/XB3zwzuqadbyy04awCpdlNxdaipvplEs/fzzz5d97WtfS56kAIzwSezPwv+Vr3xlifrSt9SNPN2OL2yShtqaGvYAcEMiH6AFYiAQKmwrAKmN2sttbnDXulW/og/NSFMvEkqZKN98xVWVtGV7B/V19tGiD0yl3qMdHJNlcJZiWklEeCpsnL77yIv0VeX2T58xg/5OCT+EGMIv2X5pMYXwI+PPuJeo1oURiU3Z8pfSWKX4JOZPCYGnKffpBp9suQ8lw9JS3aBTahJ9sP5w+fGAu1+l3P6qqnJWAOXGS0CYgM+j6Qb+R4l6nfMmpmynXWotbFEObaK6ZGeuYNQIMe7oI529tOqF12jq2Daas3ACeSjmS5kPLn+UTGya8WvdlDHlOOM5MVjICF2Ey3Skey7SnvF01H8ABZnSK5CE8J25GQvv4ziAsovG6dXNe2nMjMnUdeg4HTmwnxYtP4t6jncZRKEWbo6TpU8/41lho+nYS+vj569ADlEn71OKN6KTggNKyAfTJjmIRiGlEHrgGXBlAHmCQd1ghPJeOklzGvZQc6JdhQMRjnbgZkOwQTRapx5QAs2jEI4ZJdCnKyKADusSnYYNsxKobNFKoGYWRUubdAKQPTWPBlTo1Xukk+IwlDiPuE5ckk1x51JUhXODSmP8x7ceo1mzJ9Fr2/dQn/KObrl6LpUoTwKJ04S639a011HltBX+sBURfjsfJ+3jGBxTWlq69qKLLlqqfRU4YyHtwPjzX7/97f9P/fNTwuI6hLLJ8Lj3GYaWtjFjqL6ujgUKlQH5XFim3yUWcasGYXRIL6/6BV3Uptz03iS7+bh5K2qrac2WQxz3Lpw3hvpVnMWlacTGsJyIg9XVfPBXq+mfHnqM8xV/93d/RwA0tR87xth+JPxE+Ddv3kQvPP+C3o+YcfuNAoBgwO0fO24cJ3TA+6fn3mXj/rRJ+Om+fo9dfSgM5CYYuacuRqXyBFDiq1CvV1fozj78m+N+JPyM8OO7JcqNjypLgUy/rkBEWOj0edJJQF3HN1YXoUoiluVDQIJJhQ2DXpw629P0xGMvUktjBV12xTxmH5YyneeZkEyC3YgG9XDdPqohjp4JMchY9UhCKyEArSJFcWP1TZjn6QBSE2+SH5YklCLcs6eDNr20jc5SN/fhtw5TV2cXlTVX0eyZo1SIoxO8UabvSrFrLbP+mN23JM4xM/YHZV6/gSam+zmSvUlW0ijzousuqb7Xx6GAFnqEB90n+rg6gJIhsAK96u9+AIPUtZtTv4dGJI6xJ8BKoFfTjKEyUF8bNZ4AYNr6NKVNWTBRldBKKu1lPYGKJqUEZnFyMFpqKMYMmg9KoGP3Ecr09On7OxFhJCAg2fjh4wMePfqL1XTVjRcyc9F//ddT6v0uuuWymTSo7lPl59O+7hLqGn0uC7id8RerL4KPe1090s8888z0+++/H7wAyNBmwhRA5MHvfe8eZcm/Le681BUlpuBBDoaMQfjcYVWhAJCVnDRxop98GEIiaWX5XUUQVC2wdox/8/D639Lk4qOU0uZYCXaEqloa6Pl1e6i8tpLmTG6iwb5+DqF4pLYBynzvFy/Rl773K5owfiL977//HLPrBAn/K6+8Qs8//5zuDkQFIZLNhmbY8pfT+PHjuEUXws8cfoNWuY+FP+Urr7IyHdcXG5APavlc3lNWv5KTftrqV3PJr4yK1U0NcE8xIMDqTmGQD5KdSNIhmy9CpmVVu/ziCRisRVR9N9036J9zyQ942Ieqejq0q502Pruell+zgME3LLzoqeDMvk5sRYzr7eNXTSGfzwOy70CzCcDKYAa49AjlhDABOQJT6fETh1xyiPAxHDmWpPZ2bZUzKNMda6fi5kY6+6xGiiYHdTnX3AJagfjEcRpxZ7Wb877E9G/irHMHI1YcWAwkCD3Nu5BMcRgwqK6jJAW7e/oMbBglwpQS+kH2KGY17KO2UqUEepSkZDQBSCrpMUAIrEI1ZcoTaI0x2Sh3NvYZ5VYT15XBpOYdxLmMlzdQvH4WJapn82xCjbokzvr3Hu+jvZt2kQdFzFoyYzysDA3GS+nx322gi1bOofJi/LucvoPO1ItnUEVEozS7lZJ4o3wh43FglCWnhmEwMFQYFIt7vbKykra++eb9Kvb/AWHwAbqN1aEF4QA45P3GN77xYF1t7UdspJ8NKuAkg8kFwBOAAGFLc+bMYeEYozyClhEjyFYgrms/BPnndAu63gIWMvOJnatoal0vpeGKJiNcmy6rraNVT7xJI6aMpEnjalQI0MVEjriQsLrf+q9n6R++93uaNGEC/e3fPsDc++Dpl2w/9h3H8eqrr9JzzzzDgs6MuxKgRDRDTDkQa9wDH2dCCnG1oATSKau11yDm0JJbU12ubsJBqlXxfU1NOdf5K0pQOSlnL6C8WHsCUAZA/hWbJiCe44dkHzL0cl8Ay8ASHjVMxTpHwkAeT/fcI87mnIBkpmHV1Ot73jpKUyeOYOuydetRjgdHjqmlwa4TZjsCVDEaL23i7wxZ2Xzd6ad3wvO59NgV59hfg1kyOnVvqiTE5cL0QIqTjFprRRm6jRJgLJ5QXkkvvbnhTVpw/hzqOXaIBZr3Ccekfg9xPXcZJmS4R0Y3cKU9xiP4XXaZbJ6BQzAeRZZmHAMgwyn12xwK9GUxAggB4AlAGUAiNr+5jzED9bUVtKD1CE1rUvdHr+YTALnIgHrUOEqgtFTfv2gi4hJddULnJQYzGj0IHEVZPSUaZjF0OFY2kpGE7Amoj/Z3D9D+V3ZT8ng3FZdrhCXKseUjmujZp9+gE52ddO3lM6iX4vToz9fRB86fQsV9JzgXU6SO/0fbaqmlbbzf0g6CGDQJQfDxUB6A9/jjj/+f++6778fqEJFlRakFGicZMdbWbf6JffGLX/ysuoH/rrmlpcgfzWQhi8TdQKmhz5rgAg8AeQCss846i8dWDVr5gCCL78b/Q8g5xXKodfTIEard8ySNq1exXUaXu1Iqltx4oId2vHFIXYwGmjWlkeqUu4QKAazYT594hX781E5OyH1gxXIVT83m38A+H+/q0sKvlNRrr71Gzyrh9zsQfdnXbmVFeRlNUAoE9Xtm72XhN9Y/NWgyrRrpx5n4WNxnzKmrVoqjrZEqlPAjzq9U7j48gIryYu0JKOtfCgIPwwGAZB0sPxRpArV2zyTi0p4PPmLXX33W88E2UR+5F5XOPOPXx9W+v7R6Bx1VN9iIxmpqqKumCTPalOVV8bYmztMCHtP1fN0Hq1t7BZqrr0TUYPVN3I0KAt6JZq8VXHZP7iKD6ef4Nq27AJkXA6VF3OTYb6XswB2wfctemj6njSKpflYQEROWcB4AzTk4ZlMn5+w/NpQ2YQ87BR57JH7PAXsDEc4FMPYDuQAlMFACHPfzAJKkXxoEdLgP3YPKyu/aA17BPvbK5jYfogkVh5VS0KE6swwpa19TE6PGhghVK+FvHhFnslEmcoGySmlPANWBwQ4lpDUoz6p7oqROeQJnayUAijEogYiGag8qpdT+5h6KMUWaPs/xyhLyKmrp5z95Vim3AWpUSmncqEYaPaKUBg8eUefGo3J1zP/8QpLapi9g4Ye7j0Q8aONr1KOzo+PgX3/yk59/8cUX31Rns0M9uowS6GMF4Ag+Hgz7/fznP3+/0iJ/X1JSMqhi+yIkyexRz4IqkuGOMr0FmXQkBMchRo7HfYGTfEBON99Z7mcOHNhPldt/TS3lKvxBuQWosGiCeuNlVK7cxwElmFEl1CURXUp5bPMhqj97JS0/7zwWir1796r4fjPt3bPH75CCInj99dfpmaefZiEegqWO6OoD3P6JKqSB8DMJJYR/0Kr3G9SVEHvApa+vq+EWYbj9sPSVJTGqAtBH/Y2SX7VSCuXq/bJyneyTOn+xEmrmAIAHAo8ZCDzE3HDLUefPZHR5JhI15TcybreB6MJSKs8h069bdJE1RxIObbUdKlaNKitdV11M6WQ/pbv7fTCGp2OcLH0anqUmbbATOtkoGP2oTlZBWcZ1I5VUIiQByZ4QaHPSBgeQ0mVFXWEwvfbova+thqmnDLozUb0wIYVGzenSIrwIjVRMWXgRk1uI6HgbOAZWDlFNAKMrB4ZxGBV5YAbQ/8EUY0kl8ClWBigPAjPQ3acUgtrHQfVd4AhOdPVyKXFKzUGaUtuuPutxONDfn6GePuUJVEeZaLRKhQHNLUr4Kk0ykpusPC4RAjOQ7klRvCLOnYTRomrlCYgSaNOIS8CzlMeHikzHjoOUPn5CHYvmDYgrzzGi3Pv9u45QXGmWmnK1zY4OFbr1cYhTrK7nL3cVUeOMFRznIxTAI5FIpL/97W//7J//+Z8fVyeqXT2OmcdxSwEM2oIvgB9g/ktvv/32c6ZOnYo5Ywm1wYyy7FEoAXHn7VyAKAGbtnm6sv5oVYQrMlN5BEJ3nXNJXOd6Buam3PvWbhp96PdUWRxli5CGF8Cov4Ryq3R2PM1QVo9WvdZOmREL6IYbr6cm5fLHzUQe7O+OHTuYwWfLli20c+dOzEBgwfbZh8zvQqBByDlp4iSuWUNZsNsPzkFD6QU8fcpQWWPfq5VAQ1Nzmc/U8QHhZWtfWsIKoNKAfUq4A7CYn0uA81efRcoRbj/iZO3tR/0mIx5pFY8ZrgSPj1OTrZAWlrThqQfs1kBwNa7fY6uLXEKaLb7HrjEz/JBuquHGHtPvz6hADfzT8TxcaghYQje0sCJPZ0zuwdNUZmBciutchGeUR8ZsT5e3NBowZvql8fm0QR2yNwMUJ4hAMoYevC+pFVA0CxBjzoIi09lockBkkq1RKYdCCcYMJN3TeIWMgTsDKARsAXICAwPCxagegBCjOgD4cI/JDSjBR86gX/1mr/JAptQdpZlNHUpRZBgyDOpxyCBgwyAZrSkjamKewSjJxKG0CgESFTpPIuAh9gRYCcygWM1c5Z2NVQeIc5bmdvVkbycd3LxLeQ59DOxijgSuyMT53A52gwdxUHtQGY0I3NlbSdFpl3JVCrH+mjVrdt9yyy0/NhZfBL/d/NtWAEkB+ojwA+kHuK+ysVShYoY71Eb/GidfhlfYqCJRAlJ+sIc74j2AbBAS4Ltwn6UuGWTpiYLHg9kQ4TdeeZnmJtfoGyem6zAZydHHhS47Tlv2HqeNvS10+VVX08zp06lKuUTyO5wdBj5cuf6A9/7whz/ikd5cyjPQ0ogt/JMmc+ZdT6rRJJ6++58U65/im6xWxfLN9VUa4Qd0X5lh7Ckp9pN+QPhBITCtl1IKxUqIUBqE24/sN2ceTJNQ1PRPCApOTCu736bmzi6wwMs9zzTtaCGKSymO8fc6P0DmPTIYi6hx0e2kGhmWJs4kJ2KGMtsz/f7GU4Cgx7TwZkxNHt6JaY30vy+9BOIdREwTjAB8GPZqQj5WQAZyHDF5h0iRLmtqYIz+BlcHklrA+TtwWxH2RbM5GygL6atHgpPhxKTLhGnTSIRk4ECvxgowsxCaheAJmOoAugihGOAN9Kntja/poLMbjyjvwWNG5/5Bj70CkIvCA6hWktPUEOMWYM/wJ4JMJA6cgNq31PEkzyeMJOC4VlBRw3StBCrGG20Lz0jdU30ddPDVw9R/vE/TswP0FvNYeWciHlc2+DSrGBhYgkO9SniX/AXc/4E77rjjV2+++eZbRthFAdjCf0I9eo0CSNntvkWW8FepB6Sm9tOf/vRnlAAvwWUfNXJkVEZX2V6AzHPjBxQBpuMYkNCiRYv4ecL48awIoCiGlPesG08SPEPQg1blYP0LT9Hi+Ou6uw6z4YH/ByrD0yOVYNEQ1/1ya4ZmLr2YVpy3lEaNHGX6zzWQRNNOeXT0yGH6za9/zb+1Zt16ZvxlqjMDJ0XuYtLkSRzL94rlTw4w8yw8gKRAfZMaZVVXXUYt9dXsztsNPVzqY+quEk3jhSYfWH+Ae+D+xjX7DxQAg3rQJ2AEkglK4trKcktvPOYn/FAV4Js/qvHxcH/JZ7PNxsbyGvII8YTuDJRSoWd63rlhytSi04aNB/uguyo0SAW/HZF6fFQ382geQA0SYgwAvAJgEeJREz55hg8vphFvGe2lcMIwoZNjRJRtV5ZwxiiDNHk+Tz+XNuFVMHNRgpVNmrsBjfEwXoeUIaFAuYSJa26gyOx1qKMaHEixAoDXhiwGegi4kxCKAKVClAVN/wAShHgdYUGvsuijyztofusRRngCQ9WvlEF3j4rFgQ9ojlJtWYQajRIgc37RPxCrjLPigicQK9GhlIoBqKgRA0jmUaxiolaekRTnOoAr2fnSa3Ri32FmdI5CQnG8mbQxihpiDYUKKPz3Xonu/v5DP32CdIzfYT3ajeCL8CMBiCrAoKsAGOcPy2+EH/ClOuXCj/jkJz/5t8q1aFEXJj161KgYQgHpNnLBQXZSEEoAWUgkBblz0JQJ8TlxtYUvYDgDD55//FFaVr6be/hxExUpK5tJR/SJU1srVjfe0zt6qKvxbLrkwvNpJn5PhSAu0Sj2d+OG9SoMeIo2b9pILS2ttO/AYXrkkV+wdYcbNWnyZM5hyJDKQWP1JQTQlZBBFpzG6nIa3VJj+vMT2voj0ce1/jLD4afr+2XM0a/bfouMlUc3oHDzMdwnJhRPBlgi2PiMucmNNxAz1p/8xJ9J0JlkW8YIv5xoRuWhZBaJGh6AjOnRN0oAYQHX0j1WKr6OjuttSwszGeUEhZXmTjbdMhszIB9B5rGe93QTj5fSEGCtALTEauSwzjNI3kG8C+ZZKNb5AuxLRNiEobiS6ex+e3qaHgyBx0pB7zf2xUA29W+a71NcHyeStWA3RpkQnkCfCQfAIdDXM8AeQU+/JhVh1KB6BrCouy9FreXHaUnbMf69/oGI8gQydOJEhicHjWiNcQNRQz2UQMRv/stgHFmZ4RRIeX6ikmKlVNyoPAGwC5VP1GWByADzQOJe3b16M53Yc4CvdYR08jNj2q810jTFJ/PT339p7fqt+58wQg7B7zRC32mUQo9l+SH8iMczYQoAQ0Hr1QOzqhvb2tom3qVWUVFRMZILzU1NMZTPhiQEIRBGUHoNQEiUAGKT8coDQOlp1qxZfKGD8gEn9QNIJcD8+5lf/5TOrz+iLkqSkRTooYflRGKpVAnRgRMD9Nt9FbTonPNp2dLFBNKSk9qO1d979uyhF196kda89AJtenkDHdq/n2acPZsOHG6n9evX07SzprFl5iEUJrzRiT/NOw/rnxzQcX9TrRL+Rm35gd6DsHN5jzP9Ou7nXABi/ITG/4OtFxl/xPpo2uXyXiyqYb5RXcZjYWAMfkbH4xB2iW3JKgEaJh7dDWbcZ8BLTStqhFMHwsege+ojEscndbzMAmMsPod3SY0DiBhgEMBUuDpRE9v6DT+mK5KpzVISLujvSllS+hQyJl4XV18LOQMUtIU35LERk3iNGM9HhxGGUCOV8cMbz3gswiDEgK24Dpc4ZEmls/0mxlOImPMnn2Fadk/TnHMDEZLa6li6e40CAKlIv+Yd5IqBmeEAxuHm0i5aOuYonwc9gEQF1t1pphhraYlTHXgF0EPQGDN4iAjzCETRTlykFSIrYTSJecXsCTBqsHIS8NvqdeX+o5KlRPPAy69S+7bdxqtJ8X7zMNMio+CUEvjKL19b/7Pn3vyxEXax+F2W1e+zhB9aI20rgJgJAUotBQAPAPOqEfw3LViwYN611157MUqGVVVVnvIMIr2mMsCulFQFzIx3Rgkyf7se5ohqAABCyFTOnDnTzyUE0Ym5TELiIax//Kc0p3gvdQ+kOQSIR+MmJkRPfISe2ONR5cTFdOGKc7kEiQk8biNSe/sxjfFXCmDd2tW0Z/dO6lCvtbY205XXfpAe+eVvGdwkU2oHzSwE6bCCF4B/45hH1FVSW3MNl/Bg+RnYg/59ZeErSkupqkz38XOWv0gLPdw5KAMoL2AYWMAg0J7uVfDDHtPq7BlrLoAeibdZKKV/33gLmsLGeEyoAMDDiGlyVS9lSDliunqATju21gghIHACzeZZd0ZhRHXLLZnQTPj+uAU7rskyOLZNyWy/LCuwz1Jrjoctl3KrmatA3D/TFksxA2AyrcTk02cZKi0DMtLYA+UCx3UOBFZcsAk+7VnEMO6Q7o5MMtGmViLc2GTQnFxOjGioMdqHB+HJYhJR0iQEQSSSRIlwkLpNeMDVAsMu1KPi/6ayHlo69ijH4vAEsJ0TJzweStqslEA9OgkrVRzdFCMZic3YgITmFPAEtwCBTiWoqFkZHnQRVk1lTkUv08NswvD/d6/ZRF3bdjIkXM9O4KIrDaj9TcQy9Pyuvj2f+fcnv6KuwwHSST6x+uLyD5iHL/xkij92ErDEeAHIAdRaCgDkAU1XXXXVuUuWLDkbFxvWFScawj0EIOTMc5NBjnBXFi9ezCAFsOQiKSjf9d1+Y6Hl3zZEGJ9966WfUxu9xdqW2U9j3FjJnXJ7OlO0um80nbdiBS1cMJ8aG5uySS0jU4C9vv76a7R29Uu0ZvWLtPWN1+nokUPKXaujz33uMzRu7Dj65ne+T4/94Uk9YcgI/6ClADQwKk3N9RU0tqWWmXlh7ZHlR5kPVQB09XEzD94r122/EPgipurWYULEJPDibJmjxrXXHAVRaWDK6Jubb/S0oTQjEycb70ASeWwhDbUX3xoGMyDxtW4wy5jEodT5zflBFt635sLToN1zT6N6DPhGA3MgkLFo1rPyDNGlhB1pk6DE33EzlIVMp1vUNFRlTKmPcxdkGn8MXZZnmoCkGpNJaYFlBh7PIAFNopCBiIOa3VjCJLMjuuSIZ9PEpK2t4Rggw10IBcb5rBQLNhKW8Ajg9rMiAKcANwwlOSQAtwAzEavPdHWnqLakh84Z36GuI9qPtZNz4oQSyoSeOdBQE6UaTCNqiDJpKJ8X00kYKzWj1eCZMB2Y8mobplKifhbFoQRALKKUAA8hUUZu38YtdHTLm4wgBHvRoMnF4fTubh/svu1rv/9UKp3ZaYReMv0i/Ekj/CkRfvEAopYSKDZeQLnjBTTL45577rlk3LhxLeoie6NHj45IfByUD5DKgAx0BC558aJFHMchxoZHgM+GEYGKAsDCwM3D6x6mEZEjau9jjMbTDDi6VfWpwxXUNG0ZnXfOYpo6ZQqfsOx2I5yp37dvL728YSO99OJz9MrmTbT3rV3U1NRAf/vA/TR54gT1G0dow6bX6d//878ZK4Alwi9tlrg5RjVU0vgRdUrwdbwvkF4IfRVCAKuXH9Y/Ztx9xPo4plIeEqEFLh7NltYipr8+KtlsyYtIog/a37jgLPQGpCSlQh59ndTsvRo0pK09viejyXk7hi8B24oa11/i+7S45rghoAB8zLFx600jUtat0qFHRDL5ptKCScg+iNi8p6fdkg+vFhwDJ+uMwHP+MJYNaZgejIVdh5sRU3nQuRGP7wFWAEUxU1rU58kzQKI0YxV06MPMxVE98i1mKhrIS2TMVJ6kCQkGeAJRihuJ+pVCONGrB5AwqQiqBcwlkOTk4YneNFWX9tGitmMUyyCJqM9Rd4/Op0AJgHEYk4hqG6OscHi/BrTgwhMgg3jkeQhKCSTqJ1IM04mrZyglUafOk2ZUjsaL6OCrr9Nb6zaZVmHt9LHiUif9vn9dc/+u/UefMQIv8X7SEv60bf3FEbOVgJQCoQQqjRdQbymBloqKipGf+MQnLq2uri5XFzvT1tbG+ACbc8xHCZrKgD3aGdiAs1UIgJOEsKDENDG404Ls2B0X6ODBg9S54SfUVtanLlCE4bLRiBaEvV0R2lE8k5YuXUrz583TZT/DMa/lKELHjh1lIs+1a1bTxg3raNvWN2hEcxP9zac/SW2jWunQoQPUfbwTyCn6zdPr6fEnVvlU3owj79dlwpENFTShtY4Fm0k8TLKvslQz+6B1F16ALvVpvr4iU28Hsg9UXrJjUdOmK0kw7hQzVFrEn4+yrCXi+rW0ccEhGEUxDcxBX3uRcBPG9OekYqgVBpmEUTY5xh5HNDvEFcMyOKkXi2S5G83+pdPSpOXx2LC4aY4Syy9CLZGKeCD4rObB0/E6XHQoT/YcQF6ifhfClZZOwygZwI4Bppg0g+QK/PvDKD5uhzZTe0SBkhlNxveMp9vJObxBt15cE4BydOVlPZFBUHClNTu0hAboHsS+wcqDhRc5ASQHkXtCiNBtFAFCAygBDCCpLO6jZeM6KZFBz4E+dz09Gd6f5sYYjyZHXqCuMaY9AVyTAX2dY8UGf2IYhzMqnIhXj2XAUKJ6KsXKNLEIMv8ICd7a/Dpte2k9ezSlxdpDxNCbf/jvN76xat22b5vLJ5Z/0Ah9yo8bAhSArQSKjBIoN0qgzigBCQValOUff/fdd1+g3GQsr2XEiAiSgmmnY7Df6hWQB5TFFGWh0SsALrPZSgkEDR71wwJz4YHi6173faor89jNSsTimnhTafVX+0ZR29nn0bIlC2n8uHEkc950UjHCzT7btm+jDevX0Ya1a2jLlleopbmRPv2pT1JjfS0dPLCfuo4fo872Y9R7opO27Wmn3656iXbv2sFCz6VP9dzWVEWTR9b7gs6gnlLNzS81fwh7Dei8lWKLmE49KAid19BxOd/ExtJzgw8zFZlR1RDqwZQfImTSnp9US2e0UoiYfABuFigAnkZkJjOTuZD4XNKw9hQxq5IGjkRjgiDUOeWM7s/RDMtRU4KMZgWHXXPjzscMMjCdybZycwwZzU605UhAvIZI1rNAKdGTykREexoZI/gxU8FgGjUTNpAnFWDPf+bZfSgzxrIeUsbgCNI8+i3ib08Gu8LM4jXU8rFdKCb4XDAgSUa2EudzgGTEeepP6hZuZP+T5pxByNFG3G1aivv6dYWguz+pm4jwvlIC5Yk+mj2yncqiYBzS+9LX57HgoirQWB+h+uqoCgfgwRqFidZr7GaRDuGgDLgE2gck4WhKNM2gRO10ipeNYIr0tAciFY8OvKGM2ePPMjoQJ6hIff/7T+z+4f88u+0LRsjF7Rfrn7EUgCePCHDDx48f968lZfn/JBQIygc0L1y4cNa111yzECcLScHKysoIcPVCQSxewKC0DcMTMPkACNTCBQu4RAjYIhJ2+JxLIiKoQ/zGju1bqWH/z9XfaaPx1UGrC3psoJQOVi0itT80Z47yKEpKh1BIce5g927atGkjrV+7lst+zU2N9Nd/9Qmm2z50YB8d7zhG7ceOUMfRw9RzokO5dSl68ZU9tGbNWgb/QPhHNyrhH13PyTxYf87wo54PfL95Bo8fFBMUQnFCu/s8tMTQkTFJJjQs8hdxLYgoBWZQo4e1TpnMNlx7w+uH17Vw6dgfhLIQTe3KGiVn3EqJrdHFyN8zqDwmQs1krR4LlYH9QxDBKJzihKxWAFi4+SFQcZNcS5ox3knTIcgxuJQpoUBSGdPnL16DjndTPO1Xx9rYp0FDMCrhjVQ19edk+nDEsId5RknqzyCUGIRnwfyCGtPBcxcAmQXLMHM+mlFzJhTxvUDT4xARfIIFLJJJxjieQZ4P6OnE4KDu7QBSMMlgoCR7BsgBoB2dmYZAPWYUATyBomgfzR11nKriUAw8aU55knr/6+uAEYhqJaA8As7i4z4f1CPJBHqNSgE4FdJ9YHIfQUUts6iocSEd7mqlE539KpSMKU9ChcX7X6WXVz3NeBIomfVvDaz+yo/W3J1Jpzsc4U9Zgp+xFIDvzcmzwIIFElxivIAqCsgHXHvttcuUIE/ipGBrK99wfSaDLll0KQ+KByChAC7UOcuWcV5g1OjR7BHYSEHb+mNbG9e+QBP6n+WyHIA9sJy4IbZ5k6l1+nJatmg+dx9mR34Tu+4H9u9XFv9VWrduDW1cv56F/75772aBhfB3drQr4T9M7Ur4uzqO0kDfCY6dN+3uUWHAU6zI2pqracroBnbpyw3Ip6pcA3s4+1+uef0Y0QeeO87467FeglFgFmEAfwx1NwsrLFpUewb4WCqlQTL4LCen0hnjysdYCbECiGmXHRd9gK22mTab1hRdXE70yTPlwurf0mU+zYGP/UhxvKw7CzMmiy+5As21qO8T9lDSOgRJGwHkRJxhR0qb5hwNIIpmwV2czCMfF8ChRUbjB3BsEQPOiki+I6r3iZVbRpcGEzzcxOPihgaJZfMHGAwSixlOhIgGM2G7iXiWYg6v6Z4kz8+XRHl7OrGKMAVKLSPNR17WQ+nnUm9GxfspDinxd1fPAIcXaBvWg0fSOh+A3ACzD6XVNR2kGc2dVFcyyMJfFI9w4hqKrLYmwpTjUAJ1dVFO5jERS9Lj5iGK6aYnDCNBr0SmTx1P7UhKjFpJuw+fRRXltSwzSACWVSbpyFsv0p6XX6Ji9b2d7d6RT33ruauVzO0xQm/H/ilL8LMegO1xW0rA7guwwUF2PqBZ3ZgtKhS4eExbWyOSgmPHjo1AyKXEZ5OHcGnQ8gJQHkRFAHE7hH3atGnsEcBiyxKPANt7ftXvaHbpqyzUfOup9zq9ahoYeRF7EzOmn8WKQWjJkfQ7dOgQvfH6G/TyxvW0ft1aalLCf/ttt7K7d0i5/Wz11aNTCX6X8gL6e7uRUmblsHF3P/3+8VU0uqmSpo1pUC5+EVv/6ooSDe8Fu4+yODKcE1UJYBEgUJyfiOpnzQWnk5W6JKdjVibxTMSMNdLIPrn5Y1HpvTfQj+y9qfv6SQtaKmOEzHgN0tOZyui+Ae1lkG/1IsZrSBs3W4MCIyaG10og65rLoBPyk3tYKZNki0WzWXqJzZMmq870h7CiOJ6I3tYA+uIjGryU9rS1Z0asTNpPFkJAdI7BVBcMhj9ich+sdAQQZBSPjvekAShjkMTmGCMR/1iRKEuYRKM/78BUNhBLx4ynhQ0gBwABSBoYddKUq5Mm/kfpjecMKKnuU55AV98gezaAD4NxGkoh7SVpZvNxaioDRRzxb6fNFKKaKuUJNEapoTamFAKUgGcYl/X8AfYEEuj2jHGZE5yB8AKOFt2sZGYMlzcxGo3Lx/F+2r7hEWp/6xXqS0YHP///tly/51DHBmPppeafoWwCMFQB2DkBNylYZjwBAQg1mQcnBf/qL//yMhUGlCqhzyhLflJS0C0N9knjkPocPAfgAnBjM5eAEiThHxCgEb676rcP07xq3dbrmYt+uHwhjZ25ghYtnMehRNo05OAGO3zosAobttErr2xmyw/hv+GG69XFGKD9+/bSsSOH6Bisfmc79XR1KgXVg/Y0KlF3KUZu/WHDATq4ZztNa1OWvxQ9/HoeH9z9ynIzuae4SFN9lSR8pl6eyBPTcb1nYL2xaHYqTBFbP+POg9Ig5XfLatcY6Z60toZFpiwXMfPd2LKb9zJeFt0WM8nQjNzAGc+HFIt0eQaYo+GpmrePA0ITPyeiGojEPfSGcETCAcnk45kF2eQJfASn+ZQosygLcsTvB/C5IIwyE/x/Ku0ZT8JoN0t4dQIz47v0UfMdSYhyCGA8kojZh7Rx5eMJLeipjGHs1drEL13qnIFJFDKOwTD6xEVB6u8NZLTSShkS0m4l6BnTNNXDzMMABqV0hUD+5uoAqgQeN4pNqe+kkVWgiCMOWTMGe6UiZmqsjVITvIEG4XnQZeBUr5mlgEeZhg1Ho3FqL7+L4jUrqKw8zsljyAVmWXYd2UGvvfAD9fUkfet3Bz+/as3WfzfynDZegCT+7ARgoAJwlYDkAyQpWGWUQIOdD1BCP+muO+88XwlvTD0ySqijyAfYCUG7dbjX4g/AA5Dd0SoMAEwYSEFJCgpsF3+vf/ZXNLN8O3dhxVW80xOto+SoS2jBgvncZyAKA4/9Bw7Qzh07aOvWN1kBtI5ooSuvuJyTgW+9tYsOK+t/+PBB6mw/Sn08RrwfUbdy2yPc0IOZg89u2EYtNdrVB5iHM/2M4Td8fobHn93+Ij3LL46uxLhuXkkY95+x8RhOanj7uXuRy2uGZdgIM9fhkazLGMsW1dabE0Pg4uNZb1GOFWVwZsQoGmkG4iSbGZIBpZMo1uw0QwBAnPm3Gmc8/XtRM+XGoI4NYk9TW/HoNM+4qsal8LnvPH3T6qydoQEjE7NHPL9/n3MOyZThMzAUXhkdkjKenXNHejAGW3jKmEEqHpcAQe8FxR7TcYSfzKMomWEmsl/anZf6PryCJCs43aarpwtldI4jKt6Gif1JKy5Yei6BmsrEgAkR0CzEx4/7E95Av0bA9vJUIoMb6NPDR7jbMKnzCJPrOmh09SBX3RMGs4XTX6Ekqq4ySq0jY1RfH9MkoTFdJUkd13MIOZGMOQQlGWqPXk+Z6muopqFae33RuM6JqX3fuek3dGjbE/TDVQf+7efP7viCkeHU6SgAWwnYScESEwpIUlCUAEYMNS9evHjW1VddpZOC1dWe8gwiwiHg5wOMEugziUBRAPh7mQoFkJAEWw8GjwoTUdqAjX778P+j0YmD1HGinyfCNM64iGafs5Lmzj6bIcbyWdTvQe6BqsH2bVsZhnzxxRcoi3+Edu3aSfv37qEDKvbvOHZUeSBK+FMDfFHKimMs0Gj+2LZrHw+arGCWngTH8kVK+BjRV5JgzQhLD+HDIE/ppJNpQQJ8YQx8JguJFWsTM7WqtN8/n4Xq2rG0WCYxkFEDZZUOQCn3Za1w1I8VuL4vnBrxmG+JpcdA8gJS09dJStMlOKQ705TZMjqpFvEddBMzmu+QsaqJhJBJG48AcXYi6o/00iAj4zN4GQMi0vV8QRPG4/p3iWQUmJQidfkP+RApR4onlDHWX8KsLHW7PlE6r+CZ5CD53hFc9nj85C5UDiNTJudgPAcoKKamS2oiFAg5FIceKJLhacUwHhpVqKsHyJni37NH9dHEeu22cyiC/I+Srgpl4UE53toap/o6pagozT0Q2H7yeJKVQDTmUVljPR2N3ah8+oVU19JA0dJyjXXJpHn4LA320+o/PETff2TV//3VS9s/Zy6yHf+L8A9bAZg7yk8KSmVA8gFSGfCTgtdff/258+fNm4gLBtceC8I+hEzUAGokHOgxk3dwwZYvX84MpuDZB6nIgDXY4Pc/+yGNKzpM7ce7KVrRTFNWfJgWLlzAHYbckqtOxJ49e2nd2rW0f/8+2rdvH02bNpVWrFjOicCdO7bTnrd2G/f/sPrNbmWZBljjA7+PAY7H2o9Tu3pA2IHmA3AHwg8IL+L8Igb0RHQ9n/v1PX8iDwAnRUVxY7GjZsKLSbrFTaLNcNbFhLrbdLSBayCT1lYmwXSzkWzZLpptkGJLbVqEmVAjrZtf8DdCJ75pEBtGzESkCJlMuWGrMcqDh60kNXOPRPIRUzP3cwqRLDoT/waZBpcw/c5NyrbsWpwFycG04SmM+vBhft8Id9SAmaDgICSsHNKeL8gxg0UQvH52W8Z1N8lNnOu0KEjJcUji2ORYIiYHEI1GsgAg6YIU3gIzQQlWH8o8Y4hE5HzETM+FTElOm31NmvBk0CAHB+QZMOFePbYc1h/JQSgFfH7GiD4aX59kJYAGyag5t1VlEapTfnXrqGpqHKnsaaZPeZUed3AmuweVsFdQf8lsOtx9FjU0TaCyqgqKqdciRSVMHdd9oovv0eP7ttKXvv5PD/7XU6/8/aBylT24B8EKQMptoQrAVQLiCdggIekYtJOCI+69556Vyp1vUALvjRs3LiJYgFCosGkcgiIAgeGSJUv8zkHQG0lS8fFHfkIjo/upvfMEtcy6mOaddzlNmzrZLztiZuBzzz3HVv6IsvYIJZYuXUL7lMXfvm2ben2XEv49dFTF/X3gL8yk1MmLMJyYuQG7TiglkGEvAGU7xPu4OYtjGshTUhQzs/ii+mQk9DiujAHHyESdiElisRcQ0cSi7JYb7H0kmp2RmElne+xZkCKaulyERxBqAg3OGMYhBgcV6aEeghcgA9vl3zYj08VyCcmK8ArKe1KTl/3OmKSaKB3ZR+kWJElIRsychCiZwaG6356JSsyEILH0fHwZC90ZZySOKRtGtetuHBG/FdjzDAYiCy+OJ3QeJGNc9UjU6lCMGISjyZFwKTSeBViljRKUKoQuL0Z9OLGEYREffKTJTVD6890s0wsNBQcFn057pnSZNkogw4lGlCn7uIMQzEJprlQMmmYjKInJTb3qkeYGL4ScLFyoDlRHacz0xXTwYBnnZzABuqy6XG0fJdoSdT6qlWddSzXNjVRaXU/FFdUUSRQzMIiRh0oJVKl74uFHHv7Jvz708795a++BdGfXCRUFea7wSyIwrwKwQ4GgykBgUrC6qmr0xz7+8UuqKirKUurMT5gwgZOCDKk1Y7KkKuDyCeKBcuBZ06fzDQaQEJ6RT3hLWe/XlWsPQf7oR++iufPmchUhyVN8j9OLL7zADD9o9pkzdy7NnTuHdu/cRVu3vUm7du5kRdCBmB8jqNUdCcsOGqg9B48x3pvhumjQQQ2dqbdjfscd38gR495HY77LL6g54TIYcuKEs14IPZzPeRZTriT5/M5H+XC2jhdyabL9/wICGiIVnv26duUj2W9m74Mh+AB3aGvE789wftpgFqRb0/qctT0y4Y2EQv6WhD5czkMkW1WQ/bZpvyImHNHbJfI7iuwSiXWyBARmn3ub8ER/xvM9i4wgDT3TcpvxfE9BsCjMFWEqAp6pmJBnhTL+GTa/ro5BGThln5IyPInbK86bmogvnlDEM4JB9APfDaC42uaZNNCRZCSrp+xsWWWdUgI1fF8WFZdSUUkZJcDtrxRASVUNFSklkAGRjAqBUWrHyPtMcqDzwR89dNMvfvfEuq0790T6kJg4Of4fggTMt8KSgnbTkI0UbFaWf/JH77jjArXjUSXAGeXOR4EUZC8AGtPKB/i5AFMaxN9zlQC3qhBAkoJQHhjeAbe+vb2DbrzxRs7qC8how4YNtFE9IPz47tRp09jqv/76FvW8XYUA+3jaL3j8oroORJ3dvXT8RD+fPDxQW8WzzFq3563bo5c17j7LbhzEYhQ0DCVsTJr7OXvlmp4c9Nmw7dvbCiNhFR75sN93fzvf7wVtJ+y3w/gf8m0rbORcvv2U122gmXio9mhteU3+tp+FH9Meg+dTysEid3enjh07hpq2CByRBcA5d0px6cIJiRJ4AlACKCEXlbRSWQY9JeUYxEilSshLyquVy1+rPKBi9SihuFICpTW1VFyp3qusplhJOU/GjnP7eq/yWKP01u6dv/u3H/7wjiefXzfw1t6DqZTuuJP9CAQC5Vt2UlDgwjZ7kJsUbFm8ePHsK6+4YgG+rDRapqqqKtptlIBwCNj5AAg+uAOYd0+9d8455zAxR3NzM02aNIlDBJB3IjTAYA+pFOA1xP2g+Z49ZzaNVR7Eli2vMfhn29atPE24u/sEJ0tgDxDrITsL3nQoGHAW4nfgTeDfUAToT4gxU0+CFYAeChr1hV+e5eYaMtU4km28CWU8tm4YtwdCwoMwxSHfyyb06CTBsSnY7e8FCZXdcOV+njEHEj5Y+2s3arnHIDeL52zbngPh/r69/aABMUNKiZFseBKkMGSf7ddcohn7Ic1e9ihtm+rObwazXvcJYJ3eFbb4vb2ZTZs2dah7WiyvPd1G3BTeoUUTiqrmjyuqRP6pXElURZUSna4E1VWUKMEvp4QS7hJl5RNFFerfVVRcXsk06oliKIF6KqtvUqFAFXlxZbzU/csktz3dVKy2/uxLz93340d+9f0X1mxOHDh81E0A+vt0KgqArwdZzMGUrQxIPgBKQJKCLTfccMN5c+fMmYCLpSw6HzwE3U0K2k1DkhTEhT//Ax/gCzp+wgRuP97y6qt04UUXcZ8/Jtu+tWcPj+9i4VeeQkNjA7288WUu/W3bvp2OHj7MwzvIuHpgqC0uLmFBxwPYAVQewFEgSgCuGJSAWH4ewGkEnufUU5anMMxi2ULi3txyUwcJaZAgu8Jib9N+zRauXIJn8y/m2gdX8dj7H+a5uL/r7meYwnFbv8O2EzY8xlUYtncmSsE+rpNmXJiclAi8cFpK/kkUgHxeflPPaIz55+bpp58++sYbbwCGK3G3CL3IkITSvqs1qy1RP29cUV1RLEO1da3kdWSoTG0PWJTqmkoqKYPwK8FPlFO8qFyFBNXMFgRcQEV9C1U2j+RQAExCxeqeZrnq66Fkf8+uRx9/7OJHf//k3hfXvkJ9AwMnWf9TUQCuEpCkYBBS0FcCSAred++9l7S2tiIpmJkwcWJUTmpgv4DJBYgiADJw6ZIl/KNNyhNAow+UAb53TAn96tWrGe0HFGGFEmCM8MZYr507dqqQod2M6cpwYq0UU1LUZ2RMkgg/HmZmGgs/wgBcVDzbLrF4AvZNbFsjW9BcwXfHoLkUZbZA2VY3zAsI2n4uBSLblHHr4vba33H3P0gYXWG3j91VMEH0bvZ2Zf/tfbM9IHkv6PP2+64iFE/NDttc5WxbfRF6n9PSeKNimEQB2L+Jbcu9Ai9RCX33d7/7XfDu22w7ImgxynrPUk0TJcA7Nq013jB7bFFTfcMY8o50UU1xlO9ZMExVVyoFwJ5ApfIAKtRvl7LrX6we8ZgKX8sqqWbUWPXvWooUKU+gpJS9gEhygPYe2Pevv3jsD3/15LMvJja/ti3FY+CGIgFPSQHI50WTSXnQRQrCE/CTgkrYRv/lJz5xmXK1S5XQpydOmhRDUk80qngBchFsanEoAbj/EHC06d5z7718IfB9UHft27uXZ/ShtLN+w3rlIWyhvXv3UJcKNUDegURSWVk5C7xMShHedDygEPA6hB8XUyy+WAy5oWxrYgu7LQz5YlpZ9naClIErYEGWNCxedhVCkEDm+m6QEhmOIsr3t328QefNfc3eH9tTCZouZVt3sca2suYOwnjcB5UJslTAabb3KfwVEpqKoZLf5PBQCb7cM+r+TH35y1/evGvXLjDv2t13Yv0ZW0TZClqJpQTkdXbJJ7YWNy6aqNzk9o5IZSl6TuJ6SCyTzSiXX/1uAvG/UgRIBhYrwUcYEC9SCqGilqpGjKbiqjoVCpSzmU8pzzc90Dvw6o5tVz729HOPr3r2pcTmLVvflgcQpASCmITsyoCdFLxQXRR1faLptrY25hQcNNRaNuGG9Av0GCWAv89W7v0FF1zAsT8WKL12797N+QFUFDa9/DK9+eYbyhvABJduBtBAoMXaQ/Dr6uqYi6BKCX21En5cRHH3xdrblsMWVvtv15oHCZrrGgf9273h/Qy1fWEcYQ9ze0/ld3xBNNWHoM/a3wkLRcJCH/dG8ehkQc/1neH8RpCbb187O18jSwRfnmWUtgDRRAnI68JRIUYB9wruJYSOsPoPP/zw7v/4j/94lTTxBh425ZZwrDBmjHTpvMR6LjavmxnDGrTTUhGvWdJaOrkoHo0Bc1JVWsQEM9x+zqSyZfqeVVY+oqx/aVU1ldXUUSmqBbXNVN7QopRCAyWgBBDi9HbTiROdq59Yu/7ix554pmfj5i20/9DRjJuvOZ0l7ovNIeDSidlJwSblys+7/PLLOSmoLG9GWeCocAjYUGHWwtbUYe4rUJ8Bs/DmTZtYCYxua+OLAa/g9TfeoD1vvUVHjx5Rn+9joYFwQ/hh5SH0eEABmDlpvsUXq6/78GNDhDpI0PJl9HNlsF1L6iqR4WTFc/1uLsHPV4Gwfz/XcYUJqPu6uw9h5y6X9+F+x1bGdiJWnu1Ere1lufT1eBbX3rb88m9x9yXGl0Qx7jfcO8rad3/84x9/Tt27YNsVjn152M03bi+NhMryN+RFvICo+c5gY1m8bFJt0ajminhLRXE8BkxKVUnCJ5yBwSo1hiuaKGKLX1at7uuGEVRe10xVLW3sEcRLKyijQmBvoJfWbX718//0Hw/9w6GDB+P7Dx7O9Pb1vy0PgCibxBBF4CYFpX14SFLwphtvXK6sOZKCXtvo0ciWR/pMwsUeMCJwYQkFDhw8yChBJAJ/9KMf0TSlBFpbW2n7jh10+NAhOnL0KA/2ABeAzEYD3RgEH0hBCD5es+N8ucByw7ix5JB/6z9OEuZ87mtQSUqqBGEVgbBEl3zOFVTbU8glhGHj1sPyEfmOKUxow5a9z64rn8tjCrP4IvwJM/FJ3HxRBi5tvcT7tuCL5ReLLwrDFXwYEoSvn/3sZ9c888wzu0kLvk26Kay78ADE/beJdiVErrAeeB3KQXICWMLk019bGisaU1XUOr62eHxdeby2DF5IUVxTz6v7t7qqlHtPvEicipUSKK+toaqmEVTTOk4pg1YqrW5UoUI5JQf6qLv9aNdnvvatFc+sXrsBOLTO4yfetgKIWN+1ewZsZuHApOC99957mRLeenXCM5MnTYrKhfBRgtIvIAAh9YCl/+SnPkWblAeAC/Too4/SSKUAQBOGCoDpP9C9BErwG5Tgo6cAVr/GSvLhZrEtvmtVQoXAEHQGCXQuQREYLFmCPhQLn99ltwFCocJnhRH2d/mOymR8MJOvcJxthpXmwoQ/LJMfdG7C3g+K54POkShG3+LH9CwF+Tsm/7ZCtLRUmSzgmVj3fkP13m/uuwGTixKDgHvEThTjvvnNb36zRwn/i5Sl2ZZnPIR806bfEu9YXH4plwu3RoV5rdTITMKSp5TZFpRKVyIWSY2rKR45paFk5sjKoim1ZYkoUKYVHBIUGcWnFEOFUli1wAwowzd2AtWMHKeUQJMyNko0lXHcuOmV33z0c1+6pqe3L2mIeE8rCejfI86zmxQUuLBNLMpNQ+qktn3sYx+7XGnXEiXoKWXN4wgFOOGCcCCgdRiDORECIOP/0EMP0bFjx9gFwnck1ofAg21Y3H0oAyn34bN2cs+2Iq4gBlnvXK54Lpf8VIE8uX7L3s8wD8POyAd5AblCkyCrbC87Ox9U8XCPMwx3MJzwxd4POR5R2KK87ZDN3qYYEjvDL/0kYmzsBJ98F/eRbfFx/6j7rffmm29edQjJpSzfvi38Lu22uP8SGtvuvwi/KABRApIYjBt5ypjtYJt95veOquPsG1lV1DCtqWzhxLqSxbUlsTrQz3M3KpRAJKY8gVKqrFH3fa26/1tGUp1SAmW1LTwQtdjL0Dd/8N/3fvOhn/+b2lastqY63a3C67erAOy/gzgE3KQgK4Hx48dPvu222y4EUlBdgNTYsWPjghR0W4fxgMCjOej5559nNCAEHRcOvfhgE2pUwt+oXH24+2Lx2dVXgp+warX2zWwLRC4XdojLrV/w/45Yn7Huav8zQ4TE+Xy+2DpfzE6RyEkXL1AQrYtk7wu5v2Httw2XldfD9jP8DrFgwva5CDhOd7uuApDrxd6bFfv7Q0MdhJ4IvD241g4vZTydH+crwUEZ2Zqsm/niF7+4UYWbSPLZgi8DN4R2W4RUKgA2zt7unZH4v9J6iAIoo6GhgCiBQWv73eZ3ec5fbVlR2cT60gUzm8tXttUUzaos1sNx0h5awIupqq6GyrlvoInq2yZSRW0jHe1K0bMb3jj6z9/9v+fuP3zs9SkTx0XKy8vy9gKEXt6Q12y4sLg+wi48pH343HPPXbBy5cp5+KIS2IyK06M2sagbryEX0NnZSYcPH+ZndAxCyMEjMH36dB/QY7v6AtxxEWyBAuUIUlAuwH4vTOjybdv9jL3NXLmDfPF5mMXPZZ1zKaKgz9vbz/fbOW+egGN18QJSxrMTe/KaPNuTqSTZ5yJM5SH1fBvIIx4i7h14jSgLKyNz8Pbbb19FQ6fr2LP1IIwyZksy/0K9JSU2OzkuYTEP3KWsIhAF4IYChkTNJ/Pop6zCEUWAeX+HQes2pali5qwRFddObShdWVUSrUiC1zFRTNUNNVTZ0Eg1DfU0WNFCezMj6dCRo/TMU0/8+2OPP3H3yJEt0ZamhsyZUAC2cXPzAaIEpH14aFLwppvOV679ONCJQaDVDeAjBYOgwlAQ6Alob2/nmwW4fwg9+gWgCMTNtwE7boIt341pu8P+AQ5DyF3XOExIhmzPyw7pdLcb+rv6Q7419ehkrEDYseWqMLj7mSvnMJwsfj6F5F6bqBmHJsdjC73df2GXM90En+3u2y6/neTDtsTdFyAYhP/48eMDH/nIR558880391NW8DutvyXpB4sM4YdgitV3wT8uWE48AcmP2cIvlQEpD9qlQWxfPAFbCZyw9umYOil9Y2rLxy4YU3PVtMaSDzaUx6eAyaWiXnkCdfX043VHqGr0WTR31kzauXNn33PPrLqgJBF5YeZZk952COAFvOYSi9pJQXvcGCcFkQ9QLn29ulDps6ZNiwkiULS5nQ/o4bbdLvYAEL8g7se0IWhxsALjooqGdzPguZJUQTdxUJkul2C52woSkKDGIft77r7lev9US2nudvNZfhuAc6pJwrDKgr0tF0xlK21X+OV1vyvP84aEi7bQB7n8Mv+AeRtLdaUIlSE81L+9b3zjG69885vf3EhDh2mK8IvA2S7/IGVLfmL5sQRo46L/RAkIFsAVfvEC7HyAbE8ovvG7knPoth7ijbCnUlacqJk/pu7CJWNqPjK6ruSSY4OU+NKvtlBzSyudd+45NG7ceHBh/ro403VFXU3l2woBvJDX+fpSMLGoPXSUm4Y4KXjffZwUVBcuddb06XEIuT2Pj7O41qzBE93d7A3AK0BzEGjFcVHhEWBp3sDsjWzdjdaosEheixd4cDksaNB3PZOFd38zV3IulwCHCd+Q/RxmyTKo3GYrr3y1fBckNJz8hR1acabfqenbwm9n/+1Y3wb02KAev6wHb8C4+7INJIJhIBDjS1n41Vdfbb/55pv/0NPTI9N0XYtvu/zufD2bbFMsv5sbs8fuSW5MlIAIfhkNxQZI2CA3roQCUDiiBHopqwgEgyD7x0NAwVE5u61urjreT2zY03n10WPH6luam9lgjhs/nuKZwetG1hX97HQVQK4VhBQMIxblfMCkSZOmfuSWWy4AUhBJQbWDnBSUtmGfSsygBGH9ARDqUYoAr5973nmMEUDtHwpBbpQgEA9WkIufLzwIEp4w6xZ04+faVthnwjAAQd/NBeBxBdZ2p11sQNi+DTdn4n4mSPjdXIwIvxu+ybOd4HM79Vwwj2T35TiRD5I4X5J86r3UXXfd9fSLL76Imr5Yfdv64yGCL/P1ZKS2PWLLbfixu/2C5EBkQUICAc+VUTZEkISgVAWIskrAF3AaCkCS12w4st7XSJRqqiub+vr6L1Dn5tKmpqaLFyxY0Dxt2llvxWKRs98JBUDOwdtJwSAOAUYKLl++fNFFF144DzdKRWVluqG+PtalPAGbRWgIVNh0DSIswMVeuXIla/ixY8f6MwZyoejyxbNBwjCcGDvsxreFZTjbDgsncp50R+ixgvIS+f4O2oeg38lXwnPPry3ssh23rGd7bHbXno3ik5hehF8Ugd3Tn+BR7CU+IlRQoP/5n/+57Qtf+AJq+pLY66TgcdoiWC7G326t5cOkk62/LQcSEts5AdsbsCHCkgeQXICEEgwVpqwSkFBEHnZo4k4DsisTCIPqGxsbL541a9aNU6dO/cM7pQDk4O2kYL5pQ0AKXoCkoLq43qjRoz2UCaUy4NZzey0lgH8DHgklgBsIvQO46LhJgm7E4Sa7gixumECfClYg6DNB2x9OiHEquYBcyi1s2+75y/X5oH116/kur4JYftsjEXdfEn0i8G4pz27htbH7AuYRqw/h37t374lrrrnm8c7OzqOUFXzb5bfd/VxWnw+Nhlp9+563K6+yXCVgJwft/ID8264ICNpWFI+dGLTdfgEi2R2JQ+YA4hnnGuVylNWVAqh+pxWAffD2tKHApKC6cK333nMPJwWVUKenz5gRg5DbScEgqLAoAxwUBo3gJpg3bx5ne0UJuAIQhl4Lc+nzWUNXEMNAOacimENO5DA+l3MbecqOQUokyIIPJ8a3txtk9aU8K4LPN4k5V2LB5Xq7EHG7rGczR8t2heBFej/USj/wwAMv/fKXv0S7bpjVt5Np9jht1+rbF2A4FyNICdghgSgC9xG3nsWLIMpadAi4CLt4BEk6WQG4JKC830iEAliHTtt3UgHYJ8BNCtrEopIUHKEeTeqijbnv3nuvQFJQCXVy5syZCST9BMoZxB9gKwHwCKJhCDfCvLlz9fAIkw8YogCsncvpYtvfC6nFhykFewkgJkIUKkh2Ii78jNo8fMHLNkEnAXvy7PdJ+yznx4I0y35QiCJzgTyuIgDbksB5ZTss9MbVF8svQm63itsWHw8JIVx3H0rg8cce23vvffc9TSfH+bbgSyLNtvr2PL0gdz/XvR50i/kVThqaHLQ9ApENu1VYwoCotQ1bCYiSsl1/22MJVAD4HxLnqJy90wpADj4sKQhPAGpaOAR0UnDixKk333wztw+DUXHKlCkJ5AMGraqAPW+QQwE8G0Vx/vnnc6swXJ1p6kDlpnJvbvcGDLL+YQk/2UauxJz9mltaDFIQdvwbZIXt7Q8XyOMeTxBewf1MrtfC9tk9P7bAuy6/rSCwbJo419MTZS/WX3gkhNxEknwi+Hhub2/v/dCHPvTkrl27DtLJgu8CekTwbUBPEIc+0fCsfpgM2H+73oCtCOLOv+UzdundVgK2MrAVV04FAG9pxYoV74oCkIN2k4L2CHIBCfk9A0AKXnzRRQtwYymXJaUEOi5EIqIIBOghSkA4BFB6u+yyy/jGmKjcHIQGEiPaazgxbOgBOYChfMnEXG62+9vDBSG528nlpgdtI1eSNOhzYf92S4mu2++CeeSz4uq7EF5B7YmCt/M/dnZfevS56UsJvgr5vC9/+csbH3zwwc0Unt23k3wi+K7VFyF7u4I/5FQ6/xYFIB6BrQzsR9T5LNFQbj9XEdhzAE/iALSPBeft3VIAcgJs98clFpX24SFJQRUCjOek4KhRnrrAUbtnwKVx8isD6rlcuYOXXHIJ33zAB8AlDAIJ8Y5FTqa9CgsLbGseZtHzJeSGdbICynhh+2H/ezifC/utXPuZ63zIcnv07eYdW/hF4O3sPh5i6W2iDsn8CwknLBdq+rieQvYC4V+9evVhZfX/QLmz+3ZNPyjJN1x3/3RXJODfYhjdioH9bH/GvySUFXDX4rsjwAIVQNAOvZPLTQra7cMCFw4aNHL5iBEjGtQNkZo+fXocNwMsfUoonUxrp50P6DFKAOVASQouUvFOzAweHdbysk0sgW69dSbDrKT9GVvBhHkJ+XAFwbuZ5QTIewFyhCdD9jtHsi8oFHJdfru85yL+7KGxNpLPbtyxE30SHghPIxJYtruvrvPgbbfd9uQrr7yyj4YKfa6avuvuuwJDdOaFf8ilCPi3LeRBSsHGFviXn04W9LTzb1eR/dEUgP17YcSibvswJwXvvffeK8rUlVchwODs2bOLkA/wZw3myAdAGcyfP5+TgrAW89TfYnlO2rE8cX/QGk59PqgKEBY6hFUmhvOb+Wrz7m8FbdveVhBjsP1+GJjHfrj7ZGf2bZi3DegZtHr3pSQoBB2VpmMPwl9eXu59+9vffv2rX/3qWsqd3beTfMOt6b+by80P2IlDV/Dd9z3nQeTM/qOh1p/obSqAiLog3qmg5kIO2NZsYUhBPx8wfvz4Kbd+5CMXIymoLP6g8gSKMA1ILId9A+EZuQIpH+Jx8cUXc1IQaEEoA0kihQnTqYCBXIEeznfCvheGO5D3wspsp+q2u+/5n/E8n60o7Fjs33VjfRe/jyX1fBF+O9YX4XeRfNg3SfIJ34NN5grq7RtuuOEPSsGjKy4ouy/ufhBf3zuR5Hu7S4Q5lzJw/+1fSudv+1hyCr+7oXw7qLfw9hWAfUB226TLITBkBPmyZcvmr1y5chFuDCQFW1pa4kIsapcGbWZhyQlgXXXVVew+ovwBRSBIwVwWk3c0oFQXeECn4rKHKJ1cvxv2+aDt5VJI+X4rCEHoCr79vmvx7e2yFYfHZRFy2gAeu1tPHrLviPNh9YWgAw/AxMHHt2rVqh00vJq+CH4YOOaPLfhhKxLyb5GbIORhmCII+0zgD+XdmTOkAOyDCUoKwhOQpKB4AiOU1v/A2WefPRFJwZEjR3rqJvGTgkH8AT2mZwB/AxWGpCDcSYQFsCo2IwzvkJMwwwqi2Q4SnjBX3a3th2IEaGiM7jbmhH0+qPYe9lthAKCwbYfF+vmEPyjBZ2f2XUCPCL64+5LdtyG8P/3pT7d99rOffYmGX9MXwX8vufunsyLDfN2GfwxL+HNtPOwzCAEyZ1ABYOWaNjQELqxcwta7774bScFGdSMhKRhT8X8EQu7yB0guoM9KCqpQgpOCuMEWLVqkp9mm0/4O5RKWU11BQp0LMZevZOfuX84TO8xkX65jdUlUggTffk2Ulbj8NljHZtyV7L7NzCOoSenYk9IehH///v0nbrrppicOHjwIWq4gq+/W9F2Sjveau/921+kIX+ix5tuYG5PQGVQA9vbdpGDoCHJlFcbec889aB8uO9HVNTh37twieAFoEvL5BAUqbKy/VAbw70WLF9OUKVP4BkN5UG7YoFJZWM+AXTbMeXB5Snn2Z1whzFXey/fvfPsk3wmrOrj8CUGgHvmcbMsG84jVtxN84vLbdF12n75AeGWGA4bKfuYzn3npZz/7GSC8Ydn9oJq+m+R7J2r675WV66IP6zgjed476f0zrADs38lFLDpk0MjYsWPBKXgJpoyom2twxvTpfmVAWIX7nXxAt1EGqBhcetllTCaitsOEo0H4gDDX/qSdz5OEy/cZLHe0mHzH/a4rvPY+BI3vCtqfXO+LkNsIvzCrL7G626brTtyx3X2J8+V8i7svjTvSp69i/H133nnnU5S/pn8mILzv6+VmFYMykUPWO6AA5HeC4MKSDxAlIHRizYsXL5532WWXLcGNmIjHk6NHj07Y5UF4AQNQABIGWPkA4NqvufpqTgrOmj2bmYRtJRCEtAuy+mGIPPc95/yFJu/k/aBSXZhXErYfQa/n8mhE6G1FZGf0Xa9AXHe7W0/+Dqrny3WBsuB5905NH4+u48f7r7/hhid27959gIZf0w9rgPlzcPff8WVnFeXfZL12UqLhDCYBw/YliFjU5hDwOQWvu+6682edffYkddN5ra2tXllZGScFh3QNWqPG+ixPADfc5Zdfzjf5kiVL2BLZQzPNweZF1gWhAcOUSK73cimMoM8GCXNYCBG0TduSy+fsRJ7bn2+P6RarL7G+3a7ruvs2fl/6/qWmL4Kvzr331a9+ddN3vvOdl+lkix+U5Hs3Ibx/1itXWYFoqGeg/3hnFQBWUFLQJhYdghS86667Lh/Z2tqEQY0zZsyIqZuNk4KDufIBpm9g8uTJnBTEDQmqJNycYZ6AvXLh+N3P5cPX27/jlu9yKZXhhB5hy03uhQm/W9YTV991+d3xWnbSTyot2CaSfLa7D+v/8ssvH1WK/HEKz+6HufvvJoT3z3blcvdPqZxwhvdnOMSirATUDdV23333XVlRXl5+vKtrcOHChZwPsHHldmnQLQ+ee+653BcNoBBaicW19Q82j5st77mWOux7udzyISc5R/nvVJJ+YRUHm3rLDgXc12Uf3Y49F4TlD3JRD5utV5J89qBWM2prEEM3Nm/evJdyW/33EoT3z24FJvpC1nBPrOtReHk+637GrQzkIhYFh0BLW1vbpNtuvXWlutHiyrL3z5o1q0SUgCSkZPSz3zloFABeB0gII8WmTJ1K48aN891b/8BzuPTua0FZ/eF8N5+i8E/OMEqTQbV9G4tgE3EEWX97/4MSfEHuvo3dFy9K+vRtd18pAu/BBx98/Utf+tI6Cm7VzeXu/6nX9N9za7gK4FSE3/1erhAj7HfCkoIuXNhPCi6YP3/OFVdccQ7fuNHo4NixY7OVAYdKzEUK4ka9/vrrfXwAylBB/QL5ILf5PAN3G/mUQ9j2cvULhOUt3O8H1fftUMRO8tkWXzrzbDJO8QCEoEOQfCjtieDD6u/cubPz6quvftxAeIPadYMgvEG0XC7+vSD8p7mGowCGa8HDcgi5lECuECMsKRg0gpyTgldeccXy+fPnT1M3aqapqclTsWYMPQN+VcAaOmq3DiMfgEoAkoLoMz/vvPNYGYR1DuaD6OY8mWfg/SDvIsyLcJODQV179hKhF/y+JPiCsvt2aU+2LwQdQssFwVe/lfrkJz/5wu9///vtFBzn2zV9293/U4Pw/smtMAVwOu5+WEODu103t+AFfMbdvzBi0ZNGkN/50Y9epkKCEd3d3ckZM2bEk6lUBM1BAhISJJrtCUhlAGPHly1bxkmqJUuX+i7wSScnT33fFtBTaTgaLvrwVHIHYa6+xPtuqGOX9FzL75b2BMwjOQWU9SD8YvUR8z/66KO7PvWpTz1HQ0t6YvFl8EYQhLdQ038XVpACOFV3PyduwHktSPDzKQCsfMSiTebRrG7AUXffffdVNdXVle3t7QNLliwp7gJSECAgC5XWE5APwOMDH/gAJwUxagzEiVL6CgLhhEF0w0p3Qe/l2kYuSG8+PAGfNKcX367l29uRJJ/dp+/y8dmZfvwtIQK2Y4/aEnf/6NGj3ejYO3DgwBEKt/pBHXt/rhDe9+Q6XQUQ1poY9nc+Yc/lEeRLCrrEos2tra0Tb7/ttkuVO5pQ1r9/7ty5OilopsYIichJXgDKh+rmv/baaxkpOGfOHFYEYuX8HcwTq9uvB5Xywl7Pt23/O16WrMT+vhvjy7J78+XfIsAuO48t+DYZp8T4gt/Hsvv0RfBV6JT5/Oc/v/bHP/7xa5R76Iab5Hs/QXjfM8sW5FM5wbGQ7eQKJ8Kew14L2n6upCA8AQ4D8Kys99nXXnPNeRq2EBkcN25cUbchDR0wSkA8AHgHvZY3gJHi199wA9/cK5Yvpypl2YagAD1v6I6af3NsY4STBdE+qDDBtgXf/gxet34nUJua3zjJ5XcUwJA8gXrOmKYd5klUx9Vvsvc+itLiVrC9JlGEUCA2hBexPp6fe+65A2DnoeFDeIOSfAV3/11cZ0IBBLGV5BLu4SiEXPsaRCzqcgiwErj44ouXLV2y5GwkBRubmjLqJmUOAbd1WMhD7HAANzU8AcS1YBlGcitoWOZwvYGw93J5A7m2F5YAtN1+16uws/tBcb6UTeV8SOLPHrVlQ3jloc5j/y233LJqy5YtoOUKy+67Sb4ChPc9sFwo8HBXzPl+WCXhVKz+qYQedlLQhQv7+QD1aPnIRz6ycvy4caNPdHcn0T6shCEqRCKiCPwwwNCIiQCga3C58gBALw7EIO9kgDtvvx62cn3u7VQVTmL1sf4Wr0XadCWf4fLwuRl+m4nXbtyxJ+tC8JXr733961/fbE3WPZWafgHC+x5Yp4vpPRUFEOTGua+dauIxiFgU+QCpDIgSaFGWe8Tdd999dX19fXV7e3v/kiVLSoQyLGjUGP4WRYAHFABYhKAMMHjUFqqwNZykYNj7YR5GUO3fnTzkvu9i920wT9CYLbueL5x84u5Lkk+ad7Zt29Z+ySWX/J5OFvqgmn4uCK9H4fdJYb3D60wpAHtb+RJ7pyv87j7bHALSPhw0gry5oaFh3J133nl5sVrHjx/vX7hwYQnwAXZJqzcIH2CIRq6++mpqaWlhL6C1tTVwyIi7gkp6w830h5UZ83UYyt+yfyL09sP2fOwwyK7pC4QXYQ+svrDzICxSK3nXXXc98/zzz++ik62+m+QrQHjf42u4CsANE2LD3EaYyx+EBzjV/baTgqIEQpOCU6dOPeuGG244H99RN/jA1ClTilEZsIkpfU9AQgIVKiA5CGH48Ic+xO7vxStX8nMYV8BwcgKn6j2EJfTcz9ndjILdt5l5bFdfPB+7vCfHZI/akpq+sv7eww8/vP3++++XybpunO/W9AsQ3j+BdSYUgLty9QGcSW3vKoFcxKKsBM4777yFK1asmK+EIVNbU5NWnkEC+QBXIGwGoW5TJahV1g9wYVjDiy66iK1jLuEOE+RThRPnW7arb6P4XIvvNu3Y2X1RFra7L407eBw5cuTElVde+fhRtSh/TT/XZN0ChPc9tk43BIgGbCMfoOftuP259j8XsagkBaV7sEV5AReqmH48kILKC4hF1F1/AnMHjaBI7G9XBYRLAM1CqAggDABicDhJwNNJ8OWL+20KM9vdd1t1bSG3m3bE65HPSceeS8ZZWlKS+d9///erf/SjH71OuWv6w52sWxD899h6OwrAy7ONIIXwdtz+XPsfRiwqSUF/xoCy3C133HHHlRhBDqTgooULi0XIByQfYA8ZsfIBAA+de955jBAESAh8AkEEHKeiDIJeC2oZtpfLY+hy8dkEHeLii1KzBV+496Vjz471n3nmmb233nrrcGm57FFbBQjvn9B6O8wep4IheLc4BNxpQ/AE7EEj3DOg4tkxd370o0ws2t7R0bd0yZLSzuPH2coLlRgrABMGMKswKgNGmIAPwMBRwIbBI3Cq1v9UavtSfxdLb9fy7W49N863UXx2TV+GpEpNX5B89fX1bPVR07/xxhuffP311+2avkvQgUcBwvtnsN6uAvDy/P1uHkc+YtEGylYGWkAs+uEPfQjThmJKKAZUWFAMJdBvtbj2CkIQZUOjDIRT8Oabb2aBkSnEZ6K+b9fvbby//FuepUQnWX5/TJqD3bf79IV7H0sm68qoLTyQ5Pv617/+Mh6Uv6bfR+Gjtgo1/T+h9Y5we/0RjyUfsajdOdg8d+7cOZdfdtlSJUReVXV1sqmpyecQcFmE7FAAr0P4b7rpJnaXMXpMmHSwhpPIC+v1t11+W/CxRODt7L49FMVO7tmxv+AAhJbL5t6H5VfW/tjKlSvdmn4uWq4ChPfPZP05KQA5nnzEoqIEePjopZdccu78+fPPAqfgxEmTIvF4PCZKwE4KDmkcUh4BhA1dg5g2BBYhEImcDluP+56NMRA+Pdvaux17LnbfFn6XlksEX6y+8gRSH/zgB59Yu3YtaLmC2HnsoRsS64vgi9UvuPt/wuuMKoAg/rlcn833mbdxPMNJCvqewG233nopOAQ6OjoG5i9YUKSEiTkEBB8gcbTLJyicgvPmzWMFgMlDuY417HzZ6EKJ7W3Bt4dr2rG+zcgjfwue34Xw2u4+vJcf/OAHr3/uc59bQ/lHbdnuvp3ky9BQ4ScqCP6f3Dpj0peLvmo4LvG7NG3Ibh/2lYByi0f+xV13XamEo7Kjs7N/8eLFjBQUzkAZNWZXBkQZ4P3rrr2WlAKhSy69lIVruCGA7erLswi+O2lHBmvaSD4XyCNWX7L7wsJr1/SVkus+//zzf6uO7xiFZ/clyWeP2oLQw+q7M+gLwv8nvE5b6oZT9jrlnTmzSiAsKShwYXvwaHNDff3YO++887J4IlGETPiss88uUcJycihgdw2a+YNYt912G8fTV1xxBQte2Pmy/7bLeLb1d939oLKeW9O3ufcFwmuTcSr3P/OXf/mXz/3iF7/YRrnBPEE1/QKE9890vS0FcCaFn3fmnRs5FsQh4HIKNk+ZMmX6ddddtxwcAuVlZamRI0cmOjs7hwwYcROCwiyERplbbrmFOweBFHTZeFyhtz0AqcnbZT23Vdft1nOTfDYtFwRfGneglJ566qk9at/cmn7YjL0/p8m6hZVnnZbEnUmhH7Iz7+zIsTBiUR8lqB5N55xzzsLly5fPUUKeRkxflEhwUnBIv4CEAgYq3GvCgwkTJ9KVV15JU6dOZaCQfb7Csvs2577dsWe7+i4zj3gBkh9wJ+tKnK+203/BBRf8bv/+/Zismyu77/bpFyC875N1Kr0AvLx3SvrpHVMA8hxGLCqdg0NGjikhHqus/+CCBQsS/X19EekZAFDInjLUbf0ND2HZOedwQhDJQaETM+dtiNDbFt9F8rlTdiQEsSfu4DtC7Om6+0oBeF/5ylc2fOMb39hEuWv6BQjv+3wNR+KG8Pypmzf/XOzT2ZF3ZtyYvf9BxKIIBUQJDBk5dscdd1ze3Nxcd+zYsf5lS5eWIBQQIXSnDNlKAO+jaQiTh+ENACRk1/Fd4Q+K890knw3mcUdtweoLfBfC/9prrx1ZuXLlY3Ryj75t9XvMowDhfZ+vyCm+F1U3X5rO8HoHhd89lnzThqRzsElZ1NFICgIurKx//9w5c1gJsAsu+QAzc1AqA90mFMDx3HrrrTRq1CgGCUmpT7yBoGk7bnZfXH4RfMnuY1tI8kHwbasfj8cHlefy5MaNG/dQ8KitMHe/QMv1Pl6nogA4nv4TVQD+/lPupKB4AlwZGDNmzJQPfvCD5wMuXJRIpNra2jgp6LMKiwKwWoclFKhUsTgqA8gHzJw504/XbZffnaobNGpLFIXt7tu0XLD83/3ud7d84QtfWEvhYB47yVeg5Sosf0WG+bofS59pBfAuCb99HLmIRW2kID/ALqxc+SUgFkUDUHlZWcz1BHpkzJg0DpnOQSAFr7zqKrrwwgvZarsEHUF0XHbsL407trsvLLxQAPv37+9cunTpbyh/x55Y/QKEt7CGrHyDPOzX+PUzqQDeZeF3jyXftCGfSOT8889fvHTJkhnHjx8fnD1nTkIJZ0TYhQUlKDyC8izxO5qF5s+fT0uWLPFLemL93am6LpgHy+7YE6uvFEH69ttvf+qJJ57YRflr+kG0XDaSr+Duv4/Xu64A8k2zeRePOd+0IRsuDCKRD0yZPLkNcOHFmDbU1UUyZyCoYUjyAlh33303zxvEsq28rQDsJB+WEHTYEF7U9B955JEdH/vYx9xRW67Vd2v6Qdn9gtUvrLxVgJOm/7zdKsAfUfCDjstNCkr78ElwYeXCt95+220rW1pa6pT1H5g3f34xkIK2tbdpxW2WYWACpGlI4MM2jt9O8qGmL6O2bMFX2+5ZtmzZb5XiAYR3ODV9G8JbSPIVVuAargKQv723iwN4jygAOR43KSiVgcAR5FVVVaPvuvPOlagMYAT5hAkTiqQ8aDcLSSggCgCCraw204sfPnx4iPBLUhDLHbVlyDgzDzzwwOof/vCHMmrrVGr6BQhvYeVcw00CymunpQDeA25/ruMPSgraSMEhSkB5AOM/escdF+I7Tc3NPG0IjUNut6AdBuAZ3AFz586lgwcP+sIvuAAIPpJ8AuGF4GM24YsvvrhfhR4yaitXx14BwltYp7VOxQOQdUo64D0o9EHHGEYsasOFZdjIiOnTp5913bXXLlVCn1Z/R9OZTLTLzBnwlYChEZO/pWUYHoNYfZwbCL6M2hKrr9aAChke2759+wEaXk2/QMtVWKe1hqsAhlB9h82le49a+eGeg6BpQ1ACdlLQHzm2YsWKBcvPO29G5/Hjg8uWLi2CFyBjyP22YYMTgFJAnwA8AOnXlySfNO2Ymr731a9+dQPGbVE4C29QTb9Ay1VYp7Ui7yC0/09mRbJaK4hYVJCCUh70w4Ebrr9+ufIAxgApCA4BWHe3MsAJQvVvNBYBF8DThxMJBvMIkAcPZe2Pnn/++ULLNZzJunkhvO9k30Zh/XmsggIwyyiBIA4Bd9qQP3w0Fou13HXXXRePaGmpV+dx4Kzp04uhBDjJ57TtigLoUO+Lu29q+qmrrrrqDxs3bgQtVz7u/WFDeAvCX1jDWQUFYC1HCYRNG5KeAVYCSoBb773nnksqKyvLlFCnWlpaEjJyTAA/iPnHjhtHE1UYIKPHQSf+k5/8ZOunP/3pFyg4zj+tyboFwS+sU1kFBeAsSwnkmjYkbEKsCBobG0ff/Rd/cVFZWVmxUgAZpQziMn2YSTljMR4uioehDEtOmzbtv0kL+XBYeMMm6xbc/cJ6W6ugAJzl5APCiEXtxiEogYaRI0e2ffxjH7tQCXiJCg3SSinExfrHVcwPDADKfP/yL//yxte+9rVnaajwBzXuDHuybkH4C+t0V0EBBKwcSUHhFLSVgBCK1FVUVDTc/zd/s2LOnDmt0WjUG1QhQGlpaRQ0YSe6uvpuu/323+5Vi4YKfT53P7SmXxD8wnq7q6AAQlZIUtAeOSY5gTrzgEJAybBi7NixjZdeeukkJfilW159tWPjyy/v2bp1637Slh1CbjftDMfdP4mWqyD8hXUmVkEB5FgBSUG7Z0CUgCiCavM3Xke4EDffhfDCmkO4IeQi8EEEHXaSr+DuF9Y7vgoKIM8KUQKoDAi5KEKCSvOMR6l5P242AQGGUMuADQHx5CPoKLj7hfWOr4ICyLMCkoJ2TqCEsooAj1Lz74T5nHgAcOcFriuKwI3zCzX9wnrXV0EBDGOFKAEpEQpWQB74d9x8DgvCLFN1IOwi9GFxfqGmX1jv2ioogGEuRwnYOAHpIpRHnLLWHwsnGMIt7r3NylPI7hfWH3UVFMApLEsJ2NUB2yOQhygJLLHqIug2HVchu19Yf9RVUACnuBwl4JYKo87rWLaA2/F9Ic4vrD/6KiiA01whisAWfFsByLP7KAh+Yf1RV0EBvM3lKAL72V1DevMLgl9Y74VVUABnaEWGyYRSEPzCei+tggIorMJ6H6+CAiiswnofr4ICKKzCeh+vggIorMJ6H6+CAiiswnofr4ICKKzCeh+vggIorMJ6H6+CAiiswnofr4ICKKzCeh+vggIorMJ6H6//v506EAAAAAAQ5G89yAWRAGBMADAmABgTAIwJAMYEAGMCgDEBwJgAYEwAMCYAGBMAjAVY4CrtcW9NhQAAAABJRU5ErkJggg==')

    with open('./logo_tmp.png', 'wb') as f:
      f.write(logo_data)
    logo = wx.Image('./logo_tmp.png', wx.BITMAP_TYPE_ANY).Scale(128,128).ConvertToBitmap()
    self.logo = wx.StaticBitmap(self, -1, logo, (10, 5), (logo.GetWidth(), logo.GetHeight()))
    remove('./logo_tmp.png')
    LogoSizer.Add( self.logo, 0, wx.CENTER, 5 )
    
    RightSideBarSizer.Add( LogoSizer, 1, wx.EXPAND, 5 )
    
    MainSizer.Add( RightSideBarSizer, 1, wx.EXPAND, 5 )
    
    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    # Epilog:
    self.SetSizer( MainSizer )
    self.Layout()
    MainSizer.Fit( self )
    
    self.Centre( wx.BOTH )
  
    self.isPortsEn = lambda: self.GetMenuBar().IsChecked(self.portsEnId)
    self.GetLineSize = lambda line: "%s" % self.calc_line_size(line) 
    self.GetLineLocation = lambda line: "[" + ",".join(["(%s,%s)" % (point.x,point.y) for point in line]) + "]"
    
    menuBar.Check(self.portsEnId, True)
  
  # -------------------------------------------------------------------------------------
  def __del__( self ):
    """ MainFrame GUI destructor """

    pass
  
  # -------------------------------------------------------------------------------------
  def d2l(self, device_position):
    """ Auxiliary method, translates Device coordinates to Logical coordinates """

    logical_position_pre = self.Canvas_panel.CalcUnscrolledPosition(device_position)

    logical_position = wx.Point( logical_position_pre.x / self.Canvas_panel.GetScaleX(),
                                 logical_position_pre.y / self.Canvas_panel.GetScaleY() )

    return logical_position 
  
  # -------------------------------------------------------------------------------------
  def calc_line_size(self, line):
    """ Auxiliary method, calculates overall line size """

    point_prev = None
    size_xy = [0,0]
    for point in line:
      if point_prev:
        size_xy[0] += abs(point.x - point_prev.x)
        size_xy[1] += abs(point.y - point_prev.y)
      point_prev = point

    return str(tuple(size_xy))
  
  # -------------------------------------------------------------------------------------
  def isBetween(self, a, b, c):
    """ Auxiliary method, checks if point c is between points a and b """

    dist1 = sqrt((a.x-b.x)**2 + (a.y-b.y)**2)
    dist2 = sqrt((a.x-c.x)**2 + (a.y-c.y)**2)
    dist3 = sqrt((c.x-b.x)**2 + (c.y-b.y)**2)

    return (abs(dist1 - dist2 - dist3) < 1)
  
  # -------------------------------------------------------------------------------------
  def retrieve_user_selection(self, curr_pos):
    """ Gets input coordinates and return the selected module """

    self.Canvas_panel.selectedModule = {}
    for moduleType, ModulesDict in self.Canvas_panel.modules.iteritems():
      for moduleName, module in ModulesDict.iteritems():

        if moduleType == "Partition":
          
          x = module['Rect'].GetX()
          y = module['Rect'].GetY()
          w = module['Rect'].GetWidth()
          h = module['Rect'].GetHeight()

          if x <= curr_pos.x <= x+w and y <= curr_pos.y <= y+h:

            self.Canvas_panel.selectedModule['Name'] = moduleName
            self.Canvas_panel.selectedModule['Type'] = moduleType
            self.Canvas_panel.selectedModule['Rect'] = module['Rect']
            self.Canvas_panel.selectedModule['Ports'] = module['Ports']
            self.AddModule_choice.SetSelection(self.AddModule_choiceChoices.index(moduleType))
            return
        
        if moduleType == "Link":

          if self.isBetween(module['Line'][0], module['Line'][1], curr_pos):
            self.Canvas_panel.selectedModule['Name'] = moduleName
            self.Canvas_panel.selectedModule['Type'] = moduleType
            self.Canvas_panel.selectedModule['Line'] = module['Line']
            self.AddModule_choice.SetSelection(self.AddModule_choiceChoices.index(moduleType))
            return

  # -------------------------------------------------------------------------------------
  def clear_info(self):
    """ Auxiliary method which clears the Information panel, on the right sidebar """

    self.infoModuleName_textCtrl.Clear()
    self.infoModuleType_textCtrl.Clear()
    self.infoModuleLocation_textCtrl.Clear()
    self.infoModuleSize_textCtrl.Clear()
    self.infoModulePorts_textCtrl.Clear()
    
  # -------------------------------------------------------------------------------------
  def OnModuleNameTextEnter(self, evt):
    """ Callback function, called when typing 'Enter' in the naming text-box  """

    moduleName = self.infoModuleName_textCtrl.GetValue()
    moduleType = self.AddModule_choiceChoices[self.AddModule_choice.GetSelection()]

    # Rename an existing entry:
    if bool(self.Canvas_panel.selectedModule) and self.Canvas_panel.selectedModule['Type'] == moduleType:
      
      self.Canvas_panel.modules[moduleType][moduleName] = self.Canvas_panel.modules[moduleType][self.Canvas_panel.selectedModule['Name']]
      del self.Canvas_panel.modules[moduleType][self.Canvas_panel.selectedModule['Name']]
      self.Canvas_panel.selectedModule['Name'] = moduleName
    
    # New entry:
    else:

      self.Canvas_panel.modules[moduleType][moduleName] = {}

      if moduleType == "Partition":
        self.Canvas_panel.modules[moduleType][moduleName]['Rect'] = self.Canvas_panel.RectLast
        self.Canvas_panel.modules[moduleType][moduleName]['Ports'] = ""
        self.Canvas_panel.RectLast = None

        if self.isPortsEn():
          dlg = wx.TextEntryDialog(self, "Ports Defintion (array;names): ", defaultValue='2x1;AF0,AF1')
          dlg.ShowModal()
          ports_str = dlg.GetValue()
          dlg.Destroy()
          if ports_str:
            self.Canvas_panel.modules[moduleType][moduleName]['Ports'] = "(%s)" % ports_str

      elif moduleType == "Link":
        self.Canvas_panel.modules[moduleType][moduleName]['Line'] = self.Canvas_panel.LinesLast
        self.Canvas_panel.LineLast = None
        self.Canvas_panel.LinesLast = []
    
    self.Canvas_panel.Refresh()

  # -------------------------------------------------------------------------------------
  def OnPaint(self, evt):
    """ Callback function, called when MainFrame needs to re-paint itself, e.g. invoked by self.Canvas_panel.Refresh() """

    dc = wx.PaintDC(self.Canvas_panel)
    self.Canvas_panel.DoPrepareDC(dc)
  
    # Refresh modules:
    self.infoPartitionsNum_textCtrl.SetValue("0")

    for moduleType, ModulesDict in self.Canvas_panel.modules.iteritems():
      for moduleName, module in ModulesDict.iteritems():
        
        if moduleType == "Partition" and 'Rect' in module:

          dc.SetPen(wx.BLACK_PEN)
          if bool(self.Canvas_panel.selectedModule) and self.Canvas_panel.selectedModule['Name'] == moduleName: 
            dc.SetBrush(wx.YELLOW_BRUSH)
          else:
            dc.SetBrush(wx.WHITE_BRUSH)
        
          x = module['Rect'].GetX()
          y = module['Rect'].GetY()
          w = module['Rect'].GetWidth()
          h = module['Rect'].GetHeight()

          dc.DrawRoundedRectangle(x, y, w, h, 10)
          dc.DrawText(moduleName, x+w/2-10 ,y+h/2)

        elif moduleType == "Link" and 'Line' in module:

          if bool(self.Canvas_panel.selectedModule) and self.Canvas_panel.selectedModule['Name'] == moduleName: 
            dc.SetPen(wx.YELLOW_PEN)
          else:
            dc.SetPen(wx.BLACK_PEN)
          dc.DrawLines(module['Line'])

          # Update line's name:
          x1 = module['Line'][0].x
          y1 = module['Line'][0].y
          x2 = module['Line'][1].x
          y2 = module['Line'][1].y
          angle_rad = -atan2(y2-y1, x2-x1)
          angle_deg = degrees(angle_rad)

          dc.DrawRotatedText(moduleName, (x1+x2)/2 ,(y1+y2)/2, angle_deg)
        
      if moduleType == "Partition":
        self.infoPartitionsNum_textCtrl.SetValue(str(len(self.Canvas_panel.modules[moduleType].keys())))
      
      elif moduleType == "Link":
        self.infoLinksNum_textCtrl.SetValue(str(len(self.Canvas_panel.modules[moduleType].keys())))

    # Refresh info-bar:
    if bool(self.Canvas_panel.selectedModule):

      self.infoModuleName_textCtrl.SetValue(self.Canvas_panel.selectedModule['Name'])
      self.infoModuleType_textCtrl.SetValue(self.Canvas_panel.selectedModule['Type'])

      if self.Canvas_panel.selectedModule['Type'] == "Partition": 

        moduleLocation = "%s" % self.Canvas_panel.selectedModule['Rect'].GetPosition()
        moduleSize = "%s" % self.Canvas_panel.selectedModule['Rect'].GetSize()
        modulePorts = "%s" % self.Canvas_panel.selectedModule['Ports']
      
      elif self.Canvas_panel.selectedModule['Type'] == "Link": 

        moduleLocation = self.GetLineLocation(self.Canvas_panel.selectedModule['Line'])
        moduleSize = self.GetLineSize(self.Canvas_panel.selectedModule['Line'])
        modulePorts = ""
      
      self.infoModuleLocation_textCtrl.SetValue(moduleLocation)
      self.infoModuleSize_textCtrl.SetValue(moduleSize)
      self.infoModulePorts_textCtrl.SetValue(modulePorts)

    # Highlight last (temporary) rectangle:
    if self.Canvas_panel.RectLast and not bool(self.Canvas_panel.selectedModule):

      dc.SetPen(wx.BLACK_PEN)
      dc.SetBrush(wx.LIGHT_GREY_BRUSH)
      dc.DrawRoundedRectangle(self.Canvas_panel.RectLast.x,
                              self.Canvas_panel.RectLast.y,
                              self.Canvas_panel.RectLast.width,
                              self.Canvas_panel.RectLast.height, 
                              10)
      moduleType = self.AddModule_choiceChoices[self.AddModule_choice.GetSelection()]
      moduleLocation = "%s" % self.Canvas_panel.RectLast.GetPosition()
      moduleSize = "%s" % self.Canvas_panel.RectLast.GetSize()
      self.infoModuleType_textCtrl.SetValue(moduleType)
      self.infoModuleLocation_textCtrl.SetValue(moduleLocation)
      self.infoModuleSize_textCtrl.SetValue(moduleSize)
      self.infoModulePorts_textCtrl.SetValue("")
    
    # Highlight last (temporary) line:
    lines = list(self.Canvas_panel.LinesLast)
    if self.Canvas_panel.LineLast:
      if self.Canvas_panel.LinesLast:
        lines.append(self.Canvas_panel.LineLast[1])
      else:
        lines = self.Canvas_panel.LineLast

    if lines and not bool(self.Canvas_panel.selectedModule):

      dc.SetPen(wx.GREY_PEN)
      dc.DrawLines(lines)
      moduleType = self.AddModule_choiceChoices[self.AddModule_choice.GetSelection()]
      moduleLocation = self.GetLineLocation(lines)
      moduleSize = self.GetLineSize(lines)
      self.infoModuleType_textCtrl.SetValue(moduleType)
      self.infoModuleLocation_textCtrl.SetValue(moduleLocation)
      self.infoModuleSize_textCtrl.SetValue(moduleSize)
      self.infoModulePorts_textCtrl.SetValue("")

  # -------------------------------------------------------------------------------------
  def OnLeftDown(self, evt):
    """ Callback function, called when the left mouse button changed to down """
    
    self.Canvas_panel.CaptureMouse()
    self.Canvas_panel.selectionStart = self.d2l(evt.Position)
    self.retrieve_user_selection(self.d2l(evt.Position))

  # -------------------------------------------------------------------------------------
  def OnLeftUp(self, evt):
    """ Callback function, called when the left mouse button changed to up """
    
    if self.Canvas_panel.HasCapture():
      
      self.Canvas_panel.ReleaseMouse()
      
      moduleType = self.AddModule_choiceChoices[self.AddModule_choice.GetSelection()]

      if bool(self.Canvas_panel.selectedModule):
        modultType = self.Canvas_panel.selectedModule['Type']

      if moduleType == "Partition":
        self.Canvas_panel.RectLast = wx.RectPP(self.Canvas_panel.selectionStart, self.d2l(evt.Position))
        self.Canvas_panel.selectionStart = None

      elif moduleType == "Link":
        state = wx.GetMouseState()
        endpoint = self.d2l(evt.Position) 
        if state.ControlDown():
          endpoint = self.Canvas_panel.LineLast[1]
        self.Canvas_panel.LineLast = [self.Canvas_panel.selectionStart, endpoint]
        if bool(self.Canvas_panel.LinesLast):
          self.Canvas_panel.LinesLast.append(endpoint)
        else:
          self.Canvas_panel.LinesLast = self.Canvas_panel.LineLast
        self.Canvas_panel.selectionStart = endpoint
      
      self.Canvas_panel.Refresh()
  
  # -------------------------------------------------------------------------------------
  def OnMotion(self, evt):
    """ Callback function, called when the mouse is in motion """
    
    state = wx.GetMouseState()

    if evt.Dragging() and evt.LeftIsDown() and self.Canvas_panel.selectionStart:

      moduleType = self.AddModule_choiceChoices[self.AddModule_choice.GetSelection()]

      if bool(self.Canvas_panel.selectedModule):
        modultType = self.Canvas_panel.selectedModule['Type']
      
      if moduleType == "Partition":
        
        if bool(self.Canvas_panel.selectedModule):
          w = self.Canvas_panel.selectedModule['Rect'].GetWidth()
          h = self.Canvas_panel.selectedModule['Rect'].GetHeight()
          startpoint = (self.d2l(evt.Position).x - w/2, self.d2l(evt.Position).y - h/2)
          endpoint = (self.d2l(evt.Position).x + w/2, self.d2l(evt.Position).y + h/2)
          dragged_rect = wx.RectPP(startpoint, endpoint)
          self.Canvas_panel.modules[moduleType][self.Canvas_panel.selectedModule['Name']]['Rect'] = dragged_rect
          self.Canvas_panel.selectedModule['Rect'] = dragged_rect
        
        else:
          self.infoModuleName_textCtrl.Clear()
          self.Canvas_panel.RectLast = wx.RectPP(self.Canvas_panel.selectionStart, self.d2l(evt.Position))
      
      elif moduleType == "Link":

        delta_x = self.d2l(evt.Position).x - self.Canvas_panel.selectionStart.x
        delta_y = self.d2l(evt.Position).y - self.Canvas_panel.selectionStart.y

        if bool(self.Canvas_panel.selectedModule):
          
          dragged_line = list(self.Canvas_panel.selectedModule['Line'])
          for point in dragged_line:
            point.x += delta_x
            point.y += delta_y

          self.Canvas_panel.selectionStart = self.d2l(evt.Position) 
          self.Canvas_panel.modules[moduleType][self.Canvas_panel.selectedModule['Name']]['Line'] = dragged_line
          self.Canvas_panel.selectedModule['Line'] = dragged_line 
        
        else:

          endpoint = self.d2l(evt.Position) 
          
          if state.ControlDown():
            if abs(delta_x) > abs(delta_y):
              endpoint.y = self.Canvas_panel.selectionStart.y
            else:
              endpoint.x = self.Canvas_panel.selectionStart.x

          self.Canvas_panel.LineLast = [self.Canvas_panel.selectionStart, endpoint]

      self.Canvas_panel.Refresh()
  
  # -------------------------------------------------------------------------------------
  def OnDuplicateModule(self, evt):
    """ Callback function, called when clicking on the 'Duplicate Module' button """
       
    if bool(self.Canvas_panel.selectedModule):
      
      moduleType = self.Canvas_panel.selectedModule['Type']
      moduleName = self.Canvas_panel.selectedModule['Name']
      moduleNameList = moduleName.split('-')
      
      for k in range(1,1000):
        moduleNameNew = "%s-%d" % (moduleNameList[0], k)
        if moduleNameNew not in self.Canvas_panel.modules[moduleType]:
          break

      if moduleType == "Partition": 
        self.Canvas_panel.modules[moduleType][moduleNameNew] = {}
        self.Canvas_panel.modules[moduleType][moduleNameNew]['Rect'] = wx.RectPP((self.Canvas_panel.selectedModule['Rect'].x + 100,
                                                                                  self.Canvas_panel.selectedModule['Rect'].y + 100),
                                                                                 (self.Canvas_panel.selectedModule['Rect'].x + 100 + self.Canvas_panel.selectedModule['Rect'].width, 
                                                                                  self.Canvas_panel.selectedModule['Rect'].y + 100 + self.Canvas_panel.selectedModule['Rect'].height)) 
        self.Canvas_panel.modules[moduleType][moduleNameNew]['Ports'] = self.Canvas_panel.selectedModule['Ports']
      
      elif moduleType == "Link":
        self.Canvas_panel.modules[moduleType][moduleNameNew] = {}
        self.Canvas_panel.modules[moduleType][moduleNameNew]['Line'] = []
        for point in self.Canvas_panel.modules[moduleType][moduleName]['Line']:
          self.Canvas_panel.modules[moduleType][moduleNameNew]['Line'].append(wx.Point(point.x+100, point.y+100))
      
      self.Canvas_panel.RectLast = None
      self.Canvas_panel.LineLast = None
      self.Canvas_panel.LinesLast = []
      self.Canvas_panel.selectedModule = {}
      self.Canvas_panel.Refresh()

  # -------------------------------------------------------------------------------------
  def OnDeleteModule(self, evt):
    """ Callback function, called when clicking on the 'Delete Module' button """
       
    if bool(self.Canvas_panel.selectedModule):
      
      moduleType = self.Canvas_panel.selectedModule['Type']
      del self.Canvas_panel.modules[moduleType][self.Canvas_panel.selectedModule['Name']]
      self.Canvas_panel.selectedModule = {}
      self.Canvas_panel.Refresh()
 
  # -------------------------------------------------------------------------------------
  def OnAddModuleChoice(self, evt):
    """ Callback function, called when item in the 'Add Module' list is selected """
       
    self.Canvas_panel.RectLast = None
    self.Canvas_panel.LineLast = None
    self.Canvas_panel.LinesLast = []
    self.Canvas_panel.Refresh()
    self.clear_info()
 
  # -------------------------------------------------------------------------------------
  def OnNew(self, evt):
    """ Callback function, called when clicking on the 'New' button """

    warningMsg = "Are you sure you wish to start a new canvas?\n" + \
                 "The existing canvas will be deleted!"
    d = wx.MessageDialog( self, warningMsg, "Warning", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
    answer = d.ShowModal()
    d.Destroy()
    if answer == wx.ID_OK:
      self.Canvas_panel.modules = {}
      for choice in self.AddModule_choiceChoices:
        self.Canvas_panel.modules[choice] = {}
      
      self.Canvas_panel.RectLast = None
      self.Canvas_panel.LineLast = None
      self.Canvas_panel.LinesLast = []
      self.Canvas_panel.selectionStart = None
      self.Canvas_panel.selectedModule = {}
      self.Canvas_panel.Refresh()
  
  # -------------------------------------------------------------------------------------
  def OnOpen(self, evt):
    """ Callback function, called when clicking on the 'Open' button """

    wildcard = "LayoutAssistance Pickle (*.pkl)|*.pkl|" \
               "PLIST files (*.plist)|*.plist|" \
               "All files (*.*)|*.*"

    dlg = wx.FileDialog( self, message="Open file ...", 
                         defaultDir=getcwd(), 
                         defaultFile="", wildcard=wildcard, style=wx.FD_OPEN )

    if dlg.ShowModal() == wx.ID_OK:
      path = dlg.GetPath()
      with open(path, 'rb') as filehandle:
        self.Canvas_panel.modules = load(filehandle)
    dlg.Destroy()

    self.Canvas_panel.RectLast = None
    self.Canvas_panel.LineLast = None
    self.Canvas_panel.LinesLast = []
    self.Canvas_panel.selectionStart = None
    self.Canvas_panel.selectedModule = {}
    self.Canvas_panel.Refresh()
  
  # -------------------------------------------------------------------------------------
  def OnSave(self, evt):
    """ Callback function, called when clicking on the 'Save' button 
        (Note: High-Sierra users will get an exception here, but it may be ignored) """

    wildcard = "LayoutAssistance Pickle (*.pkl)|*.pkl|" \
               "PLIST files (*.plist)|*.plist|" \
               "All files (*.*)|*.*"

    dlg = wx.FileDialog( self, message="Save file as ...", 
                         defaultDir=getcwd(), 
                         defaultFile="", wildcard=wildcard, style=wx.FD_SAVE )

    if dlg.ShowModal() == wx.ID_OK:
      path = dlg.GetPath()
      with open(path, 'wb') as filehandle:
        dump(self.Canvas_panel.modules, filehandle, HIGHEST_PROTOCOL)
    dlg.Destroy()
  
  # -------------------------------------------------------------------------------------
  def OnDumpLayout(self, evt):
    """ Callback function, called when clicking on the 'Dump Layout' button """
    
    partitions_num = self.infoPartitionsNum_textCtrl.GetValue()
    links_num = self.infoLinksNum_textCtrl.GetValue()

    YELLOW = "\033[1;33m"
    BOLD    = "\033[;1m"
    RESET = "\033[0;0m"

    print "%s#Partition:%s %s" % (YELLOW, RESET, partitions_num)
    print "%s#Links:%s %s" % (YELLOW, RESET, links_num)

    for moduleType, ModulesDict in self.Canvas_panel.modules.iteritems():
      for moduleName, module in ModulesDict.iteritems():
        
        if moduleType == "Partition":
          moduleLocation =  module['Rect'].GetPosition()
          moduleSize = module['Rect'].GetSize()
          modulePorts =  module['Ports']
          
          print "%sType%s: %10s,\t %sName%s: %10s,\t %sSize%s: %10s,\t %sLocation%s: %10s,\t %sPorts%s: %s" \
              % (BOLD, RESET, moduleType, BOLD, RESET, moduleName, BOLD, RESET, moduleSize, BOLD, RESET, moduleLocation, BOLD, RESET, modulePorts)
        
        elif moduleType == "Link":
          moduleLocation = self.GetLineLocation(module['Line'])
          moduleSize = self.GetLineSize(module['Line'])
          
          print "%sType%s: %10s,\t %sName%s: %10s,\t %sSize%s: %10s,\t %sLocation%s: %s" \
              % (BOLD, RESET, moduleType, BOLD, RESET, moduleName, BOLD, RESET, moduleSize, BOLD, RESET, moduleLocation)
          
        else:
          continue
         
  # -------------------------------------------------------------------------------------
  def OnExit(self, evt):
    """ Callback function, called when clicking on the 'Exit' button """

    warningMsg = "Are you sure you wish to exit?\n" + \
                 "The existing canvas will be deleted!"
    d = wx.MessageDialog( self, warningMsg, "Warning", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
    answer = d.ShowModal()
    d.Destroy()
    if answer == wx.ID_OK:
      self.Destroy()
  
  # -------------------------------------------------------------------------------------
  def OnKeyUP(self, evt):
    """ Callback function, called when keyboard key is released """

    keyCode = evt.GetKeyCode()

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. --
    if keyCode == wx.WXK_ESCAPE:

      self.Canvas_panel.RectLast = None
      self.Canvas_panel.LineLast = None
      self.Canvas_panel.LinesLast = []
      self.Canvas_panel.selectionStart = None
      self.Canvas_panel.selectedModule = {}
      self.Canvas_panel.Refresh()

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. --
    elif keyCode == wx.WXK_NUMPAD_DELETE or \
         keyCode == wx.WXK_DELETE or \
         keyCode == wx.WXK_BACK:

      if bool(self.Canvas_panel.selectedModule):
        moduleType = self.Canvas_panel.selectedModule['Type']
        moduleName = self.Canvas_panel.selectedModule['Name']
        del self.Canvas_panel.modules[moduleType][moduleName]
        self.Canvas_panel.RectLast = None
        self.Canvas_panel.LineLast = None
        self.Canvas_panel.LinesLast = []
        self.Canvas_panel.selectionStart = None
        self.Canvas_panel.selectedModule = {}
        self.Canvas_panel.Refresh()

      elif self.Canvas_panel.LinesLast:
        self.Canvas_panel.LinesLast.pop()
        self.Canvas_panel.Refresh()

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. --
    elif keyCode == wx.WXK_TAB:

      self.OnDuplicateModule(evt)

    evt.Skip()  

  # -------------------------------------------------------------------------------------
  def OnCanvasSize(self, evt):
    """ Callback function, called when clicking on the 'Canvas Size' button (from MenuBar) """

    dlg = wx.TextEntryDialog(self, "Canvas Size: ", defaultValue='(10000,10000)')
    dlg.ShowModal()
    canvasSize = eval(dlg.GetValue())
    dlg.Destroy()

    self.Canvas_panel.SetScrollbars(self.ppu_x, self.ppu_y, canvasSize[0]/self.ppu_x, canvasSize[1]/self.ppu_y)
    self.Canvas_panel.Layout()
 
  # -------------------------------------------------------------------------------------
  def OnZoomIn(self, evt):
    """ Callback function, called when clicking on the 'Zoom In' button (from MenuBar) """
      
    self.Canvas_panel.SetScale(2.0,2.0) 
    self.Canvas_panel.Refresh()

  # -------------------------------------------------------------------------------------
  def OnZoomOut(self, evt):
    """ Callback function, called when clicking on the 'Zoom In' button (from MenuBar) """
      
    self.Canvas_panel.SetScale(0.5,0.5) 
    self.Canvas_panel.Refresh()
  
  # -------------------------------------------------------------------------------------
  def OnZoom(self, evt):
    """ Callback function, called when clicking on the 'Zoom' button (from MenuBar) """
      
    dlg = wx.TextEntryDialog(self, "Zoom Factor: ", defaultValue='1.0')
    dlg.ShowModal()
    scl = eval(dlg.GetValue())
    dlg.Destroy()
      
    self.Canvas_panel.SetScale(scl,scl) 
    self.Canvas_panel.Refresh()
  
  # -------------------------------------------------------------------------------------
  def OnZoomActual(self, evt):
    """ Callback function, called when clicking on the 'Zoom In' button (from MenuBar) """
    
    self.Canvas_panel.SetScale(1.0,1.0) 
    self.Canvas_panel.Refresh()
  
  # -------------------------------------------------------------------------------------
  def OnUsage(self, evt):
    """ Callback function, called when clicking on the 'Usage' button (from MenuBar) """

    UsageMsg = "(-) Use the 'Module Type' choice-box to select the desired Module type\n\n" + \
               "(-) Use the mouse to draw the selected Module, finish registering the Module by entering a name to it (+Enter)\n\n" + \
               "(-) Use the mouse to select and drag Modules\n\n" + \
               "(-) Hold the CMD key while drawing Links, in order to keep the lines straight\n\n" + \
               "(-) Hold the CMD key while drawing Links, in order to keep the lines straight\n\n" + \
               "(-) Use the ESC key for cancelling an ongoing drawing\n\n" + \
               "(-) Use the Backspace key for cancelling last marked point in an ongoing Link drawing\n\n" + \
               "(-) Use the 'Duplicate Module' button or the 'TAB' key for duplicating a selected module\n\n" + \
               "(-) Use the 'Delete Module' button or the 'Backspace' key for removing selected modules\n\n" + \
               "(-) Use the 'Dump Layout' button for printint out the layout content (to stdout)\n\n" + \
               "(-) Use the 'Load'/'Save' buttons to hold and resume your work\n\n" + \
               "(-) Use the 'View' Menu options to control the zoom over the canvas\n\n" + \
               "(-) Use the 'Ports Enabling' menu option to control Partitions behavior (contains Ports or not)\n\n" + \
               "(-) Use the 'Canvas Size' menu option for modifying the canvas size"

    d = wx.MessageDialog(self, UsageMsg, "Usage", wx.OK|wx.ICON_INFORMATION)
    d.ShowModal()
    d.Destroy()
  
  # -------------------------------------------------------------------------------------
  def OnAbout(self, evt):
    """ Callback function, called when clicking on the 'About' button (from MenuBar) """

    AboutMsg = "Layout Assistant tool, created by Shahar Gino on November-2017"

    d = wx.MessageDialog(self, AboutMsg, "About", wx.OK|wx.ICON_INFORMATION)
    d.ShowModal()
    d.Destroy()

# ===============================================================================================================
#  __  __       _
# |  \/  | __ _(_)_ __       Main script starts here
# | |\/| |/ _` | | '_ \      (if not importing the MainFrame class
# | |  | | (_| | | | | |      directly from external script/app)
# |_|  |_|\__,_|_|_| |_|

if __name__ == '__main__':

  if version_info[0] != 2:
    print "This application requires Python 2, while Python %d.%d has been detected" % (version_info[0],version_info[1])
    exit(0)

  app = wx.App(False)
  frame = MainFrame(None)
  frame.Show()
  app.MainLoop()

