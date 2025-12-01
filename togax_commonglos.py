import toga
from toga.style.pack import COLUMN, ROW, Pack
from toga_iOS.window import MainWindow as MainWindow_Impl
from toga.window import MainWindow
from toga_iOS.container import ControlledContainer, NavigationContainer, Container
from toga_iOS.libs import UIScrollView, UIViewAutoresizing, UIView, UINavigationController, UIViewController, UIColor, UIWindow, UIScreen, UITabBarController, UITabBarItem, UIApplication, UIScreen, NSNotificationCenter, uikit
from rubicon.objc import NSMakeSize, CGRectMake, objc_method, objc_property, SEL, send_super, CGSize, NSObject, ObjCInstance, objc_const, ObjCClass
UIDeviceOrientationDidChangeNotification = objc_const(uikit, "UIDeviceOrientationDidChangeNotification")
UIDevice = ObjCClass("UIDevice")
import toga_iOS.factory
from enum import Enum
import platform

class TabType(Enum):
    NORMAL = 1
    SCROLL = 2
    WEB = 3

UIScrollViewContentInsetAdjustmentAlways = 3

class GlosScrollView(UIScrollView):
    container = objc_property(object, weak=True)

    @objc_method
    def safeAreaInsetsDidChange(self):
        send_super(__class__, self, "safeAreaInsetsDidChange")
        self.performSelector(SEL("refreshContent"), withObject=None, afterDelay=0)

    @objc_method
    def refreshContent(self):
        if self.container:
            if self.container.content:
                self.container.content.interface.refresh()
                self.container.refreshed()

class Scroll_ContainerMixin:
    def _prep_natives(self):
        self.contain_native = self.native
        self.scroll = GlosScrollView.alloc().init()
        self.scroll.container = self
        # Suspect this is a native bug... I've set everything up as documented.
        # But it's quite trivial to fix and there are no horizontal insets anyways so...
        self.scroll.contentInsetAdjustmentBehavior = UIScrollViewContentInsetAdjustmentAlways
        self.contain_native.addSubview(self.scroll)
        self.scroll.translatesAutoresizingMaskIntoConstraints = True
        self.scroll.autoresizingMask = (
            UIViewAutoresizing.FlexibleWidth | UIViewAutoresizing.FlexibleHeight
        )
        # aka. document container!
        self.native = UIView.alloc().init()
        self.native.translatesAutoresizingMaskIntoConstraints = True
        self.native.autoresizingMask = (
            UIViewAutoresizing.FlexibleWidth | UIViewAutoresizing.FlexibleHeight
        )
        self.scroll.addSubview(self.native)
    
    @property
    def top_offset(self):
        return 0
    
    @property
    def width(self):
        return self.scroll.safeAreaLayoutGuide.layoutFrame.size.width
    
    @property
    def height(self):
        # Squish all widgets to the minimum since I'm too lazy
        # to do math
        return 0

class NavigationScrollContainer(Scroll_ContainerMixin, NavigationContainer):
    def __init__(
        self,
        content=None,
        layout_native=None,
        on_refresh=None,
    ):
        super().__init__(
            content=content,
            layout_native=layout_native,
            on_refresh=on_refresh,
        )
        self._prep_natives()
        self.layout_native = self.native if layout_native is None else layout_native

class GlosScroll_Container(Scroll_ContainerMixin, ControlledContainer):
    def __init__(
        self,
        content=None,
        layout_native=None,
        on_refresh=None,
    ):
        super().__init__(
            content=content,
            layout_native=layout_native,
            on_refresh=on_refresh,
        )
        self._prep_natives()
        self.layout_native = self.native if layout_native is None else layout_native

class ScrollMainWindow_Impl(MainWindow_Impl):
    def create_container(self):
        # NavigationScrollContainer provides a titlebar for the window,
        # with "Liquid Glass" scrolling.
        self.container = NavigationScrollContainer(on_refresh=self.content_refreshed)
    
    def content_refreshed(self, container):
        # Do not make horizontally scrollable
        width = self.container.width
        height = self.interface.content.layout.height
        self.container.scroll.contentSize = NSMakeSize(width, height)
        self.container.native.frame = CGRectMake(0, 0, width, height)
        

toga_iOS.factory._glos_ScrollMainWindow = ScrollMainWindow_Impl

class ScrollMainWindow(MainWindow):
    _WINDOW_CLASS = "_glos_ScrollMainWindow"

class OffsetlessNavigationContainer(NavigationContainer):
    @property
    def top_offset(self):
        return 0

class OffsetlessControlledContainer(ControlledContainer):
    @property
    def top_offset(self):
        return 0

class WebMainWindow_Impl(MainWindow_Impl):
    def create_container(self):
        self.container = OffsetlessNavigationContainer(on_refresh=self.content_refreshed)

toga_iOS.factory._glos_WebMainWindow = WebMainWindow_Impl

class __WebMainWindow(MainWindow):
    _WINDOW_CLASS = "_glos_WebMainWindow"

def create_webview_window(*args, **kwargs):
    window = __WebMainWindow()
    window.content = toga.WebView(*args, **kwargs)
    return window

class GlosViewController(UIViewController):
    container = objc_property(object, weak=True)

    @objc_method
    def viewSafeAreaInsetsDidChange(self):
        send_super(__class__, self, "viewSafeAreaInsetsDidChange")
        self.performSelector(SEL("refreshContent"), withObject=None, afterDelay=0)

    @objc_method
    def refreshContent(self):
        if self.container:
            if self.container.content:
                self.container.content.interface.refresh()
                self.container.refreshed()

class OrientationMonitor(NSObject):

    @objc_method
    def deviceOrientationDidChange_(self, notification):
        self.performSelector(SEL("refreshContent"), withObject=None, afterDelay=0)

    
    @objc_method
    def refreshContent(self):
        if hasattr(toga.App.app.main_window, "refresh_content"):
            toga.App.app.main_window.refresh_content()

MONITOR = OrientationMonitor.alloc().init()

center = NSNotificationCenter.defaultCenter
center.addObserver_selector_name_object_(
    MONITOR,
    SEL("deviceOrientationDidChange:"),   # selector
    UIDeviceOrientationDidChangeNotification,
    None
)
UIDevice.currentDevice.beginGeneratingDeviceOrientationNotifications()

class SafeBottomContainer(Container):
    
    def __init__(
        self,
        content=None,
        layout_native=None,
        on_refresh=None,
    ):
        super().__init__(
            content=content,
            layout_native=layout_native,
            on_refresh=on_refresh,
        )
        self.controller = GlosViewController.alloc().init()
        self.controller.container = self
        self.controller.view = self.native
        self._top_offset = 0

    @property
    def height(self):
        if platform.system() == "iPadOS":
            return super().height
        return super().height - self.native.safeAreaInsets.bottom
    
    @property
    def top_offset(self):
        if platform.system() == "iPadOS":
            return self.layout_native.safeAreaInsets.top
        return self._top_offset

class GlosTabBarController(UITabBarController):
    impl = objc_property(object, weak=True)

    @objc_method
    def tabBarController_didSelectViewController_(self, contr, vc) -> None:
#        print("DID SEL")
        # An item that actually on the tab bar has been selected
        self.performSelector(SEL("refreshContent"), withObject=None, afterDelay=0)
    
    @objc_method
    def refreshContent(self) -> None:
        # Find the currently visible container, and refresh layout of the content.
        for container in self.impl.subconts:
            if container.controller == self.selectedViewController:
#                print("REFRESH", container)
                container.content.interface.refresh()
                container.refreshed()

class OptionWindow_Impl(MainWindow_Impl):
    def set_tabs(self, tabs):
        subconts = []
        controllers = []
        if len(tabs) > 4:
            raise RuntimeError("Handling more tabs is not supported")
        for tab in tabs:
            if tab[3] == TabType.NORMAL:
                container = SafeBottomContainer(on_refresh=self.content_refreshed)
                container.content = tab[0]._impl
#            elif tab[3] == TabType.NORMAL_FULL:
#                container = ControlledContainer(on_refresh=self.content_refreshed)
                container.content = tab[0]._impl
            elif tab[3] == TabType.SCROLL:
                container = GlosScroll_Container(on_refresh=self.content_refreshed)
                container.content = tab[0]._impl
            else:
                container = OffsetlessControlledContainer(on_refresh=self.content_refreshed)
                container.content = toga.WebView(*tab[0][0], **tab[0][1])._impl
            container.enabled = True
            subconts.append(container)
            controllers.append(container.controller)
            self.setup_tab(container, tab[1], tab[2])
            container._top_offset = UIApplication.sharedApplication.statusBarFrame.size.height + self.nav.navigationBar.frame.size.height
        
        self.tabbar_controller.setViewControllers(
            controllers,
            animated=False,
        )
        for subcont in subconts:
            subcont.content.interface.refresh()
        self.subconts = subconts
    def __init__(self, interface, title, position, size):
        self.interface = interface
        self.interface._impl = self
        
        self.native = UIWindow.alloc().initWithFrame(UIScreen.mainScreen.bounds)
        
        tabbar_controller = GlosTabBarController.alloc().init()
        tabbar_controller.impl = self
        tabbar_controller.delegate = tabbar_controller
        tabbar_controller.view.translatesAutoresizingMaskIntoConstraints = True
        tabbar_controller.view.autoresizingMask = (
            UIViewAutoresizing.FlexibleWidth | UIViewAutoresizing.FlexibleHeight
        )
        self.nav = UINavigationController.alloc().initWithRootViewController(
            tabbar_controller
        )
        
        self.native.rootViewController = self.nav
        
        # Set the background color of the root content.
        try:
            # systemBackgroundColor() was introduced in iOS 13
            # We don't test on iOS 12, so mark the other branch as nocover
            self.native.backgroundColor = UIColor.systemBackgroundColor()
        except AttributeError:  # pragma: no cover
            self.native.backgroundColor = UIColor.whiteColor

        self.set_title(title)
        
        self.tabbar_controller = tabbar_controller
    
    def content_refreshed(self, container):
        container.min_width = container.content.interface.layout.min_width
        container.min_height = container.content.interface.layout.min_height
#        print(container.content.interface.layout.height)
        if hasattr(container, "scroll"):
            width = container.width
#            print(container.content)
#            print("==0:", container.height)
            height = container.content.interface.layout.height
#            print(width, height)
            container.scroll.contentSize = NSMakeSize(width, height)
            container.native.frame = CGRectMake(0, 0, width, height)
    
    def setup_tab(self, container, text, icon):
        # Create a UITabViewItem for the content
        container.icon = icon

        container.controller.tabBarItem = UITabBarItem.alloc().initWithTitle(
            text,
            image=(
                icon if icon else toga.Icon.OPTION_CONTAINER_DEFAULT_TAB_ICON
            )._impl.native,
            tag=0,
        )
    
    def get_title(self):
        return str(self.nav.topViewController.title)

    def set_title(self, title):
        self.nav.topViewController.title = title
    
    def refresh_content(self):
#        print("REFRESH")
        for subcont in self.subconts:
            subcont.content.interface.refresh()

toga_iOS.factory._glos_OptionWindow = OptionWindow_Impl

class OptionWindow(MainWindow):
    _WINDOW_CLASS = "_glos_OptionWindow"
    def __init__(self, tabs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._impl.set_tabs(tabs)
    def refresh_content(self):
        self._impl.refresh_content()
        
__all__ = ["OptionWindow", "create_webview_window", "ScrollMainWindow", "TabType"]
